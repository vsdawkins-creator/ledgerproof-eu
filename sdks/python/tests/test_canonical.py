"""Tests for canonical JSON serialization and SHA-256 hashing.

The canonical JSON must match the Rust server's serde_json output exactly,
or signatures fail. These tests pin the behavior with explicit fixtures.
"""

from __future__ import annotations

import json

import pytest

from ledgerproof.canonical import (
    artifact_hash,
    canonical_json,
    content_hash,
    entry_hash,
    sha256_hex,
)


class TestCanonicalJson:
    """Output must be deterministic, sorted, ASCII-safe."""

    def test_keys_sorted_alphabetically(self) -> None:
        obj = {"zebra": 1, "alpha": 2, "mango": 3}
        out = canonical_json(obj)
        assert out == '{"alpha":2,"mango":3,"zebra":1}'

    def test_nested_dicts_sorted_at_every_depth(self) -> None:
        obj = {"outer": {"z": 1, "a": 2}, "inner": {"y": 3, "b": 4}}
        out = canonical_json(obj)
        # Keys at every level must be sorted.
        assert out == '{"inner":{"b":4,"y":3},"outer":{"a":2,"z":1}}'

    def test_compact_separators_no_whitespace(self) -> None:
        obj = {"a": 1, "b": [2, 3]}
        out = canonical_json(obj)
        assert " " not in out
        assert "\n" not in out
        assert "\t" not in out

    def test_ascii_safe_escapes_non_ascii(self) -> None:
        obj = {"text": "Café résumé"}
        out = canonical_json(obj)
        # ensure_ascii=True escapes non-ASCII as \uXXXX
        assert "\\u00e9" in out  # é
        assert "Café" not in out  # raw form should not appear

    def test_no_nan_or_infinity(self) -> None:
        with pytest.raises(ValueError):
            canonical_json({"x": float("nan")})
        with pytest.raises(ValueError):
            canonical_json({"x": float("inf")})

    def test_roundtrips_through_json_parse(self) -> None:
        """Canonical output must be valid JSON itself."""
        obj = {
            "ai_system_id": "openai/gpt-4o/2024-11-20",
            "deployer_id": "LEI:5493001KJTIIGC8Y1R12",
            "deployer_country": "DE",
            "content_category": "SYNTHETIC_TEXT",
        }
        out = canonical_json(obj)
        reparsed = json.loads(out)
        assert reparsed == obj

    def test_deterministic_across_dict_insertion_order(self) -> None:
        """Same logical object → same bytes, regardless of insertion order."""
        a = {"z": 1, "a": 2, "m": 3}
        b = {"a": 2, "m": 3, "z": 1}
        c = {"m": 3, "z": 1, "a": 2}
        assert canonical_json(a) == canonical_json(b) == canonical_json(c)


class TestSha256Hex:
    """Hashing primitives."""

    def test_empty_bytes(self) -> None:
        assert sha256_hex(b"") == (
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

    def test_empty_string(self) -> None:
        # str gets utf-8 encoded then hashed.
        assert sha256_hex("") == sha256_hex(b"")

    def test_known_vector(self) -> None:
        # SHA-256("abc") per NIST FIPS 180-4 worked example, Appendix B.1.
        assert sha256_hex(b"abc") == (
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        )

    def test_output_is_lowercase_hex_64_chars(self) -> None:
        out = sha256_hex(b"any input")
        assert len(out) == 64
        assert out == out.lower()
        assert all(c in "0123456789abcdef" for c in out)

    def test_str_and_bytes_equivalent_for_ascii(self) -> None:
        assert sha256_hex("hello") == sha256_hex(b"hello")


class TestContentHash:
    """content_hash is SHA-256 of canonical JSON of the content."""

    def test_matches_manual_computation(self) -> None:
        content = {"foo": "bar", "n": 42}
        manual = sha256_hex(canonical_json(content))
        assert content_hash(content) == manual


class TestEntryHash:
    """entry_hash is SHA-256 of canonical JSON of the entry envelope."""

    def test_matches_manual_computation(self) -> None:
        entry = {
            "content": {"x": 1},
            "content_hash": "a" * 64,
            "content_type": "ai/article-50/v1",
            "entry_timestamp": "2026-05-25T08:00:00.000Z",
            "key_id": "test-key",
            "prev_hash": "0" * 64,
            "protocol_version": "ledgerproof/1.0",
            "publisher_id": "LEI:test",
            "sequence": 0,
        }
        manual = sha256_hex(canonical_json(entry))
        assert entry_hash(entry) == manual


class TestArtifactHash:
    """artifact_hash is SHA-256 of the raw artifact bytes."""

    def test_text_artifact(self) -> None:
        text = "LedgerProof EU smoke test artifact"
        assert artifact_hash(text) == sha256_hex(text.encode("utf-8"))

    def test_bytes_artifact(self) -> None:
        blob = b"\x00\x01\x02\x03binary content"
        assert artifact_hash(blob) == sha256_hex(blob)


class TestProtocolFidelity:
    """Spot checks against the reference smoke-test implementation.

    These match the canonicalization done in eu-ai-act-50-test-receipt.py
    which has been verified end-to-end against the live api-eu server.
    """

    def test_article_50_content_canonicalization(self) -> None:
        """Mirror the content shape used by the working smoke test."""
        content = {
            "ai_system_id": "test-ai-system-ledgerproof-smoke-001",
            "ai_system_version": "1.0.0",
            "artifact_bytes": 35,
            "artifact_content_type": "text/plain",
            "artifact_hash": "a" * 64,
            "content_category": "SYNTHETIC_TEXT",
            "deployer_country": "US",
            "deployer_id": "LedgerProof-Foundation-EU-Pilot",
            "deployer_name": "LedgerProof Foundation",
        }
        canonical = canonical_json(content)
        # Keys must appear in alphabetical order.
        assert canonical.index('"ai_system_id"') < canonical.index('"deployer_name"')
        assert canonical.index('"deployer_country"') < canonical.index('"deployer_id"')
        # No whitespace.
        assert ": " not in canonical
        # Reparse must match input.
        assert json.loads(canonical) == content
