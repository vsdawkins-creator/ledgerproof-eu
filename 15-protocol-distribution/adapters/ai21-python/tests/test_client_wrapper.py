"""
Client wrapper tests using mocked AI21 clients (no network, no real API key).

We mock the inner `ai21.AI21Client` / `AsyncAI21Client` instance so the tests
run on a fresh venv without `AI21_API_KEY` set.
"""

from __future__ import annotations

import asyncio
import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from ledgerproof_ai21 import (
    LedgerProofAI21,
    LedgerProofAsyncAI21,
    QueueEmitter,
)
from ledgerproof_ai21.canonical import canonical_encode
from ledgerproof_ai21.signer import Ed25519Signer, verify


# ---------------------------------------------------------------------------
# Fixtures: shape an AI21 ChatCompletionResponse-like object
# (AI21 ships OpenAI-compatible structure)
# ---------------------------------------------------------------------------


def _fake_chat_response(
    text: str = "Shalom, world.",
    response_id: str = "cmpl_test_001",
    with_tool_call: bool = False,
):
    if with_tool_call:
        tool_call = SimpleNamespace(
            id="call_abc_1",
            function=SimpleNamespace(name="get_weather", arguments='{"city": "Tel Aviv"}'),
        )
        message = SimpleNamespace(role="assistant", content=text, tool_calls=[tool_call])
    else:
        message = SimpleNamespace(role="assistant", content=text, tool_calls=None)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id=response_id,
        model="jamba-1.5-large",
        object="chat.completion",
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=12, completion_tokens=22, total_tokens=34),
    )


def _make_wrapper(emitter_sink, with_tool_call=False, **kwargs):
    fake_inner = MagicMock()
    fake_inner.chat.completions.create.return_value = _fake_chat_response(
        with_tool_call=with_tool_call
    )
    return LedgerProofAI21(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(emitter_sink.append),
        signer=Ed25519Signer(),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Sync non-streaming
# ---------------------------------------------------------------------------


def test_sync_completions_create_emits_receipt_and_returns_response_unchanged():
    captured: list = []
    wrapper = _make_wrapper(captured)
    response = wrapper.chat.completions.create(
        model="jamba-1.5-large",
        messages=[{"role": "user", "content": "Hi there"}],
    )
    # C7: response is passed through unchanged.
    assert response.id == "cmpl_test_001"
    assert response.choices[0].message.content == "Shalom, world."

    assert len(captured) == 1
    signed = captured[0]
    assert signed["signature_alg"] == "ed25519"
    assert signed["receipt"]["deployer_id"] == "acme-eu-test"
    assert signed["receipt"]["schema"] == "chatbot_session/v1"
    assert signed["receipt"]["streaming"] is False
    assert signed["receipt"]["model"]["provider"] == "ai21"
    assert signed["receipt"]["model"]["model_id"] == "jamba-1.5-large"

    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles and "assistant" in roles


def test_sync_completions_create_with_tool_call_captures_tool_use_ref():
    captured: list = []
    wrapper = _make_wrapper(captured, with_tool_call=True)
    wrapper.chat.completions.create(
        model="jamba-1.5-large",
        messages=[{"role": "user", "content": "What's the weather in Tel Aviv?"}],
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
    wrapper = LedgerProofAI21(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=_Boom(),
        signer=Ed25519Signer(),
    )
    # Must NOT raise.
    response = wrapper.chat.completions.create(
        model="jamba-1.5-large",
        messages=[{"role": "user", "content": "Hi"}],
    )
    assert response.id == "cmpl_test_001"


# ---------------------------------------------------------------------------
# Sync streaming
# ---------------------------------------------------------------------------


def _fake_stream_chunks(text_parts: list[str]):
    """Mimic AI21 ChatCompletionStreamResponse chunks (OpenAI-compatible)."""
    chunks = []
    for i, part in enumerate(text_parts):
        delta = SimpleNamespace(role="assistant" if i == 0 else None, content=part)
        choice = SimpleNamespace(index=0, delta=delta, finish_reason=None)
        chunks.append(
            SimpleNamespace(
                id="cmpl_stream_001",
                model="jamba-1.5-large",
                object="chat.completion.chunk",
                choices=[choice],
            )
        )
    # Final chunk often carries finish_reason
    delta_final = SimpleNamespace(role=None, content=None)
    choice_final = SimpleNamespace(index=0, delta=delta_final, finish_reason="stop")
    chunks.append(
        SimpleNamespace(
            id="cmpl_stream_001",
            model="jamba-1.5-large",
            object="chat.completion.chunk",
            choices=[choice_final],
            usage=SimpleNamespace(prompt_tokens=5, completion_tokens=10, total_tokens=15),
        )
    )
    return chunks


def test_sync_streaming_emits_receipt_with_incremental_hash():
    captured: list = []
    text_parts = ["Sha", "lom, ", "lon", "g context."]
    chunks = _fake_stream_chunks(text_parts)

    fake_inner = MagicMock()
    fake_inner.chat.completions.create.return_value = iter(chunks)

    wrapper = LedgerProofAI21(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    received_text_parts: list[str] = []
    for chunk in wrapper.chat.completions.create(
        model="jamba-1.5-large",
        messages=[{"role": "user", "content": "Hi"}],
        stream=True,
    ):
        delta_content = chunk.choices[0].delta.content
        if delta_content:
            received_text_parts.append(delta_content)

    assert "".join(received_text_parts) == "Shalom, long context."
    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["streaming"] is True
    asst = next(c for c in signed["receipt"]["content_refs"] if c["role"] == "assistant")
    assert asst["byte_length"] == len("Shalom, long context.".encode("utf-8"))


def test_sync_streaming_emits_receipt_on_early_close():
    """If the caller breaks early, receipt should still emit on stream.close()."""
    captured: list = []
    chunks = _fake_stream_chunks(["AB", "CD", "EF"])

    fake_inner = MagicMock()
    fake_inner.chat.completions.create.return_value = iter(chunks)

    wrapper = LedgerProofAI21(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    stream = wrapper.chat.completions.create(
        model="jamba-1.5-large",
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


def test_async_completions_create_emits_receipt():
    captured: list = []

    fake_inner = MagicMock()
    fake_inner.chat.completions.create = AsyncMock(return_value=_fake_chat_response())

    wrapper = LedgerProofAsyncAI21(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        response = await wrapper.chat.completions.create(
            model="jamba-1.5-large",
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

    wrapper = LedgerProofAsyncAI21(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        stream = await wrapper.chat.completions.create(
            model="jamba-1.5-large",
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
    wrapper = LedgerProofAI21(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )
    wrapper.chat.completions.create(
        model="jamba-1.5-large",
        messages=[{"role": "user", "content": "Verify me"}],
    )
    signed = captured[0]
    canonical_bytes = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)


# ---------------------------------------------------------------------------
# Long-context and Jamba-hybrid attestation schemas
# ---------------------------------------------------------------------------


def test_long_context_schema_is_emitted_when_configured():
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.chat.completions.create.return_value = _fake_chat_response()
    wrapper = LedgerProofAI21(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        schema="long_context_inference/v1",
        long_context={
            "declared_context_window": 262144,
            "effective_input_tokens": 150_000,
            "long_context_workload": "rag",
            "truncation_applied": False,
        },
    )
    wrapper.chat.completions.create(
        model="jamba-1.5-large",
        messages=[{"role": "user", "content": "Summarize 100 PDFs"}],
    )
    signed = captured[0]
    assert signed["receipt"]["schema"] == "long_context_inference/v1"
    assert signed["receipt"]["long_context"]["declared_context_window"] == 262144
    assert signed["receipt"]["long_context"]["effective_input_tokens"] == 150_000


def test_jamba_hybrid_schema_is_emitted_when_configured():
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.chat.completions.create.return_value = _fake_chat_response()
    wrapper = LedgerProofAI21(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        schema="jamba_hybrid_attribution/v1",
        jamba_hybrid={
            "architecture_family": "mamba-transformer-hybrid",
            "model_variant": "jamba-1.5-large",
            "parameter_class": "398B-MoE",
            "attention_layer_ratio": "1:7",
        },
    )
    wrapper.chat.completions.create(
        model="jamba-1.5-large",
        messages=[{"role": "user", "content": "Hi"}],
    )
    signed = captured[0]
    assert signed["receipt"]["schema"] == "jamba_hybrid_attribution/v1"
    assert signed["receipt"]["jamba_hybrid"]["model_variant"] == "jamba-1.5-large"
    assert signed["receipt"]["jamba_hybrid"]["architecture_family"] == "mamba-transformer-hybrid"
