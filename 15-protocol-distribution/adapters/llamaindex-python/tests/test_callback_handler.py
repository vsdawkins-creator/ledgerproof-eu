"""End-to-end tests for the LedgerProof LlamaIndex callback handler.

These tests stand up a real ``CallbackManager`` and drive synthetic LLM /
QUERY events through it. We then assert on what the in-memory
``QueueEmitter`` sees — verifying:

  1. The handler emits at least one envelope per signed event.
  2. The signature actually verifies against the public key in the envelope.
  3. C7 is respected: the input payload object handed to ``on_event_end`` is
     not mutated (the LlamaIndex response is byte-for-byte unchanged).
  4. Stray ``on_event_end`` without a matching start is a no-op (no crash).
"""

from __future__ import annotations

import copy
import queue

import pytest

pytest.importorskip("llama_index.core.callbacks.base_handler")

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.callbacks.schema import CBEventType, EventPayload

from ledgerproof_llamaindex import (
    Ed25519Signer,
    LedgerProofCallbackHandler,
    QueueEmitter,
)


def _build(handler_kwargs=None):
    q: queue.Queue = queue.Queue()
    handler = LedgerProofCallbackHandler(
        deployer_id="acme-bank-eu",
        signer=Ed25519Signer.ephemeral(),
        emitter=QueueEmitter(q),
        model_provider="openai",
        model_name="gpt-4-test",
        **(handler_kwargs or {}),
    )
    manager = CallbackManager([handler])
    return manager, handler, q


def test_llm_event_emits_signed_receipt():
    manager, handler, q = _build()
    manager.start_trace(trace_id="t-1")
    eid = handler.on_event_start(
        CBEventType.LLM,
        payload={EventPayload.PROMPT: "What is your refund policy?"},
        event_id="e-llm-1",
    )
    handler.on_event_end(
        CBEventType.LLM,
        payload={EventPayload.RESPONSE: "Refunds within 30 days."},
        event_id=eid,
    )
    manager.end_trace(trace_id="t-1")

    env = q.get_nowait()
    assert env["envelope_version"] == "lpr/0.1"
    assert env["payload"]["schema_id"] == "rag_chatbot_session/v1"
    assert env["payload"]["deployer_id"] == "acme-bank-eu"
    assert env["signature"]["alg"] == "ed25519"


def test_signature_verifies_against_published_public_key():
    manager, handler, q = _build()
    manager.start_trace(trace_id="t-2")
    eid = handler.on_event_start(
        CBEventType.LLM,
        payload={EventPayload.PROMPT: "hi"},
        event_id="e-llm-2",
    )
    handler.on_event_end(CBEventType.LLM, payload={}, event_id=eid)
    manager.end_trace(trace_id="t-2")

    env = q.get_nowait()
    pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(env["signature"]["public_key"]))
    digest = bytes.fromhex(env["digest"])
    sig = bytes.fromhex(env["signature"]["sig"])
    # Will raise InvalidSignature on failure.
    pub.verify(sig, digest)


def test_query_event_emits_synthesized_response_receipt():
    manager, handler, q = _build()
    manager.start_trace(trace_id="t-3")
    eid = handler.on_event_start(
        CBEventType.QUERY,
        payload={EventPayload.QUERY_STR: "what is the SLA?"},
        event_id="evt-query-001",
    )

    class _Resp:
        def __str__(self):
            return "Our SLA is 99.9%."

        source_nodes = []

    handler.on_event_end(
        CBEventType.QUERY,
        payload={EventPayload.RESPONSE: _Resp()},
        event_id=eid,
    )
    manager.end_trace(trace_id="t-3")

    env = q.get_nowait()
    assert env["payload"]["schema_id"] == "rag_synthesized_response/v1"
    assert env["payload"]["query_hash"] != env["payload"]["response_hash"]


def test_c7_payload_is_not_mutated():
    manager, handler, q = _build()
    manager.start_trace(trace_id="t-4")
    end_payload = {EventPayload.RESPONSE: "answer"}
    snapshot = copy.deepcopy(end_payload)
    eid = handler.on_event_start(
        CBEventType.LLM,
        payload={EventPayload.PROMPT: "q"},
        event_id="e-llm-3",
    )
    handler.on_event_end(CBEventType.LLM, payload=end_payload, event_id=eid)
    manager.end_trace(trace_id="t-4")
    assert end_payload == snapshot


def test_stray_event_end_is_a_no_op():
    manager, handler, q = _build()
    # No matching start.
    handler.on_event_end(CBEventType.LLM, payload={}, event_id="ghost")
    assert q.empty()


def test_non_llm_non_query_events_do_not_emit():
    manager, handler, q = _build()
    eid = handler.on_event_start(
        CBEventType.EMBEDDING,
        payload={EventPayload.SERIALIZED: {"x": 1}},
        event_id="e-emb-1",
    )
    handler.on_event_end(CBEventType.EMBEDDING, payload={}, event_id=eid)
    assert q.empty()
