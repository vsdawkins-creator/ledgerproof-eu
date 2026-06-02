"""Canonical CBOR determinism + digest stability."""

import pytest

from ledgerproof_semantic_kernel.canonical import canonical_encode, receipt_digest


def test_canonical_encode_is_deterministic_across_key_order():
    a = {"a": 1, "b": 2, "c": 3}
    b = {"c": 3, "b": 2, "a": 1}
    assert canonical_encode(a) == canonical_encode(b)


def test_canonical_encode_rejects_non_mapping():
    with pytest.raises(TypeError):
        canonical_encode([1, 2, 3])  # type: ignore[arg-type]


def test_receipt_digest_is_sha256_length():
    d = receipt_digest({"hello": "world"})
    assert isinstance(d, bytes)
    assert len(d) == 32


def test_receipt_digest_stable():
    obj = {"schema_id": "chatbot_session/v1", "x": 1}
    assert receipt_digest(obj) == receipt_digest(dict(obj))
