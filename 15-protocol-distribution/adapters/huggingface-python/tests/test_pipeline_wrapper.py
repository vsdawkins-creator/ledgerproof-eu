"""Tests for LedgerProofPipeline (transformers.Pipeline wrapper) with mocks."""

from __future__ import annotations

import hashlib
import queue
from types import SimpleNamespace

from ledgerproof_huggingface import LedgerProofPipeline, QueueEmitter


class _FakePipeline:
    """Mimics enough of transformers.Pipeline for tests — no torch required."""

    def __init__(self, output, *, task="text-generation", device="cpu",
                 model_name="meta-llama/Llama-3.1-8B-Instruct"):
        self._output = output
        self.task = task
        self.device = device
        self.model = SimpleNamespace(name_or_path=model_name)

    def __call__(self, prompt, **kwargs):
        return self._output


def test_pipeline_wrapper_emits_local_inference_receipt():
    output = [{"generated_text": "Hello, world!"}]
    pipe = _FakePipeline(output)

    q: queue.Queue = queue.Queue()
    lp = LedgerProofPipeline(
        pipe,
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
    )

    result = lp("Hello,")
    assert result is output

    envelope = q.get_nowait()
    assert envelope["receipt"]["schema_id"] == "local_inference/v1"
    assert envelope["receipt"]["framework"] == "transformers"
    assert envelope["receipt"]["task"] == "text-generation"
    assert envelope["receipt"]["device"] == "cpu"
    assert envelope["receipt"]["model_id"] == "meta-llama/Llama-3.1-8B-Instruct"
    assert isinstance(envelope["receipt"]["host_environment"], dict)
    assert "hostname" in envelope["receipt"]["host_environment"]

    expected = hashlib.sha256(b"Hello, world!").hexdigest()
    assert envelope["receipt"]["response_sha256"] == expected
    expected_prompt = hashlib.sha256(b"Hello,").hexdigest()
    assert envelope["receipt"]["prompt_sha256"] == expected_prompt


def test_pipeline_wrapper_chat_format_output():
    # text-generation in chat-template mode returns a list of message dicts
    output = [
        {
            "generated_text": [
                {"role": "user", "content": "hi"},
                {"role": "assistant", "content": "hello back"},
            ]
        }
    ]
    pipe = _FakePipeline(output)
    q: queue.Queue = queue.Queue()
    lp = LedgerProofPipeline(
        pipe,
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(q),
    )

    lp([{"role": "user", "content": "hi"}])
    envelope = q.get_nowait()
    # Hash concatenates the role contents we saw
    expected = hashlib.sha256(b"hihello back").hexdigest()
    assert envelope["receipt"]["response_sha256"] == expected


def test_pipeline_wrapper_response_returned_unmodified():
    """C7: the pipeline output is returned exactly as-is, identity preserved."""
    output = [{"generated_text": "verbatim"}]
    pipe = _FakePipeline(output)
    lp = LedgerProofPipeline(
        pipe,
        deployer_id="urn:eu:deployer:acme",
        emitter=QueueEmitter(),
    )
    result = lp("x")
    assert result is output  # identity, not just equality


def test_pipeline_wrapper_does_not_raise_on_emit_failure():
    class _BoomEmitter:
        def emit(self, envelope):
            raise RuntimeError("boom")

    pipe = _FakePipeline([{"generated_text": "ok"}])
    lp = LedgerProofPipeline(
        pipe,
        deployer_id="urn:eu:deployer:acme",
        emitter=_BoomEmitter(),
    )
    # Must not raise — C7 discipline
    assert lp("x") == [{"generated_text": "ok"}]


def test_pipeline_wrapper_accepts_chatbot_schema_override():
    pipe = _FakePipeline([{"generated_text": "ok"}])
    q: queue.Queue = queue.Queue()
    lp = LedgerProofPipeline(
        pipe,
        deployer_id="urn:eu:deployer:acme",
        regulatory_context={"schema": "chatbot_session/v1"},
        emitter=QueueEmitter(q),
    )
    lp("hi")
    envelope = q.get_nowait()
    assert envelope["receipt"]["schema_id"] == "chatbot_session/v1"
