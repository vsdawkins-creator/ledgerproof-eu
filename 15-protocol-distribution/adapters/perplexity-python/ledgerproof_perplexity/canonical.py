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


def citation_list_hash_hex(citations: list[str] | None) -> str:
    """Stable SHA-256 hash of a list of citation URLs.

    Deterministic across runs: sorts URLs lexicographically before hashing so
    that two semantically identical citation sets produce the same digest.
    Empty / None input hashes the canonical empty list.

    The deployer is responsible for ensuring that the citation list passed
    here is the *exact* list they intend to anchor — typically pulled directly
    from `response.citations` returned by the Perplexity API. The adapter does
    not fetch or validate URLs (C4 — local verification only).
    """
    items = sorted(citations or [])
    payload = canonical_encode(items)
    return hashlib.sha256(payload).hexdigest()
