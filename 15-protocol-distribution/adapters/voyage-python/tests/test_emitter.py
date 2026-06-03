"""Emitter tests."""

from __future__ import annotations

import io
import json

import pytest

from ledgerproof_voyage.emitter import (
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
    WebhookEmitter,
)


def _sample_receipt():
    return {"receipt": {"deployer_id": "acme-eu"}, "signature_b64": "AAAA"}


def test_log_emitter_writes_json_to_stream():
    buf = io.StringIO()
    em = LogEmitter(stream=buf)
    em.emit(_sample_receipt())
    line = buf.getvalue().strip()
    assert json.loads(line)["receipt"]["deployer_id"] == "acme-eu"


def test_queue_emitter_invokes_sink():
    captured = []
    em = QueueEmitter(captured.append)
    em.emit(_sample_receipt())
    assert captured and captured[0]["signature_b64"] == "AAAA"


def test_queue_emitter_swallows_sink_exceptions():
    def boom(_):
        raise RuntimeError("nope")

    em = QueueEmitter(boom)
    # Must NOT raise — emitters are best-effort (C7).
    em.emit(_sample_receipt())


def test_multi_emitter_fans_out():
    captured_a, captured_b = [], []
    em = MultiEmitter(QueueEmitter(captured_a.append), QueueEmitter(captured_b.append))
    em.emit(_sample_receipt())
    assert captured_a and captured_b


def test_webhook_emitter_rejects_non_http_urls():
    with pytest.raises(ValueError):
        WebhookEmitter("ftp://nope.example.com")
