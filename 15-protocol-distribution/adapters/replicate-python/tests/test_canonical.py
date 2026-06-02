"""Canonical CBOR determinism and incremental hashing tests."""

from __future__ import annotations

import hashlib
import io

import pytest

from ledgerproof_replicate.canonical import (
    IncrementalBytesHasher,
    IncrementalTextHasher,
    canonical_encode,
    canonical_hash,
    hash_bytes,
    hash_stream,
    hash_text,
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


def test_hash_bytes_matches_sha256():
    assert hash_bytes(b"\x00\xff\x10") == hashlib.sha256(b"\x00\xff\x10").digest()


def test_incremental_text_hasher_matches_full_hash():
    parts = ["Hello, ", "world", "!"]
    inc = IncrementalTextHasher()
    for p in parts:
        inc.update(p)
    full = hashlib.sha256("".join(parts).encode("utf-8")).digest()
    assert inc.digest() == full
    assert inc.byte_count == len("Hello, world!".encode("utf-8"))


def test_incremental_text_hasher_disallows_update_after_finalize():
    inc = IncrementalTextHasher()
    inc.update("x")
    inc.digest()
    with pytest.raises(RuntimeError):
        inc.update("y")


def test_incremental_bytes_hasher_matches_full_hash():
    chunks = [b"\x00\x01", b"\x02\x03", b"\x04"]
    inc = IncrementalBytesHasher()
    for c in chunks:
        inc.update(c)
    full = hashlib.sha256(b"\x00\x01\x02\x03\x04").digest()
    assert inc.digest() == full
    assert inc.byte_count == 5


def test_hash_stream_matches_full_hash_for_large_input():
    data = b"x" * (128 * 1024 + 7)  # > one chunk
    digest, total = hash_stream(io.BytesIO(data))
    assert digest == hashlib.sha256(data).digest()
    assert total == len(data)
