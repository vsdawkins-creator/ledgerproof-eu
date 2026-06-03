"""Canonical CBOR determinism and incremental hashing tests."""

from __future__ import annotations

import hashlib

import pytest

from ledgerproof_mistral_codestral.canonical import (
    IncrementalTextHasher,
    canonical_encode,
    canonical_hash,
    hash_text,
)


def test_canonical_encoding_is_deterministic_across_key_order():
    a = {"b": 2, "a": 1, "c": 3}
    b = {"c": 3, "a": 1, "b": 2}
    assert canonical_encode(a) == canonical_encode(b)


def test_canonical_encoding_is_stable_for_nested_maps():
    a = {"outer": {"y": 2, "x": 1}, "k": "v"}
    b = {"k": "v", "outer": {"x": 1, "y": 2}}
    assert canonical_encode(a) == canonical_encode(b)


def test_canonical_hash_changes_on_value_change():
    base = {"x": "hello", "n": 1}
    mutated = {"x": "hello", "n": 2}
    assert canonical_hash(base) != canonical_hash(mutated)


def test_hash_text_matches_sha256():
    assert hash_text("def fib(n):") == hashlib.sha256(b"def fib(n):").digest()


def test_incremental_hasher_matches_full_hash():
    parts = ["def ", "fib(n):\n", "    return ", "1 if n<2 else ", "fib(n-1)+fib(n-2)\n"]
    inc = IncrementalTextHasher()
    for p in parts:
        inc.update(p)
    full = hashlib.sha256("".join(parts).encode("utf-8")).digest()
    assert inc.digest() == full
    assert inc.byte_count == len("".join(parts).encode("utf-8"))


def test_incremental_hasher_counts_lines():
    inc = IncrementalTextHasher()
    inc.update("line1\nline2\n")
    inc.update("line3\n")
    assert inc.line_count == 3


def test_incremental_hasher_disallows_update_after_finalize():
    inc = IncrementalTextHasher()
    inc.update("x")
    inc.digest()
    with pytest.raises(RuntimeError):
        inc.update("y")
