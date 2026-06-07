"""Canonical CBOR encoding for deterministic receipt serialization.

Uses cbor2 with canonical=True so encoded output is byte-stable across runs,
machines, and Python versions. This is what gets fed into the Ed25519 signer
and into the Merkle tree leaf hash.
"""

from __future__ import annotations

import hashlib
from typing import Any

import cbor2


def canonical_encode(obj: Any) -> bytes:
    """Encode `obj` to canonical (deterministic) CBOR.

    Canonical CBOR sorts map keys, uses smallest integer encoding, and forbids
    indefinite-length items. Two semantically identical Python dicts will always
    produce byte-identical output.
    """
    return cbor2.dumps(obj, canonical=True)


def canonical_hash(obj: Any) -> bytes:
    """SHA-256 of the canonical CBOR encoding of `obj`."""
    return hashlib.sha256(canonical_encode(obj)).digest()


def canonical_hash_hex(obj: Any) -> str:
    """SHA-256 hex digest of the canonical CBOR encoding of `obj`."""
    return canonical_hash(obj).hex()
