"""Deterministic canonical encoding for receipt payloads.

We use deterministic CBOR (RFC 8949 Section 4.2) so that signers and verifiers
produce byte-identical bytes for identical inputs. The same content is also
SHA-256 hashed incrementally (C6) so streaming generators can be supported
without buffering the entire output in memory.
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

import cbor2


def canonicalize(payload: Mapping[str, Any]) -> bytes:
    """Encode `payload` in deterministic CBOR.

    `cbor2.dumps(..., canonical=True)` produces the deterministic encoding
    required by the LedgerProof protocol: shortest-form integers, sorted map
    keys, definite-length collections.
    """
    return cbor2.dumps(_to_jsonable(payload), canonical=True)


def _to_jsonable(value: Any) -> Any:
    """Coerce Pydantic / dataclass-like objects to plain dict/list/scalars."""
    if hasattr(value, "model_dump"):  # pydantic v2
        return value.model_dump(mode="json")
    if isinstance(value, Mapping):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    return value


class IncrementalDigest:
    """Streaming SHA-256 digest for stream-aware signing (C6).

    Usage::

        d = IncrementalDigest()
        for chunk in stream:
            d.update(chunk)
        digest = d.finalize()
    """

    def __init__(self) -> None:
        self._h = hashlib.sha256()

    def update(self, data: bytes | str) -> "IncrementalDigest":
        if isinstance(data, str):
            data = data.encode("utf-8")
        self._h.update(data)
        return self

    def finalize(self) -> bytes:
        return self._h.digest()

    def hexdigest(self) -> str:
        return self._h.hexdigest()


def sha256_hex(data: bytes | str) -> str:
    """One-shot SHA-256 hex digest convenience helper."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()
