"""Tests for emitter side-channel behavior — C7 must hold."""

from __future__ import annotations

import logging
import queue

import pytest

from ledgerproof_llamaindex.emitter import (
    LogEmitter,
    QueueEmitter,
    WebhookEmitter,
)


def test_log_emitter_writes_at_configured_level(caplog):
    em = LogEmitter(level=logging.INFO)
    env = {"envelope_version": "lpr/0.1", "payload": {"x": 1}}
    with caplog.at_level(logging.INFO, logger="ledgerproof.llamaindex"):
        em.emit(env)
    assert any("ledgerproof_receipt" in rec.message for rec in caplog.records)


def test_log_emitter_handles_non_serializable_payload(caplog):
    em = LogEmitter(level=logging.INFO)
    # Functions are not JSON-serializable.
    env = {"x": lambda: 1}
    with caplog.at_level(logging.INFO, logger="ledgerproof.llamaindex"):
        em.emit(env)  # must not raise
    assert any("ledgerproof_receipt" in rec.message for rec in caplog.records)


def test_queue_emitter_pushes_envelope():
    q: queue.Queue = queue.Queue()
    em = QueueEmitter(q)
    env = {"hello": "world"}
    em.emit(env)
    assert q.get_nowait() == env


def test_queue_emitter_full_does_not_raise():
    q: queue.Queue = queue.Queue(maxsize=1)
    em = QueueEmitter(q, block=False)
    em.emit({"a": 1})
    em.emit({"b": 2})  # full — must be swallowed
    assert q.qsize() == 1


def test_queue_emitter_rejects_bad_sink():
    with pytest.raises(TypeError):
        QueueEmitter(object())


def test_webhook_emitter_rejects_non_http_url():
    with pytest.raises(ValueError):
        WebhookEmitter("ftp://nope.example.com")


def test_webhook_emitter_swallows_network_error(caplog):
    # Port 0 on an invalid host will fail fast.
    em = WebhookEmitter("http://127.0.0.1:1/never", timeout_s=0.1)
    with caplog.at_level(logging.WARNING, logger="ledgerproof.llamaindex"):
        em.emit({"x": 1})  # must not raise
