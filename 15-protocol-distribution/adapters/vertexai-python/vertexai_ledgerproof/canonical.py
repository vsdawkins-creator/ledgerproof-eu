"""Deterministic canonicalization for receipt payloads.

LedgerProof canonical form: CBOR (RFC 8949) with deterministic encoding
(canonical option), sorted map keys, definite-length encoding. The result
is what gets hashed (SHA-256) and signed (Ed25519).

Constraint C5: canonicalization must be byte-stable across runtimes so
local verification produces the same digest.
"""
from __future__ import annotations

import hashlib
from typing import Any

import cbor2


def canonicalize(payload: dict[str, Any]) -> bytes:
    """Encode payload to deterministic CBOR bytes."""
    return cbor2.dumps(payload, canonical=True)


def digest(payload: dict[str, Any]) -> bytes:
    """Return SHA-256 digest of canonicalized payload."""
    return hashlib.sha256(canonicalize(payload)).digest()


def hex_digest(payload: dict[str, Any]) -> str:
    """Convenience: hex-encoded SHA-256 digest of canonicalized payload."""
    return digest(payload).hex()
