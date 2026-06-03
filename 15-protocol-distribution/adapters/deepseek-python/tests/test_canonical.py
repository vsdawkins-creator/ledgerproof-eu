"""Determinism + stability tests for canonical CBOR encoding."""

from ledgerproof_deepseek.canonical import (
    canonical_encode,
    canonical_hash,
    canonical_hash_hex,
)


def test_canonical_encode_is_deterministic_across_key_order():
    a = {"b": 1, "a": 2, "c": [1, 2, 3]}
    b = {"c": [1, 2, 3], "a": 2, "b": 1}
    assert canonical_encode(a) == canonical_encode(b)


def test_canonical_hash_differs_for_different_payloads():
    h1 = canonical_hash({"x": 1})
    h2 = canonical_hash({"x": 2})
    assert h1 != h2
    assert len(h1) == 32  # SHA-256


def test_canonical_hash_hex_is_64_lowercase_hex():
    h = canonical_hash_hex({"x": 1})
    assert len(h) == 64
    assert h == h.lower()
    assert all(c in "0123456789abcdef" for c in h)


def test_canonical_encoding_is_byte_stable_for_nested_structs():
    payload_1 = {"messages": [{"role": "user", "content": "hi"}], "model": "deepseek-chat"}
    payload_2 = {"model": "deepseek-chat", "messages": [{"role": "user", "content": "hi"}]}
    assert canonical_encode(payload_1) == canonical_encode(payload_2)
