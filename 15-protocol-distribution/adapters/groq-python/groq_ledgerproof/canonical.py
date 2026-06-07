"""Canonical serialization for LedgerProof receipts.

We use deterministic CBOR (RFC 8949 §4.2.1, "Core Deterministic Encoding")
so that two implementations of the protocol produce byte-identical
signing inputs for the same logical receipt.
"""

from __future__ import annotations

from typing import Any

import cbor2


def canonical_cbor(payload: dict[str, Any]) -> bytes:
    """Encode a dict as deterministic CBOR.

    cbor2 already sorts map keys with `canonical=True`, uses shortest int
    encoding, and rejects indefinite-length items.
    """
    return cbor2.dumps(payload, canonical=True)


def canonical_decode(blob: bytes) -> dict[str, Any]:
    return cbor2.loads(blob)
