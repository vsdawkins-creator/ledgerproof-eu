"""Signer + signature verification tests."""
from __future__ import annotations

import base64

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from ledgerproof_vertexai.signer import (
    EphemeralEd25519Signer,
    GcpKmsEd25519Signer,
)


def test_signer_round_trips():
    s = EphemeralEd25519Signer()
    msg = b"hello receipt"
    sig = s.sign(msg)
    assert sig.algorithm == "Ed25519"

    pk_raw = base64.b64decode(sig.public_key_b64)
    pk = Ed25519PublicKey.from_public_bytes(pk_raw)
    # Should not raise
    pk.verify(base64.b64decode(sig.signature_b64), msg)


def test_signatures_differ_across_keys():
    a = EphemeralEd25519Signer()
    b = EphemeralEd25519Signer()
    assert a.public_key_b64 != b.public_key_b64


def test_kms_signer_phase2_stub():
    with pytest.raises(NotImplementedError):
        GcpKmsEd25519Signer("projects/p/locations/europe-west4/keyRings/kr/cryptoKeys/k/cryptoKeyVersions/1")
