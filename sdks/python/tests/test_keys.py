"""Tests for the Keypair class: generation, persistence, signing, verification."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from ledgerproof.errors import KeyManagementError
from ledgerproof.keys import Keypair


class TestKeypairGeneration:
    def test_generate_produces_valid_keypair(self) -> None:
        kp = Keypair.generate()
        assert isinstance(kp.public_b64(), str)
        assert len(kp.public_b64()) >= 40  # base64 of 32 bytes is 44 chars padded

    def test_distinct_generations_produce_distinct_keys(self) -> None:
        a = Keypair.generate()
        b = Keypair.generate()
        assert a.public_b64() != b.public_b64()


class TestKeypairFromHex:
    def test_roundtrip_via_hex(self) -> None:
        a = Keypair.generate()
        hex_seed = a.private_hex()
        b = Keypair.from_hex(hex_seed)
        assert a.public_b64() == b.public_b64()

    def test_rejects_wrong_length(self) -> None:
        with pytest.raises(KeyManagementError):
            Keypair.from_hex("abcd")

    def test_rejects_non_hex(self) -> None:
        with pytest.raises(KeyManagementError):
            Keypair.from_hex("g" * 64)


class TestKeypairFromEnv:
    def test_returns_none_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("LEDGERPROOF_SIGNING_KEY_HEX", raising=False)
        assert Keypair.from_env() is None

    def test_loads_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        kp = Keypair.generate()
        monkeypatch.setenv("LEDGERPROOF_SIGNING_KEY_HEX", kp.private_hex())
        loaded = Keypair.from_env()
        assert loaded is not None
        assert loaded.public_b64() == kp.public_b64()


class TestKeypairPersistence:
    def test_save_creates_file_with_secure_perms(self, tmp_path: Path) -> None:
        kp = Keypair.generate()
        key_path = tmp_path / "key.bin"
        kp.save(key_path)
        assert key_path.exists()
        if os.name != "nt":  # POSIX-only check
            mode = stat.S_IMODE(key_path.stat().st_mode)
            assert mode == 0o600

    def test_save_then_load_roundtrip(self, tmp_path: Path) -> None:
        kp = Keypair.generate()
        key_path = tmp_path / "key.bin"
        kp.save(key_path)
        loaded = Keypair.load(key_path)
        assert kp.public_b64() == loaded.public_b64()

    def test_save_is_idempotent_for_same_key(self, tmp_path: Path) -> None:
        kp = Keypair.generate()
        key_path = tmp_path / "key.bin"
        kp.save(key_path)
        # Second save of the SAME key should not raise.
        kp.save(key_path)

    def test_save_refuses_to_overwrite_different_key(self, tmp_path: Path) -> None:
        a = Keypair.generate()
        b = Keypair.generate()
        key_path = tmp_path / "key.bin"
        a.save(key_path)
        with pytest.raises(KeyManagementError, match="refusing to overwrite"):
            b.save(key_path)

    def test_load_rejects_insecure_perms(self, tmp_path: Path) -> None:
        if os.name == "nt":
            pytest.skip("POSIX permissions only")
        kp = Keypair.generate()
        key_path = tmp_path / "key.bin"
        kp.save(key_path)
        # Loosen permissions deliberately.
        os.chmod(key_path, 0o644)
        with pytest.raises(KeyManagementError, match="insecure permissions"):
            Keypair.load(key_path)

    def test_load_rejects_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(KeyManagementError, match="not found"):
            Keypair.load(tmp_path / "nonexistent.bin")

    def test_load_rejects_malformed_file(self, tmp_path: Path) -> None:
        key_path = tmp_path / "key.bin"
        key_path.write_bytes(b"only 8b!")
        os.chmod(key_path, 0o600)
        with pytest.raises(KeyManagementError, match="32 bytes"):
            Keypair.load(key_path)


class TestKeypairLoadOrGenerate:
    def test_generates_when_missing(self, tmp_path: Path) -> None:
        key_path = tmp_path / "key.bin"
        kp, generated = Keypair.load_or_generate(key_path)
        assert generated is True
        assert key_path.exists()
        assert kp.public_b64() != ""

    def test_loads_when_present(self, tmp_path: Path) -> None:
        key_path = tmp_path / "key.bin"
        original, gen1 = Keypair.load_or_generate(key_path)
        assert gen1 is True
        loaded, gen2 = Keypair.load_or_generate(key_path)
        assert gen2 is False
        assert original.public_b64() == loaded.public_b64()


class TestSignAndVerify:
    def test_signs_arbitrary_bytes(self) -> None:
        kp = Keypair.generate()
        msg = b"hello, LedgerProof"
        sig = kp.sign(msg)
        assert isinstance(sig, bytes)
        assert len(sig) == 64  # Ed25519 signature length

    def test_verify_accepts_valid_signature(self) -> None:
        kp = Keypair.generate()
        msg = b"sign me"
        sig = kp.sign(msg)
        assert kp.verify(sig, msg) is True

    def test_verify_rejects_tampered_signature(self) -> None:
        kp = Keypair.generate()
        msg = b"sign me"
        sig = bytearray(kp.sign(msg))
        sig[0] ^= 0xFF
        assert kp.verify(bytes(sig), msg) is False

    def test_verify_rejects_tampered_message(self) -> None:
        kp = Keypair.generate()
        sig = kp.sign(b"original")
        assert kp.verify(sig, b"tampered") is False

    def test_signs_32_byte_entry_hash(self) -> None:
        """The LPR protocol signs the raw 32 bytes of the SHA-256 entry hash."""
        kp = Keypair.generate()
        entry_hash_hex = "a" * 64
        entry_hash_bytes = bytes.fromhex(entry_hash_hex)
        assert len(entry_hash_bytes) == 32
        sig = kp.sign(entry_hash_bytes)
        assert kp.verify(sig, entry_hash_bytes) is True


class TestRepr:
    def test_repr_does_not_leak_private_key(self) -> None:
        kp = Keypair.generate()
        r = repr(kp)
        # The full private hex should never appear in repr.
        assert kp.private_hex() not in r
        # Should contain a truncated public key marker.
        assert "Keypair" in r
