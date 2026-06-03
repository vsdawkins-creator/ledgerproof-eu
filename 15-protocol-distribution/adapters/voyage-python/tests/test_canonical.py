"""Canonical CBOR + vector canonicalization tests."""

from __future__ import annotations

import hashlib
import struct

import pytest

from ledgerproof_voyage.canonical import (
    IncrementalTextHasher,
    canonical_encode,
    canonical_hash,
    canonicalize_vector,
    hash_text,
    hash_vector,
)


def test_canonical_encoding_is_deterministic_across_key_order():
    a = {"b": 2, "a": 1, "c": 3}
    b = {"c": 3, "a": 1, "b": 2}
    assert canonical_encode(a) == canonical_encode(b)


def test_canonical_hash_changes_on_value_change():
    base = {"x": "hello", "n": 1}
    mutated = {"x": "hello", "n": 2}
    assert canonical_hash(base) != canonical_hash(mutated)


def test_hash_text_matches_sha256():
    assert hash_text("hello") == hashlib.sha256(b"hello").digest()


def test_canonicalize_vector_is_big_endian_float64():
    vec = [1.0, -0.5, 0.125]
    expected = b"".join(struct.pack("!d", f) for f in vec)
    assert canonicalize_vector(vec) == expected
    assert len(canonicalize_vector(vec)) == 24


def test_hash_vector_is_deterministic_across_runs():
    vec = [0.1, 0.2, 0.3, 0.4]
    h1 = hash_vector(vec)
    h2 = hash_vector(list(vec))
    assert h1 == h2
    assert h1 == hashlib.sha256(b"".join(struct.pack("!d", f) for f in vec)).digest()


def test_hash_vector_differs_for_different_dims():
    a = hash_vector([1.0, 2.0])
    b = hash_vector([1.0, 2.0, 0.0])
    assert a != b


def test_incremental_hasher_matches_full_hash():
    parts = ["Hello, ", "world", "!"]
    inc = IncrementalTextHasher()
    for p in parts:
        inc.update(p)
    full = hashlib.sha256("".join(parts).encode("utf-8")).digest()
    assert inc.digest() == full


def test_incremental_hasher_disallows_update_after_finalize():
    inc = IncrementalTextHasher()
    inc.update("x")
    inc.digest()
    with pytest.raises(RuntimeError):
        inc.update("y")
