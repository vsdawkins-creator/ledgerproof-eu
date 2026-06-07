"""Deterministic canonicalization for receipts.

CBOR canonical form (RFC 8949 Section 4.2.1) is used for byte-for-byte
reproducible hashing. Keys are sorted lexicographically; integers use
shortest encoding; floats use canonical CBOR float encoding.
"""

from __future__ import annotations

import hashlib
from typing import Any

import cbor2


def canonical_cbor(obj: Any) -> bytes:
    """Encode a Python object as deterministic CBOR (RFC 8949 §4.2.1)."""
    return cbor2.dumps(obj, canonical=True)


def sha256_hex(data: bytes | str) -> str:
    """Return hex-encoded SHA-256 of bytes or a UTF-8 string."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def hash_payload(payload: Any) -> str:
    """Canonical CBOR + SHA-256 hex digest for any JSON-like Python value."""
    return sha256_hex(canonical_cbor(payload))


def merkle_root(leaves: list[str]) -> str:
    """Compute a SHA-256 Merkle root over a list of hex leaf digests.

    Duplicate-last-on-odd convention (Bitcoin-compatible). Returns the
    empty-leaf sentinel if `leaves` is empty.
    """
    if not leaves:
        return sha256_hex(b"")
    layer = [bytes.fromhex(leaf) for leaf in leaves]
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        layer = [hashlib.sha256(layer[i] + layer[i + 1]).digest() for i in range(0, len(layer), 2)]
    return layer[0].hex()
