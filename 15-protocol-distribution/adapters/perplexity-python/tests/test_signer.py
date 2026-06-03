"""Signer tests — Ed25519 round-trip + HSM stub."""

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from ledgerproof_perplexity import Ed25519Signer, HSMSigner


def test_ed25519_signer_round_trip_signs_and_verifies():
    s = Ed25519Signer()
    sig = s.sign(b"hello")
    pub = Ed25519PublicKey.from_public_bytes(s.public_key_bytes())
    # verify() raises on failure
    pub.verify(sig, b"hello")


def test_ed25519_signer_signatures_differ_for_different_messages():
    s = Ed25519Signer()
    assert s.sign(b"a") != s.sign(b"b")


def test_ed25519_signer_deterministic_keypair_load():
    s1 = Ed25519Signer()
    raw = s1.private_key_bytes()
    s2 = Ed25519Signer(private_key_bytes=raw)
    assert s1.public_key_bytes() == s2.public_key_bytes()


def test_hsm_signer_stub_raises_until_implemented():
    h = HSMSigner(key_id="alias/test")
    with pytest.raises(NotImplementedError):
        h.sign(b"x")
    with pytest.raises(NotImplementedError):
        h.public_key_bytes()
