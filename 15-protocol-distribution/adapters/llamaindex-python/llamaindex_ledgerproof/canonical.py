"""Canonical CBOR encoding for LedgerProof receipts.

The protocol requires byte-deterministic serialization so that the same logical
receipt always produces the same hash. We use cbor2 with canonical=True, which
follows the CBOR deterministic encoding rules from RFC 8949 Section 4.2:

- Integers in the smallest possible representation
- Map keys sorted by their canonical (length-then-lex) encoding
- Definite-length strings, arrays, and maps
- No indefinite-length items

We also normalize input (datetimes → ISO 8601 UTC strings, bytes → hex) so that
upstream encoders do not have to think about CBOR-native types.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

import cbor2


def _normalize(value: Any) -> Any:
    """Recursively normalize a Python value into CBOR-friendly primitives.

    Datetimes become RFC 3339 UTC strings (microsecond precision). Bytes become
    hex strings (we keep payloads JSON-friendly downstream). Sets become sorted
    lists. Pydantic v2 models are dumped via ``model_dump`` if present.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, datetime):
        # Ensure tz-aware UTC, then ISO format.
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return [_normalize(v) for v in sorted(value, key=repr)]
    # Pydantic v2 models.
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        return _normalize(dump(mode="json"))
    # Fallback: stringify so we never raise inside the encoder.
    return str(value)


def canonical_cbor(payload: dict[str, Any]) -> bytes:
    """Return the canonical CBOR encoding of a receipt payload.

    Determinism is enforced by cbor2's canonical mode plus our own input
    normalization. Same dict (modulo key ordering and tz representation) → same
    bytes, on any Python version supported by this package.
    """
    if not isinstance(payload, dict):
        raise TypeError("canonical_cbor requires a dict at the top level")
    return cbor2.dumps(_normalize(payload), canonical=True)


def transcript_hash(parts: list[Any]) -> str:
    """SHA-256 over canonical CBOR of a list — used for streaming commitments.

    Phase C6 calls for committing the input transcript hash at event start so
    that the streamed body cannot be silently rewritten before signing.
    """
    blob = canonical_cbor({"transcript": parts})
    return hashlib.sha256(blob).hexdigest()


def receipt_digest(payload: dict[str, Any]) -> str:
    """SHA-256 of canonical CBOR — the bytes that get signed and Merkle-batched."""
    return hashlib.sha256(canonical_cbor(payload)).hexdigest()
