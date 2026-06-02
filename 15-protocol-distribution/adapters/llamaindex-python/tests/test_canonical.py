"""Determinism + structural tests for canonical CBOR encoding."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from ledgerproof_llamaindex.canonical import (
    canonical_cbor,
    receipt_digest,
    transcript_hash,
)


def test_canonical_cbor_is_deterministic_across_key_order():
    a = {"b": 1, "a": 2, "c": [3, 4]}
    b = {"a": 2, "c": [3, 4], "b": 1}
    assert canonical_cbor(a) == canonical_cbor(b)


def test_canonical_cbor_normalizes_datetime():
    naive = datetime(2026, 6, 1, 12, 0, 0)
    aware = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert canonical_cbor({"t": naive}) == canonical_cbor({"t": aware})


def test_canonical_cbor_normalizes_bytes_to_hex():
    payload = {"sig": b"\x01\x02\x03"}
    encoded = canonical_cbor(payload)
    # Encoded payload should contain the hex string, not the raw bytes.
    import cbor2

    decoded = cbor2.loads(encoded)
    assert decoded == {"sig": "010203"}


def test_receipt_digest_is_sha256_hex():
    digest = receipt_digest({"k": "v"})
    assert len(digest) == 64
    int(digest, 16)  # raises if not hex


def test_transcript_hash_changes_with_content():
    a = transcript_hash([{"k": "messages", "v": "hello"}])
    b = transcript_hash([{"k": "messages", "v": "world"}])
    assert a != b
    assert a == transcript_hash([{"k": "messages", "v": "hello"}])


def test_canonical_cbor_rejects_non_dict_top_level():
    with pytest.raises(TypeError):
        canonical_cbor([1, 2, 3])  # type: ignore[arg-type]
