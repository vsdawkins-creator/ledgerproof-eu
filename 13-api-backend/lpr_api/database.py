"""
LPR API — async PostgreSQL layer using asyncpg.

Schema:
  receipts        — one row per issued receipt (canonical CBOR + metadata)
  anchor_queue    — pending receipts waiting for the next Merkle tree build
  anchors         — completed anchor transactions (Merkle root → BTC txid)
  receipt_proofs  — post-anchor Merkle inclusion proofs per receipt
  api_keys        — hashed API keys and rate-limit tiers
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

import asyncpg  # type: ignore[import-untyped]

logger = logging.getLogger("lpr.database")

# Lazy connection pool (initialized on startup).
_pool: Optional[asyncpg.Pool] = None


async def init_pool() -> None:
    """Create the asyncpg connection pool. Called on app startup."""
    global _pool
    dsn = os.environ["DATABASE_URL"]
    _pool = await asyncpg.create_pool(
        dsn,
        min_size=2,
        max_size=20,
        command_timeout=10,
        statement_cache_size=200,
    )
    logger.info("PostgreSQL pool initialized (min=2, max=20)")


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("PostgreSQL pool closed")


@asynccontextmanager
async def conn() -> AsyncGenerator[asyncpg.Connection, None]:
    """Yield a connection from the pool."""
    assert _pool is not None, "Database pool not initialized — call init_pool() on startup"
    async with _pool.acquire() as connection:
        yield connection


# ---------------------------------------------------------------------------
# Schema migrations (run at startup via alembic, but also here for self-check)
# ---------------------------------------------------------------------------

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS receipts (
    receipt_id          TEXT PRIMARY KEY,
    trace_id            TEXT NOT NULL,
    timestamp_ns        BIGINT NOT NULL,
    timestamp_iso       TEXT NOT NULL,
    lpr_version         INTEGER NOT NULL DEFAULT 1,
    profile             TEXT,
    jurisdiction_profile TEXT,
    content_hash        TEXT NOT NULL,
    content_type        TEXT NOT NULL,
    content_bytes       BIGINT NOT NULL,
    actor_type          TEXT NOT NULL,
    actor_id            TEXT NOT NULL,
    actor_assertion     TEXT NOT NULL,
    tool_chain          JSONB NOT NULL DEFAULT '[]',
    prev_receipt_id     TEXT,
    eu_ai_act_50        JSONB,
    signer_pubkey       TEXT NOT NULL,
    signature_bytes     TEXT NOT NULL,       -- hex-encoded Ed25519 signature
    receipt_cbor        BYTEA NOT NULL,      -- canonical CBOR of the full receipt
    leaf_hash_hex       TEXT,                -- hex-encoded RFC 6962 leaf hash (for proof lookup)
    anchor_status       TEXT NOT NULL DEFAULT 'PENDING',
    anchor_id           TEXT,                -- FK to anchors.anchor_id
    api_key_id          TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ          -- GDPR Article 17 soft-delete
);

CREATE INDEX IF NOT EXISTS receipts_trace_id_idx ON receipts(trace_id);
CREATE INDEX IF NOT EXISTS receipts_anchor_status_idx ON receipts(anchor_status);
CREATE INDEX IF NOT EXISTS receipts_content_hash_idx ON receipts(content_hash);
CREATE INDEX IF NOT EXISTS receipts_created_at_idx ON receipts(created_at);

-- Anchor queue: set of pending receipt IDs to include in next Merkle tree.
CREATE TABLE IF NOT EXISTS anchor_queue (
    receipt_id          TEXT PRIMARY KEY REFERENCES receipts(receipt_id),
    leaf_hash           TEXT NOT NULL,       -- hex-encoded RFC 6962 leaf hash
    queued_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Completed Bitcoin anchors.
CREATE TABLE IF NOT EXISTS anchors (
    anchor_id           TEXT PRIMARY KEY,    -- UUID v7
    merkle_root         TEXT NOT NULL,       -- hex
    btc_txid            TEXT UNIQUE,         -- set after broadcast
    btc_block_height    INTEGER,             -- set after confirmation
    anchored_at         TIMESTAMPTZ,
    receipt_count       INTEGER NOT NULL,
    leaf_hashes         JSONB NOT NULL,      -- ordered array of hex leaf hashes
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Per-receipt Merkle inclusion proofs (populated after anchor confirmation).
CREATE TABLE IF NOT EXISTS receipt_proofs (
    receipt_id          TEXT PRIMARY KEY REFERENCES receipts(receipt_id),
    anchor_id           TEXT NOT NULL REFERENCES anchors(anchor_id),
    leaf_index          INTEGER NOT NULL,
    tree_size           INTEGER NOT NULL,
    proof_path          JSONB NOT NULL,      -- array of hex-encoded sibling hashes
    merkle_root         TEXT NOT NULL,
    btc_txid            TEXT NOT NULL,
    btc_block_height    INTEGER NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- API key store (hashed).
CREATE TABLE IF NOT EXISTS api_keys (
    key_id              TEXT PRIMARY KEY,    -- UUID v7
    key_hash            TEXT UNIQUE NOT NULL, -- HMAC-SHA256 of the raw key
    name                TEXT NOT NULL,
    tier                TEXT NOT NULL DEFAULT 'standard',  -- standard | enterprise | internal
    rate_limit_rpm      INTEGER NOT NULL DEFAULT 60,
    eu_mode             BOOLEAN NOT NULL DEFAULT FALSE,
    active              BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_used_at        TIMESTAMPTZ
);
"""


async def ensure_schema() -> None:
    """Create tables if they do not exist. Safe to call multiple times."""
    async with conn() as c:
        await c.execute(CREATE_TABLES_SQL)
    logger.info("Schema check complete")


# ---------------------------------------------------------------------------
# Receipt operations
# ---------------------------------------------------------------------------

async def insert_receipt(
    receipt_id: str,
    trace_id: str,
    timestamp_ns: int,
    timestamp_iso: str,
    profile: Optional[str],
    jurisdiction_profile: Optional[str],
    content_hash: str,
    content_type: str,
    content_bytes: int,
    actor_type: str,
    actor_id: str,
    actor_assertion: str,
    tool_chain: list[dict],
    prev_receipt_id: Optional[str],
    eu_ai_act_50: Optional[dict],
    signer_pubkey: str,
    signature_bytes: str,
    receipt_cbor: bytes,
    leaf_hash: str,
    api_key_id: Optional[str],
) -> None:
    """Insert a new receipt and add it to the anchor queue in one transaction."""
    import json

    async with conn() as c:
        async with c.transaction():
            await c.execute(
                """
                INSERT INTO receipts (
                    receipt_id, trace_id, timestamp_ns, timestamp_iso,
                    lpr_version, profile, jurisdiction_profile,
                    content_hash, content_type, content_bytes,
                    actor_type, actor_id, actor_assertion, tool_chain,
                    prev_receipt_id, eu_ai_act_50,
                    signer_pubkey, signature_bytes, receipt_cbor,
                    leaf_hash_hex, anchor_status, api_key_id
                ) VALUES (
                    $1, $2, $3, $4,
                    1, $5, $6,
                    $7, $8, $9,
                    $10, $11, $12, $13::jsonb,
                    $14, $15::jsonb,
                    $16, $17, $18,
                    $20, 'PENDING', $19
                )
                """,
                receipt_id, trace_id, timestamp_ns, timestamp_iso,
                profile, jurisdiction_profile,
                content_hash, content_type, content_bytes,
                actor_type, actor_id, actor_assertion, json.dumps(tool_chain),
                prev_receipt_id, json.dumps(eu_ai_act_50) if eu_ai_act_50 else None,
                signer_pubkey, signature_bytes, receipt_cbor,
                api_key_id, leaf_hash,
            )
            await c.execute(
                "INSERT INTO anchor_queue (receipt_id, leaf_hash) VALUES ($1, $2)",
                receipt_id, leaf_hash,
            )


async def get_receipt(receipt_id: str) -> Optional[dict[str, Any]]:
    """Fetch a receipt by ID. Returns None if not found or soft-deleted."""
    async with conn() as c:
        row = await c.fetchrow(
            "SELECT * FROM receipts WHERE receipt_id = $1 AND deleted_at IS NULL",
            receipt_id,
        )
    return dict(row) if row else None


async def get_receipt_proof(receipt_id: str) -> Optional[dict[str, Any]]:
    """Fetch the Merkle inclusion proof for an anchored receipt."""
    async with conn() as c:
        row = await c.fetchrow(
            "SELECT * FROM receipt_proofs WHERE receipt_id = $1",
            receipt_id,
        )
    return dict(row) if row else None


async def count_pending() -> int:
    """Count receipts in the anchor queue."""
    async with conn() as c:
        val = await c.fetchval("SELECT COUNT(*) FROM anchor_queue")
    return int(val or 0)


async def get_last_anchor() -> Optional[dict[str, Any]]:
    """Fetch the most recent completed anchor."""
    async with conn() as c:
        row = await c.fetchrow(
            "SELECT * FROM anchors WHERE btc_txid IS NOT NULL ORDER BY created_at DESC LIMIT 1"
        )
    return dict(row) if row else None


async def soft_delete_receipt(receipt_id: str) -> bool:
    """GDPR Article 17: soft-delete a receipt record."""
    async with conn() as c:
        result = await c.execute(
            "UPDATE receipts SET deleted_at = now() WHERE receipt_id = $1 AND deleted_at IS NULL",
            receipt_id,
        )
    return result == "UPDATE 1"


# ---------------------------------------------------------------------------
# API key operations
# ---------------------------------------------------------------------------

_API_KEY_SALT: Optional[str] = None


def _get_salt() -> str:
    global _API_KEY_SALT
    if _API_KEY_SALT is None:
        _API_KEY_SALT = os.environ.get("API_KEY_SALT", "")
        if not _API_KEY_SALT:
            logger.warning("API_KEY_SALT not set — API key hashing is insecure")
    return _API_KEY_SALT


def hash_api_key(raw_key: str) -> str:
    """HMAC-SHA256 the raw API key with the configured salt."""
    return hmac.new(
        _get_salt().encode(),
        raw_key.encode(),
        hashlib.sha256,
    ).hexdigest()


async def validate_api_key(raw_key: str) -> Optional[dict[str, Any]]:
    """Check an API key and return its record, or None if invalid/inactive."""
    key_hash = hash_api_key(raw_key)
    async with conn() as c:
        row = await c.fetchrow(
            "SELECT * FROM api_keys WHERE key_hash = $1 AND active = TRUE",
            key_hash,
        )
        if row:
            await c.execute(
                "UPDATE api_keys SET last_used_at = now() WHERE key_id = $1",
                row["key_id"],
            )
    return dict(row) if row else None
