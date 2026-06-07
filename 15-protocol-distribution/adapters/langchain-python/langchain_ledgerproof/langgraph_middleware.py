"""LangGraph node middleware: `@lpr_receipt_node` decorator.

Wraps a LangGraph node function so that, on the resume edge (i.e. after the
node returns its state update), a LedgerProof receipt is emitted. Designed
for human-review nodes that establish the Article 50(4) editorial-control
exemption: the receipt captures reviewer identity, role, and outcome.

Usage:

    from langchain_ledgerproof import (
        lpr_receipt_node, LogEmitter, Ed25519Signer,
    )

    signer = Ed25519Signer()
    emitter = LogEmitter("./receipts.jsonl")

    @lpr_receipt_node(
        deployer_id="acme-corp-eu",
        schema="human_review/v1",
        emitter=emitter,
        signer=signer,
    )
    def human_review(state):
        # ... reviewer interaction ...
        return {
            "decision": "approved",
            "lpr": {
                "reviewer_id": "reviewer-7421",
                "reviewer_role": "editor",
                "review_outcome": "approved",
                "review_rationale": "Spot-checked, factual.",
                "transcript_sha256": state["transcript_sha256"],
            },
        }

The decorator looks for an `lpr` key in the returned state update and uses
it to build the receipt. The original returned state is passed through
unmodified — the receipt is emitted as a side channel.
"""

from __future__ import annotations

import base64
import functools
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from .canonical import canonical_encode
from .emitter import BaseEmitter, LogEmitter
from .schema import SCHEMAS, get_schema
from .signer import BaseSigner, Ed25519Signer


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def lpr_receipt_node(
    deployer_id: str,
    schema: str = "human_review/v1",
    emitter: Optional[BaseEmitter] = None,
    signer: Optional[BaseSigner] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory. See module docstring for usage."""

    if schema not in SCHEMAS:
        raise ValueError(
            f"Unknown receipt schema: {schema!r}. Known: {sorted(SCHEMAS)}"
        )

    _emitter: BaseEmitter = emitter or LogEmitter("./ledgerproof-receipts.jsonl")
    _signer: BaseSigner = signer or Ed25519Signer()
    _extra: Dict[str, Any] = dict(extra or {})

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = fn(*args, **kwargs)

            # Side-channel only: never modify the node's return value.
            try:
                _emit_receipt(result)
            except Exception:
                # A receipt-emission failure must not break the graph.
                # Phase 2 wires this to a structured operational log.
                pass

            return result

        def _emit_receipt(result: Any) -> None:
            if not isinstance(result, dict):
                return
            lpr_block = result.get("lpr")
            if not isinstance(lpr_block, dict):
                return

            receipt_fields: Dict[str, Any] = {
                "schema_id": schema,
                "run_id": str(lpr_block.get("run_id") or uuid.uuid4()),
                "timestamp_utc": _utc_now(),
                "deployer_id": deployer_id,
                "transcript_sha256": lpr_block.get(
                    "transcript_sha256", hashlib.sha256(b"").hexdigest()
                ),
            }
            # Merge schema-specific fields supplied by the node.
            for k, v in lpr_block.items():
                if k in ("run_id", "transcript_sha256"):
                    continue
                receipt_fields.setdefault(k, v)
            # Caller-supplied extras override.
            receipt_fields.update(_extra)

            validated = get_schema(schema)(**receipt_fields).model_dump()
            body_bytes = canonical_encode(validated)
            body_digest = hashlib.sha256(body_bytes).digest()
            signature = _signer.sign(body_digest)

            envelope: Dict[str, Any] = {
                "body": validated,
                "body_sha256": body_digest.hex(),
                "signature_ed25519": base64.urlsafe_b64encode(signature)
                .rstrip(b"=")
                .decode("ascii"),
                "public_key_ed25519": _signer.public_key_b64(),
                "alg": "Ed25519",
            }
            _emitter.emit(envelope)

        return wrapper

    return decorator
