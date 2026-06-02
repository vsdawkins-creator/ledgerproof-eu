"""Shared fixtures + vertexai mock injection.

We install a synthetic `vertexai` module into sys.modules so the adapter
imports work without google-cloud-aiplatform being installed in CI.
"""
from __future__ import annotations

import sys
import types
from typing import Any

import pytest


# ---- Synthetic vertexai package ---------------------------------------------


class _FakeResponse:
    def __init__(self, text: str = "ok") -> None:
        self.text = text

        class _Part:
            def __init__(self, t: str) -> None:
                self.text = t

        class _Content:
            def __init__(self, t: str) -> None:
                self.parts = [_Part(t)]

        class _Candidate:
            def __init__(self, t: str) -> None:
                self.content = _Content(t)

        self.candidates = [_Candidate(text)]


class _FakeChatSession:
    def __init__(self) -> None:
        self.history: list[Any] = []

    def send_message(self, content: Any, *, stream: bool = False, **kwargs: Any) -> Any:
        text = f"reply:{content}"
        if stream:
            return iter([_FakeResponse(text)])
        return _FakeResponse(text)


class _FakeGenerativeModel:
    def __init__(self, model_name: str, **kwargs: Any) -> None:
        self.model_name = model_name
        self.last_kwargs = kwargs

    def generate_content(
        self, contents: Any, *, stream: bool = False, **kwargs: Any
    ) -> Any:
        text = f"vertex-says:{contents}"
        if stream:
            return iter([_FakeResponse("vertex-says:"), _FakeResponse(str(contents))])
        return _FakeResponse(text)

    def start_chat(self, **kwargs: Any) -> _FakeChatSession:
        return _FakeChatSession()


def _install_fake_vertexai() -> None:
    if "vertexai" in sys.modules:
        return
    vertexai = types.ModuleType("vertexai")
    vertexai._project = None
    vertexai._location = None

    def init(*, project: str | None = None, location: str | None = None, **_: Any) -> None:
        vertexai._project = project
        vertexai._location = location

    vertexai.init = init  # type: ignore[attr-defined]

    gen_models = types.ModuleType("vertexai.generative_models")
    gen_models.GenerativeModel = _FakeGenerativeModel  # type: ignore[attr-defined]
    gen_models.ChatSession = _FakeChatSession  # type: ignore[attr-defined]

    sys.modules["vertexai"] = vertexai
    sys.modules["vertexai.generative_models"] = gen_models


_install_fake_vertexai()


# ---- Reusable fixtures ------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_emitter_config():
    from ledgerproof_vertexai import emitter

    emitter._cfg = emitter.EmitterConfig()
    yield
    emitter._cfg = emitter.EmitterConfig()


@pytest.fixture
def captured_sink():
    captured: list[dict] = []

    def sink(env: dict) -> None:
        captured.append(env)

    return captured, sink


@pytest.fixture
def configured(captured_sink):
    captured, sink = captured_sink
    from ledgerproof_vertexai import configure

    configure(deployer_id="urn:lpr:deployer:test-tenant", sink=sink)
    return captured
