"""Ed25519 signer + canonical CBOR round-trip tests."""


def test_signer_generate_and_verify():
    from ledgerproof_groq.signer import Ed25519Signer
    s = Ed25519Signer.generate()
    msg = b"hello ledgerproof"
    sig = s.sign(msg)
    assert s.verify(sig, msg) is True
    assert s.verify(sig, msg + b"!") is False


def test_canonical_cbor_deterministic():
    from ledgerproof_groq.canonical import canonical_cbor
    a = {"b": 2, "a": 1, "c": [1, 2, 3]}
    b = {"c": [1, 2, 3], "a": 1, "b": 2}
    assert canonical_cbor(a) == canonical_cbor(b)


def test_verify_signature_helper_local_only():
    from ledgerproof_groq.signer import Ed25519Signer, verify_signature
    s = Ed25519Signer.generate()
    msg = b"local-verify"
    sig = s.sign(msg)
    assert verify_signature(s.public_key_b64, sig, msg) is True


def test_signed_receipt_to_dict_has_fields():
    from ledgerproof_groq.canonical import canonical_cbor
    from ledgerproof_groq.signer import Ed25519Signer, SignedReceipt
    s = Ed25519Signer.generate()
    cbor = canonical_cbor({"hello": "world"})
    sig = s.sign(cbor)
    sr = SignedReceipt(payload_cbor=cbor, signature=sig, public_key_b64=s.public_key_b64)
    d = sr.to_dict()
    assert "signature_b64" in d
    assert "payload_cbor_b64" in d
    assert d["algorithm"] == "ed25519"
