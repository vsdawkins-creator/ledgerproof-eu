"""Canonical CBOR encoding for LedgerProof receipts.

Deterministic byte output: the same logical receipt MUST encode to the same
bytes on any platform, any Python version, any time. This is the contract
that lets verifiers re-derive the signed digest offline (C4: local
verification only — no network round-trip required).

We rely on cbor2's deterministic encoding mode (canonical=True), which:
  - Sorts map keys by their CBOR-encoded byte order.
  - Uses the shortest integer / length encodings.
  - Forbids indefinite-length items.
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

import cbor2


def canonical_encode(obj: Mapping[str, Any]) -> bytes:
    """Encode a mapping as canonical (deterministic) CBOR.

    Raises:
        TypeError: if `obj` is not a Mapping or contains non-CBOR values.
    """
    if not isinstance(obj, Mapping):
        raise TypeError(
            f"canonical_encode requires a Mapping, got {type(obj).__name__}"
        )
    return cbor2.dumps(dict(obj), canonical=True, date_as_datetime=False)


def receipt_digest(obj: Mapping[str, Any]) -> bytes:
    """Return the SHA-256 digest of the canonical CBOR encoding of `obj`.

    This is the bytestring the Ed25519 signer signs.
    """
    return hashlib.sha256(canonical_encode(obj)).digest()
