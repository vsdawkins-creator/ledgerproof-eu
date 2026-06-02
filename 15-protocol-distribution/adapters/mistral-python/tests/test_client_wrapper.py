"""
Client wrapper tests using mocked Mistral clients (no network, no real API key).

We mock the inner `mistralai.Mistral` instance so the tests run on a fresh venv
without `MISTRAL_API_KEY` set.
"""

from __future__ import annotations

import asyncio
import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from ledgerproof_mistral import (
    LedgerProofAsyncMistral,
    LedgerProofMistral,
    QueueEmitter,
)
from ledgerproof_mistral.canonical import canonical_encode
from ledgerproof_mistral.signer import Ed25519Signer, verify


# ---------------------------------------------------------------------------
# Fixtures: shape a Mistral ChatCompletionResponse-like object
# ---------------------------------------------------------------------------


def _fake_chat_response(
    text: str = "Bonjour, le monde.",
    response_id: str = "cmpl_test_001",
    with_tool_call: bool = False,
):
    if with_tool_call:
        tool_call = SimpleNamespace(
            id="call_abc_1",
            function=SimpleNamespace(name="get_weather", arguments='{"city": "Paris"}'),
        )
        message = SimpleNamespace(role="assistant", content=text, tool_calls=[tool_call])
    else:
        message = SimpleNamespace(role="assistant", content=text, tool_calls=None)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id=response_id,
        model="mistral-large-latest",
        object="chat.completion",
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=20, total_tokens=30),
    )


def _make_wrapper(emitter_sink, with_tool_call=False):
    fake_inner = MagicMock()
    fake_inner.chat.complete.return_value = _fake_chat_response(with_tool_call=with_tool_call)
    return LedgerProofMistral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(emitter_sink.append),
        signer=Ed25519Signer(),
    )


# ---------------------------------------------------------------------------
# Sync non-streaming
# ---------------------------------------------------------------------------


def test_sync_complete_emits_receipt_and_returns_response_unchanged():
    captured: list = []
    wrapper = _make_wrapper(captured)
    response = wrapper.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Hi there"}],
    )
    # C7: response is passed through unchanged.
    assert response.id == "cmpl_test_001"
    assert response.choices[0].message.content == "Bonjour, le monde."

    assert len(captured) == 1
    signed = captured[0]
    assert signed["signature_alg"] == "ed25519"
    assert signed["receipt"]["deployer_id"] == "acme-eu-test"
    assert signed["receipt"]["schema"] == "chatbot_session/v1"
    assert signed["receipt"]["streaming"] is False
    assert signed["receipt"]["model"]["provider"] == "mistral"
    assert signed["receipt"]["model"]["model_id"] == "mistral-large-latest"

    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles and "assistant" in roles


def test_sync_complete_with_tool_call_captures_tool_use_ref():
    captured: list = []
    wrapper = _make_wrapper(captured, with_tool_call=True)
    wrapper.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "What's the weather in Paris?"}],
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
    fake_inner.chat.complete.return_value = _fake_chat_response()
    wrapper = LedgerProofMistral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=_Boom(),
        signer=Ed25519Signer(),
    )
    # Must NOT raise.
    response = wrapper.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Hi"}],
    )
    assert response.id == "cmpl_test_001"


# ---------------------------------------------------------------------------
# Sync streaming
# ---------------------------------------------------------------------------


def _fake_stream_chunks(text_parts: list[str]):
    """Mimic Mistral ChatCompletionStreamResponse chunks."""
    chunks = []
    for i, part in enumerate(text_parts):
        delta = SimpleNamespace(role="assistant" if i == 0 else None, content=part)
        choice = SimpleNamespace(index=0, delta=delta, finish_reason=None)
        data = SimpleNamespace(
            id="cmpl_stream_001",
            model="mistral-large-latest",
            object="chat.completion.chunk",
            choices=[choice],
        )
        chunks.append(SimpleNamespace(data=data))
    # Final chunk often carries finish_reason
    delta_final = SimpleNamespace(role=None, content=None)
    choice_final = SimpleNamespace(index=0, delta=delta_final, finish_reason="stop")
    data_final = SimpleNamespace(
        id="cmpl_stream_001",
        model="mistral-large-latest",
        object="chat.completion.chunk",
        choices=[choice_final],
        usage=SimpleNamespace(prompt_tokens=5, completion_tokens=10, total_tokens=15),
    )
    chunks.append(SimpleNamespace(data=data_final))
    return chunks


def test_sync_streaming_emits_receipt_with_incremental_hash():
    captured: list = []
    text_parts = ["Bon", "jour, ", "le ", "monde."]
    chunks = _fake_stream_chunks(text_parts)

    fake_inner = MagicMock()
    fake_inner.chat.stream.return_value = iter(chunks)

    wrapper = LedgerProofMistral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    received_text_parts: list[str] = []
    for chunk in wrapper.chat.stream(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Hi"}],
    ):
        # Forward verification: chunks pass through unchanged.
        delta_content = chunk.data.choices[0].delta.content
        if delta_content:
            received_text_parts.append(delta_content)

    assert "".join(received_text_parts) == "Bonjour, le monde."
    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["streaming"] is True
    asst = next(c for c in signed["receipt"]["content_refs"] if c["role"] == "assistant")
    assert asst["byte_length"] == len("Bonjour, le monde.".encode("utf-8"))


def test_sync_streaming_emits_receipt_on_early_close():
    """If the caller breaks early, receipt should still emit on stream.close()."""
    captured: list = []
    chunks = _fake_stream_chunks(["AB", "CD", "EF"])

    fake_inner = MagicMock()
    fake_inner.chat.stream.return_value = iter(chunks)

    wrapper = LedgerProofMistral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    stream = wrapper.chat.stream(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Hi"}],
    )
    # Consume only the first chunk, then close.
    next(stream)
    stream.close()

    assert len(captured) == 1
    assert captured[0]["receipt"]["streaming"] is True


# ---------------------------------------------------------------------------
# Async non-streaming
# ---------------------------------------------------------------------------


def test_async_complete_emits_receipt():
    captured: list = []

    fake_inner = MagicMock()
    fake_inner.chat.complete_async = AsyncMock(return_value=_fake_chat_response())

    wrapper = LedgerProofAsyncMistral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        response = await wrapper.chat.complete_async(
            model="mistral-large-latest",
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
    fake_inner.chat.stream_async = AsyncMock(return_value=_AsyncIter(chunks))

    wrapper = LedgerProofAsyncMistral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        stream = await wrapper.chat.stream_async(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": "Hi"}],
        )
        collected = []
        async for chunk in stream:
            delta_content = chunk.data.choices[0].delta.content
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
    fake_inner.chat.complete.return_value = _fake_chat_response()
    wrapper = LedgerProofMistral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )
    wrapper.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Verify me"}],
    )
    signed = captured[0]
    canonical_bytes = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)


# ---------------------------------------------------------------------------
# EU-sovereign attribution schema
# ---------------------------------------------------------------------------


def test_eu_sovereign_schema_is_emitted_when_configured():
    captured: list = []
    fake_inner = MagicMock()
    fake_inner.chat.complete.return_value = _fake_chat_response()
    wrapper = LedgerProofMistral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        schema="eu_sovereign_ai_session/v1",
        eu_sovereignty={
            "inference_region": "eu-west-3",
            "eu_data_residency": True,
            "eu_operated_infrastructure": True,
            "provider_eu_headquartered": True,
            "provider_legal_entity": "Mistral AI SAS",
        },
    )
    wrapper.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Bonjour"}],
    )
    signed = captured[0]
    assert signed["receipt"]["schema"] == "eu_sovereign_ai_session/v1"
    assert signed["receipt"]["eu_sovereignty"]["inference_region"] == "eu-west-3"
    assert signed["receipt"]["eu_sovereignty"]["provider_eu_headquartered"] is True
