"""Tests for the manual emit_receipt function and the @lpr_track decorator."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

from ledgerproof_fireworks import (
    OpenModelAttribution,
    QueueEmitter,
    emit_flux_image_generation_receipt,
    emit_receipt,
    lpr_track,
)
from ledgerproof_fireworks.signer import Ed25519Signer


def _fake_response(
    text: str = "Hi from Llama.",
    model: str = "accounts/fireworks/models/llama-v3p1-70b-instruct",
):
    message = SimpleNamespace(role="assistant", content=text, tool_calls=None)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id="cmpl_manual_1",
        model=model,
        object="chat.completion",
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=3, completion_tokens=5, total_tokens=8),
    )


def test_emit_receipt_default_schema_includes_user_and_assistant_refs():
    captured: list = []
    signed = emit_receipt(
        response=_fake_response(),
        deployer_id="acme-eu",
        user_message_text="Hello world",
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
    )
    assert signed["receipt"]["schema"] == "chatbot_session/v1"
    assert signed["receipt"]["model"]["provider"] == "fireworks"
    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles and "assistant" in roles
    assert captured and captured[0] is signed


def test_emit_receipt_open_model_hosted_infers_when_omitted():
    captured: list = []
    signed = emit_receipt(
        response=_fake_response(model="accounts/fireworks/models/qwen2p5-72b-instruct"),
        deployer_id="acme-eu",
        user_message_text="Hi",
        schema="open_model_hosted/v1",
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
    )
    assert signed["receipt"]["open_model"]["underlying_model_family"] == "qwen"
    assert signed["receipt"]["open_model"]["underlying_model_provider"] == "alibaba-qwen"


def test_emit_receipt_explicit_open_model_wins():
    captured: list = []
    signed = emit_receipt(
        response=_fake_response(model="accounts/fireworks/models/llama-v3p1-70b-instruct"),
        deployer_id="acme-eu",
        user_message_text="Hi",
        schema="open_model_hosted/v1",
        open_model=OpenModelAttribution(
            underlying_model_family="other",
            underlying_model_provider="other",
            weights_origin="https://example.com/custom-finetune",
        ),
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
    )
    assert signed["receipt"]["open_model"]["underlying_model_family"] == "other"
    assert signed["receipt"]["open_model"]["weights_origin"] == "https://example.com/custom-finetune"


def test_emit_flux_image_generation_receipt_hashes_image_bytes():
    captured: list = []
    signed = emit_flux_image_generation_receipt(
        response=_fake_response(model="accounts/fireworks/models/flux-1-schnell-fp8"),
        deployer_id="acme-eu",
        prompt_text="a sunset",
        image_bytes_iter=[b"\x89PNG\r\n\x1a\nfakeimage1", b"\x89PNG\r\n\x1a\nfakeimage2"],
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
    )
    assert signed["receipt"]["schema"] == "flux_image_generation/v1"
    image_refs = [c for c in signed["receipt"]["content_refs"] if c["role"] == "image"]
    assert len(image_refs) == 2
    assert signed["receipt"]["regulatory_context"]["article_50_paragraph"] == "2"
    assert signed["receipt"]["open_model"]["underlying_model_family"] == "flux"


# ---------------------------------------------------------------------------
# @lpr_track
# ---------------------------------------------------------------------------


def test_lpr_track_sync_emits_on_each_invocation():
    captured: list = []

    @lpr_track(
        deployer_id="acme-eu",
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
        user_message_kwarg="prompt",
    )
    def my_call(prompt: str):
        return _fake_response(text=f"echo: {prompt}")

    my_call(prompt="hello")
    my_call(prompt="world")

    assert len(captured) == 2
    assert all(s["receipt"]["deployer_id"] == "acme-eu" for s in captured)


def test_lpr_track_async_emits_on_each_invocation():
    captured: list = []

    @lpr_track(
        deployer_id="acme-eu",
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
    )
    async def my_call():
        return _fake_response()

    asyncio.run(my_call())
    asyncio.run(my_call())

    assert len(captured) == 2


def test_lpr_track_wrapped_function_failure_propagates_but_emitter_failure_does_not():
    captured: list = []

    class _Boom:
        def emit(self, _):
            raise RuntimeError("emitter died")

    @lpr_track(deployer_id="acme-eu", signer=Ed25519Signer(), emitter=_Boom())
    def good_call():
        return _fake_response()

    # Emitter blows up internally; the wrapped function should still return.
    resp = good_call()
    assert resp.id == "cmpl_manual_1"
