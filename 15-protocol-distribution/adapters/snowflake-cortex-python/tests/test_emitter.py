"""Emitter side-channel discipline (C7) tests."""

import json


def test_async_emitter_runs_in_background():
    from ledgerproof_snowflake_cortex.emitter import AsyncEmitter, ReceiptSink
    from ledgerproof_snowflake_cortex.signer import Ed25519Signer, SignedReceipt
    from ledgerproof_snowflake_cortex.canonical import canonical_cbor

    seen = []

    class Cap(ReceiptSink):
        def write(self, r):
            seen.append(r)

    em = AsyncEmitter(Cap())
    signer = Ed25519Signer.generate()
    cbor = canonical_cbor({"x": 1})
    sig = signer.sign(cbor)
    em.submit(SignedReceipt(payload_cbor=cbor, signature=sig,
                            public_key_b64=signer.public_key_b64))
    em.flush()
    assert len(seen) == 1


def test_file_sink_writes_jsonl(tmp_path):
    from ledgerproof_snowflake_cortex.emitter import FileSink
    from ledgerproof_snowflake_cortex.signer import Ed25519Signer, SignedReceipt
    from ledgerproof_snowflake_cortex.canonical import canonical_cbor

    path = tmp_path / "receipts.jsonl"
    sink = FileSink(path)
    signer = Ed25519Signer.generate()
    cbor = canonical_cbor({"x": 1})
    sig = signer.sign(cbor)
    sink.write(SignedReceipt(payload_cbor=cbor, signature=sig,
                             public_key_b64=signer.public_key_b64))
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert "signature_b64" in parsed
    assert parsed["algorithm"] == "ed25519"


def test_null_sink_does_not_raise():
    from ledgerproof_snowflake_cortex.emitter import NullSink
    from ledgerproof_snowflake_cortex.signer import Ed25519Signer, SignedReceipt
    from ledgerproof_snowflake_cortex.canonical import canonical_cbor

    sink = NullSink()
    signer = Ed25519Signer.generate()
    cbor = canonical_cbor({"x": 1})
    sig = signer.sign(cbor)
    sink.write(SignedReceipt(payload_cbor=cbor, signature=sig,
                             public_key_b64=signer.public_key_b64))


def test_envelope_has_adapter_and_protocol_version():
    from ledgerproof_snowflake_cortex import emit_receipt
    from ledgerproof_snowflake_cortex.canonical import canonical_decode
    from ledgerproof_snowflake_cortex.emitter import AsyncEmitter, ReceiptSink
    from ledgerproof_snowflake_cortex.signer import Ed25519Signer

    captured = []

    class Cap(ReceiptSink):
        def write(self, r):
            captured.append(r)

    em = AsyncEmitter(Cap())
    signer = Ed25519Signer.generate()
    emit_receipt(
        "generated_content/v1",
        signer=signer,
        deployer_id="d",
        model="llama3.1-70b",
        emitter=em,
        fields={"content_hash": "sha256:" + "0" * 64},
    )
    em.flush()
    decoded = canonical_decode(captured[0].payload_cbor)
    assert decoded["adapter"] == "ledgerproof-snowflake-cortex"
    assert decoded["lpr"] == "lpr/0.1"
