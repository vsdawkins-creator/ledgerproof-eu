"""Test fixtures for ledgerproof-snowflake-cortex.

We mock both `snowflake.snowpark` (`Session`) and `snowflake.cortex`
(`Complete`, `Summarize`, `Translate`, `ExtractAnswer`, `Sentiment`) so tests
don't require a live Snowflake account.
"""

from __future__ import annotations

import sys
import types
from typing import Any, List

import pytest


# ---------------------------------------------------------------------------
# Fake snowflake.snowpark.Session
# ---------------------------------------------------------------------------


class _FakeSession:
    def __init__(self, configs: dict | None = None):
        self.configs = configs or {}
        self.closed = False

    def close(self):
        self.closed = True


class _FakeSessionBuilder:
    def configs(self, cfg):
        self._cfg = cfg
        return self

    def create(self):
        return _FakeSession(self._cfg)


class _FakeSessionFactory:
    builder = _FakeSessionBuilder()


# ---------------------------------------------------------------------------
# Fake snowflake.cortex surface
# ---------------------------------------------------------------------------


def _Complete(model, prompt, session=None, **kwargs):  # noqa: N802 — match real API
    # Echo a deterministic, schema-friendly answer.
    if isinstance(prompt, list):
        return "Cortex chat response."
    return f"Cortex response for prompt of length {len(str(prompt))}."


def _Summarize(text, session=None, **kwargs):  # noqa: N802
    return f"Summary of {len(text)} chars."


def _Translate(text, from_language, to_language, session=None, **kwargs):  # noqa: N802
    return f"[{to_language}] {text}"


def _ExtractAnswer(text, question, session=None, **kwargs):  # noqa: N802
    return [{"answer": "42", "score": 0.99}]


def _Sentiment(text, session=None, **kwargs):  # noqa: N802
    return 0.5


# ---------------------------------------------------------------------------
# Fake Cortex Search Service
# ---------------------------------------------------------------------------


class _FakeSearchService:
    def __init__(self, name: str):
        self.name = name

    def search(self, *, query, columns=None, limit=10, **kwargs):
        rows = [
            {"CHUNK": f"chunk-{i}", "SOURCE_URL": f"https://example/{i}"}
            for i in range(min(3, limit))
        ]
        return {"results": rows}


def _service_resolver_default(name: str) -> _FakeSearchService:
    return _FakeSearchService(name)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _patch_snowflake(monkeypatch):
    """Install fake `snowflake.snowpark` + `snowflake.cortex` modules."""
    parent = types.ModuleType("snowflake")
    snowpark = types.ModuleType("snowflake.snowpark")
    snowpark.Session = _FakeSessionFactory  # type: ignore[attr-defined]
    cortex = types.ModuleType("snowflake.cortex")
    cortex.Complete = _Complete  # type: ignore[attr-defined]
    cortex.Summarize = _Summarize  # type: ignore[attr-defined]
    cortex.Translate = _Translate  # type: ignore[attr-defined]
    cortex.ExtractAnswer = _ExtractAnswer  # type: ignore[attr-defined]
    cortex.Sentiment = _Sentiment  # type: ignore[attr-defined]
    parent.snowpark = snowpark  # type: ignore[attr-defined]
    parent.cortex = cortex  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "snowflake", parent)
    monkeypatch.setitem(sys.modules, "snowflake.snowpark", snowpark)
    monkeypatch.setitem(sys.modules, "snowflake.cortex", cortex)
    # Force re-import so wrappers pick up the fakes.
    for name in [
        "ledgerproof_snowflake_cortex",
        "ledgerproof_snowflake_cortex.cortex_wrapper",
        "ledgerproof_snowflake_cortex.search_wrapper",
    ]:
        if name in sys.modules:
            del sys.modules[name]
    yield


@pytest.fixture
def fake_session():
    return _FakeSession({"account": "test"})


@pytest.fixture
def fake_service_resolver():
    return _service_resolver_default


def capture_sink():
    """Helper: build a (sink, captured_list) pair for tests."""
    from ledgerproof_snowflake_cortex.emitter import ReceiptSink

    captured: List = []

    class Cap(ReceiptSink):
        def write(self, r):
            captured.append(r)

    return Cap(), captured
