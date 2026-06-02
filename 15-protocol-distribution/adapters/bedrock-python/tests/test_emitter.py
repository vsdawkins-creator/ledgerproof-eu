"""Emitter behaviour, including failure isolation."""

from __future__ import annotations

import io
import json

from ledgerproof_bedrock.emitter import (
    CloudWatchEmitter,
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
)


def test_log_emitter_writes_json_to_stream():
    buf = io.StringIO()
    em = LogEmitter(stream=buf)
    em.emit({"a": 1, "b": [1, 2]})
    parsed = json.loads(buf.getvalue().strip())
    assert parsed == {"a": 1, "b": [1, 2]}


def test_queue_emitter_dispatches_to_callable():
    out = []
    em = QueueEmitter(out.append)
    em.emit({"hello": "bedrock"})
    assert out == [{"hello": "bedrock"}]


def test_queue_emitter_swallows_sink_errors():
    def bad_sink(_):
        raise RuntimeError("boom")

    em = QueueEmitter(bad_sink)
    em.emit({"x": 1})  # must not raise


def test_multi_emitter_fans_out():
    out1, out2 = [], []
    em = MultiEmitter(QueueEmitter(out1.append), QueueEmitter(out2.append))
    em.emit({"k": "v"})
    assert out1 == [{"k": "v"}]
    assert out2 == [{"k": "v"}]


def test_multi_emitter_isolates_failures():
    out = []

    class _Boom:
        def emit(self, _):
            raise RuntimeError("nope")

    em = MultiEmitter(_Boom(), QueueEmitter(out.append))
    em.emit({"k": "v"})
    assert out == [{"k": "v"}]


def test_cloudwatch_emitter_calls_put_log_events():
    calls = []

    class _Logs:
        def put_log_events(self, **kwargs):
            calls.append(kwargs)

    em = CloudWatchEmitter(
        logs_client=_Logs(),
        log_group="/lpr/receipts",
        log_stream="prod",
    )
    em.emit({"hello": "world"})
    assert len(calls) == 1
    assert calls[0]["logGroupName"] == "/lpr/receipts"
    assert calls[0]["logStreamName"] == "prod"
    assert "message" in calls[0]["logEvents"][0]


def test_cloudwatch_emitter_swallows_client_errors():
    class _Logs:
        def put_log_events(self, **kwargs):
            raise RuntimeError("kms-down")

    em = CloudWatchEmitter(logs_client=_Logs(), log_group="g", log_stream="s")
    em.emit({"x": 1})  # must not raise
