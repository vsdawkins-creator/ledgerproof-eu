"""
Canonical CBOR encoding for LedgerProof Codestral receipts.

Determinism is load-bearing: identical receipt content MUST produce identical bytes
across processes, machines, and Python versions, so that signatures verify offline
(constraint C4) against the Merkle tree anchored to Bitcoin.

We use CBOR with deterministic encoding (RFC 8949 Section 4.2) via cbor2's
canonical=True flag.
"""

from __future__ import annotations

import hashlib
from typing import Any

import cbor2


def canonical_encode(payload: dict[str, Any]) -> bytes:
    """
    Deterministically CBOR-encode a receipt payload.

    Uses RFC 8949 deterministic encoding:
      - Smallest integer encoding
      - Length-then-lexical map key ordering
      - No indefinite-length items
      - Float canonicalization
    """
    return cbor2.dumps(payload, canonical=True, datetime_as_timestamp=True)


def canonical_hash(payload: dict[str, Any]) -> bytes:
    """SHA-256 over the canonical CBOR encoding of the payload."""
    return hashlib.sha256(canonical_encode(payload)).digest()


def hash_text(text: str) -> bytes:
    """SHA-256 of a UTF-8 encoded string. Used for prompt/response content hashes."""
    return hashlib.sha256(text.encode("utf-8")).digest()


def hash_bytes(data: bytes) -> bytes:
    """SHA-256 of raw bytes. Used for hashing already-encoded payloads."""
    return hashlib.sha256(data).digest()


class IncrementalTextHasher:
    """
    Stream-aware SHA-256 hasher for streaming Codestral responses (constraint C6).

    Feed text deltas as they arrive; finalize once the stream completes.
    Never buffers the full body — only updates the SHA-256 state and a counter.

    Codestral note: streamed code is line-dense; do NOT buffer for "pretty print"
    purposes. The receipt MUST reference what was actually emitted on the wire.
    """

    def __init__(self) -> None:
        self._h = hashlib.sha256()
        self._byte_count = 0
        self._line_count = 0
        self._finalized = False

    def update(self, delta: str) -> None:
        if self._finalized:
            raise RuntimeError("IncrementalTextHasher already finalized")
        encoded = delta.encode("utf-8")
        self._h.update(encoded)
        self._byte_count += len(encoded)
        # Count newlines incrementally — useful for generated_code/v1 line_count.
        self._line_count += delta.count("\n")

    def digest(self) -> bytes:
        self._finalized = True
        return self._h.digest()

    @property
    def byte_count(self) -> int:
        return self._byte_count

    @property
    def line_count(self) -> int:
        """Number of newline characters seen. Approximates lines of code."""
        return self._line_count
