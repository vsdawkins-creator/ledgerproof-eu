"""Emitter behavior."""

import json
import queue

import pytest

from ledgerproof_semantic_kernel.emitter import (
    LogEmitter,
    QueueEmitter,
    WebhookEmitter,
)


def test_log_emitter_writes_jsonl(tmp_path):
    path = tmp_path / "sub" / "receipts.jsonl"
    emitter = LogEmitter(path)
    emitter.emit({"hello": "world"})
    emitter.emit({"a": 1})
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"hello": "world"}
    assert json.loads(lines[1]) == {"a": 1}


def test_queue_emitter_round_trip():
    e = QueueEmitter()
    e.emit({"x": 1})
    item = e.queue.get_nowait()
    assert item == {"x": 1}


def test_queue_emitter_uses_supplied_queue():
    q: "queue.Queue[dict]" = queue.Queue()
    e = QueueEmitter(q)
    e.emit({"y": 2})
    assert q.get_nowait() == {"y": 2}


def test_webhook_emitter_validates_scheme():
    with pytest.raises(ValueError):
        WebhookEmitter("ftp://example.com/receipts")


def test_webhook_emitter_swallows_errors():
    # Point at an unroutable port; should not raise.
    e = WebhookEmitter("http://127.0.0.1:1", timeout_seconds=0.05)
    e.emit({"x": 1})  # must return cleanly
