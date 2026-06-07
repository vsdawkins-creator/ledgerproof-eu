"""
Canonical CBOR encoding for LedgerProof receipts.

Determinism is load-bearing: identical receipt content MUST produce identical bytes
across processes, machines, and Python versions, so that signatures verify offline
(constraint C4) against the Merkle tree anchored to Bitcoin.

We use CBOR with deterministic encoding (RFC 8949 Section 4.2) via cbor2's
canonical=True flag, plus stable key ordering for nested mappings.

For embedding adapters specifically, we also expose helpers to canonicalize an
embedding vector (list[float]) into bytes so that a stable hash of the resulting
vector can be bound into the receipt — this is what makes after-the-fact
verification of a RAG pipeline tractable: the verifier can recompute the
SHA-256 of `(model_id, input_type, text_sha256, vector_dim, vector_bytes)` and
compare to the signed reference.
"""

from __future__ import annotations

import hashlib
import struct
from typing import Any, Iterable

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
    """SHA-256 of a UTF-8 encoded string. Used for input text content hashes."""
    return hashlib.sha256(text.encode("utf-8")).digest()


def hash_bytes(b: bytes) -> bytes:
    """SHA-256 of raw bytes."""
    return hashlib.sha256(b).digest()


def canonicalize_vector(vector: Iterable[float]) -> bytes:
    """
    Canonical byte representation of an embedding vector.

    We use IEEE-754 big-endian float64 ("!d") for each component, in order. This
    is portable across machines and Python builds. A SHA-256 over this byte
    string is deterministic and independent of the host's native float layout.

    NOTE: Voyage returns float32 by default but exposes higher-precision dtypes
    (int8, uint8, binary, ubinary) via the `output_dtype=` kwarg. We always
    canonicalize through float64 to keep one wire format; the caller is free to
    inspect the raw dtype separately if needed.
    """
    floats = [float(x) for x in vector]
    return b"".join(struct.pack("!d", f) for f in floats)


def hash_vector(vector: Iterable[float]) -> bytes:
    """SHA-256 of the canonical byte representation of an embedding vector."""
    return hashlib.sha256(canonicalize_vector(vector)).digest()


class IncrementalTextHasher:
    """
    Stream-aware SHA-256 hasher (constraint C6).

    Voyage's embed/rerank APIs are not streaming today, but the LedgerProof
    receipt envelope is shared across adapters and downstream RAG-pipeline
    receipts may bind streaming chat output. We retain this primitive so the
    rag_pipeline_evidence schema can chain to a streaming downstream chatbot.
    """

    def __init__(self) -> None:
        self._h = hashlib.sha256()
        self._byte_count = 0
        self._finalized = False

    def update(self, delta: str) -> None:
        if self._finalized:
            raise RuntimeError("IncrementalTextHasher already finalized")
        encoded = delta.encode("utf-8")
        self._h.update(encoded)
        self._byte_count += len(encoded)

    def digest(self) -> bytes:
        self._finalized = True
        return self._h.digest()

    @property
    def byte_count(self) -> int:
        return self._byte_count
