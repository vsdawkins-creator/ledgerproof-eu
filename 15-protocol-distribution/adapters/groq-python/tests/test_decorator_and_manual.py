"""Decorator and manual emission tests."""

from typing import List


def _capture_sink():
    from ledgerproof_groq.emitter import ReceiptSink
    captured: List = []

    class Cap(ReceiptSink):
        def write(self, r):
            captured.append(r)

    return Cap(), captured


def test_lpr_track_decorator_sync():
    from ledgerproof_groq import lpr_track
    from ledgerproof_groq.emitter import AsyncEmitter
    from ledgerproof_groq.signer import Ed25519Signer

    sink, captured = _capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    @lpr_track(signer=signer, deployer_id="d-deco", model="llama-3.3-70b-versatile",
               emitter=emitter)
    def gen_text():
        return "synthetic text"

    out = gen_text()
    assert out == "synthetic text"
    emitter.flush()
    assert len(captured) == 1


def test_lpr_track_decorator_stream_aware():
    from ledgerproof_groq import lpr_track
    from ledgerproof_groq.emitter import AsyncEmitter
    from ledgerproof_groq.signer import Ed25519Signer

    sink, captured = _capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    @lpr_track(signer=signer, deployer_id="d-deco", model="llama-3.3-70b-versatile",
               emitter=emitter)
    def streamy():
        for piece in ["a", "b", "c"]:
            yield piece

    pieces = list(streamy())
    assert pieces == ["a", "b", "c"]
    emitter.flush()
    assert len(captured) == 1


def test_manual_emit_receipt():
    from ledgerproof_groq import emit_receipt
    from ledgerproof_groq.emitter import AsyncEmitter
    from ledgerproof_groq.signer import Ed25519Signer

    sink, captured = _capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    emit_receipt(
        "generated_content/v1",
        signer=signer,
        deployer_id="d-manual",
        model="llama-3.3-70b-versatile",
        emitter=emitter,
        fields={"content_hash": "sha256:" + "f" * 64, "content_type": "text"},
    )
    emitter.flush()
    assert len(captured) == 1
