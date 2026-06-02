"""
Canonical CBOR encoding for LedgerProof receipts.

Determinism is load-bearing: identical receipt content MUST produce identical bytes
across processes, machines, and Python versions, so that signatures verify offline
(constraint C4) against the Merkle tree anchored to Bitcoin.

We use CBOR with deterministic encoding (RFC 8949 Section 4.2) via cbor2's
canonical=True flag, plus stable key ordering for nested mappings.
"""

from __future__ import annotations

import hashlib
from typing import Any, BinaryIO

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


def hash_bytes(b: bytes) -> bytes:
    """SHA-256 of raw bytes. Used for image/audio/video output content hashes."""
    return hashlib.sha256(b).digest()


def hash_stream(stream: BinaryIO, chunk_size: int = 65536) -> tuple[bytes, int]:
    """
    SHA-256 of a binary stream, returning (digest, byte_length).

    Replicate frequently returns FileOutput objects (URLs that resolve to image,
    audio, or video bytes). For very large generated artifacts (a 10s ZeroScope
    video, a MusicGen 30s clip) we MUST stream the hash rather than loading the
    full output into memory.
    """
    h = hashlib.sha256()
    total = 0
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        h.update(chunk)
        total += len(chunk)
    return h.digest(), total


class IncrementalTextHasher:
    """
    Stream-aware SHA-256 hasher for streaming Replicate text responses
    (constraint C6). Replicate's `client.stream()` yields events with `.data`
    text increments (e.g. LLaMA text generation token-by-token).
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


class IncrementalBytesHasher:
    """
    Stream-aware SHA-256 hasher for streaming binary outputs (constraint C6).

    Used when the caller hashes a Replicate file output piecewise (e.g. while
    downloading a FLUX image or MusicGen audio clip in chunks). Symmetric to
    IncrementalTextHasher but accepts bytes.
    """

    def __init__(self) -> None:
        self._h = hashlib.sha256()
        self._byte_count = 0
        self._finalized = False

    def update(self, chunk: bytes) -> None:
        if self._finalized:
            raise RuntimeError("IncrementalBytesHasher already finalized")
        self._h.update(chunk)
        self._byte_count += len(chunk)

    def digest(self) -> bytes:
        self._finalized = True
        return self._h.digest()

    @property
    def byte_count(self) -> int:
        return self._byte_count
