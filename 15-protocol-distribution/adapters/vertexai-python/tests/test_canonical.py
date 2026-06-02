"""Canonicalization byte-stability + digest tests."""
from __future__ import annotations

from ledgerproof_vertexai.canonical import canonicalize, digest, hex_digest


def test_canonical_key_order_independence():
    a = {"b": 1, "a": 2}
    b = {"a": 2, "b": 1}
    assert canonicalize(a) == canonicalize(b)


def test_digest_is_32_bytes():
    d = digest({"x": 1})
    assert isinstance(d, bytes)
    assert len(d) == 32


def test_hex_digest_is_64_chars():
    h = hex_digest({"x": 1})
    assert len(h) == 64
    int(h, 16)  # must be valid hex


def test_changes_to_payload_change_digest():
    a = hex_digest({"x": 1})
    b = hex_digest({"x": 2})
    assert a != b
