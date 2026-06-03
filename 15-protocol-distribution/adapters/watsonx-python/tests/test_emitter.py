"""Emitter behaviour, including failure isolation."""

from __future__ import annotations

import io
import json

from ledgerproof_watsonx.emitter import (
    IbmCloudLogsEmitter,
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
    em.emit({"hello": "watsonx"})
    assert out == [{"hello": "watsonx"}]


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


def test_ibm_cloud_logs_emitter_calls_ingest():
    lines: list[str] = []
    em = IbmCloudLogsEmitter(ingest_fn=lines.append)
    em.emit({"hello": "world"})
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed == {"hello": "world"}


def test_ibm_cloud_logs_emitter_swallows_ingest_errors():
    def bad_ingest(_):
        raise RuntimeError("logs-down")

    em = IbmCloudLogsEmitter(ingest_fn=bad_ingest)
    em.emit({"x": 1})  # must not raise
