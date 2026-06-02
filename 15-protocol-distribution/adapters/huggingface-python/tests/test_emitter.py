"""Emitter tests."""

import io
import json
import queue

from ledgerproof_huggingface.emitter import LogEmitter, QueueEmitter, WebhookEmitter


def test_log_emitter_writes_json_line():
    buf = io.StringIO()
    LogEmitter(stream=buf).emit({"hello": "world", "n": 1})
    out = buf.getvalue().strip()
    assert json.loads(out) == {"hello": "world", "n": 1}


def test_queue_emitter_pushes_envelope():
    q: queue.Queue = queue.Queue()
    QueueEmitter(q).emit({"x": 1})
    assert q.get_nowait() == {"x": 1}


def test_queue_emitter_default_constructs_queue():
    emitter = QueueEmitter()
    emitter.emit({"y": 2})
    assert emitter.q.get_nowait() == {"y": 2}


def test_webhook_emitter_swallows_failures():
    """C7: receipt emission failures must never raise into caller path."""
    e = WebhookEmitter(url="http://127.0.0.1:1/never-listens", timeout=0.05)
    # Should not raise even though the URL is unreachable.
    e.emit({"x": 1})
