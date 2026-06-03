"""Decorator and manual emission tests."""

from typing import List


def _capture_sink():
    from ledgerproof_cerebras.emitter import ReceiptSink
    captured: List = []

    class Cap(ReceiptSink):
        def write(self, r):
            captured.append(r)

    return Cap(), captured


def test_lpr_track_decorator_sync():
    from ledgerproof_cerebras import lpr_track
    from ledgerproof_cerebras.emitter import AsyncEmitter
    from ledgerproof_cerebras.signer import Ed25519Signer

    sink, captured = _capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    @lpr_track(signer=signer, deployer_id="d-deco", model="llama3.1-70b",
               emitter=emitter)
    def gen_text():
        return "synthetic text"

    out = gen_text()
    assert out == "synthetic text"
    emitter.flush()
    assert len(captured) == 1


def test_lpr_track_decorator_stream_aware():
    from ledgerproof_cerebras import lpr_track
    from ledgerproof_cerebras.emitter import AsyncEmitter
    from ledgerproof_cerebras.signer import Ed25519Signer

    sink, captured = _capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    @lpr_track(signer=signer, deployer_id="d-deco", model="llama3.1-70b",
               emitter=emitter)
    def streamy():
        for piece in ["a", "b", "c"]:
            yield piece

    pieces = list(streamy())
    assert pieces == ["a", "b", "c"]
    emitter.flush()
    assert len(captured) == 1


def test_lpr_track_decorator_reasoning_schema():
    from ledgerproof_cerebras import lpr_track
    from ledgerproof_cerebras.emitter import AsyncEmitter
    from ledgerproof_cerebras.signer import Ed25519Signer

    sink, captured = _capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    @lpr_track(
        signer=signer,
        deployer_id="d-deco",
        model="deepseek-r1-distill-llama-70b",
        schema="reasoning_distilled/v1",
        emitter=emitter,
    )
    def think():
        return "the answer"

    think()
    emitter.flush()
    assert len(captured) == 1


def test_manual_emit_receipt_wafer_scale():
    from ledgerproof_cerebras import emit_receipt
    from ledgerproof_cerebras.emitter import AsyncEmitter
    from ledgerproof_cerebras.signer import Ed25519Signer

    sink, captured = _capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    emit_receipt(
        "wafer_scale_inference/v1",
        signer=signer,
        deployer_id="d-manual",
        model="llama3.1-70b",
        emitter=emitter,
        fields={
            "inference_latency_ms": 18.0,
            "tokens_per_second": 2200.0,
            "prompt_tokens": 100,
            "completion_tokens": 40,
            "total_tokens": 140,
        },
    )
    emitter.flush()
    assert len(captured) == 1


def test_manual_emit_receipt_generated_content():
    from ledgerproof_cerebras import emit_receipt
    from ledgerproof_cerebras.emitter import AsyncEmitter
    from ledgerproof_cerebras.signer import Ed25519Signer

    sink, captured = _capture_sink()
    emitter = AsyncEmitter(sink)
    signer = Ed25519Signer.generate()

    emit_receipt(
        "generated_content/v1",
        signer=signer,
        deployer_id="d-manual",
        model="llama3.1-70b",
        emitter=emitter,
        fields={"content_hash": "sha256:" + "f" * 64, "content_type": "text"},
    )
    emitter.flush()
    assert len(captured) == 1
