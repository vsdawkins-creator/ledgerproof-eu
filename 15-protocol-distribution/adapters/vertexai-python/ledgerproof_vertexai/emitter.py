"""Receipt assembly, signing, and sink emission.

C7: emitter is strictly side-channel. It never touches the Vertex AI
response object.
C4: receipts are written to a local sink (file, callable, or in-memory
buffer). No network egress is performed by this module.
"""
from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from .canonical import canonicalize, hex_digest
from .schema import VertexContext, build_receipt_payload
from .signer import EphemeralEd25519Signer, Signature
from .version import PROTOCOL_VERSION


Sink = Callable[[dict[str, Any]], None] | str | None


@dataclass
class EmitterConfig:
    deployer_id: str | None = None
    sink: Sink = None
    signer: EphemeralEd25519Signer | None = None
    # Map common Vertex AI locations to a short region-of-inference label.
    region_attestation_map: dict[str, str] = field(
        default_factory=lambda: {
            "europe-west1": "EU/BE",
            "europe-west3": "EU/DE",
            "europe-west4": "EU/NL",
            "europe-west9": "EU/FR",
            "europe-west12": "EU/IT",
            "europe-southwest1": "EU/ES",
            "europe-north1": "EU/FI",
            "us-central1": "US/IA",
            "us-east4": "US/VA",
            "us-east5": "US/OH",
            "us-west1": "US/OR",
            "asia-east1": "ASIA/TW",
            "asia-northeast1": "ASIA/JP",
        }
    )


_lock = threading.Lock()
_cfg = EmitterConfig()


def configure(
    *,
    deployer_id: str | None = None,
    sink: Sink = None,
    signer: EphemeralEd25519Signer | None = None,
) -> None:
    """Configure the process-wide emitter."""
    with _lock:
        if deployer_id is not None:
            _cfg.deployer_id = deployer_id
        if sink is not None:
            _cfg.sink = sink
        if signer is not None:
            _cfg.signer = signer
        if _cfg.signer is None:
            _cfg.signer = EphemeralEd25519Signer()


def get_config() -> EmitterConfig:
    return _cfg


def _now_rfc3339() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def _region_attestation(location: str | None) -> str | None:
    if not location:
        return None
    return _cfg.region_attestation_map.get(location, location)


def _digest_text(text: str) -> str:
    """SHA-256 hex of a UTF-8 string, framed as a one-key payload so that
    digests are canonicalized the same way as full receipts."""
    return hex_digest({"text": text})


def build_vertex_context(
    *, model: str, project: str | None, location: str | None
) -> VertexContext:
    return VertexContext(
        project=project,
        location=location,
        model=model,
        region_of_inference_attestation=_region_attestation(location),
    )


def emit_receipt(
    schema_name: str,
    *,
    model: str,
    project: str | None,
    location: str | None,
    input_text: str | None = None,
    output_text: str | None = None,
    deployer_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build, sign, and dispatch a single receipt. Returns the signed envelope."""
    cfg = _cfg
    eff_deployer = deployer_id or cfg.deployer_id
    if not eff_deployer:
        raise RuntimeError(
            "LedgerProof: deployer_id is not set. Call configure(deployer_id=...) "
            "before emitting receipts."
        )

    vertex_ctx = build_vertex_context(
        model=model, project=project, location=location
    )

    fields: dict[str, Any] = {}
    if input_text is not None:
        fields["input_digest"] = _digest_text(input_text)
    if output_text is not None:
        fields["output_digest"] = _digest_text(output_text)
    if extra:
        fields.update(extra)

    payload = build_receipt_payload(
        schema_name=schema_name,
        deployer_id=eff_deployer,
        occurred_at=_now_rfc3339(),
        vertex=vertex_ctx,
        **fields,
    )

    # Sign the canonical payload digest.
    assert cfg.signer is not None
    sig: Signature = cfg.signer.sign(canonicalize(payload))

    envelope = {
        "protocol": PROTOCOL_VERSION,
        "payload": payload,
        "signature": {
            "algorithm": sig.algorithm,
            "public_key": sig.public_key_b64,
            "value": sig.signature_b64,
        },
    }

    _dispatch(envelope)
    return envelope


def _dispatch(envelope: dict[str, Any]) -> None:
    """Write the envelope to the configured sink."""
    sink = _cfg.sink
    if sink is None:
        return
    if callable(sink):
        try:
            sink(envelope)
        except Exception:  # pragma: no cover
            # C7: never let sink failures impact caller's response flow.
            pass
        return
    if isinstance(sink, str):
        # Append as JSONL.
        line = json.dumps(envelope, separators=(",", ":")) + "\n"
        try:
            os.makedirs(os.path.dirname(os.path.abspath(sink)) or ".", exist_ok=True)
            with open(sink, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:  # pragma: no cover
            pass
