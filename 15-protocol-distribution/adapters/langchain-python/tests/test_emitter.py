"""Emitter tests."""

import json
import queue

import pytest

from ledgerproof_langchain.emitter import LogEmitter, QueueEmitter, WebhookEmitter


_SAMPLE = {"body": {"schema_id": "chatbot_session/v1", "run_id": "abc"}, "alg": "Ed25519"}


def test_log_emitter_appends_jsonl(tmp_path):
    path = tmp_path / "out" / "receipts.jsonl"
    em = LogEmitter(path)
    em.emit(_SAMPLE)
    em.emit({**_SAMPLE, "extra": True})

    assert path.exists()
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    parsed = [json.loads(line) for line in lines]
    assert parsed[0]["body"]["run_id"] == "abc"
    assert parsed[1]["extra"] is True


def test_queue_emitter_pushes():
    em = QueueEmitter()
    em.emit(_SAMPLE)
    em.emit({"x": 1})
    assert em.queue.qsize() == 2
    first = em.queue.get_nowait()
    assert first["body"]["run_id"] == "abc"


def test_queue_emitter_accepts_external_queue():
    q: "queue.Queue[dict]" = queue.Queue()
    em = QueueEmitter(q)
    em.emit({"k": "v"})
    assert q.get_nowait() == {"k": "v"}


def test_webhook_emitter_rejects_bad_url():
    with pytest.raises(ValueError):
        WebhookEmitter("ftp://example.com/hook")


def test_webhook_emitter_swallows_network_error():
    # Use a URL that should not resolve. The emitter must not raise —
    # receipt emission failures are operational, not response-blocking.
    em = WebhookEmitter("http://127.0.0.1:1/lpr-test-nope", timeout_seconds=0.1)
    em.emit(_SAMPLE)  # must not raise
