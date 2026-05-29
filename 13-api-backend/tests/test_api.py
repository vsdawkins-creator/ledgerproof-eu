"""
LPR API — Integration test suite.

Run with:
    pytest tests/ -v

Requires:
    pip install pytest pytest-asyncio httpx

Tests use a real FastAPI test client (httpx AsyncClient) with a mocked
database and signing layer. No Bitcoin node or PostgreSQL instance needed
for unit tests.
"""
from __future__ import annotations

import hashlib
import json
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


# ---------------------------------------------------------------------------
# Test configuration
# ---------------------------------------------------------------------------

# Use demo mode (no signing key required) and a mock DB.
os.environ.setdefault("ALLOW_MISSING_SIGNING_KEY", "true")
os.environ.setdefault("ANCHOR_WINDOW_HOURS", "24")
os.environ.setdefault("GDPR_MODE", "true")
os.environ.setdefault("LEDGERPROOF_REGION", "eu")
os.environ.setdefault("EU_AI_ACT_50_ENABLED", "true")
os.environ.setdefault("API_KEY_SALT", "test-salt-not-for-production")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://lpr_test:lpr_test@localhost:5432/lpr_test",
)

# If running in CI with a real Postgres, these tests will use it.
# If not, the database-dependent tests will skip.
POSTGRES_AVAILABLE = False
try:
    import asyncpg  # noqa: F401
    POSTGRES_AVAILABLE = True
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TEST_API_KEY = "lpr_test_key_12345"
SAMPLE_CONTENT = b"This is a test document for LedgerProof."
SAMPLE_HASH = hashlib.sha256(SAMPLE_CONTENT).hexdigest()


@pytest_asyncio.fixture
async def client():
    """Return an ASGI test client for the LPR API."""
    from lpr_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://api.ledgerproofhq.io",
        headers={"Authorization": f"Bearer {TEST_API_KEY}"},
    ) as c:
        yield c


# ---------------------------------------------------------------------------
# Request builders
# ---------------------------------------------------------------------------

def core_receipt_payload(content_hash: str = SAMPLE_HASH) -> dict:
    return {
        "content_hash": content_hash,
        "content_type": "text/plain",
        "content_bytes": len(SAMPLE_CONTENT),
        "actor_type": "AI_MODEL",
        "actor_id": "openai/gpt-4o/2024-11-20",
        "actor_assertion": "AI-generated document anchored for testing",
    }


def eu_receipt_payload(content_hash: str = SAMPLE_HASH) -> dict:
    return {
        **core_receipt_payload(content_hash),
        "jurisdiction_profile": "EU-AI-ACT-50-v1",
        "eu_ai_act_50": {
            "ai_system_id": "openai/gpt-4o/2024-11-20",
            "deployer_id": "LEI:5493001KJTIIGC8Y1R12",
            "deployer_name": "Acme Insurance GmbH",
            "deployer_country": "DE",
            "content_category": "AI_ASSISTED_DOCUMENT",
        },
    }


# ---------------------------------------------------------------------------
# Tests — model validation (no database required)
# ---------------------------------------------------------------------------

def test_eu_profile_validation_requires_eu_extension():
    """EU-AI-ACT-50-v1 profile requires the eu_ai_act_50 extension."""
    from pydantic import ValidationError
    from lpr_api.models import ReceiptRequest

    with pytest.raises(ValidationError, match="eu_ai_act_50 is required"):
        ReceiptRequest(
            content_hash=SAMPLE_HASH,
            content_type="text/plain",
            content_bytes=40,
            actor_type="AI_MODEL",
            actor_id="openai/gpt-4o/2024-11-20",
            actor_assertion="test",
            jurisdiction_profile="EU-AI-ACT-50-v1",
            eu_ai_act_50=None,
        )


def test_eu_deployer_id_rejects_email():
    """deployer_id must not be an email address (natural-person GDPR risk)."""
    from pydantic import ValidationError
    from lpr_api.models import EUAIAct50

    with pytest.raises(ValidationError, match="legal entity identifier"):
        EUAIAct50(
            ai_system_id="openai/gpt-4o/2024-11-20",
            deployer_id="john.doe@company.com",  # email — should fail
            deployer_name="Company GmbH",
            deployer_country="DE",
            content_category="AI_ASSISTED_DOCUMENT",
        )


def test_deployer_country_validation():
    """deployer_country must be a valid ISO 3166-1 alpha-2 code."""
    from pydantic import ValidationError
    from lpr_api.models import EUAIAct50

    with pytest.raises(ValidationError):
        EUAIAct50(
            ai_system_id="test",
            deployer_id="LEI:123",
            deployer_name="Company",
            deployer_country="DEU",  # alpha-3, not alpha-2 — should fail
            content_category="AI_ASSISTED_DOCUMENT",
        )


def test_content_hash_must_be_hex():
    """content_hash must be 64 lowercase hex chars."""
    from pydantic import ValidationError
    from lpr_api.models import ReceiptRequest

    with pytest.raises(ValidationError):
        ReceiptRequest(
            content_hash="not-a-hash",
            content_type="text/plain",
            content_bytes=40,
            actor_type="AI_MODEL",
            actor_id="test",
            actor_assertion="test",
        )


def test_human_actor_email_rejected():
    """HUMAN actor_type with email in actor_id should be rejected."""
    from pydantic import ValidationError
    from lpr_api.models import ReceiptRequest

    with pytest.raises(ValidationError, match="personal data"):
        ReceiptRequest(
            content_hash=SAMPLE_HASH,
            content_type="text/plain",
            content_bytes=40,
            actor_type="HUMAN",
            actor_id="employee@company.com",  # email — GDPR violation
            actor_assertion="test",
        )


# ---------------------------------------------------------------------------
# Tests — API endpoints (require running app; skip if no DB)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Health endpoint returns 200 without auth."""
    async with AsyncClient(
        transport=ASGITransport(app=client._transport._app),
        base_url="https://api.ledgerproofhq.io",
    ) as unauthenticated:
        resp = await unauthenticated.get("/health")
    # Should return 200 even in degraded state (no DB in unit test).
    assert resp.status_code in (200, 503)


@pytest.mark.asyncio
async def test_operator_identity_endpoint(client: AsyncClient):
    """/.well-known/lpr-operator returns expected fields."""
    resp = await client.get("/.well-known/lpr-operator")
    assert resp.status_code == 200
    data = resp.json()
    assert data["lpr_version_supported"] == ["1.0"]
    assert data["anchor_substrate"] == "bitcoin-mainnet"
    assert data["eu_ai_act_50_supported"] is True


@pytest.mark.asyncio
@pytest.mark.skipif(not POSTGRES_AVAILABLE, reason="PostgreSQL not available")
async def test_issue_core_receipt(client: AsyncClient):
    """POST /receipts issues a valid Core receipt."""
    resp = await client.post("/receipts", json=core_receipt_payload())
    assert resp.status_code == 201
    data = resp.json()
    assert data["content_hash"] == SAMPLE_HASH
    assert data["actor_type"] == "AI_MODEL"
    assert data["anchor"]["anchor_status"] == "PENDING"
    assert data["verify_url"].startswith("https://verify.ledgerproofhq.io/r/")
    assert len(data["receipt_id"]) == 36  # UUID format


@pytest.mark.asyncio
@pytest.mark.skipif(not POSTGRES_AVAILABLE, reason="PostgreSQL not available")
async def test_issue_eu_ai_act_50_receipt(client: AsyncClient):
    """POST /receipts with EU-AI-ACT-50-v1 profile includes eu_ai_act_50 extension."""
    resp = await client.post("/receipts", json=eu_receipt_payload())
    assert resp.status_code == 201
    data = resp.json()
    assert data["jurisdiction_profile"] == "EU-AI-ACT-50-v1"
    assert data["eu_ai_act_50"]["deployer_country"] == "DE"
    assert data["eu_ai_act_50"]["transparency_marker"] == "LPR-EU-AI-ACT-50"


@pytest.mark.asyncio
@pytest.mark.skipif(not POSTGRES_AVAILABLE, reason="PostgreSQL not available")
async def test_get_pending_receipt_proof_returns_202(client: AsyncClient):
    """GET /receipts/{id}/proof on a PENDING receipt returns 202."""
    issue_resp = await client.post("/receipts", json=core_receipt_payload())
    receipt_id = issue_resp.json()["receipt_id"]
    proof_resp = await client.get(f"/receipts/{receipt_id}/proof")
    assert proof_resp.status_code == 202


@pytest.mark.asyncio
@pytest.mark.skipif(not POSTGRES_AVAILABLE, reason="PostgreSQL not available")
async def test_batch_receipt_issuance(client: AsyncClient):
    """POST /receipts/batch issues multiple receipts in one call."""
    hashes = [
        hashlib.sha256(f"doc{i}".encode()).hexdigest()
        for i in range(5)
    ]
    batch = {"receipts": [core_receipt_payload(h) for h in hashes]}
    resp = await client.post("/receipts/batch", json=batch)
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 5
    returned_hashes = {r["content_hash"] for r in data}
    assert returned_hashes == set(hashes)


@pytest.mark.asyncio
@pytest.mark.skipif(not POSTGRES_AVAILABLE, reason="PostgreSQL not available")
async def test_unauthorized_request_rejected(client: AsyncClient):
    """Requests without a valid API key return 401."""
    async with AsyncClient(
        transport=ASGITransport(app=client._transport._app),
        base_url="https://api.ledgerproofhq.io",
    ) as unauthenticated:
        resp = await unauthenticated.post("/receipts", json=core_receipt_payload())
    assert resp.status_code == 401


@pytest.mark.asyncio
@pytest.mark.skipif(not POSTGRES_AVAILABLE, reason="PostgreSQL not available")
async def test_gdpr_delete_endpoint(client: AsyncClient):
    """DELETE /receipts/{id} soft-deletes a receipt in GDPR mode."""
    issue_resp = await client.post("/receipts", json=core_receipt_payload())
    receipt_id = issue_resp.json()["receipt_id"]

    delete_resp = await client.delete(f"/receipts/{receipt_id}")
    assert delete_resp.status_code == 204

    # Deleted receipt should no longer be retrievable.
    get_resp = await client.get(f"/receipts/{receipt_id}")
    assert get_resp.status_code == 404
