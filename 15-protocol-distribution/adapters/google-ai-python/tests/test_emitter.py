"""Emitter behavior tests (best-effort, no exceptions surface)."""

from __future__ import annotations

import io
import json

import pytest

from ledgerproof_google_ai.emitter import (
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
    StderrEmitter,
    WebhookEmitter,
)


def test_log_emitter_to_stream_writes_json_line():
    buf = io.StringIO()
    em = LogEmitter(stream=buf)
    em.emit({"receipt": {"hello": "world"}, "signature_alg": "ed25519"})
    out = buf.getvalue().strip()
    parsed = json.loads(out)
    assert parsed["signature_alg"] == "ed25519"


def test_queue_emitter_calls_sink():
    captured = []
    em = QueueEmitter(captured.append)
    em.emit({"x": 1})
    assert captured == [{"x": 1}]


def test_queue_emitter_swallows_sink_exceptions():
    def boom(_):
        raise RuntimeError("nope")

    em = QueueEmitter(boom)
    em.emit({"x": 1})  # must not raise


def test_multi_emitter_fans_out_and_isolates_failures():
    good_a = []
    good_b = []

    def fail(_):
        raise RuntimeError("nope")

    multi = MultiEmitter(
        QueueEmitter(good_a.append),
        QueueEmitter(fail),
        QueueEmitter(good_b.append),
    )
    multi.emit({"x": "y"})
    assert good_a == [{"x": "y"}]
    assert good_b == [{"x": "y"}]


def test_webhook_emitter_rejects_non_http_urls():
    with pytest.raises(ValueError):
        WebhookEmitter("ftp://example.com")


def test_stderr_emitter_is_log_emitter_subclass():
    em = StderrEmitter()
    assert isinstance(em, LogEmitter)
