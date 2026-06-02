"""Signer behaviour: ephemeral Ed25519, KMS stubs raise NotImplementedError."""

from __future__ import annotations

import pytest

from ledgerproof_bedrock import (
    AwsKmsEd25519Signer,
    Ed25519Signer,
    GcpKmsEd25519Signer,
    verify,
)


def test_ephemeral_sign_round_trip():
    s = Ed25519Signer()
    msg = b"hello bedrock"
    sig = s.sign(msg)
    assert verify(s.public_key_bytes(), msg, sig)
    assert not verify(s.public_key_bytes(), b"tampered", sig)


def test_from_seed_is_deterministic():
    seed = bytes(range(32))
    a = Ed25519Signer.from_seed(seed)
    b = Ed25519Signer.from_seed(seed)
    assert a.public_key_bytes() == b.public_key_bytes()


def test_from_seed_rejects_wrong_length():
    with pytest.raises(ValueError):
        Ed25519Signer.from_seed(b"short")


def test_key_id_format():
    s = Ed25519Signer()
    assert s.key_id.startswith("lpr-ed25519-")


def test_aws_kms_stub_raises():
    s = AwsKmsEd25519Signer("arn:aws:kms:eu-west-1:123456789012:key/abc")
    assert s.key_id.startswith("arn:aws:kms:")
    with pytest.raises(NotImplementedError):
        s.sign(b"x")


def test_gcp_kms_stub_raises():
    s = GcpKmsEd25519Signer("projects/p/locations/eu/keyRings/kr/cryptoKeys/k")
    with pytest.raises(NotImplementedError):
        s.sign(b"x")
