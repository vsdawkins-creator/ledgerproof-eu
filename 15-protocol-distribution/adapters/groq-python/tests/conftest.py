"""Test fixtures for ledgerproof-groq.

We mock the upstream Groq SDK so tests don't require network access or an API key.
"""

from __future__ import annotations

import sys
import types
from types import SimpleNamespace
from typing import Any

import pytest


def _make_chat_completion(content: str = "Hello there.", usage=None):
    msg = SimpleNamespace(content=content, role="assistant")
    choice = SimpleNamespace(message=msg, finish_reason="stop", index=0)
    return SimpleNamespace(
        id="chatcmpl-test",
        choices=[choice],
        model="llama-3.3-70b-versatile",
        usage=usage or SimpleNamespace(prompt_tokens=5, completion_tokens=3, total_tokens=8),
    )


def _make_stream_event(delta_content: str):
    delta = SimpleNamespace(content=delta_content, role=None)
    choice = SimpleNamespace(delta=delta, index=0, finish_reason=None)
    return SimpleNamespace(id="chatcmpl-stream", choices=[choice])


class _FakeChatCompletions:
    def __init__(self):
        self.last_kwargs: dict[str, Any] = {}

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        if kwargs.get("stream"):
            def gen():
                for piece in ["Hel", "lo ", "there."]:
                    yield _make_stream_event(piece)
            return gen()
        return _make_chat_completion()


class _FakeChat:
    def __init__(self):
        self.completions = _FakeChatCompletions()


class _FakeAudioTranscriptions:
    def create(self, **kwargs):
        return SimpleNamespace(text="transcript text", language="en")


class _FakeAudio:
    def __init__(self):
        self.transcriptions = _FakeAudioTranscriptions()


class _FakeGroq:
    def __init__(self, *a, **kw):
        self.chat = _FakeChat()
        self.audio = _FakeAudio()


class _FakeAsyncChatCompletions:
    async def create(self, **kwargs):
        if kwargs.get("stream"):
            async def gen():
                for piece in ["Hel", "lo ", "there."]:
                    yield _make_stream_event(piece)
            return gen()
        return _make_chat_completion()


class _FakeAsyncChat:
    def __init__(self):
        self.completions = _FakeAsyncChatCompletions()


class _FakeAsyncAudioTranscriptions:
    async def create(self, **kwargs):
        return SimpleNamespace(text="async transcript", language="en")


class _FakeAsyncAudio:
    def __init__(self):
        self.transcriptions = _FakeAsyncAudioTranscriptions()


class _FakeAsyncGroq:
    def __init__(self, *a, **kw):
        self.chat = _FakeAsyncChat()
        self.audio = _FakeAsyncAudio()


@pytest.fixture(autouse=True)
def _patch_groq(monkeypatch):
    """Install a fake `groq` module before each test."""
    fake = types.ModuleType("groq")
    fake.Groq = _FakeGroq
    fake.AsyncGroq = _FakeAsyncGroq
    monkeypatch.setitem(sys.modules, "groq", fake)
    # Force re-import of wrapper modules so they pick up the fake.
    for name in [
        "ledgerproof_groq",
        "ledgerproof_groq.client_wrapper",
        "ledgerproof_groq.async_client_wrapper",
    ]:
        if name in sys.modules:
            del sys.modules[name]
    yield
