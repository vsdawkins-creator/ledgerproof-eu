"""Emitter tests."""

import io
import json
import queue

from ledgerproof_deepseek.emitter import (
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
    StderrEmitter,
    WebhookEmitter,
)


def test_log_emitter_writes_json_line():
    buf = io.StringIO()
    LogEmitter(stream=buf).emit({"hello": "world", "n": 1})
    out = buf.getvalue().strip()
    assert json.loads(out) == {"hello": "world", "n": 1}


def test_stderr_emitter_writes_json(capsys):
    StderrEmitter().emit({"a": 1})
    err = capsys.readouterr().err.strip()
    assert json.loads(err) == {"a": 1}


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


def test_multi_emitter_fans_out_to_all_children():
    q1: queue.Queue = queue.Queue()
    q2: queue.Queue = queue.Queue()
    MultiEmitter([QueueEmitter(q1), QueueEmitter(q2)]).emit({"x": 1})
    assert q1.get_nowait() == {"x": 1}
    assert q2.get_nowait() == {"x": 1}


def test_multi_emitter_isolates_child_failures():
    """One broken emitter must NOT prevent siblings from receiving — C7."""

    class _Boom:
        def emit(self, env):
            raise RuntimeError("boom")

    q: queue.Queue = queue.Queue()
    MultiEmitter([_Boom(), QueueEmitter(q)]).emit({"x": 1})
    # Survivor still received the envelope
    assert q.get_nowait() == {"x": 1}
