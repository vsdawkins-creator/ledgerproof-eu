"""Tests for the manual emit_receipt() helper and @lpr_track decorator."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

from ledgerproof_qwen import (
    QueueEmitter,
    emit_receipt,
    lpr_track,
)
from ledgerproof_qwen.signer import Ed25519Signer


def _fake_response(text: str = "Reply.", request_id: str = "req_manual_001"):
    output = SimpleNamespace(text=text, choices=None, finish_reason="stop")
    return SimpleNamespace(
        request_id=request_id,
        output=output,
        usage=SimpleNamespace(input_tokens=3, output_tokens=4, total_tokens=7),
        status_code=200,
    )


def test_emit_receipt_returns_signed_payload_and_does_not_mutate_response():
    captured: list = []
    response = _fake_response()
    before = (response.request_id, response.output.text)
    signed = emit_receipt(
        response=response,
        deployer_id="acme-eu",
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        user_message_text="Hello",
        model_id="qwen-turbo",
    )
    # Returned dict matches what was emitted.
    assert captured and captured[0] is signed
    assert signed["receipt"]["deployer_id"] == "acme-eu"
    assert signed["receipt"]["model"]["model_id"] == "qwen-turbo"
    # C7: response itself is untouched.
    assert (response.request_id, response.output.text) == before


def test_emit_receipt_with_chinese_inference_block_via_dict():
    captured: list = []
    emit_receipt(
        response=_fake_response(),
        deployer_id="acme-eu",
        schema="multilingual_chinese_inference/v1",
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        user_message_text="你好",
        model_id="qwen-max",
        chinese_inference={
            "chinese_disclosure_shown": True,
            "endpoint_region": "hong-kong",
            "avoids_mainland_residency": True,
        },
    )
    signed = captured[0]
    assert signed["receipt"]["schema"] == "multilingual_chinese_inference/v1"
    assert signed["receipt"]["chinese_inference"]["endpoint_region"] == "hong-kong"


def test_lpr_track_sync_decorator_emits_on_each_call():
    captured: list = []

    @lpr_track(
        deployer_id="acme-eu",
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        user_message_kwarg="prompt",
    )
    def my_qwen_call(*, model: str, prompt: str):
        return _fake_response()

    my_qwen_call(model="qwen-turbo", prompt="What is the EU AI Act?")
    my_qwen_call(model="qwen-turbo", prompt="Second call")
    assert len(captured) == 2
    assert all(c["receipt"]["model"]["model_id"] == "qwen-turbo" for c in captured)


def test_lpr_track_async_decorator_emits_on_each_call():
    captured: list = []

    @lpr_track(
        deployer_id="acme-eu",
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        user_message_kwarg="prompt",
    )
    async def my_qwen_call(*, model: str, prompt: str):
        return _fake_response()

    async def _run():
        await my_qwen_call(model="qwen-plus", prompt="Hello?")

    asyncio.run(_run())
    assert len(captured) == 1
    assert captured[0]["receipt"]["model"]["model_id"] == "qwen-plus"


def test_lpr_track_swallows_emitter_exceptions():
    class _Boom:
        def emit(self, _):
            raise RuntimeError("emitter died")

    @lpr_track(deployer_id="acme-eu", emitter=_Boom(), signer=Ed25519Signer())
    def my_qwen_call(*, model: str = "qwen-turbo"):
        return _fake_response()

    # Must NOT raise.
    result = my_qwen_call(model="qwen-turbo")
    assert result.request_id == "req_manual_001"
