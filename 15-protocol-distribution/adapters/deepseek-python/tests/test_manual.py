"""Manual emit_receipt tests."""

import hashlib
import queue
from types import SimpleNamespace

from ledgerproof_deepseek import QueueEmitter, emit_receipt


def _fake_response(
    text="hi from deepseek",
    model="deepseek-chat",
    reasoning_content=None,
):
    message = SimpleNamespace(
        role="assistant", content=text, reasoning_content=reasoning_content
    )
    choice = SimpleNamespace(index=0, message=message, finish_reason="stop")
    return SimpleNamespace(id="ds-cmpl-99", model=model, choices=[choice])


def test_manual_emit_basic_receipt():
    q: queue.Queue = queue.Queue()
    resp = _fake_response()
    env = emit_receipt(
        resp,
        deployer_id="urn:eu:deployer:acme",
        messages=[{"role": "user", "content": "hello"}],
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["model_id"] == "deepseek-chat"
    assert env["receipt"]["model_provider"] == "deepseek"
    assert env["adapter"]["name"] == "ledgerproof-deepseek"
    assert q.get_nowait() == env


def test_manual_emit_auto_records_reasoning_for_reasoner_schema():
    q: queue.Queue = queue.Queue()
    resp = _fake_response(
        text="Final answer: 42",
        model="deepseek-reasoner",
        reasoning_content="step 1... step 2...",
    )
    env = emit_receipt(
        resp,
        deployer_id="urn:eu:deployer:acme",
        messages=[{"role": "user", "content": "compute"}],
        regulatory_context={"schema": "reasoning_trace/v1"},
        emitter=QueueEmitter(q),
    )
    expected_reasoning = hashlib.sha256(b"step 1... step 2...").hexdigest()
    assert env["receipt"]["schema_id"] == "reasoning_trace/v1"
    assert env["receipt"]["reasoning_sha256"] == expected_reasoning


def test_manual_emit_code_generation_schema_with_language():
    q: queue.Queue = queue.Queue()
    resp = _fake_response(
        text="def add(a, b): return a + b", model="deepseek-coder"
    )
    env = emit_receipt(
        resp,
        deployer_id="urn:eu:deployer:acme",
        messages=[{"role": "user", "content": "addition"}],
        regulatory_context={"schema": "code_generation/v1"},
        extra_fields={"programming_language": "python"},
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["schema_id"] == "code_generation/v1"
    assert env["receipt"]["content_modality"] == "code"
    assert env["receipt"]["programming_language"] == "python"


def test_manual_emit_swallows_emitter_failures():
    """C7: even manual emit must not propagate emitter errors."""

    class _Boom:
        def emit(self, env):
            raise RuntimeError("nope")

    resp = _fake_response()
    # Must not raise
    env = emit_receipt(
        resp,
        deployer_id="urn:eu:deployer:acme",
        messages=[{"role": "user", "content": "hi"}],
        emitter=_Boom(),
    )
    # Envelope is still returned for the caller to persist if they want
    assert env["adapter"]["name"] == "ledgerproof-deepseek"
