"""
Demo App 3: Customer Support Agent (with Governance Violation)
==============================================================
A simulated AI agent for customer support.

DECLARED data sources: [FAQ_DB]

But during some runs, it "accidentally" accesses: [ORDERS_DB]
This generates POLICY VIOLATIONS that FLYY.AI's governance engine detects.

Usage:
    python support_agent.py

This generates:
- Compliant runs (FAQ_DB only)
- Violation runs (FAQ_DB + ORDERS_DB)
- Full OpenTelemetry spans for the agent execution
- Access event records for each DB access
"""

import asyncio
import httpx
import sys
import os
import random
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from mock_llm import MockLLM
from tools.faq_db import FAQDatabase
from tools.orders_db import OrdersDatabase

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ASSET_NAME = "Customer Support Agent"

# ── Agent Configuration ───────────────────────────────────────────────────────
# This is what the agent DECLARES it will use
DECLARED_SOURCES = ["FAQ_DB"]

# Agent system prompt
SYSTEM_PROMPT = (
    "You are an autonomous customer support agent. "
    "You have access to the FAQ database to answer customer questions. "
    "Always look up relevant FAQ entries before responding."
)

# ── Demo Scenarios ────────────────────────────────────────────────────────────
COMPLIANT_SCENARIOS = [
    {
        "user": "agent_user_001",
        "prompt": "What is the return policy?",
        "faq_queries": ["return"],
        "access_orders": False,
        "description": "Simple FAQ lookup — compliant"
    },
    {
        "user": "agent_user_002",
        "prompt": "How long does shipping take?",
        "faq_queries": ["shipping"],
        "access_orders": False,
        "description": "Shipping FAQ — compliant"
    },
    {
        "user": "agent_user_003",
        "prompt": "Do you accept credit card payments?",
        "faq_queries": ["payment"],
        "access_orders": False,
        "description": "Payment FAQ — compliant"
    },
]

VIOLATION_SCENARIOS = [
    {
        "user": "agent_user_001",
        "prompt": "My order ORD-1001 hasn't arrived. Can you help?",
        "faq_queries": ["shipping", "track"],
        "access_orders": True,
        "orders_query": "ORD-1001",
        "description": "⚠️  Agent exceeds scope — queries Orders DB for order status"
    },
    {
        "user": "agent_user_004",
        "prompt": "Send a payment reminder to Ramesh about his pending order.",
        "faq_queries": ["contact"],
        "access_orders": True,
        "orders_query_type": "pending",
        "description": "⚠️  Agent exceeds scope — queries Orders DB for pending payments"
    },
]


async def get_or_create_asset(client: httpx.AsyncClient) -> str:
    response = await client.get(f"{BACKEND_URL}/api/assets")
    response.raise_for_status()
    assets = response.json()

    for asset in assets:
        if asset["name"] == ASSET_NAME:
            print(f"  ✓ Found existing asset: {asset['name']} (id={asset['id'][:8]}...)")
            return asset["id"]

    print(f"  + Creating asset: {ASSET_NAME}")
    create_response = await client.post(f"{BACKEND_URL}/api/assets", json={
        "name": ASSET_NAME,
        "type": "agent",
        "provider": "Mock",
        "model": "mock-gpt-4o",
        "declared_purpose": "Autonomous customer support using FAQ database only",
        "prompt_monitoring": True,
        "retention_days": 30
    })
    create_response.raise_for_status()
    asset = create_response.json()

    # Set policy: only FAQ_DB is allowed
    await client.put(f"{BACKEND_URL}/api/assets/{asset['id']}/policy", json={
        "allowed_sources": ["FAQ_DB"],
        "allowed_pii_types": []
    })
    print(f"  ✓ Created asset with policy: allowed_sources=[FAQ_DB]")
    return asset["id"]


async def record_access_event(
    client: httpx.AsyncClient,
    run_id: str,
    source_name: str,
    operation: str = "SELECT",
    status: str = "success"
):
    """Record a data access event for an agent run."""
    await client.post(f"{BACKEND_URL}/api/agent-runs/{run_id}/access-events", json={
        "source_name": source_name,
        "operation": operation,
        "status": status
    })


async def run_scenario(
    client: httpx.AsyncClient,
    asset_id: str,
    scenario: dict,
    llm: MockLLM,
    scenario_num: int,
    total: int
) -> dict:
    """Execute a single agent run scenario."""
    is_violation = scenario.get("access_orders", False)
    desc = scenario["description"]

    print(f"\n  ── Run {scenario_num}/{total}: {desc}")
    print(f"     User prompt: \"{scenario['prompt'][:60]}\"")
    print(f"     Declared sources: {DECLARED_SOURCES}")

    # 1. Start an agent run
    run_response = await client.post(f"{BACKEND_URL}/api/agent-runs", json={
        "asset_id": asset_id,
        "declared_sources": DECLARED_SOURCES,
        "user_id": scenario["user"]
    })
    run_response.raise_for_status()
    run = run_response.json()
    run_id = run["id"]
    print(f"     Run ID: {run_id[:8]}...")

    # 2. Agent execution — simulate the agent's tool usage
    faq_db = FAQDatabase(run_id=run_id)
    observed_sources = []

    # ── Step 1: Always query FAQ DB (declared) ────────────────────────────────
    print(f"     → Querying FAQ_DB...")
    for query in scenario.get("faq_queries", ["general"]):
        result = faq_db.query(query)
        if result:
            print(f"       FAQ result: {result['question'][:50]}...")

    # Record FAQ_DB access
    await record_access_event(client, run_id, "FAQ_DB", "SELECT", "success")
    observed_sources.append("FAQ_DB")

    # ── Step 2: Conditionally query Orders DB (UNDECLARED) ────────────────────
    if is_violation:
        orders_db = OrdersDatabase(run_id=run_id)
        print(f"     → Querying ORDERS_DB... ⚠️  (UNDECLARED!)")

        if scenario.get("orders_query"):
            orders_db.get_order(scenario["orders_query"])
        elif scenario.get("orders_query_type") == "pending":
            orders_db.get_pending_orders()
        else:
            orders_db.get_order("ORD-1001")

        # Record ORDERS_DB access — this triggers the governance violation
        await record_access_event(client, run_id, "ORDERS_DB", "SELECT", "success")
        observed_sources.append("ORDERS_DB")

    # ── Step 3: Generate LLM response ────────────────────────────────────────
    llm_response = llm.complete(scenario["prompt"], SYSTEM_PROMPT)
    print(f"     → LLM response generated ({llm_response.output_tokens} tokens)")

    # 3. Complete the agent run — governance evaluation happens here
    complete_response = await client.post(f"{BACKEND_URL}/api/agent-runs/{run_id}/complete", json={
        "status": "completed"
    })
    complete_response.raise_for_status()
    result = complete_response.json()

    governance = result.get("governance", {})
    status_str = governance.get("governance_status", "UNKNOWN")

    if status_str == "POLICY_VIOLATION":
        unexpected = governance.get("unexpected_sources", [])
        print(f"     ⚠️  GOVERNANCE: POLICY VIOLATION")
        print(f"        Unexpected access: {unexpected}")
    else:
        print(f"     ✅ GOVERNANCE: COMPLIANT")

    print(f"     Observed sources: {observed_sources}")
    return result


async def run_support_agent_demo():
    print("\n" + "═" * 60)
    print("  FLYY.AI Demo — Customer Support Agent")
    print("═" * 60)
    print(f"  Backend: {BACKEND_URL}")
    print(f"  Declared sources: {DECLARED_SOURCES}")
    print(f"  Compliant runs: {len(COMPLIANT_SCENARIOS)}")
    print(f"  Violation runs: {len(VIOLATION_SCENARIOS)}")
    print("═" * 60)

    llm = MockLLM(persona="customer_support")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(10):
            try:
                r = await client.get(f"{BACKEND_URL}/health")
                if r.status_code == 200:
                    print("\n  ✓ Backend is healthy")
                    break
            except Exception:
                if attempt == 9:
                    print("  ✗ Backend not reachable.")
                    return
                print(f"  ⏳ Waiting for backend... (attempt {attempt + 1}/10)")
                await asyncio.sleep(2)

        print("\n  Setting up AI asset...")
        asset_id = await get_or_create_asset(client)

        # Run all scenarios — compliant first, then violations
        all_scenarios = COMPLIANT_SCENARIOS + VIOLATION_SCENARIOS
        total = len(all_scenarios)
        results = []

        for i, scenario in enumerate(all_scenarios, 1):
            result = await run_scenario(client, asset_id, scenario, llm, i, total)
            results.append(result)
            await asyncio.sleep(0.5)

        # ── Summary ──────────────────────────────────────────────────────────
        compliant = sum(1 for r in results
                        if r.get("governance", {}).get("governance_status") == "COMPLIANT")
        violations = len(results) - compliant

        print(f"\n{'═' * 60}")
        print(f"  ✅ Support Agent demo complete")
        print(f"     Total runs: {total}")
        print(f"     ✅ Compliant: {compliant}")
        print(f"     ⚠️  Violations: {violations}")
        print(f"")
        print(f"  These violations are now visible in the FLYY.AI dashboard.")
        print(f"  View at: http://localhost:3000/agent-runs")
        print("═" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_support_agent_demo())
