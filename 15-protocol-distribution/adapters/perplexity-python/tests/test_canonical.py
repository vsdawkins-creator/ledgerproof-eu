"""Determinism + stability tests for canonical CBOR encoding and citation hashing."""

import hashlib

from ledgerproof_perplexity.canonical import (
    canonical_encode,
    canonical_hash,
    canonical_hash_hex,
    citation_list_hash_hex,
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


def test_citation_list_hash_is_order_independent():
    """Sorting must make the hash deterministic regardless of input order."""
    urls_1 = ["https://b.example/2", "https://a.example/1", "https://c.example/3"]
    urls_2 = ["https://a.example/1", "https://b.example/2", "https://c.example/3"]
    assert citation_list_hash_hex(urls_1) == citation_list_hash_hex(urls_2)


def test_citation_list_hash_distinguishes_content():
    h1 = citation_list_hash_hex(["https://a.example/1"])
    h2 = citation_list_hash_hex(["https://a.example/2"])
    assert h1 != h2


def test_citation_list_hash_empty_and_none_agree():
    h_none = citation_list_hash_hex(None)
    h_empty = citation_list_hash_hex([])
    assert h_none == h_empty
    assert len(h_none) == 64
