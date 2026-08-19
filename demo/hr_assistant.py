"""
Demo App 2: HR Assistant
========================
A simulated HR assistant LLM application.
Handles policy questions — no PII expected.

Usage:
    python hr_assistant.py

This generates:
- Clean interactions (no PII)
- Policy-based responses
- Demonstrates monitoring of a compliant AI asset
"""

import asyncio
import httpx
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from mock_llm import MockLLM

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ASSET_NAME = "HR Assistant"

SYSTEM_PROMPT = (
    "You are an internal HR assistant for a company. "
    "Answer employee queries about policies, benefits, leaves, "
    "onboarding, and company procedures. Be professional and concise. "
    "Never share confidential employee data."
)

DEMO_INTERACTIONS = [
    {"user": "emp_001", "prompt": "What is the company's annual leave policy?"},
    {"user": "emp_002", "prompt": "How many sick days am I entitled to per year?"},
    {"user": "emp_003", "prompt": "What health insurance benefits does the company provide?"},
    {"user": "emp_004", "prompt": "When is the annual salary review conducted?"},
    {"user": "emp_001", "prompt": "What is the work from home policy?"},
    {"user": "emp_005", "prompt": "How do I apply for maternity leave?"},
    {"user": "emp_002", "prompt": "What is the learning and development budget?"},
    {"user": "emp_003", "prompt": "How many days is the onboarding program?"},
    {"user": "emp_006", "prompt": "What is the notice period for resignation?"},
    {"user": "emp_004", "prompt": "Does the company offer flexible working hours?"},
    {"user": "emp_001", "prompt": "How do I submit a reimbursement claim?"},
    {"user": "emp_007", "prompt": "What are the company's public holidays this year?"},
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
        "type": "llm",
        "provider": "Mock",
        "model": "mock-gpt-4o",
        "declared_purpose": "Answer employee HR policy queries about leave, benefits, and procedures",
        "prompt_monitoring": True,
        "retention_days": 7
    })
    create_response.raise_for_status()
    asset = create_response.json()
    print(f"  ✓ Created asset: {asset['name']} (id={asset['id'][:8]}...)")
    return asset["id"]


async def run_hr_assistant_demo():
    print("\n" + "═" * 60)
    print("  FLYY.AI Demo — HR Assistant")
    print("═" * 60)
    print(f"  Backend: {BACKEND_URL}")
    print(f"  Interactions to send: {len(DEMO_INTERACTIONS)}")
    print("═" * 60 + "\n")

    llm = MockLLM(persona="hr")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(10):
            try:
                r = await client.get(f"{BACKEND_URL}/health")
                if r.status_code == 200:
                    print("  ✓ Backend is healthy\n")
                    break
            except Exception:
                if attempt == 9:
                    print("  ✗ Backend not reachable.")
                    return
                print(f"  ⏳ Waiting for backend... (attempt {attempt + 1}/10)")
                await asyncio.sleep(2)

        print("  Setting up AI asset...")
        asset_id = await get_or_create_asset(client)
        print()

        for i, interaction in enumerate(DEMO_INTERACTIONS, 1):
            prompt = interaction["prompt"]
            user = interaction["user"]
            truncated = prompt[:55] + "..." if len(prompt) > 55 else prompt
            print(f"  [{i:2d}/{len(DEMO_INTERACTIONS)}] {user}: \"{truncated}\"")

            llm_response = llm.complete(prompt, SYSTEM_PROMPT)

            result = await client.post(f"{BACKEND_URL}/api/interactions", json={
                "asset_id": asset_id,
                "user_id": user,
                "prompt": prompt,
                "model": llm_response.model,
                "input_tokens": llm_response.input_tokens,
                "output_tokens": llm_response.output_tokens,
                "latency_ms": llm_response.latency_ms,
                "status": "success"
            })
            result.raise_for_status()
            data = result.json()

            pii = data.get("pii_detected", {})
            if pii:
                print(f"         ⚠️  Unexpected PII: {list(pii.keys())}")
            else:
                print(f"         ✅ Clean — no PII (as expected for HR queries)")

            await asyncio.sleep(0.3)

        print(f"\n{'═' * 60}")
        print(f"  ✅ HR Assistant demo complete")
        print(f"     Interactions sent: {len(DEMO_INTERACTIONS)}")
        print(f"     Expected PII: 0 (HR policy queries are clean)")
        print("═" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_hr_assistant_demo())
