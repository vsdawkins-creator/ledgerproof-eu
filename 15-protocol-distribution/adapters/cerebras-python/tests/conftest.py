"""Test fixtures for ledgerproof-cerebras.

We mock the upstream Cerebras Cloud SDK so tests don't require network access
or an API key.
"""

from __future__ import annotations

import sys
import types
from types import SimpleNamespace
from typing import Any

import pytest


def _make_chat_completion(content: str = "Hello there.", usage=None,
                           model: str = "llama3.1-70b"):
    msg = SimpleNamespace(content=content, role="assistant")
    choice = SimpleNamespace(message=msg, finish_reason="stop", index=0)
    return SimpleNamespace(
        id="chatcmpl-test",
        choices=[choice],
        model=model,
        usage=usage or SimpleNamespace(
            prompt_tokens=5,
            completion_tokens=3,
            total_tokens=8,
            reasoning_tokens=None,
        ),
    )


def _make_reasoning_completion():
    return _make_chat_completion(
        content="Final answer.",
        model="deepseek-r1-distill-llama-70b",
        usage=SimpleNamespace(
            prompt_tokens=12,
            completion_tokens=8,
            total_tokens=20,
            reasoning_tokens=42,
        ),
    )


def _make_stream_event(delta_content: str):
    delta = SimpleNamespace(content=delta_content, role=None)
    choice = SimpleNamespace(delta=delta, index=0, finish_reason=None)
    return SimpleNamespace(id="chatcmpl-stream", choices=[choice], usage=None)


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
        model = kwargs.get("model", "llama3.1-70b")
        if "r1" in model.lower() or "thinking" in model.lower():
            return _make_reasoning_completion()
        return _make_chat_completion(model=model)


class _FakeChat:
    def __init__(self):
        self.completions = _FakeChatCompletions()


class _FakeCerebras:
    def __init__(self, *a, **kw):
        self.chat = _FakeChat()


class _FakeAsyncChatCompletions:
    async def create(self, **kwargs):
        if kwargs.get("stream"):
            async def gen():
                for piece in ["Hel", "lo ", "there."]:
                    yield _make_stream_event(piece)
            return gen()
        model = kwargs.get("model", "llama3.1-70b")
        if "r1" in model.lower() or "thinking" in model.lower():
            return _make_reasoning_completion()
        return _make_chat_completion(model=model)


class _FakeAsyncChat:
    def __init__(self):
        self.completions = _FakeAsyncChatCompletions()


class _FakeAsyncCerebras:
    def __init__(self, *a, **kw):
        self.chat = _FakeAsyncChat()


@pytest.fixture(autouse=True)
def _patch_cerebras(monkeypatch):
    """Install a fake `cerebras.cloud.sdk` module before each test."""
    parent = types.ModuleType("cerebras")
    cloud = types.ModuleType("cerebras.cloud")
    sdk = types.ModuleType("cerebras.cloud.sdk")
    sdk.Cerebras = _FakeCerebras
    sdk.AsyncCerebras = _FakeAsyncCerebras
    parent.cloud = cloud
    cloud.sdk = sdk
    monkeypatch.setitem(sys.modules, "cerebras", parent)
    monkeypatch.setitem(sys.modules, "cerebras.cloud", cloud)
    monkeypatch.setitem(sys.modules, "cerebras.cloud.sdk", sdk)
    # Force re-import of wrapper modules so they pick up the fake.
    for name in [
        "ledgerproof_cerebras",
        "ledgerproof_cerebras.client_wrapper",
        "ledgerproof_cerebras.async_client_wrapper",
    ]:
        if name in sys.modules:
            del sys.modules[name]
    yield
