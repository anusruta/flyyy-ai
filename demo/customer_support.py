"""
Demo App 1: Customer Support AI
================================
A simulated customer support LLM application.
Sends interactions to the FLYY.AI monitoring backend.

Usage:
    python customer_support.py

This generates:
- Interactions WITH PII (names, phones, emails)
- Interactions WITHOUT PII (clean queries)
- OpenTelemetry spans for observability research
"""

import asyncio
import httpx
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from mock_llm import MockLLM

# ── Configuration ────────────────────────────────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ASSET_NAME = "Customer Support AI"
USER_ALIASES = ["user_cs_001", "user_cs_002", "user_cs_003", "user_cs_004"]

# System prompt for this AI application
SYSTEM_PROMPT = (
    "You are a helpful customer support assistant for an e-commerce company. "
    "Answer customer queries about orders, returns, shipping, and products. "
    "Be concise and professional."
)

# Demo prompts — mix of PII and non-PII
DEMO_INTERACTIONS = [
    # ── PII-containing prompts ────────────────────────────────────────────────
    {
        "user": "user_cs_001",
        "prompt": "Send a reminder to Ramesh at 9876543210 about his pending invoice."
    },
    {
        "user": "user_cs_002",
        "prompt": "My order hasn't arrived. Contact Priya Sharma at priya.sharma@company.com about refund."
    },
    {
        "user": "user_cs_001",
        "prompt": "Please update the delivery address for Vikram Singh, phone 8765432109, to 45 MG Road Bangalore."
    },
    {
        "user": "user_cs_003",
        "prompt": "Send confirmation email to ananya.patel@gmail.com for order ORD-1004."
    },
    {
        "user": "user_cs_004",
        "prompt": "Ramesh Kumar called on 9012345678 asking about PAN card ABCDE1234F verification for order."
    },
    {
        "user": "user_cs_002",
        "prompt": "Contact John at john.doe@company.com and +91-9876543211 regarding his warranty claim."
    },
    {
        "user": "user_cs_001",
        "prompt": "Escalate complaint from Suresh (9123456780) about damaged product ORD-2021."
    },
    # ── Clean prompts (no PII) ────────────────────────────────────────────────
    {
        "user": "user_cs_003",
        "prompt": "What is the return policy for electronics?"
    },
    {
        "user": "user_cs_004",
        "prompt": "How long does standard shipping take?"
    },
    {
        "user": "user_cs_001",
        "prompt": "Do you offer express delivery?"
    },
    {
        "user": "user_cs_002",
        "prompt": "What payment methods are accepted?"
    },
    {
        "user": "user_cs_003",
        "prompt": "Is there a warranty on the products?"
    },
    {
        "user": "user_cs_004",
        "prompt": "How can I track my order?"
    },
    {
        "user": "user_cs_001",
        "prompt": "Can I cancel an order after placing it?"
    },
    {
        "user": "user_cs_002",
        "prompt": "What are your customer support hours?"
    },
]


async def get_or_create_asset(client: httpx.AsyncClient) -> str:
    """Get the Customer Support AI asset ID, creating it if necessary."""
    response = await client.get(f"{BACKEND_URL}/api/assets")
    response.raise_for_status()
    assets = response.json()

    for asset in assets:
        if asset["name"] == ASSET_NAME:
            print(f"  ✓ Found existing asset: {asset['name']} (id={asset['id'][:8]}...)")
            return asset["id"]

    # Create if not found
    print(f"  + Creating asset: {ASSET_NAME}")
    create_response = await client.post(f"{BACKEND_URL}/api/assets", json={
        "name": ASSET_NAME,
        "type": "llm",
        "provider": "Mock",
        "model": "mock-gpt-4o",
        "declared_purpose": "Handle customer queries about orders, returns, shipping, and products",
        "prompt_monitoring": True,
        "retention_days": 30
    })
    create_response.raise_for_status()
    asset = create_response.json()
    print(f"  ✓ Created asset: {asset['name']} (id={asset['id'][:8]}...)")
    return asset["id"]


async def send_interaction(
    client: httpx.AsyncClient,
    asset_id: str,
    user_id: str,
    prompt: str,
    llm: MockLLM
) -> dict:
    """Send a single interaction through the FLYY.AI monitoring pipeline."""
    # Run the mock LLM (generates realistic token count + latency)
    llm_response = llm.complete(prompt, SYSTEM_PROMPT)

    # POST to backend — PII detection + redaction happens INSIDE the backend
    # before any database write. We never store the raw prompt ourselves.
    payload = {
        "asset_id": asset_id,
        "user_id": user_id,
        "prompt": prompt,             # raw prompt — backend will redact this
        "model": llm_response.model,
        "input_tokens": llm_response.input_tokens,
        "output_tokens": llm_response.output_tokens,
        "latency_ms": llm_response.latency_ms,
        "status": "success"
    }

    response = await client.post(f"{BACKEND_URL}/api/interactions", json=payload)
    response.raise_for_status()
    return response.json()


async def run_customer_support_demo():
    print("\n" + "═" * 60)
    print("  FLYY.AI Demo — Customer Support AI")
    print("═" * 60)
    print(f"  Backend: {BACKEND_URL}")
    print(f"  Interactions to send: {len(DEMO_INTERACTIONS)}")
    print("═" * 60 + "\n")

    llm = MockLLM(persona="customer_support")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Wait for backend
        for attempt in range(10):
            try:
                r = await client.get(f"{BACKEND_URL}/health")
                if r.status_code == 200:
                    print("  ✓ Backend is healthy\n")
                    break
            except Exception:
                if attempt == 9:
                    print("  ✗ Backend not reachable. Start it with: cd backend && uvicorn app.main:app")
                    return
                print(f"  ⏳ Waiting for backend... (attempt {attempt + 1}/10)")
                await asyncio.sleep(2)

        # Get or create asset
        print("  Setting up AI asset...")
        asset_id = await get_or_create_asset(client)
        print()

        # Send interactions
        pii_count = 0
        clean_count = 0

        for i, interaction in enumerate(DEMO_INTERACTIONS, 1):
            prompt = interaction["prompt"]
            user = interaction["user"]
            truncated = prompt[:55] + "..." if len(prompt) > 55 else prompt
            print(f"  [{i:2d}/{len(DEMO_INTERACTIONS)}] {user}: \"{truncated}\"")

            result = await send_interaction(client, asset_id, user, prompt, llm)

            pii = result.get("pii_detected", {})
            if pii:
                pii_str = ", ".join(f"<{k}>" for k in pii.keys())
                print(f"         🔐 PII detected: {pii_str}")
                print(f"         📝 Stored: \"{result.get('sanitized_prompt', '')[:55]}...\"")
                pii_count += 1
            else:
                print(f"         ✅ No PII detected — prompt stored as-is")
                clean_count += 1

            await asyncio.sleep(0.3)

        print(f"\n{'═' * 60}")
        print(f"  ✅ Customer Support AI demo complete")
        print(f"     Interactions sent: {len(DEMO_INTERACTIONS)}")
        print(f"     PII incidents: {pii_count}")
        print(f"     Clean interactions: {clean_count}")
        print("═" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_customer_support_demo())
