"""
API Integration Tests

Tests the full FastAPI request-response cycle against an in-memory SQLite database.
Validates the complete pipeline: request → PII detection → DB write → response.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_asset(client):
    resp = await client.post("/api/assets", json={
        "name": "Test Support AI",
        "type": "llm",
        "provider": "Mock",
        "model": "mock-gpt-4o",
        "prompt_monitoring": True,
        "retention_days": 30
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Support AI"
    assert data["prompt_monitoring"] is True
    return data["id"]


@pytest.mark.asyncio
async def test_interaction_with_pii(client):
    # Create asset first
    asset_resp = await client.post("/api/assets", json={
        "name": "PII Test Asset",
        "type": "llm",
        "prompt_monitoring": True,
        "retention_days": 30
    })
    asset_id = asset_resp.json()["id"]

    # Send interaction with PII
    resp = await client.post("/api/interactions", json={
        "asset_id": asset_id,
        "user_id": "test_user",
        "prompt": "Call Ramesh at 9876543210 about his invoice",
        "model": "mock-gpt-4o",
        "input_tokens": 10,
        "output_tokens": 20,
        "latency_ms": 100
    })
    assert resp.status_code == 200
    data = resp.json()

    # Raw PII must not appear in sanitized prompt
    assert "9876543210" not in (data.get("sanitized_prompt") or "")
    assert "<PHONE>" in (data.get("sanitized_prompt") or "")

    # PII counts must be recorded
    assert "PHONE" in data["pii_detected"]
    assert data["pii_detected"]["PHONE"] == 1


@pytest.mark.asyncio
async def test_interaction_monitoring_off(client):
    # Create asset with monitoring OFF
    asset_resp = await client.post("/api/assets", json={
        "name": "No Monitor Asset",
        "type": "llm",
        "prompt_monitoring": False,
        "retention_days": 7
    })
    asset_id = asset_resp.json()["id"]

    resp = await client.post("/api/interactions", json={
        "asset_id": asset_id,
        "user_id": "test_user",
        "prompt": "Call Ramesh at 9876543210",
        "model": "mock-gpt-4o",
        "input_tokens": 5,
        "output_tokens": 10,
        "latency_ms": 80
    })
    assert resp.status_code == 200
    data = resp.json()

    # Prompt must be null when monitoring is disabled
    assert data["sanitized_prompt"] is None
    # PII metadata must also be empty (no processing)
    assert data["pii_detected"] == {}


@pytest.mark.asyncio
async def test_interaction_clean_prompt(client):
    asset_resp = await client.post("/api/assets", json={
        "name": "Clean Test Asset",
        "type": "llm",
        "prompt_monitoring": True,
        "retention_days": 30
    })
    asset_id = asset_resp.json()["id"]

    clean_prompt = "What is the return policy for electronics?"
    resp = await client.post("/api/interactions", json={
        "asset_id": asset_id,
        "prompt": clean_prompt,
        "model": "mock-gpt-4o",
        "input_tokens": 8,
        "output_tokens": 50,
        "latency_ms": 120
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["pii_detected"] == {}
    assert data["sanitized_prompt"] == clean_prompt


@pytest.mark.asyncio
async def test_agent_run_compliant(client):
    asset_resp = await client.post("/api/assets", json={
        "name": "Agent Test Asset",
        "type": "agent",
        "prompt_monitoring": True,
        "retention_days": 30
    })
    asset_id = asset_resp.json()["id"]

    # Create run
    run_resp = await client.post("/api/agent-runs", json={
        "asset_id": asset_id,
        "declared_sources": ["FAQ_DB"]
    })
    assert run_resp.status_code == 200
    run_id = run_resp.json()["id"]

    # Record FAQ_DB access
    await client.post(f"/api/agent-runs/{run_id}/access-events", json={
        "source_name": "FAQ_DB",
        "operation": "SELECT",
        "status": "success"
    })

    # Complete run
    complete_resp = await client.post(f"/api/agent-runs/{run_id}/complete")
    assert complete_resp.status_code == 200
    data = complete_resp.json()

    assert data["violation"] is False
    assert data["governance_result"]["governance_status"] == "COMPLIANT"


@pytest.mark.asyncio
async def test_agent_run_violation(client):
    asset_resp = await client.post("/api/assets", json={
        "name": "Violating Agent Asset",
        "type": "agent",
        "prompt_monitoring": True,
        "retention_days": 30
    })
    asset_id = asset_resp.json()["id"]

    # Create run
    run_resp = await client.post("/api/agent-runs", json={
        "asset_id": asset_id,
        "declared_sources": ["FAQ_DB"]
    })
    run_id = run_resp.json()["id"]

    # Record FAQ_DB (expected) + ORDERS_DB (unexpected)
    await client.post(f"/api/agent-runs/{run_id}/access-events", json={
        "source_name": "FAQ_DB", "operation": "SELECT", "status": "success"
    })
    await client.post(f"/api/agent-runs/{run_id}/access-events", json={
        "source_name": "ORDERS_DB", "operation": "SELECT", "status": "success"
    })

    # Complete run
    complete_resp = await client.post(f"/api/agent-runs/{run_id}/complete")
    data = complete_resp.json()

    assert data["violation"] is True
    assert data["governance_result"]["governance_status"] == "POLICY_VIOLATION"
    assert "ORDERS_DB" in data["governance_result"]["unexpected_sources"]


@pytest.mark.asyncio
async def test_overview_analytics(client):
    resp = await client.get("/api/analytics/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_assets" in data
    assert "total_interactions" in data
    assert "total_pii_incidents" in data
    assert "total_violations" in data
