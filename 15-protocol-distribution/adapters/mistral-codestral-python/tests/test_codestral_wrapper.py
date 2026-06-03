"""
Codestral client wrapper tests using mocked clients (no network, no API key).
"""

from __future__ import annotations

import asyncio
import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from ledgerproof_mistral_codestral import (
    LedgerProofAsyncCodestral,
    LedgerProofCodestral,
    QueueEmitter,
)
from ledgerproof_mistral_codestral.canonical import canonical_encode
from ledgerproof_mistral_codestral.signer import Ed25519Signer, verify


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


def _fake_chat_response(
    text: str = "def fib(n):\n    return n if n<2 else fib(n-1)+fib(n-2)\n",
    response_id: str = "cmpl_cstr_001",
):
    message = SimpleNamespace(role="assistant", content=text, tool_calls=None)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id=response_id,
        model="codestral-latest",
        object="chat.completion",
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=15, completion_tokens=30, total_tokens=45),
    )


def _fake_fim_response(middle: str = "    return result\n", response_id: str = "fim_cstr_001"):
    """Codestral FIM uses the same ChatCompletionResponse envelope."""
    message = SimpleNamespace(role="assistant", content=middle, tool_calls=None)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id=response_id,
        model="codestral-latest",
        object="chat.completion",
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=20, completion_tokens=8, total_tokens=28),
    )


def _fake_stream_chunks(text_parts):
    chunks = []
    for i, part in enumerate(text_parts):
        delta = SimpleNamespace(role="assistant" if i == 0 else None, content=part)
        choice = SimpleNamespace(index=0, delta=delta, finish_reason=None)
        data = SimpleNamespace(
            id="cmpl_stream_001",
            model="codestral-latest",
            object="chat.completion.chunk",
            choices=[choice],
        )
        chunks.append(SimpleNamespace(data=data))
    delta_final = SimpleNamespace(role=None, content=None)
    choice_final = SimpleNamespace(index=0, delta=delta_final, finish_reason="stop")
    data_final = SimpleNamespace(
        id="cmpl_stream_001",
        model="codestral-latest",
        object="chat.completion.chunk",
        choices=[choice_final],
        usage=SimpleNamespace(prompt_tokens=5, completion_tokens=10, total_tokens=15),
    )
    chunks.append(SimpleNamespace(data=data_final))
    return chunks


def _make_wrapper(emitter_sink, *, fake_inner=None, **kwargs):
    if fake_inner is None:
        fake_inner = MagicMock()
        fake_inner.chat.complete.return_value = _fake_chat_response()
    return LedgerProofCodestral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(emitter_sink.append),
        signer=Ed25519Signer(),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Chat (sync)
# ---------------------------------------------------------------------------


def test_sync_chat_complete_emits_generated_code_receipt():
    captured = []
    wrapper = _make_wrapper(captured, language="python")
    response = wrapper.chat.complete(
        model="codestral-latest",
        messages=[{"role": "user", "content": "Write a Python fib()."}],
    )
    # C7: response passed through unchanged.
    assert response.id == "cmpl_cstr_001"
    assert "def fib" in response.choices[0].message.content

    assert len(captured) == 1
    signed = captured[0]
    assert signed["signature_alg"] == "ed25519"
    assert signed["receipt"]["deployer_id"] == "acme-eu-test"
    assert signed["receipt"]["schema"] == "generated_code/v1"  # default for chat
    assert signed["receipt"]["model"]["provider"] == "mistral-codestral"
    assert signed["receipt"]["model"]["model_id"] == "codestral-latest"
    assert signed["receipt"]["code_attributes"]["language"] == "python"
    assert signed["receipt"]["code_attributes"]["line_count"] >= 1
    assert signed["receipt"]["code_attributes"]["has_security_pattern"] is False


def test_sync_chat_complete_emitter_failure_does_not_break_call():
    """C7: emitter failure must never propagate."""

    class _Boom:
        def emit(self, _):
            raise RuntimeError("emitter died")

    fake_inner = MagicMock()
    fake_inner.chat.complete.return_value = _fake_chat_response()
    wrapper = LedgerProofCodestral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=_Boom(),
        signer=Ed25519Signer(),
    )
    response = wrapper.chat.complete(
        model="codestral-latest",
        messages=[{"role": "user", "content": "Hi"}],
    )
    assert response.id == "cmpl_cstr_001"


def test_sync_chat_streaming_emits_receipt_with_incremental_hash():
    captured = []
    text_parts = ["def ", "fib(n):\n", "    return n"]
    chunks = _fake_stream_chunks(text_parts)

    fake_inner = MagicMock()
    fake_inner.chat.stream.return_value = iter(chunks)

    wrapper = LedgerProofCodestral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        language="python",
    )

    received = []
    for chunk in wrapper.chat.stream(
        model="codestral-latest",
        messages=[{"role": "user", "content": "Write fib"}],
    ):
        delta = chunk.data.choices[0].delta.content
        if delta:
            received.append(delta)

    assert "".join(received) == "".join(text_parts)
    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["streaming"] is True
    asst = next(c for c in signed["receipt"]["content_refs"] if c["role"] == "assistant")
    assert asst["byte_length"] == len("".join(text_parts).encode("utf-8"))


def test_sync_streaming_emits_on_early_close():
    captured = []
    chunks = _fake_stream_chunks(["AB", "CD", "EF"])
    fake_inner = MagicMock()
    fake_inner.chat.stream.return_value = iter(chunks)
    wrapper = LedgerProofCodestral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    stream = wrapper.chat.stream(
        model="codestral-latest",
        messages=[{"role": "user", "content": "Hi"}],
    )
    next(stream)
    stream.close()
    assert len(captured) == 1
    assert captured[0]["receipt"]["streaming"] is True


# ---------------------------------------------------------------------------
# FIM (sync)
# ---------------------------------------------------------------------------


def test_sync_fim_complete_emits_fim_completion_receipt():
    captured = []
    fake_inner = MagicMock()
    fake_inner.fim.complete.return_value = _fake_fim_response(middle="    return memo[n]\n")
    wrapper = LedgerProofCodestral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        language="python",
    )
    response = wrapper.fim.complete(
        model="codestral-latest",
        prompt="def fib(n):\n    ",
        suffix="\n    return memo[n]",
    )
    assert response.id == "fim_cstr_001"

    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["schema"] == "fim_completion/v1"
    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "prefix" in roles and "suffix" in roles and "middle" in roles
    assert signed["receipt"]["fim_positions"]["prefix_byte_length"] == len(
        "def fib(n):\n    ".encode("utf-8")
    )
    assert signed["receipt"]["fim_positions"]["suffix_byte_length"] == len(
        "\n    return memo[n]".encode("utf-8")
    )
    assert signed["receipt"]["fim_positions"]["middle_byte_length"] == len(
        "    return memo[n]\n".encode("utf-8")
    )
    assert signed["receipt"]["code_attributes"]["language"] == "python"


def test_sync_fim_streaming_emits_with_positions():
    captured = []
    chunks = _fake_stream_chunks(["mem", "o[n] = ", "fib(n-1)"])
    fake_inner = MagicMock()
    fake_inner.fim.stream.return_value = iter(chunks)
    wrapper = LedgerProofCodestral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        language="python",
    )
    received = []
    for chunk in wrapper.fim.stream(
        model="codestral-latest",
        prompt="def fib(n):\n    ",
        suffix="\n    return memo[n]",
    ):
        delta = chunk.data.choices[0].delta.content
        if delta:
            received.append(delta)
    assert "".join(received) == "memo[n] = fib(n-1)"
    signed = captured[0]
    assert signed["receipt"]["schema"] == "fim_completion/v1"
    assert signed["receipt"]["streaming"] is True
    middle = next(c for c in signed["receipt"]["content_refs"] if c["role"] == "middle")
    assert middle["byte_length"] == len("memo[n] = fib(n-1)".encode("utf-8"))


# ---------------------------------------------------------------------------
# Async chat + FIM
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


def test_async_chat_complete_emits_receipt():
    captured = []
    fake_inner = MagicMock()
    fake_inner.chat.complete_async = AsyncMock(return_value=_fake_chat_response())
    wrapper = LedgerProofAsyncCodestral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        language="python",
    )

    async def _run():
        response = await wrapper.chat.complete_async(
            model="codestral-latest",
            messages=[{"role": "user", "content": "Hi async"}],
        )
        assert response.id == "cmpl_cstr_001"

    asyncio.run(_run())
    assert len(captured) == 1
    assert captured[0]["receipt"]["schema"] == "generated_code/v1"


def test_async_fim_complete_emits_receipt():
    captured = []
    fake_inner = MagicMock()
    fake_inner.fim.complete_async = AsyncMock(return_value=_fake_fim_response())
    wrapper = LedgerProofAsyncCodestral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        language="python",
    )

    async def _run():
        response = await wrapper.fim.complete_async(
            model="codestral-latest",
            prompt="def fib(n):\n    ",
            suffix="\n    return result",
        )
        assert response.id == "fim_cstr_001"

    asyncio.run(_run())
    assert len(captured) == 1
    assert captured[0]["receipt"]["schema"] == "fim_completion/v1"
    assert captured[0]["receipt"]["fim_positions"]["prefix_byte_length"] > 0


def test_async_chat_streaming_emits_receipt():
    captured = []
    chunks = _fake_stream_chunks(["abc", "def"])
    fake_inner = MagicMock()
    fake_inner.chat.stream_async = AsyncMock(return_value=_AsyncIter(chunks))
    wrapper = LedgerProofAsyncCodestral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        stream = await wrapper.chat.stream_async(
            model="codestral-latest",
            messages=[{"role": "user", "content": "Hi"}],
        )
        out = []
        async for chunk in stream:
            d = chunk.data.choices[0].delta.content
            if d:
                out.append(d)
        return "".join(out)

    text = asyncio.run(_run())
    assert text == "abcdef"
    assert len(captured) == 1
    assert captured[0]["receipt"]["streaming"] is True


# ---------------------------------------------------------------------------
# C4: offline verification
# ---------------------------------------------------------------------------


def test_signature_verifies_with_published_public_key():
    captured = []
    signer = Ed25519Signer()
    fake_inner = MagicMock()
    fake_inner.chat.complete.return_value = _fake_chat_response()
    wrapper = LedgerProofCodestral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )
    wrapper.chat.complete(
        model="codestral-latest",
        messages=[{"role": "user", "content": "Verify me"}],
    )
    signed = captured[0]
    canonical_bytes = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)


# ---------------------------------------------------------------------------
# Schema override (e.g. chatbot_session/v1 for an IDE chat panel)
# ---------------------------------------------------------------------------


def test_chat_schema_override_to_chatbot_session():
    captured = []
    fake_inner = MagicMock()
    fake_inner.chat.complete.return_value = _fake_chat_response()
    wrapper = LedgerProofCodestral(
        deployer_id="acme-eu-test",
        client=fake_inner,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        chat_schema="chatbot_session/v1",
    )
    wrapper.chat.complete(
        model="codestral-latest",
        messages=[{"role": "user", "content": "Bonjour"}],
    )
    assert captured[0]["receipt"]["schema"] == "chatbot_session/v1"
