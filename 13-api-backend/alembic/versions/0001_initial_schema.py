"""Initial schema — receipts, anchor_queue, anchors, receipt_proofs, api_keys.

Revision ID: 0001
Create Date: 2026-05-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, BYTEA

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
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
        signature_bytes     TEXT NOT NULL,
        receipt_cbor        BYTEA NOT NULL,
        leaf_hash_hex       TEXT,
        anchor_status       TEXT NOT NULL DEFAULT 'PENDING',
        anchor_id           TEXT,
        api_key_id          TEXT,
        created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
        deleted_at          TIMESTAMPTZ
    )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS receipts_trace_id_idx ON receipts(trace_id)")
    op.execute("CREATE INDEX IF NOT EXISTS receipts_anchor_status_idx ON receipts(anchor_status)")
    op.execute("CREATE INDEX IF NOT EXISTS receipts_content_hash_idx ON receipts(content_hash)")
    op.execute("CREATE INDEX IF NOT EXISTS receipts_created_at_idx ON receipts(created_at)")

    op.execute("""
    CREATE TABLE IF NOT EXISTS anchor_queue (
        receipt_id          TEXT PRIMARY KEY REFERENCES receipts(receipt_id),
        leaf_hash           TEXT NOT NULL,
        queued_at           TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS anchors (
        anchor_id           TEXT PRIMARY KEY,
        merkle_root         TEXT NOT NULL,
        btc_txid            TEXT UNIQUE,
        btc_block_height    INTEGER,
        anchored_at         TIMESTAMPTZ,
        receipt_count       INTEGER NOT NULL,
        leaf_hashes         JSONB NOT NULL,
        created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS receipt_proofs (
        receipt_id          TEXT PRIMARY KEY REFERENCES receipts(receipt_id),
        anchor_id           TEXT NOT NULL REFERENCES anchors(anchor_id),
        leaf_index          INTEGER NOT NULL,
        tree_size           INTEGER NOT NULL,
        proof_path          JSONB NOT NULL,
        merkle_root         TEXT NOT NULL,
        btc_txid            TEXT NOT NULL,
        btc_block_height    INTEGER NOT NULL,
        created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
        key_id              TEXT PRIMARY KEY,
        key_hash            TEXT UNIQUE NOT NULL,
        name                TEXT NOT NULL,
        tier                TEXT NOT NULL DEFAULT 'standard',
        rate_limit_rpm      INTEGER NOT NULL DEFAULT 60,
        eu_mode             BOOLEAN NOT NULL DEFAULT FALSE,
        active              BOOLEAN NOT NULL DEFAULT TRUE,
        created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
        last_used_at        TIMESTAMPTZ
    )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS receipt_proofs CASCADE")
    op.execute("DROP TABLE IF EXISTS anchor_queue CASCADE")
    op.execute("DROP TABLE IF EXISTS receipt_proofs CASCADE")
    op.execute("DROP TABLE IF EXISTS anchors CASCADE")
    op.execute("DROP TABLE IF EXISTS receipts CASCADE")
    op.execute("DROP TABLE IF EXISTS api_keys CASCADE")
