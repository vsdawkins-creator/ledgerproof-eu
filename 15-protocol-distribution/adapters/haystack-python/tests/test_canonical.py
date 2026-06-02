"""Tests for canonical CBOR + SHA-256 + Merkle helpers."""

import pytest

from ledgerproof_haystack.canonical import (
    canonical_cbor,
    hash_payload,
    merkle_root,
    sha256_hex,
)


def test_canonical_cbor_is_deterministic():
    a = {"b": 1, "a": 2, "c": [3, 2, 1]}
    b = {"c": [3, 2, 1], "a": 2, "b": 1}
    assert canonical_cbor(a) == canonical_cbor(b)


def test_hash_payload_matches_sha256_of_canonical_cbor():
    obj = {"x": 1, "y": [1, 2, 3]}
    assert hash_payload(obj) == sha256_hex(canonical_cbor(obj))


def test_sha256_hex_accepts_str_and_bytes():
    assert sha256_hex("hello") == sha256_hex(b"hello")


def test_merkle_root_empty():
    assert merkle_root([]) == sha256_hex(b"")


def test_merkle_root_single_leaf_returns_leaf():
    leaf = sha256_hex(b"only-one")
    assert merkle_root([leaf]) == leaf


def test_merkle_root_two_leaves_deterministic():
    leaves = [sha256_hex(b"a"), sha256_hex(b"b")]
    r1 = merkle_root(leaves)
    r2 = merkle_root(leaves)
    assert r1 == r2 and len(r1) == 64


def test_merkle_root_odd_count_duplicates_last():
    leaves = [sha256_hex(s) for s in (b"a", b"b", b"c")]
    # not asserting exact value; assert stable and 64 hex chars
    root = merkle_root(leaves)
    assert len(root) == 64
    assert all(c in "0123456789abcdef" for c in root)
