"""Signer/verify tests."""

from __future__ import annotations

import pytest

from ledgerproof_ai21.signer import (
    AwsKmsEd25519Signer,
    AzureKeyVaultEd25519Signer,
    Ed25519Signer,
    GcpKmsEd25519Signer,
    verify,
)


def test_ed25519_signer_sign_and_verify_round_trip():
    signer = Ed25519Signer()
    msg = b"jamba long context body"
    sig = signer.sign(msg)
    assert verify(signer.public_key_bytes(), msg, sig)


def test_ed25519_signer_verify_fails_on_tampered_message():
    signer = Ed25519Signer()
    sig = signer.sign(b"original")
    assert not verify(signer.public_key_bytes(), b"tampered", sig)


def test_ed25519_signer_from_seed_is_deterministic():
    seed = b"\x01" * 32
    a = Ed25519Signer.from_seed(seed)
    b = Ed25519Signer.from_seed(seed)
    assert a.public_key_bytes() == b.public_key_bytes()
    # Same key id derived from the same public key.
    assert a.key_id == b.key_id


def test_ed25519_signer_from_seed_rejects_wrong_length():
    with pytest.raises(ValueError):
        Ed25519Signer.from_seed(b"\x00" * 16)


def test_ed25519_signer_key_id_is_stable_for_same_key():
    signer = Ed25519Signer()
    kid1 = signer.key_id
    kid2 = signer.key_id
    assert kid1 == kid2
    assert kid1.startswith("lpr-ed25519-")


def test_hsm_stubs_raise_not_implemented():
    """MVP HSM stubs raise — we don't ship a half-baked KMS path."""
    aws = AwsKmsEd25519Signer("arn:aws:kms:eu-west-1:000:key/abc")
    with pytest.raises(NotImplementedError):
        aws.sign(b"x")
    assert aws.key_id.startswith("arn:aws:kms")

    gcp = GcpKmsEd25519Signer("projects/p/locations/l/keyRings/r/cryptoKeys/k")
    with pytest.raises(NotImplementedError):
        gcp.sign(b"x")

    az = AzureKeyVaultEd25519Signer("https://vault.azure.net/keys/x/123")
    with pytest.raises(NotImplementedError):
        az.sign(b"x")
