"""Wrapper tests with mocked OpenAI clients (no network calls)."""

from __future__ import annotations

import hashlib
import queue
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

from ledgerproof_deepseek import (
    LedgerProofAsyncDeepSeek,
    LedgerProofDeepSeek,
    QueueEmitter,
    lpr_track,
)


def _fake_chat_completion(
    text: str = "hello world",
    id_: str = "ds-cmpl-abc",
    model: str = "deepseek-chat",
    reasoning_content: str | None = None,
):
    """Build an object shaped like a DeepSeek ChatCompletion."""
    message = SimpleNamespace(
        role="assistant",
        content=text,
        reasoning_content=reasoning_content,
    )
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id=id_,
        model=model,
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=3, completion_tokens=2, total_tokens=5),
    )


def _fake_stream_chunks(
    parts: list[str],
    id_: str = "ds-stream",
    model: str = "deepseek-chat",
    reasoning_parts: list[str] | None = None,
):
    reasoning_parts = reasoning_parts or [None] * len(parts)
    for i, (part, rc) in enumerate(zip(parts, reasoning_parts)):
        delta = SimpleNamespace(
            role="assistant" if i == 0 else None,
            content=part,
            reasoning_content=rc,
        )
        choice = SimpleNamespace(index=0, delta=delta, finish_reason=None)
        yield SimpleNamespace(id=id_, model=model, choices=[choice])


def _build_mock_openai() -> Any:
    inner = MagicMock()
    inner.chat = MagicMock()
    inner.chat.completions = MagicMock()
    return inner


# ---------------------------------------------------------------------------
# Sync, non-streaming
# ---------------------------------------------------------------------------


def test_sync_non_streaming_emits_receipt_and_returns_response_unmodified():
    fake = _build_mock_openai()
    completion = _fake_chat_completion(text="bonjour")
    fake.chat.completions.create.return_value = completion

    q: queue.Queue = queue.Queue()
    client = LedgerProofDeepSeek(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake,
    )

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "hi"}],
    )

    # C7 — response must be returned exactly as-is
    assert resp is completion
    assert resp.choices[0].message.content == "bonjour"

    envelope = q.get_nowait()
    assert envelope["adapter"]["name"] == "ledgerproof-deepseek"
    assert envelope["signature_alg"] == "ed25519"
    assert envelope["receipt"]["schema_id"] == "chatbot_session/v1"
    assert envelope["receipt"]["model_id"] == "deepseek-chat"
    assert envelope["receipt"]["model_provider"] == "deepseek"
    assert envelope["receipt"]["deployer_id"] == "urn:eu:deployer:acme"
    assert envelope["receipt"]["extra"]["provider"] == "deepseek"


def test_sync_reasoning_trace_schema_records_trace_hash():
    fake = _build_mock_openai()
    fake.chat.completions.create.return_value = _fake_chat_completion(
        text="sqrt(2) is irrational.",
        model="deepseek-reasoner",
        reasoning_content="Suppose sqrt(2) = p/q in lowest terms... <much thinking>",
    )

    q: queue.Queue = queue.Queue()
    client = LedgerProofDeepSeek(
        deployer_id="urn:eu:deployer:acme",
        regulatory_context={
            "schema": "reasoning_trace/v1",
            "trace_surfaced_to_user": True,
        },
        emitter=QueueEmitter(q),
        openai_client=fake,
    )
    client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[{"role": "user", "content": "Prove sqrt(2) irrational."}],
    )
    env = q.get_nowait()
    expected_reasoning = hashlib.sha256(
        b"Suppose sqrt(2) = p/q in lowest terms... <much thinking>"
    ).hexdigest()
    assert env["receipt"]["schema_id"] == "reasoning_trace/v1"
    assert env["receipt"]["reasoning_sha256"] == expected_reasoning
    assert env["receipt"]["trace_surfaced_to_user"] is True


def test_sync_code_generation_schema_records_language():
    fake = _build_mock_openai()
    fake.chat.completions.create.return_value = _fake_chat_completion(
        text="def rev(s): return s[::-1]", model="deepseek-coder"
    )

    q: queue.Queue = queue.Queue()
    client = LedgerProofDeepSeek(
        deployer_id="urn:eu:deployer:acme",
        regulatory_context={
            "schema": "code_generation/v1",
            "programming_language": "python",
        },
        emitter=QueueEmitter(q),
        openai_client=fake,
    )
    client.chat.completions.create(
        model="deepseek-coder",
        messages=[{"role": "user", "content": "Write a function to reverse a string."}],
    )
    env = q.get_nowait()
    assert env["receipt"]["schema_id"] == "code_generation/v1"
    assert env["receipt"]["content_modality"] == "code"
    assert env["receipt"]["programming_language"] == "python"


# ---------------------------------------------------------------------------
# Sync, streaming
# ---------------------------------------------------------------------------


def test_sync_streaming_emits_receipt_after_drain_with_full_text_hash():
    fake = _build_mock_openai()
    parts = ["Hello, ", "world", "!"]
    fake.chat.completions.create.return_value = _fake_stream_chunks(parts)

    q: queue.Queue = queue.Queue()
    client = LedgerProofDeepSeek(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake,
    )

    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "hi"}],
        stream=True,
    )

    # Receipt must NOT have been emitted yet
    assert q.empty()

    seen = list(stream)
    assert len(seen) == 3

    envelope = q.get_nowait()
    expected = hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()
    assert envelope["receipt"]["response_sha256"] == expected
    assert envelope["receipt"]["extra"]["streaming"] is True
    assert envelope["receipt"]["extra"]["provider"] == "deepseek"


def test_sync_streaming_reasoning_trace_incremental_hash():
    """C6: streaming reasoning trace must be hashed incrementally."""
    fake = _build_mock_openai()
    answer_parts = ["The ", "answer ", "is 42."]
    reasoning_parts = ["Let me ", "think ", "carefully."]
    fake.chat.completions.create.return_value = _fake_stream_chunks(
        answer_parts, model="deepseek-reasoner", reasoning_parts=reasoning_parts,
    )

    q: queue.Queue = queue.Queue()
    client = LedgerProofDeepSeek(
        deployer_id="urn:eu:deployer:acme",
        regulatory_context={"schema": "reasoning_trace/v1"},
        emitter=QueueEmitter(q),
        openai_client=fake,
    )
    stream = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[{"role": "user", "content": "compute"}],
        stream=True,
    )
    list(stream)

    env = q.get_nowait()
    expected_answer = hashlib.sha256(b"The answer is 42.").hexdigest()
    expected_reasoning = hashlib.sha256(b"Let me think carefully.").hexdigest()
    assert env["receipt"]["response_sha256"] == expected_answer
    assert env["receipt"]["reasoning_sha256"] == expected_reasoning


# ---------------------------------------------------------------------------
# Async, non-streaming
# ---------------------------------------------------------------------------


async def test_async_non_streaming_emits_receipt():
    fake_inner = MagicMock()
    fake_inner.chat = MagicMock()
    fake_inner.chat.completions = MagicMock()

    completion = _fake_chat_completion(text="ciao")

    async def fake_create(*args, **kwargs):
        return completion

    fake_inner.chat.completions.create = fake_create

    q: queue.Queue = queue.Queue()
    client = LedgerProofAsyncDeepSeek(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake_inner,
    )

    resp = await client.chat.completions.create(
        model="deepseek-chat", messages=[{"role": "user", "content": "hi"}]
    )

    assert resp is completion
    envelope = q.get_nowait()
    assert envelope["receipt"]["interaction_id"] == "ds-cmpl-abc"
    assert envelope["receipt"]["model_provider"] == "deepseek"


# ---------------------------------------------------------------------------
# Async, streaming
# ---------------------------------------------------------------------------


async def test_async_streaming_emits_receipt_after_drain():
    fake_inner = MagicMock()
    fake_inner.chat = MagicMock()
    fake_inner.chat.completions = MagicMock()

    parts = ["abc", "def", "ghi"]

    class _AsyncIter:
        def __init__(self, items):
            self._iter = iter(items)

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self._iter)
            except StopIteration:
                raise StopAsyncIteration

    async def fake_create(*args, **kwargs):
        return _AsyncIter(list(_fake_stream_chunks(parts)))

    fake_inner.chat.completions.create = fake_create

    q: queue.Queue = queue.Queue()
    client = LedgerProofAsyncDeepSeek(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake_inner,
    )

    stream = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "hi"}],
        stream=True,
    )

    assert q.empty()

    collected = []
    async for chunk in stream:
        collected.append(chunk)
    assert len(collected) == 3

    envelope = q.get_nowait()
    expected = hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()
    assert envelope["receipt"]["response_sha256"] == expected


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------


def test_decorator_emits_receipt_on_sync_function():
    q: queue.Queue = queue.Queue()

    @lpr_track(deployer_id="urn:eu:deployer:acme", emitter=QueueEmitter(q))
    def ask(question: str, *, messages):
        return _fake_chat_completion(text=f"echo: {question}")

    resp = ask("ping", messages=[{"role": "user", "content": "ping"}])
    assert resp.choices[0].message.content == "echo: ping"

    envelope = q.get_nowait()
    assert envelope["receipt"]["model_id"] == "deepseek-chat"
    assert envelope["adapter"]["name"] == "ledgerproof-deepseek"


def test_decorator_does_not_break_caller_when_emitter_fails():
    class _BoomEmitter:
        def emit(self, envelope):
            raise RuntimeError("boom")

    @lpr_track(deployer_id="urn:eu:deployer:acme", emitter=_BoomEmitter())
    def ask(*, messages):
        return _fake_chat_completion()

    # Must not raise — C7 discipline
    resp = ask(messages=[{"role": "user", "content": "hi"}])
    assert resp.choices[0].message.content == "hello world"
