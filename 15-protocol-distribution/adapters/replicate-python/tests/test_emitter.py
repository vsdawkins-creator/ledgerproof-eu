"""Emitter behaviour tests."""

from __future__ import annotations

import io
import json

import pytest

from ledgerproof_replicate.emitter import (
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
    WebhookEmitter,
)


def test_log_emitter_writes_json_to_stream():
    buf = io.StringIO()
    em = LogEmitter(stream=buf)
    em.emit({"receipt": {"schema": "synthetic_image/v1"}, "sig": "abc"})
    written = buf.getvalue().strip()
    parsed = json.loads(written)
    assert parsed["receipt"]["schema"] == "synthetic_image/v1"


def test_queue_emitter_calls_sink():
    sink_calls: list = []
    em = QueueEmitter(sink_calls.append)
    em.emit({"hello": "world"})
    assert sink_calls == [{"hello": "world"}]


def test_queue_emitter_swallows_sink_exception():
    """Best-effort: a sink raising must not propagate (C7)."""
    def bad_sink(x):
        raise RuntimeError("boom")

    em = QueueEmitter(bad_sink)
    # Should NOT raise:
    em.emit({"hello": "world"})


def test_multi_emitter_fans_out():
    a: list = []
    b: list = []
    em = MultiEmitter(QueueEmitter(a.append), QueueEmitter(b.append))
    em.emit({"x": 1})
    assert a == [{"x": 1}]
    assert b == [{"x": 1}]


def test_webhook_emitter_rejects_non_http_url():
    with pytest.raises(ValueError):
        WebhookEmitter("ftp://example.com/")
