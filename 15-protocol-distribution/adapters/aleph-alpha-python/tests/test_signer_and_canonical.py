"""Signer + canonicalization round-trip tests."""

from __future__ import annotations

import base64

from ledgerproof_aleph_alpha.canonical import (
    IncrementalDigest,
    canonicalize,
    sha256_hex,
)
from ledgerproof_aleph_alpha.signer import EphemeralEd25519Signer, verify_receipt
from ledgerproof_aleph_alpha.version import PROTOCOL_VERSION


def test_canonicalize_is_deterministic():
    a = canonicalize({"b": 1, "a": 2})
    b = canonicalize({"a": 2, "b": 1})
    assert a == b


def test_incremental_digest_matches_oneshot():
    text = "hallo welt — Aleph Alpha Luminous"
    d = IncrementalDigest()
    d.update("hallo ").update("welt ").update("— Aleph Alpha Luminous")
    assert d.hexdigest() == sha256_hex(text)


def test_ephemeral_signer_round_trip():
    signer = EphemeralEd25519Signer()
    payload = {
        "schema_name": "generated_content/v1",
        "article": "50(2)",
        "prompt_sha256": "a" * 64,
        "completion_sha256": "b" * 64,
        "model": "luminous-base",
        "model_version": None,
        "ts_unix_ms": 1_700_000_000_000,
        "content_type": "text",
        "marker_applied": False,
        "deployer_id": None,
    }
    canon, sig = signer.sign_canonical(payload)
    assert canon == canonicalize(payload)

    receipt = {
        "protocol": PROTOCOL_VERSION,
        "payload": payload,
        "sig": base64.b64encode(sig).decode("ascii"),
        "pubkey": signer.public_key_b64,
    }
    assert verify_receipt(receipt) is True


def test_verify_rejects_tampered_payload():
    signer = EphemeralEd25519Signer()
    payload = {
        "schema_name": "generated_content/v1",
        "article": "50(2)",
        "prompt_sha256": "a" * 64,
        "completion_sha256": "b" * 64,
        "model": "luminous-base",
        "model_version": None,
        "ts_unix_ms": 1,
        "content_type": "text",
        "marker_applied": False,
        "deployer_id": None,
    }
    _, sig = signer.sign_canonical(payload)
    tampered = dict(payload, model="evil-model")
    receipt = {
        "protocol": PROTOCOL_VERSION,
        "payload": tampered,
        "sig": base64.b64encode(sig).decode("ascii"),
        "pubkey": signer.public_key_b64,
    }
    assert verify_receipt(receipt) is False


def test_verify_handles_malformed_receipt():
    assert verify_receipt({}) is False
    assert verify_receipt({"sig": "!!!", "pubkey": "!!!", "payload": {}}) is False
