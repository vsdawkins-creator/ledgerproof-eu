"""
Client wrapper tests using mocked DashScope `Generation` (no network, no real key).

We mock `Generation` so the tests run on a fresh venv without `DASHSCOPE_API_KEY`
set.
"""

from __future__ import annotations

import asyncio
import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from ledgerproof_qwen import (
    LedgerProofAsyncQwen,
    LedgerProofQwen,
    QueueEmitter,
)
from ledgerproof_qwen.canonical import canonical_encode
from ledgerproof_qwen.signer import Ed25519Signer, verify


# ---------------------------------------------------------------------------
# Fixtures: shape a DashScope GenerationResponse-like object
# ---------------------------------------------------------------------------


def _fake_chat_response(
    text: str = "你好,世界。",
    request_id: str = "req_test_001",
    with_tool_call: bool = False,
):
    if with_tool_call:
        tool_call = {
            "id": "call_abc_1",
            "type": "function",
            "function": {"name": "get_weather", "arguments": '{"city": "Shanghai"}'},
        }
        message = SimpleNamespace(role="assistant", content=text, tool_calls=[tool_call])
    else:
        message = SimpleNamespace(role="assistant", content=text, tool_calls=None)
    choice = SimpleNamespace(message=message, finish_reason="stop")
    output = SimpleNamespace(text=None, choices=[choice], finish_reason="stop")
    return SimpleNamespace(
        request_id=request_id,
        output=output,
        usage=SimpleNamespace(input_tokens=10, output_tokens=20, total_tokens=30),
        status_code=200,
    )


def _make_wrapper(emitter_sink, with_tool_call=False):
    fake_generation = MagicMock()
    fake_generation.call.return_value = _fake_chat_response(with_tool_call=with_tool_call)
    return LedgerProofQwen(
        deployer_id="acme-eu-test",
        generation=fake_generation,
        emitter=QueueEmitter(emitter_sink.append),
        signer=Ed25519Signer(),
    )


# ---------------------------------------------------------------------------
# Sync non-streaming
# ---------------------------------------------------------------------------


def test_sync_call_emits_receipt_and_returns_response_unchanged():
    captured: list = []
    wrapper = _make_wrapper(captured)
    response = wrapper.generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": "Hi there"}],
    )
    # C7: response is passed through unchanged.
    assert response.request_id == "req_test_001"
    assert response.output.choices[0].message.content == "你好,世界。"

    assert len(captured) == 1
    signed = captured[0]
    assert signed["signature_alg"] == "ed25519"
    assert signed["receipt"]["deployer_id"] == "acme-eu-test"
    assert signed["receipt"]["schema"] == "chatbot_session/v1"
    assert signed["receipt"]["streaming"] is False
    assert signed["receipt"]["model"]["provider"] == "qwen"
    assert signed["receipt"]["model"]["model_id"] == "qwen-max"
    # DashScope usage shape (input_tokens / output_tokens) is normalised.
    assert signed["receipt"]["model"]["prompt_tokens"] == 10
    assert signed["receipt"]["model"]["completion_tokens"] == 20

    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles and "assistant" in roles


def test_sync_call_with_tool_call_captures_tool_use_ref():
    captured: list = []
    wrapper = _make_wrapper(captured, with_tool_call=True)
    wrapper.generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": "Weather in Shanghai?"}],
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

    fake_generation = MagicMock()
    fake_generation.call.return_value = _fake_chat_response()
    wrapper = LedgerProofQwen(
        deployer_id="acme-eu-test",
        generation=fake_generation,
        emitter=_Boom(),
        signer=Ed25519Signer(),
    )
    # Must NOT raise.
    response = wrapper.generation.call(
        model="qwen-plus",
        messages=[{"role": "user", "content": "Hi"}],
    )
    assert response.request_id == "req_test_001"


def test_sync_call_supports_plain_prompt_arg():
    """DashScope accepts prompt='...' as an alternative to messages."""
    captured: list = []
    fake_generation = MagicMock()
    # Plain-text response mode: output.text populated, output.choices empty.
    fake_generation.call.return_value = SimpleNamespace(
        request_id="req_test_plain",
        output=SimpleNamespace(text="Plain reply.", choices=None, finish_reason="stop"),
        usage=SimpleNamespace(input_tokens=1, output_tokens=2, total_tokens=3),
        status_code=200,
    )
    wrapper = LedgerProofQwen(
        deployer_id="acme-eu-test",
        generation=fake_generation,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )
    wrapper.generation.call(model="qwen-turbo", prompt="say hi")
    assert len(captured) == 1
    signed = captured[0]
    roles = [c["role"] for c in signed["receipt"]["content_refs"]]
    assert "user" in roles


# ---------------------------------------------------------------------------
# Sync streaming (DashScope: cumulative-output mode is the default)
# ---------------------------------------------------------------------------


def _fake_stream_chunks_cumulative(text_parts: list[str]):
    """DashScope cumulative streaming: each chunk repeats the full text so far."""
    chunks = []
    cumulative = ""
    for part in text_parts:
        cumulative += part
        message = SimpleNamespace(role="assistant", content=cumulative)
        choice = SimpleNamespace(message=message, finish_reason=None)
        output = SimpleNamespace(text=None, choices=[choice], finish_reason=None)
        chunks.append(
            SimpleNamespace(
                request_id="req_stream_001",
                output=output,
                usage=None,
                status_code=200,
            )
        )
    # Final chunk with finish_reason
    final_message = SimpleNamespace(role="assistant", content=cumulative)
    final_choice = SimpleNamespace(message=final_message, finish_reason="stop")
    final_output = SimpleNamespace(text=None, choices=[final_choice], finish_reason="stop")
    chunks.append(
        SimpleNamespace(
            request_id="req_stream_001",
            output=final_output,
            usage=SimpleNamespace(input_tokens=5, output_tokens=10, total_tokens=15),
            status_code=200,
        )
    )
    return chunks


def test_sync_streaming_cumulative_emits_receipt_with_incremental_hash():
    captured: list = []
    text_parts = ["你", "好,", "世界", "。"]
    chunks = _fake_stream_chunks_cumulative(text_parts)

    fake_generation = MagicMock()
    fake_generation.call.return_value = iter(chunks)

    wrapper = LedgerProofQwen(
        deployer_id="acme-eu-test",
        generation=fake_generation,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    received = []
    for chunk in wrapper.generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": "Hi"}],
        stream=True,
    ):
        received.append(chunk.output.choices[0].message.content)

    # Last cumulative payload should be the full string.
    assert received[-1] == "你好,世界。"

    assert len(captured) == 1
    signed = captured[0]
    assert signed["receipt"]["streaming"] is True
    asst = next(c for c in signed["receipt"]["content_refs"] if c["role"] == "assistant")
    # Critical: incremental hasher saw only the DELTA bytes, not the cumulative
    # repetitions — so byte_length should equal the final string length.
    assert asst["byte_length"] == len("你好,世界。".encode("utf-8"))


def test_sync_streaming_emits_receipt_on_early_close():
    """If the caller breaks early, receipt should still emit on stream.close()."""
    captured: list = []
    chunks = _fake_stream_chunks_cumulative(["AB", "CD", "EF"])

    fake_generation = MagicMock()
    fake_generation.call.return_value = iter(chunks)

    wrapper = LedgerProofQwen(
        deployer_id="acme-eu-test",
        generation=fake_generation,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    stream = wrapper.generation.call(
        model="qwen-max",
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


def test_async_call_emits_receipt():
    captured: list = []

    fake_generation = MagicMock()
    fake_generation.call = AsyncMock(return_value=_fake_chat_response())

    wrapper = LedgerProofAsyncQwen(
        deployer_id="acme-eu-test",
        generation=fake_generation,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        response = await wrapper.generation.call(
            model="qwen-max",
            messages=[{"role": "user", "content": "Hi async"}],
        )
        assert response.request_id == "req_test_001"

    asyncio.run(_run())

    assert len(captured) == 1
    assert captured[0]["receipt"]["deployer_id"] == "acme-eu-test"
    assert captured[0]["receipt"]["model"]["model_id"] == "qwen-max"


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


def test_async_streaming_cumulative_emits_receipt_with_incremental_hash():
    captured: list = []
    chunks = _fake_stream_chunks_cumulative(["Hel", "lo!"])

    fake_generation = MagicMock()
    fake_generation.call = AsyncMock(return_value=_AsyncIter(chunks))

    wrapper = LedgerProofAsyncQwen(
        deployer_id="acme-eu-test",
        generation=fake_generation,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
    )

    async def _run():
        stream = await wrapper.generation.call(
            model="qwen-plus",
            messages=[{"role": "user", "content": "Hi"}],
            stream=True,
        )
        last = ""
        async for chunk in stream:
            last = chunk.output.choices[0].message.content
        return last

    final_text = asyncio.run(_run())
    assert final_text == "Hello!"
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
    fake_generation = MagicMock()
    fake_generation.call.return_value = _fake_chat_response()
    wrapper = LedgerProofQwen(
        deployer_id="acme-eu-test",
        generation=fake_generation,
        emitter=QueueEmitter(captured.append),
        signer=signer,
    )
    wrapper.generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": "Verify me"}],
    )
    signed = captured[0]
    canonical_bytes = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_bytes, sig)


# ---------------------------------------------------------------------------
# Qwen-specific schemas
# ---------------------------------------------------------------------------


def test_multilingual_chinese_inference_schema_is_emitted_when_configured():
    captured: list = []
    fake_generation = MagicMock()
    fake_generation.call.return_value = _fake_chat_response()
    import hashlib

    disclosure_hash = hashlib.sha256("此为AI生成内容".encode("utf-8")).hexdigest()
    wrapper = LedgerProofQwen(
        deployer_id="acme-eu-test",
        generation=fake_generation,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        schema="multilingual_chinese_inference/v1",
        chinese_inference={
            "chinese_disclosure_shown": True,
            "chinese_disclosure_text_hash_sha256_hex": disclosure_hash,
            "endpoint_region": "singapore",
            "avoids_mainland_residency": True,
            "provider_legal_entity": "Alibaba Cloud (Singapore) Private Limited",
        },
    )
    wrapper.generation.call(
        model="qwen-max",
        messages=[{"role": "user", "content": "你好"}],
    )
    signed = captured[0]
    assert signed["receipt"]["schema"] == "multilingual_chinese_inference/v1"
    assert signed["receipt"]["chinese_inference"]["endpoint_region"] == "singapore"
    assert signed["receipt"]["chinese_inference"]["avoids_mainland_residency"] is True


def test_cross_jurisdictional_routing_schema_is_emitted_when_configured():
    captured: list = []
    fake_generation = MagicMock()
    fake_generation.call.return_value = _fake_chat_response()
    wrapper = LedgerProofQwen(
        deployer_id="acme-eu-test",
        generation=fake_generation,
        emitter=QueueEmitter(captured.append),
        signer=Ed25519Signer(),
        schema="cross_jurisdictional_routing/v1",
        cross_jurisdictional_route={
            "endpoint_region": "singapore",
            "endpoint_base_url": "https://dashscope-intl.aliyuncs.com",
            "avoids_mainland_residency": True,
            "transfer_mechanism": "SCCs-2021/914 + supplementary measures",
        },
    )
    wrapper.generation.call(
        model="qwen-plus",
        messages=[{"role": "user", "content": "Bonjour"}],
    )
    signed = captured[0]
    assert signed["receipt"]["schema"] == "cross_jurisdictional_routing/v1"
    cjr = signed["receipt"]["cross_jurisdictional_route"]
    assert cjr["endpoint_region"] == "singapore"
    assert cjr["endpoint_base_url"] == "https://dashscope-intl.aliyuncs.com"
    assert cjr["avoids_mainland_residency"] is True
