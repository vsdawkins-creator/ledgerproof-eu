"""
SEP-1763 sidecar interceptor for the Model Context Protocol.

Runs as an HTTP service. The MCP host invokes this interceptor on every
`tools/call` (and optionally other features). For each invocation, we:

  1. Hash the canonical JSON-RPC request and response payloads.
  2. Build an LPR v1.0 receipt with actor_type = AI_MODEL or HYBRID.
  3. Sign with our Ed25519 key.
  4. Push to the LedgerProof Anchor API for inclusion in the daily Merkle tree.
  5. Return a SEP-1763-compliant ValidationResult with the receipt's
     signature populating the spec's reserved `signature` field.

Reference implementation, MIT licensed. Not production-hardened.

Dependencies:
    fastapi >= 0.115
    uvicorn >= 0.32
    cbor2 >= 5.6
    cryptography >= 42
    httpx >= 0.27
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx  # type: ignore[import-untyped]
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from receipt import (
    ACTOR_AI_MODEL,
    ACTOR_HYBRID,
    Artifact,
    Authorship,
    build_receipt,
    sha256_of_bytes,
)


# ----- configuration -----

KEY_PATH = Path(os.environ.get("LPR_INTERCEPTOR_KEY", "~/.lpr/interceptor.key")).expanduser()
ANCHOR_API = os.environ.get("LPR_ANCHOR_API", "https://api.ledgerproofhq.io")
ANCHOR_API_KEY = os.environ.get("LPR_ANCHOR_API_KEY")
LOCAL_LOG = Path(os.environ.get("LPR_LOCAL_LOG", "~/.lpr/receipts.jsonl")).expanduser()


def _load_signing_key() -> Ed25519PrivateKey:
    if not KEY_PATH.exists():
        sys.exit(
            f"Signing key not found at {KEY_PATH}. "
            "Generate one with: python -m lpr_interceptor.keygen"
        )
    pem = KEY_PATH.read_bytes()
    key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        sys.exit(f"{KEY_PATH} is not an Ed25519 private key.")
    return key


SIGNING_KEY = _load_signing_key()


# ----- SEP-1763 wire types -----


class InterceptRequest(BaseModel):
    """The body the MCP host sends to a SEP-1763 interceptor."""

    operation: str = Field(..., description="validate | mutate | observe")
    feature: str = Field(..., description="e.g. 'tools/call'")
    request: dict[str, Any]
    response: dict[str, Any] | None = None
    host_signature: str | None = None
    metadata: dict[str, Any] | None = None


class ValidationSignature(BaseModel):
    """The `signature` field of the SEP-1763 ValidationResult. v1.0 reserved-but-unimplemented in the SEP."""

    algorithm: str = "Ed25519"
    sig_bytes: str  # base64url
    signer_pubkey: str  # base64url
    receipt_id: str  # the LPR receipt id this signature corresponds to
    verifier_url: str  # public verifier URL for the receipt


class ValidationResult(BaseModel):
    valid: bool
    reason: str | None = None
    signature: ValidationSignature | None = None


# ----- application -----

app = FastAPI(
    title="LPR MCP Interceptor",
    description="SEP-1763 reference implementation. Emits LedgerProof Receipts for MCP tool calls.",
    version="0.1.0",
)


@app.post("/intercept", response_model=ValidationResult)
async def intercept(req: InterceptRequest) -> ValidationResult:
    """The SEP-1763-compliant interceptor endpoint."""
    if req.feature != "tools/call":
        # v0.1 supports only tools/call. Other features can be added in
        # subsequent revisions of this reference implementation.
        return ValidationResult(valid=True, reason="feature not instrumented")

    if req.operation == "validate":
        return await _validate_and_sign(req)
    if req.operation == "observe":
        return await _observe_only(req)
    if req.operation == "mutate":
        # Mutation intentionally not implemented to preserve operator trust posture.
        return ValidationResult(valid=True, reason="mutation not implemented by design")
    return ValidationResult(valid=False, reason=f"unknown operation {req.operation}")


async def _validate_and_sign(req: InterceptRequest) -> ValidationResult:
    """The core path: build, sign, anchor, return an LPR-backed validation signature."""
    artifact_bytes = _canonical_invocation_bytes(req)
    artifact = Artifact(
        content_hash=sha256_of_bytes(artifact_bytes),
        content_type="application/vnd.mcp.tools-call+json",
        content_bytes=len(artifact_bytes),
    )
    authorship = Authorship(
        actor_type=ACTOR_HYBRID if req.metadata and req.metadata.get("user_approved") else ACTOR_AI_MODEL,
        actor_id=req.metadata.get("agent_id") if req.metadata else "anonymous-agent",
        actor_assertion=(
            f"Agent invoked MCP tool '{req.request.get('params', {}).get('name', '?')}' "
            f"and received the response captured in this artifact."
        ),
        tool_chain=req.metadata.get("tool_chain", []) if req.metadata else [],
    )

    receipt = build_receipt(artifact=artifact, authorship=authorship, signer_key=SIGNING_KEY)
    await _push_to_anchor(receipt)
    _append_local_log(receipt)

    return ValidationResult(
        valid=True,
        signature=ValidationSignature(
            sig_bytes=_b64(receipt["signature"]["sig_bytes"]),
            signer_pubkey=_b64(receipt["signature"]["signer_pubkey"]),
            receipt_id=receipt["receipt_id"],
            verifier_url=f"https://verify.ledgerproofhq.io/r/{receipt['receipt_id']}",
        ),
    )


async def _observe_only(req: InterceptRequest) -> ValidationResult:
    """Observability mode: write to local log only, no anchor."""
    artifact_bytes = _canonical_invocation_bytes(req)
    artifact = Artifact(
        content_hash=sha256_of_bytes(artifact_bytes),
        content_type="application/vnd.mcp.tools-call+json",
        content_bytes=len(artifact_bytes),
    )
    authorship = Authorship(
        actor_type=ACTOR_AI_MODEL,
        actor_id="observation",
        actor_assertion="Observation-mode log of MCP tool invocation.",
    )
    receipt = build_receipt(artifact=artifact, authorship=authorship, signer_key=SIGNING_KEY)
    _append_local_log(receipt)
    return ValidationResult(valid=True)


# ----- helpers -----


def _canonical_invocation_bytes(req: InterceptRequest) -> bytes:
    """Canonical bytes the receipt attests to: the request and the response, sorted."""
    return json.dumps(
        {"request": req.request, "response": req.response},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


async def _push_to_anchor(receipt: dict[str, Any]) -> None:
    """Push the receipt to the LedgerProof Anchor API for inclusion in the daily Merkle tree."""
    if not ANCHOR_API_KEY:
        # No API key — this is local-test mode. Skip the push.
        return
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(
                f"{ANCHOR_API}/v1/receipts",
                json=_jsonable(receipt),
                headers={"Authorization": f"Bearer {ANCHOR_API_KEY}"},
            )
        except Exception:
            # Anchor push is best-effort in v0.1 — the receipt is locally signed and logged.
            # A production deployment would use a durable queue.
            pass


def _append_local_log(receipt: dict[str, Any]) -> None:
    LOCAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOCAL_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(_jsonable(receipt)) + "\n")


def _b64(b: bytes) -> str:
    import base64

    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _jsonable(obj: Any) -> Any:
    """Convert bytes fields to base64 for JSON serialization."""
    if isinstance(obj, bytes):
        return _b64(obj)
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_jsonable(v) for v in obj]
    return obj


if __name__ == "__main__":
    import uvicorn  # type: ignore[import-untyped]

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("LPR_INTERCEPTOR_PORT", "9090")))
