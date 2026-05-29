"""
LedgerProof Receipt API — v1.0

Endpoints:
  POST  /receipts           — Issue a receipt
  POST  /receipts/batch     — Issue up to 1000 receipts in one call
  GET   /receipts/{id}      — Retrieve a receipt
  GET   /receipts/{id}/proof — Retrieve the Merkle inclusion proof
  DELETE /receipts/{id}     — GDPR Art. 17 soft-delete
  GET   /health             — Health check
  GET   /.well-known/lpr-operator — Operator identity document

Auth:
  Bearer token via Authorization header (API key).
  Internal health check does not require auth.

Rate limits (enforced per API key tier):
  standard:   60 req/min
  enterprise: 600 req/min
  internal:   unlimited

GDPR mode (GDPR_MODE=true):
  - EU data residency assertions added to all receipts
  - Personal data field validation enforced
  - Soft-delete endpoint enabled
"""
from __future__ import annotations

import asyncio
import binascii
import hashlib
import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from lpr_api import database as db
from lpr_api.anchor_worker import BitcoinRPC, anchor_worker_loop
from lpr_api.models import (
    AnchorInfo,
    AnchorStatus,
    BatchReceiptRequest,
    ErrorResponse,
    HealthResponse,
    ProofResponse,
    ReceiptRequest,
    ReceiptResponse,
)
from lpr_api.signing import get_signing_key, get_signer_pubkey_hex, load_signing_key

logger = logging.getLogger("lpr.api")

# ---------------------------------------------------------------------------
# Startup / shutdown
# ---------------------------------------------------------------------------

_btc_rpc: Optional[BitcoinRPC] = None
_anchor_task: Optional[asyncio.Task] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup → run → shutdown."""
    global _btc_rpc, _anchor_task

    # Load signing key from disk.
    try:
        load_signing_key()
        logger.info("Signing key loaded")
    except FileNotFoundError as exc:
        # Allow startup without signing key for development/testing.
        if os.environ.get("ALLOW_MISSING_SIGNING_KEY") == "true":
            logger.warning("Signing key missing — running in DEMO mode (no signing)")
        else:
            raise

    # Init database pool.
    await db.init_pool()
    await db.ensure_schema()

    # Start Bitcoin anchor worker.
    _btc_rpc = BitcoinRPC()
    btc_ok = await _btc_rpc.test_connection()
    if btc_ok:
        _anchor_task = asyncio.create_task(anchor_worker_loop(_btc_rpc))
        logger.info("Anchor worker started")
    else:
        logger.warning(
            "Bitcoin RPC not reachable — anchor worker NOT started. "
            "Receipts will queue but not anchor until node is available."
        )

    yield  # Application runs here.

    # Shutdown.
    if _anchor_task:
        _anchor_task.cancel()
        try:
            await _anchor_task
        except asyncio.CancelledError:
            pass
    if _btc_rpc:
        await _btc_rpc.close()
    await db.close_pool()
    logger.info("LPR API shutdown complete")


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="LedgerProof Receipt API",
    description="LPR v1.0 — Bitcoin-anchored cryptographic provenance receipts",
    version="1.0.0",
    docs_url="/docs" if os.environ.get("ENV") != "production" else None,
    redoc_url="/redoc" if os.environ.get("ENV") != "production" else None,
    lifespan=lifespan,
)

# CORS — restrict to approved origins.
_cors_origins = os.environ.get(
    "CORS_ORIGINS",
    "https://publish.ledgerproofhq.io,https://verify.ledgerproofhq.io",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------

async def require_api_key(
    authorization: Optional[str] = Header(default=None),
) -> dict[str, Any]:
    """Extract and validate the Bearer API key. Returns the key record."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization: Bearer <api_key> required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    raw_key = authorization.removeprefix("Bearer ").strip()
    key_record = await db.validate_api_key(raw_key)
    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return key_record


# ---------------------------------------------------------------------------
# Receipt issuance helper
# ---------------------------------------------------------------------------

def _build_base_url() -> str:
    region = os.environ.get("LEDGERPROOF_REGION", "")
    if region == "eu":
        return "https://api-eu.ledgerproofhq.io"
    return "https://api.ledgerproofhq.io"


async def _issue_receipt(
    req: ReceiptRequest,
    api_key_id: str,
) -> ReceiptResponse:
    """Core receipt issuance logic. Shared by POST /receipts and batch endpoint."""
    from cryptography.hazmat.primitives import serialization

    now_ns = time.time_ns()

    # Build IDs.
    receipt_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4()) if req.prev_receipt_id is None else req.prev_receipt_id

    # ISO timestamp.
    seconds, nanos = divmod(now_ns, 1_000_000_000)
    ts = time.gmtime(seconds)
    timestamp_iso = time.strftime("%Y-%m-%dT%H:%M:%S", ts) + f".{nanos:09d}Z"

    # Compute leaf hash for the Merkle tree.
    # Leaf data = content_hash || actor_id || timestamp_ns (deterministic, per spec §5.2).
    leaf_data = (
        bytes.fromhex(req.content_hash)
        + req.actor_id.encode("utf-8")
        + now_ns.to_bytes(8, "big")
    )
    leaf_hash_bytes = hashlib.sha256(b"\x00" + leaf_data).digest()
    leaf_hash_hex = leaf_hash_bytes.hex()

    # Build the body for signing (mirrors receipt.py build_receipt body structure).
    body: dict[str, Any] = {
        "lpr_version": 1,
        "receipt_id": receipt_id,
        "trace_id": trace_id,
        "timestamp_ns": now_ns,
        "timestamp_iso": timestamp_iso,
        "artifact": {
            "content_hash": bytes.fromhex(req.content_hash),
            "hash_algo": "SHA-256",
            "content_type": req.content_type,
            "content_bytes": req.content_bytes,
        },
        "authorship": {
            "actor_type": req.actor_type.value,
            "actor_id": req.actor_id,
            "actor_assertion": req.actor_assertion,
            "tool_chain": req.tool_chain,
        },
        "chain": {"prev_receipt_hash": None},
    }

    # Add EU AI Act 50 extension if present.
    eu_ai_act_50_dict: Optional[dict[str, Any]] = None
    if req.eu_ai_act_50:
        eu_ai_act_50_dict = req.eu_ai_act_50.model_dump()
        body["eu_ai_act_50"] = eu_ai_act_50_dict
        body["jurisdiction_profile"] = req.jurisdiction_profile.value if req.jurisdiction_profile else None

    # Add GDPR region assertion if EU mode.
    if os.environ.get("GDPR_MODE") == "true":
        body["data_residency"] = {
            "jurisdiction": "EU",
            "region": os.environ.get("LEDGERPROOF_REGION", "eu"),
            "country": os.environ.get("CALENDAR_OPERATOR_COUNTRY", "DE"),
        }

    # Sign: canonical CBOR of body.
    import cbor2  # type: ignore[import-untyped]
    body_cbor = cbor2.dumps(body, canonical=True)

    try:
        signing_key = get_signing_key()
        sig_bytes = signing_key.sign(body_cbor)
        signer_pubkey_hex = get_signer_pubkey_hex()
    except RuntimeError:
        # Demo mode (no signing key loaded).
        sig_bytes = b"\x00" * 64
        signer_pubkey_hex = "0" * 64
        logger.warning("DEMO MODE: receipt %s not cryptographically signed", receipt_id)

    sig_hex = sig_bytes.hex()

    # Build full receipt CBOR (including signature + anchor stub).
    full_receipt: dict[str, Any] = {
        **body,
        "signature": {
            "sig_algo": "Ed25519",
            "sig_bytes": sig_bytes,
            "signer_pubkey": bytes.fromhex(signer_pubkey_hex),
        },
        "anchor": {
            "substrate": os.environ.get("ANCHOR_SUBSTRATE", "bitcoin-mainnet"),
            "merkle_leaf_hash": leaf_hash_bytes,
            "anchor_status": "PENDING",
        },
    }
    receipt_cbor = cbor2.dumps(full_receipt, canonical=True)

    # Persist to database.
    await db.insert_receipt(
        receipt_id=receipt_id,
        trace_id=trace_id,
        timestamp_ns=now_ns,
        timestamp_iso=timestamp_iso,
        profile=None,
        jurisdiction_profile=req.jurisdiction_profile.value if req.jurisdiction_profile else None,
        content_hash=req.content_hash,
        content_type=req.content_type,
        content_bytes=req.content_bytes,
        actor_type=req.actor_type.value,
        actor_id=req.actor_id,
        actor_assertion=req.actor_assertion,
        tool_chain=req.tool_chain,
        prev_receipt_id=req.prev_receipt_id,
        eu_ai_act_50=eu_ai_act_50_dict,
        signer_pubkey=signer_pubkey_hex,
        signature_bytes=sig_hex,
        receipt_cbor=receipt_cbor,
        leaf_hash=leaf_hash_hex,
        api_key_id=api_key_id,
    )

    base_url = _build_base_url()
    verify_url = f"https://verify.ledgerproofhq.io/r/{receipt_id}"

    return ReceiptResponse(
        receipt_id=receipt_id,
        trace_id=trace_id,
        timestamp_ns=now_ns,
        timestamp_iso=timestamp_iso,
        lpr_version=1,
        profile=None,
        jurisdiction_profile=req.jurisdiction_profile.value if req.jurisdiction_profile else None,
        content_hash=req.content_hash,
        content_type=req.content_type,
        content_bytes=req.content_bytes,
        actor_type=req.actor_type.value,
        actor_id=req.actor_id,
        signer_pubkey=signer_pubkey_hex,
        anchor=AnchorInfo(
            substrate=os.environ.get("ANCHOR_SUBSTRATE", "bitcoin-mainnet"),
            merkle_leaf_hash=leaf_hash_hex,
            anchor_status=AnchorStatus.PENDING,
        ),
        eu_ai_act_50=eu_ai_act_50_dict,
        verify_url=verify_url,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post(
    "/receipts",
    response_model=ReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Issue a receipt",
    description=(
        "Submit a content hash and authorship metadata. Returns a receipt with a unique ID "
        "and PENDING anchor status. The receipt will be anchored to Bitcoin mainnet in the "
        "next anchor window (default: every 24 hours; High-Assurance profile: every hour)."
    ),
    tags=["Receipts"],
)
async def issue_receipt(
    req: ReceiptRequest,
    key_record: dict = Depends(require_api_key),
) -> ReceiptResponse:
    try:
        return await _issue_receipt(req, key_record["key_id"])
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Receipt issuance failed: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error during receipt issuance")


@app.post(
    "/receipts/batch",
    response_model=list[ReceiptResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Issue up to 1000 receipts in one call",
    description=(
        "Batch issuance. All receipts in the batch will be included in the same Merkle tree "
        "at the next anchor window. Returns an array of ReceiptResponse in the same order "
        "as the input array."
    ),
    tags=["Receipts"],
)
async def issue_receipts_batch(
    batch: BatchReceiptRequest,
    key_record: dict = Depends(require_api_key),
) -> list[ReceiptResponse]:
    results = []
    errors = []
    for i, req in enumerate(batch.receipts):
        try:
            result = await _issue_receipt(req, key_record["key_id"])
            results.append(result)
        except Exception as exc:
            errors.append({"index": i, "error": str(exc)})

    if errors and not results:
        raise HTTPException(status_code=422, detail=errors)
    if errors:
        # Partial success — return 207 with results. In practice, log errors.
        logger.warning("Batch issuance partial failure: %d errors out of %d", len(errors), len(batch.receipts))

    return results


@app.get(
    "/receipts/{receipt_id}",
    response_model=ReceiptResponse,
    summary="Retrieve a receipt",
    tags=["Receipts"],
)
async def get_receipt(
    receipt_id: str,
    key_record: dict = Depends(require_api_key),
) -> ReceiptResponse:
    row = await db.get_receipt(receipt_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Receipt not found")

    # Reconstruct anchor info.
    anchor_status = AnchorStatus(row["anchor_status"])
    proof = None
    if anchor_status == AnchorStatus.ANCHORED:
        proof = await db.get_receipt_proof(receipt_id)

    anchor = AnchorInfo(
        substrate=os.environ.get("ANCHOR_SUBSTRATE", "bitcoin-mainnet"),
        merkle_leaf_hash=row.get("leaf_hash_hex", ""),
        anchor_status=anchor_status,
        btc_txid=proof["btc_txid"] if proof else None,
        btc_block_height=proof["btc_block_height"] if proof else None,
        merkle_path=json.loads(proof["proof_path"]) if proof else None,
    )

    base_url = _build_base_url()
    eu_data = row.get("eu_ai_act_50")

    return ReceiptResponse(
        receipt_id=row["receipt_id"],
        trace_id=row["trace_id"],
        timestamp_ns=row["timestamp_ns"],
        timestamp_iso=row["timestamp_iso"],
        lpr_version=row["lpr_version"],
        profile=row.get("profile"),
        jurisdiction_profile=row.get("jurisdiction_profile"),
        content_hash=row["content_hash"],
        content_type=row["content_type"],
        content_bytes=row["content_bytes"],
        actor_type=row["actor_type"],
        actor_id=row["actor_id"],
        signer_pubkey=row["signer_pubkey"],
        anchor=anchor,
        eu_ai_act_50=json.loads(eu_data) if isinstance(eu_data, str) else eu_data,
        verify_url=f"https://verify.ledgerproofhq.io/r/{receipt_id}",
    )


@app.get(
    "/receipts/{receipt_id}/proof",
    response_model=ProofResponse,
    summary="Retrieve the Merkle inclusion proof for an anchored receipt",
    tags=["Receipts"],
)
async def get_proof(
    receipt_id: str,
    key_record: dict = Depends(require_api_key),
) -> ProofResponse:
    row = await db.get_receipt(receipt_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    if row["anchor_status"] != "ANCHORED":
        raise HTTPException(
            status_code=202,
            detail=(
                f"Receipt {receipt_id} is {row['anchor_status']} — "
                "not yet anchored. Proof will be available after the next anchor window."
            ),
        )

    proof = await db.get_receipt_proof(receipt_id)
    if proof is None:
        raise HTTPException(status_code=500, detail="Receipt is marked ANCHORED but proof record is missing")

    return ProofResponse(
        receipt_id=receipt_id,
        leaf_hash=row.get("leaf_hash_hex", ""),
        leaf_index=proof["leaf_index"],
        tree_size=proof["tree_size"],
        proof_path=json.loads(proof["proof_path"]),
        merkle_root=proof["merkle_root"],
        btc_txid=proof["btc_txid"],
        btc_block_height=proof["btc_block_height"],
        verification_url=f"https://verify.ledgerproofhq.io/r/{receipt_id}",
    )


@app.delete(
    "/receipts/{receipt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="GDPR Article 17 — request erasure of off-chain receipt record",
    description=(
        "Soft-deletes the off-chain receipt record. The on-chain Bitcoin anchor (Merkle root) "
        "is permanent and cannot be erased. After deletion, the receipt's Merkle inclusion "
        "proof is no longer available through this API."
    ),
    tags=["Receipts", "GDPR"],
)
async def delete_receipt(
    receipt_id: str,
    key_record: dict = Depends(require_api_key),
) -> Response:
    if os.environ.get("GDPR_MODE") != "true":
        raise HTTPException(
            status_code=403,
            detail="Receipt deletion is only available on EU/GDPR-mode deployments",
        )
    deleted = await db.soft_delete_receipt(receipt_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Receipt not found or already deleted")
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health",
    tags=["Operations"],
)
async def health_check() -> HealthResponse:
    # DB check.
    db_ok = False
    try:
        async with db.conn() as c:
            await c.fetchval("SELECT 1")
        db_ok = True
    except Exception:
        pass

    # BTC check.
    btc_ok = False
    hot_wallet_sats: Optional[int] = None
    if _btc_rpc:
        try:
            btc_ok = await _btc_rpc.test_connection()
            if btc_ok:
                hot_wallet_sats = await _btc_rpc.get_balance()
        except Exception:
            pass

    pending = await db.count_pending() if db_ok else -1
    last_anchor = await db.get_last_anchor() if db_ok else None

    return HealthResponse(
        status="ok" if (db_ok) else "degraded",
        region=os.environ.get("LEDGERPROOF_REGION", "global"),
        lpr_version="1.0",
        pending_receipts=pending,
        last_anchor_time=last_anchor["anchored_at"] if last_anchor else None,
        last_anchor_txid=last_anchor["btc_txid"] if last_anchor else None,
        last_anchor_block=last_anchor["btc_block_height"] if last_anchor else None,
        hot_wallet_balance_sats=hot_wallet_sats,
        db_ok=db_ok,
        btc_node_ok=btc_ok,
    )


# ---------------------------------------------------------------------------
# Operator identity document
# ---------------------------------------------------------------------------

@app.get(
    "/.well-known/lpr-operator",
    summary="Operator identity document",
    tags=["Operations"],
)
async def operator_identity() -> dict[str, Any]:
    """Returns the LPR operator identity document per spec §6.4."""
    try:
        pubkey = get_signer_pubkey_hex()
    except RuntimeError:
        pubkey = "not-loaded"

    return {
        "operator_name": os.environ.get("OPERATOR_NAME", "LedgerProof Foundation"),
        "operator_did": os.environ.get("OPERATOR_DID", "did:web:api.ledgerproofhq.io"),
        "operator_country": os.environ.get("OPERATOR_COUNTRY", "US"),
        "operator_contact": os.environ.get("OPERATOR_CONTACT", "operators@ledgerproofhq.io"),
        "lpr_version_supported": ["1.0"],
        "anchor_substrate": os.environ.get("ANCHOR_SUBSTRATE", "bitcoin-mainnet"),
        "anchor_window_hours": int(os.environ.get("ANCHOR_WINDOW_HOURS", "24")),
        "public_key": pubkey,
        "gdpr_mode": os.environ.get("GDPR_MODE") == "true",
        "data_residency": os.environ.get("CALENDAR_OPERATOR_JURISDICTION"),
        "eu_ai_act_50_supported": os.environ.get("EU_AI_ACT_50_ENABLED") == "true",
    }


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": str(exc)},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )
