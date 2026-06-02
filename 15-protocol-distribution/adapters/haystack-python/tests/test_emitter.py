"""Tests for side-channel emitters."""

import json
from pathlib import Path

from ledgerproof_haystack.emitter import (
    CallableEmitter,
    FileEmitter,
    JSONLEmitter,
    MemoryEmitter,
)


def _env(rid="r1"):
    return {
        "receipt": {"receipt_id": rid, "schema_id": "x/v1"},
        "signature_b64": "AAA",
    }


def test_memory_emitter_collects():
    e = MemoryEmitter()
    e.emit(_env("a"))
    e.emit(_env("b"))
    assert len(e) == 2
    assert e.records[0]["receipt"]["receipt_id"] == "a"
    e.clear()
    assert len(e) == 0


def test_file_emitter_writes_cbor(tmp_path: Path):
    e = FileEmitter(tmp_path)
    e.emit(_env("xyz"))
    files = list(tmp_path.glob("*.cbor"))
    assert len(files) == 1
    assert files[0].read_bytes()  # non-empty


def test_jsonl_emitter_appends(tmp_path: Path):
    p = tmp_path / "receipts.jsonl"
    e = JSONLEmitter(p)
    e.emit(_env("one"))
    e.emit(_env("two"))
    lines = p.read_text().strip().splitlines()
    assert len(lines) == 2
    parsed = [json.loads(line) for line in lines]
    assert parsed[0]["receipt"]["receipt_id"] == "one"


def test_callable_emitter():
    captured = []
    e = CallableEmitter(captured.append)
    e.emit(_env("c1"))
    assert len(captured) == 1
    assert captured[0]["receipt"]["receipt_id"] == "c1"
