"""Wrapper tests with mocked OpenAI clients (no network calls)."""

from __future__ import annotations

import hashlib
import queue
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from ledgerproof_perplexity import (
    LedgerProofAsyncPerplexity,
    LedgerProofPerplexity,
    QueueEmitter,
    citation_list_hash_hex,
    lpr_track,
)


def _fake_chat_completion(
    text: str = "hello world",
    id_: str = "pplx-cmpl-abc",
    model: str = "sonar",
    citations: list[str] | None = None,
):
    """Build an object shaped like a Perplexity ChatCompletion (Sonar flavor)."""
    message = SimpleNamespace(role="assistant", content=text)
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(
        id=id_,
        model=model,
        choices=[choice],
        usage=SimpleNamespace(prompt_tokens=3, completion_tokens=2, total_tokens=5),
        citations=citations or [],
    )


def _fake_stream_chunks(
    parts: list[str],
    id_: str = "pplx-stream",
    model: str = "sonar",
    final_citations: list[str] | None = None,
):
    last_idx = len(parts) - 1
    for i, part in enumerate(parts):
        delta = SimpleNamespace(role="assistant" if i == 0 else None, content=part)
        choice = SimpleNamespace(index=0, delta=delta, finish_reason=None)
        chunk = SimpleNamespace(
            id=id_,
            model=model,
            choices=[choice],
            citations=final_citations if (i == last_idx and final_citations) else None,
        )
        yield chunk


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
    client = LedgerProofPerplexity(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake,
    )

    resp = client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": "hi"}],
    )

    # C7 — response must be returned exactly as-is
    assert resp is completion
    assert resp.choices[0].message.content == "bonjour"

    envelope = q.get_nowait()
    assert envelope["adapter"]["name"] == "ledgerproof-perplexity"
    assert envelope["signature_alg"] == "ed25519"
    assert envelope["receipt"]["schema_id"] == "chatbot_session/v1"
    assert envelope["receipt"]["model_id"] == "sonar"
    assert envelope["receipt"]["model_provider"] == "perplexity"
    assert envelope["receipt"]["deployer_id"] == "urn:eu:deployer:acme"
    assert envelope["receipt"]["extra"]["provider"] == "perplexity"


def test_sync_ai_search_schema_auto_extracts_citations():
    fake = _build_mock_openai()
    urls = ["https://b.example/2", "https://a.example/1"]
    fake.chat.completions.create.return_value = _fake_chat_completion(
        text="Per sources...", citations=urls
    )

    q: queue.Queue = queue.Queue()
    client = LedgerProofPerplexity(
        deployer_id="urn:eu:deployer:acme",
        regulatory_context={"schema": "ai_search_with_citations/v1"},
        emitter=QueueEmitter(q),
        openai_client=fake,
    )
    client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": "What's the EU AI Act timeline?"}],
    )
    env = q.get_nowait()
    assert env["receipt"]["schema_id"] == "ai_search_with_citations/v1"
    assert env["receipt"]["citations_count"] == 2
    # The hash must be sort-stable
    assert env["receipt"]["citations_sha256"] == citation_list_hash_hex(urls)


def test_sync_public_interest_text_schema_carries_disclosure_fields():
    fake = _build_mock_openai()
    fake.chat.completions.create.return_value = _fake_chat_completion(
        text="Public health summary...",
        citations=["https://who.example/factsheet"],
    )

    q: queue.Queue = queue.Queue()
    client = LedgerProofPerplexity(
        deployer_id="urn:eu:deployer:acme-media-de",
        regulatory_context={
            "schema": "public_interest_text/v1",
            "disclosure_label_shown": True,
            "editorial_review": True,
            "subject_category": "health.public_health",
        },
        emitter=QueueEmitter(q),
        openai_client=fake,
    )
    client.chat.completions.create(
        model="sonar-pro",
        messages=[{"role": "user", "content": "Summarise WHO factsheet"}],
    )
    env = q.get_nowait()
    assert env["receipt"]["schema_id"] == "public_interest_text/v1"
    assert env["receipt"]["article_basis"] == "EU_AI_Act_Art_50_4"
    assert env["receipt"]["disclosure_label_shown"] is True
    assert env["receipt"]["editorial_review"] is True
    assert env["receipt"]["subject_category"] == "health.public_health"
    assert env["receipt"]["citations_count"] == 1


# ---------------------------------------------------------------------------
# Sync, streaming
# ---------------------------------------------------------------------------


def test_sync_streaming_emits_receipt_after_drain_with_full_text_hash():
    fake = _build_mock_openai()
    parts = ["Hello, ", "world", "!"]
    fake.chat.completions.create.return_value = _fake_stream_chunks(parts)

    q: queue.Queue = queue.Queue()
    client = LedgerProofPerplexity(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake,
    )

    stream = client.chat.completions.create(
        model="sonar",
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
    assert envelope["receipt"]["extra"]["provider"] == "perplexity"


def test_sync_streaming_ai_search_schema_captures_terminal_citations():
    """Perplexity often attaches the citation list on the *final* chunk —
    the streaming proxy should accumulate them and emit on drain."""
    fake = _build_mock_openai()
    urls = ["https://x.example/a", "https://y.example/b"]
    fake.chat.completions.create.return_value = _fake_stream_chunks(
        ["foo", "bar"], final_citations=urls
    )

    q: queue.Queue = queue.Queue()
    client = LedgerProofPerplexity(
        deployer_id="urn:eu:deployer:acme",
        regulatory_context={"schema": "ai_search_with_citations/v1"},
        emitter=QueueEmitter(q),
        openai_client=fake,
    )
    stream = client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": "news"}],
        stream=True,
    )
    list(stream)
    env = q.get_nowait()
    assert env["receipt"]["citations_count"] == 2
    assert env["receipt"]["citations_sha256"] == citation_list_hash_hex(urls)


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
    client = LedgerProofAsyncPerplexity(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake_inner,
    )

    resp = await client.chat.completions.create(
        model="sonar", messages=[{"role": "user", "content": "hi"}]
    )

    assert resp is completion
    envelope = q.get_nowait()
    assert envelope["receipt"]["interaction_id"] == "pplx-cmpl-abc"
    assert envelope["receipt"]["model_provider"] == "perplexity"


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
    client = LedgerProofAsyncPerplexity(
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
        openai_client=fake_inner,
    )

    stream = await client.chat.completions.create(
        model="sonar",
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
    def search(question: str, *, messages):
        return _fake_chat_completion(text=f"echo: {question}")

    resp = search("ping", messages=[{"role": "user", "content": "ping"}])
    assert resp.choices[0].message.content == "echo: ping"

    envelope = q.get_nowait()
    assert envelope["receipt"]["model_id"] == "sonar"
    assert envelope["adapter"]["name"] == "ledgerproof-perplexity"


def test_decorator_does_not_break_caller_when_emitter_fails():
    class _BoomEmitter:
        def emit(self, envelope):
            raise RuntimeError("boom")

    @lpr_track(deployer_id="urn:eu:deployer:acme", emitter=_BoomEmitter())
    def search(*, messages):
        return _fake_chat_completion()

    # Must not raise — C7 discipline
    resp = search(messages=[{"role": "user", "content": "hi"}])
    assert resp.choices[0].message.content == "hello world"
