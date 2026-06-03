"""
Client wrapper tests using mocked Fireworks clients (no network, no real API key).
"""

from __future__ import annotations

import asyncio
import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from ledgerproof_fireworks import (
    LedgerProofAsyncFireworks,
    LedgerProofFireworks,
    OpenModelAttribution,
    QueueEmitter,
)
from ledgerproof_fireworks.canonical import canonical_encode
from ledgerproof_fireworks.signer import Ed25519Signer, verify


# ---------------------------------------------------------------------------
# Fixtures: shape a Fireworks ChatCompletion-like object (OpenAI shape)
# ---------------------------------------------------------------------------


def _fake_chat_response(
    text: str = "Hallo Welt.",
    response_id: str = "cmpl_test_001",
    model: str = "accounts/fireworks/models/llama-v3p1-70b-instruct",
    with_tool_call: bool = False,
):
    if with_tool_call:
        tool_call = SimpleNamespace(
            id="call_abc_1",
            function=SimpleNamespace(name="get_weather", arguments='{"city": "Berlin"}'),
        )
        message = SimpleNamespace(role="assistant", content=text, tool_calls=[tool_call])
    else:
        message = SimpleNamespace(role="assistant", content=text, tool_calls=None)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id=response_id,
        model=model,
        object="chat.completion",
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=20, total_tokens=30),
    )


def _make_wrapper(emitter_sink, with_tool_call=False, **wrapper_kwargs):
    fake_inner = MagicMock()
    fake_inner.chat.completions.create.return_value = _fake_chat_response(
        with_tool_call=with_tool_call
    )
    return LedgerProofFireworks(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(emitter_sink.append),
        signer=Ed25519Signer(),
        **wrapper_kwargs,
    )


# ---------------------------------------------------------------------------
# Sync non-streaming
# ---------------------------------------------------------------------------


def test_sync_create_emits_receipt_and_returns_response_unchanged():
    captured: list = []
    wrapper = _make_wrapper(captured)
    response = wrapper.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-70b-instruct",
        messages=[{"role": "user", "content": "Hi there"}],
    )
    # C7: response is passed through unchanged.
    assert response.id == "cmpl_test_001"
    assert response.choices[0].message.content == "Hallo Welt."

    assert len(captured) == 1
    signed = captured[0]
    assert signed["signature_alg"] == "ed25519"
    assert signed["receipt"]["deployer_id"] == "acme-eu-test"
    assert signed["receipt"]["schema"] == "chatbot_session/v1"
    assert signed["receipt"]["streaming"] is False
    assert signed["receipt"]["model"]["provider"] == "fireworks"
    assert signed["receipt"]["model"]["model_id"] == "accounts/fireworks/models/llama-v3p1-70b-instruct"

    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles and "assistant" in roles


def test_sync_create_with_tool_call_captures_tool_use_ref():
    captured: list = []
    wrapper = _make_wrapper(captured, with_tool_call=True)
    wrapper.chat.completions.create(
        model="accounts/fireworks/models/firefunction-v2",
        messages=[{"role": "user", "content": "What's the weather in Berlin?"}],
    )
    signed = captured[0]
    tool_uses = signed["receipt"]["tool_uses"]
    assert len(tool_uses) == 1
    assert tool_uses[0]["tool_name"] == "get_weather"
    assert tool_uses[0]["tool_use_id"] == "call_abc_1"
    # Input is hashed, not stored raw.
    assert len(tool_uses[0]["input_sha256_hex"]) == 64


def test_sync_emitter_failure_does_not_break_call():
    """C7: emitter failure must never propagate into the caller's response path."""

    class _Boom:
        def emit(self, _):
            raise RuntimeError("emitter died")

    fake_inner = MagicMock()
    fake_inner.chat.completions.create.return_value = _fake_chat_response()
    wrapper = LedgerProofFireworks(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=_Boom(),
        signer=Ed25519Signer(),
    )
    # Must NOT raise.
    response = wrapper.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-70b-instruct",
        messages=[{"role": "user", "content": "Hi"}],
    )
    assert response.id == "cmpl_test_001"


# ---------------------------------------------------------------------------
# Sync streaming
# ---------------------------------------------------------------------------


def _fake_stream_chunks(text_parts: list[str], model: str = "accounts/fireworks/models/llama-v3p1-70b-instruct"):
    """Mimic Fireworks ChatCompletionChunk stream (OpenAI-compatible shape)."""
    chunks = []
    for i, part in enumerate(text_parts):
        delta = SimpleNamespace(role="assistant" if i == 0 else None, content=part)
        choice = SimpleNamespace(index=0, delta=delta, finish_reason=None)
        chunks.append(
            SimpleNamespace(
                id="cmpl_stream_001",
                model=model,
                object="chat.completion.chunk",
                choices=[choice],
            )
        )
    delta_final = SimpleNamespace(role=None, content=None)
    choice_final = SimpleNamespace(index=0, delta=delta_final, finish_reason="stop")
    chunks.append(
        SimpleNamespace(
            id="cmpl_stream_001",
            model=model,
            object="chat.completion.chunk",
            choices=[choice_final],
            usage=SimpleNamespace(prompt_tokens=5, completion_tokens=10, total_tokens=15),
        )
    )
    return chunks


def test_sync_streaming_emits_receipt_with_incremental_hash():
    captured: list = []
    text_parts = ["Hal", "lo ", "Welt", "."]
    chunks = _fake_stream_chunks(text_parts)

    fake_inner = MagicMock()
    fake_inner.chat.completions.create.return_value = iter(chunks)

    wrapper = LedgerProofFireworks(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    received_text_parts: list[str] = []
    for chunk in wrapper.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-70b-instruct",
        messages=[{"role": "user", "content": "Hi"}],
        stream=True,
    ):
        delta_content = chunk.choices[0].delta.content
        if delta_content:
            received_text_parts.append(delta_content)

    assert "".join(received_text_parts) == "Hallo Welt."
    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["streaming"] is True
    asst = next(c for c in signed["receipt"]["content_refs"] if c["role"] == "assistant")
    assert asst["byte_length"] == len("Hallo Welt.".encode("utf-8"))


def test_sync_streaming_emits_receipt_on_early_close():
    """If the caller breaks early, receipt should still emit on stream.close()."""
    captured: list = []
    chunks = _fake_stream_chunks(["AB", "CD", "EF"])

    fake_inner = MagicMock()
    fake_inner.chat.completions.create.return_value = iter(chunks)

    wrapper = LedgerProofFireworks(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    stream = wrapper.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-70b-instruct",
        messages=[{"role": "user", "content": "Hi"}],
        stream=True,
    )
    next(stream)
    stream.close()

    assert len(captured) == 1
    assert captured[0]["receipt"]["streaming"] is True


# ---------------------------------------------------------------------------
# Async non-streaming
# ---------------------------------------------------------------------------


def test_async_create_emits_receipt():
    captured: list = []

    fake_inner = MagicMock()
    fake_inner.chat.completions.create = AsyncMock(return_value=_fake_chat_response())
    # Some Fireworks versions expose acreate; ensure the wrapper handles either.
    if hasattr(fake_inner.chat.completions, "acreate"):
        del fake_inner.chat.completions.acreate

    wrapper = LedgerProofAsyncFireworks(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        response = await wrapper.chat.completions.create(
            model="accounts/fireworks/models/llama-v3p1-70b-instruct",
            messages=[{"role": "user", "content": "Hi async"}],
        )
        assert response.id == "cmpl_test_001"

    asyncio.run(_run())

    assert len(captured) == 1
    assert captured[0]["receipt"]["deployer_id"] == "acme-eu-test"


# ---------------------------------------------------------------------------
# Async streaming
# ---------------------------------------------------------------------------


class _AsyncIter:
    def __init__(self, items):
        self._items = list(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._items:
            raise StopAsyncIteration
        return self._items.pop(0)


def test_async_streaming_emits_receipt_with_incremental_hash():
    captured: list = []
    chunks = _fake_stream_chunks(["Hel", "lo!"])

    fake_inner = MagicMock()
    fake_inner.chat.completions.create = AsyncMock(return_value=_AsyncIter(chunks))

    wrapper = LedgerProofAsyncFireworks(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        stream = await wrapper.chat.completions.create(
            model="accounts/fireworks/models/llama-v3p1-70b-instruct",
            messages=[{"role": "user", "content": "Hi"}],
            stream=True,
        )
        collected = []
        async for chunk in stream:
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                collected.append(delta_content)
        return "".join(collected)

    text = asyncio.run(_run())
    assert text == "Hello!"
    assert len(captured) == 1
    assert captured[0]["receipt"]["streaming"] is True
    asst = next(c for c in captured[0]["receipt"]["content_refs"] if c["role"] == "assistant")
    assert asst["byte_length"] == len("Hello!".encode("utf-8"))


# ---------------------------------------------------------------------------
# C4: offline verification
# ---------------------------------------------------------------------------


def test_signature_verifies_with_published_public_key():
    """C4: offline verification works given the public key bytes."""
    captured: list = []
    signer = Ed25519Signer()
    fake_inner = MagicMock()
    fake_inner.chat.completions.create.return_value = _fake_chat_response()
    wrapper = LedgerProofFireworks(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )
    wrapper.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-70b-instruct",
        messages=[{"role": "user", "content": "Verify me"}],
    )
    signed = captured[0]
    canonical_bytes = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)


# ---------------------------------------------------------------------------
# Open-model attribution schema
# ---------------------------------------------------------------------------


def test_open_model_hosted_schema_uses_supplied_attribution():
    captured: list = []
    wrapper = _make_wrapper(
        captured,
        schema="open_model_hosted/v1",
        open_model=OpenModelAttribution(
            underlying_model_family="llama",
            underlying_model_provider="meta",
            model_license="llama-3.1-community",
        ),
    )
    wrapper.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-70b-instruct",
        messages=[{"role": "user", "content": "Hi"}],
    )
    signed = captured[0]
    assert signed["receipt"]["schema"] == "open_model_hosted/v1"
    assert signed["receipt"]["open_model"]["underlying_model_provider"] == "meta"
    assert signed["receipt"]["open_model"]["host_provider"] == "fireworks"
    assert signed["receipt"]["open_model"]["model_license"] == "llama-3.1-community"


def test_open_model_hosted_schema_infers_attribution_when_omitted():
    """If schema is open_model_hosted/v1 and no attribution is given,
    the adapter should infer (family, provider) from the model_id."""
    captured: list = []
    wrapper = _make_wrapper(captured, schema="open_model_hosted/v1")
    wrapper.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-70b-instruct",
        messages=[{"role": "user", "content": "Hi"}],
    )
    signed = captured[0]
    assert signed["receipt"]["open_model"]["underlying_model_family"] == "llama"
    assert signed["receipt"]["open_model"]["underlying_model_provider"] == "meta"


# ---------------------------------------------------------------------------
# Image generation (FLUX)
# ---------------------------------------------------------------------------


def test_image_generate_emits_flux_image_generation_receipt():
    captured: list = []
    # Simulate Fireworks FLUX returning an object with raw image_bytes.
    fake_response = SimpleNamespace(
        id="img_001",
        model="accounts/fireworks/models/flux-1-schnell-fp8",
        image_bytes=b"\x89PNG\r\n\x1a\nfake-png-bytes",
    )
    fake_inner = MagicMock()
    fake_inner.image.generate.return_value = fake_response

    wrapper = LedgerProofFireworks(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    response = wrapper.image.generate(
        model="accounts/fireworks/models/flux-1-schnell-fp8",
        prompt="A photograph of an alpine lake at sunrise.",
    )

    # C7: response is passed through unchanged.
    assert response.id == "img_001"

    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["schema"] == "flux_image_generation/v1"
    assert signed["receipt"]["model"]["model_id"] == "accounts/fireworks/models/flux-1-schnell-fp8"
    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles
    assert "image" in roles
    # Attribution should be inferred to FLUX / black-forest-labs.
    assert signed["receipt"]["open_model"]["underlying_model_family"] == "flux"
    assert signed["receipt"]["open_model"]["underlying_model_provider"] == "black-forest-labs"
