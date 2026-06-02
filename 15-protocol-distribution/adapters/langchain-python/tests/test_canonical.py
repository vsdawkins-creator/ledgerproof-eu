"""Determinism tests for canonical CBOR encoding."""

from ledgerproof_langchain.canonical import canonical_encode, receipt_digest


def test_canonical_encode_deterministic_same_input():
    obj = {
        "schema_id": "chatbot_session/v1",
        "run_id": "abc-123",
        "timestamp_utc": "2026-06-01T12:00:00Z",
        "deployer_id": "acme-corp",
        "transcript_sha256": "0" * 64,
    }
    a = canonical_encode(obj)
    b = canonical_encode(obj)
    assert a == b
    assert isinstance(a, bytes)
    assert len(a) > 0


def test_canonical_encode_key_order_independent():
    a = canonical_encode({"a": 1, "b": 2, "c": 3})
    b = canonical_encode({"c": 3, "a": 1, "b": 2})
    assert a == b, "key order must not affect canonical encoding"


def test_receipt_digest_is_sha256_size():
    obj = {"x": 1}
    d = receipt_digest(obj)
    assert isinstance(d, bytes)
    assert len(d) == 32  # SHA-256


def test_canonical_encode_rejects_non_mapping():
    import pytest

    with pytest.raises(TypeError):
        canonical_encode([1, 2, 3])  # type: ignore[arg-type]
