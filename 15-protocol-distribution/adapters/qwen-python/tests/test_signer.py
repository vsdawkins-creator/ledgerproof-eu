"""Signer tests — sign/verify roundtrip and seed determinism."""

from __future__ import annotations

import pytest

from ledgerproof_qwen.signer import (
    AwsKmsEd25519Signer,
    AzureKeyVaultEd25519Signer,
    Ed25519Signer,
    GcpKmsEd25519Signer,
    verify,
)


def test_sign_and_verify_roundtrip():
    signer = Ed25519Signer()
    msg = b"hello qwen"
    sig = signer.sign(msg)
    assert verify(signer.public_key_bytes(), msg, sig)


def test_verify_fails_on_wrong_message():
    signer = Ed25519Signer()
    sig = signer.sign(b"original")
    assert not verify(signer.public_key_bytes(), b"tampered", sig)


def test_verify_fails_on_wrong_signature():
    signer = Ed25519Signer()
    assert not verify(signer.public_key_bytes(), b"msg", b"\x00" * 64)


def test_key_id_is_deterministic_fingerprint_format():
    signer = Ed25519Signer()
    assert signer.key_id.startswith("lpr-ed25519-")
    assert len(signer.key_id) == len("lpr-ed25519-") + 16


def test_from_seed_is_deterministic():
    seed = bytes.fromhex("00" * 32)
    a = Ed25519Signer.from_seed(seed)
    b = Ed25519Signer.from_seed(seed)
    assert a.public_key_bytes() == b.public_key_bytes()


def test_from_seed_rejects_wrong_length():
    with pytest.raises(ValueError):
        Ed25519Signer.from_seed(b"short")


def test_hsm_stubs_carry_key_ids_but_raise_on_sign():
    aws = AwsKmsEd25519Signer("arn:aws:kms:eu-west-1:123:key/abc")
    assert aws.key_id.startswith("arn:aws:kms:")
    with pytest.raises(NotImplementedError):
        aws.sign(b"x")

    gcp = GcpKmsEd25519Signer("projects/p/locations/europe-west3/keyRings/r/cryptoKeys/k/cryptoKeyVersions/1")
    assert "europe-west3" in gcp.key_id
    with pytest.raises(NotImplementedError):
        gcp.sign(b"x")

    az = AzureKeyVaultEd25519Signer("https://kv.vault.azure.net/keys/k/v")
    assert az.key_id.startswith("https://")
    with pytest.raises(NotImplementedError):
        az.sign(b"x")
