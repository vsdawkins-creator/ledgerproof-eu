"""Signer behaviour: ephemeral Ed25519, IBM KMS stubs raise NotImplementedError."""

from __future__ import annotations

import pytest

from ledgerproof_watsonx import (
    Ed25519Signer,
    IbmHpcsEd25519Signer,
    IbmKeyProtectEd25519Signer,
    verify,
)


def test_ephemeral_sign_round_trip():
    s = Ed25519Signer()
    msg = b"hello watsonx"
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


def test_ibm_keyprotect_stub_raises():
    s = IbmKeyProtectEd25519Signer(
        "crn:v1:bluemix:public:kms:eu-de:a/acc:inst:key:abc"
    )
    assert s.key_id.startswith("crn:v1:bluemix")
    with pytest.raises(NotImplementedError):
        s.sign(b"x")


def test_ibm_hpcs_stub_raises():
    s = IbmHpcsEd25519Signer("hpcs-instance-xyz", "lpr-receipts-key")
    assert s.key_id == "hpcs:hpcs-instance-xyz:lpr-receipts-key"
    with pytest.raises(NotImplementedError):
        s.sign(b"x")
