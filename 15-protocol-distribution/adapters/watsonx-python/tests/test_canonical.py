"""Canonical encoding determinism + hasher correctness."""

from __future__ import annotations

import hashlib

from ledgerproof_watsonx.canonical import (
    IncrementalTextHasher,
    canonical_encode,
    canonical_hash,
    hash_bytes,
    hash_text,
)


def test_canonical_encode_is_deterministic_under_key_reordering():
    a = {"b": 1, "a": 2, "c": [1, 2, 3]}
    b = {"c": [1, 2, 3], "a": 2, "b": 1}
    assert canonical_encode(a) == canonical_encode(b)


def test_canonical_hash_matches_sha256_over_encoding():
    payload = {"x": "y", "n": 7}
    assert canonical_hash(payload) == hashlib.sha256(canonical_encode(payload)).digest()


def test_hash_text_and_hash_bytes_agree_on_utf8():
    assert hash_text("héllo") == hash_bytes("héllo".encode("utf-8"))


def test_incremental_hasher_matches_one_shot():
    parts = ["Hallo, ", "Welt", "!"]
    full = "".join(parts)
    h = IncrementalTextHasher()
    for p in parts:
        h.update(p)
    assert h.byte_count == len(full.encode("utf-8"))
    assert h.digest() == hash_text(full)


def test_incremental_hasher_byte_mode_matches_text_mode():
    h_text = IncrementalTextHasher()
    h_bytes = IncrementalTextHasher()
    text = "watsonx-stream"
    h_text.update(text)
    h_bytes.update_bytes(text.encode("utf-8"))
    assert h_text.digest() == h_bytes.digest()


def test_incremental_hasher_finalized_guard():
    h = IncrementalTextHasher()
    h.update("a")
    h.digest()
    try:
        h.update("b")
    except RuntimeError:
        return
    raise AssertionError("expected RuntimeError on update-after-finalize")
