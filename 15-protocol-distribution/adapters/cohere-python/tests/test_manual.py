"""Manual emit + helper tests."""

from __future__ import annotations

import hashlib
from types import SimpleNamespace

from ledgerproof_cohere import QueueEmitter, emit_receipt
from ledgerproof_cohere.manual import (
    build_disclosure_ref,
    build_model_ref,
    build_retrieved_document_refs,
    extract_assistant_text,
    extract_tool_uses,
)
from ledgerproof_cohere.signer import Ed25519Signer


def _fake_response(text="Hello.", with_tool_use=False):
    msg = SimpleNamespace(
        role="assistant",
        content=[SimpleNamespace(type="text", text=text)],
        tool_calls=None,
    )
    if with_tool_use:
        msg.tool_calls = [
            SimpleNamespace(
                id="tc_1",
                function=SimpleNamespace(name="lookup", arguments='{"k":"v"}'),
            )
        ]
    return SimpleNamespace(
        id="resp_m_001",
        model="command-a-03-2025",
        message=msg,
        finish_reason="COMPLETE",
        usage=SimpleNamespace(tokens=SimpleNamespace(input_tokens=5, output_tokens=8)),
    )


def test_emit_receipt_returns_signed_dict_and_emits():
    captured: list = []
    signed = emit_receipt(
        response=_fake_response(),
        deployer_id="acme-eu",
        signer=Ed25519Signer(),
        emitter=QueueEmitter(captured.append),
        user_message_text="hi",
    )
    assert signed["signature_alg"] == "ed25519"
    assert len(captured) == 1
    assert captured[0]["receipt"]["deployer_id"] == "acme-eu"


def test_extract_assistant_text_v2_shape():
    assert extract_assistant_text(_fake_response("hello world")) == "hello world"


def test_extract_assistant_text_dict_shape():
    response = {"message": {"content": [{"type": "text", "text": "Salut"}]}}
    assert extract_assistant_text(response) == "Salut"


def test_extract_assistant_text_none_safe():
    assert extract_assistant_text(None) is None


def test_extract_tool_uses_v2():
    refs = extract_tool_uses(_fake_response(with_tool_use=True))
    assert len(refs) == 1
    assert refs[0].tool_name == "lookup"
    assert refs[0].tool_call_id == "tc_1"


def test_build_model_ref_extracts_v2_tokens():
    mr = build_model_ref(_fake_response())
    assert mr.model_id == "command-a-03-2025"
    assert mr.response_id == "resp_m_001"
    assert mr.input_tokens == 5
    assert mr.output_tokens == 8
    assert mr.finish_reason == "COMPLETE"


def test_build_retrieved_document_refs_with_rerank():
    docs = [
        {"id": "a", "text": "first"},
        {"id": "b", "text": "second"},
    ]
    rerank = [
        SimpleNamespace(index=1, relevance_score=0.9),
        SimpleNamespace(index=0, relevance_score=0.4),
    ]
    refs = build_retrieved_document_refs(docs, rerank_results=rerank)
    assert len(refs) == 2
    assert refs[0].rerank_relevance_score == 0.4
    assert refs[1].rerank_relevance_score == 0.9
    # SHA-256 should match raw bytes.
    assert refs[0].sha256_hex == hashlib.sha256(b"first").hexdigest()


def test_build_disclosure_ref_hashes_text():
    text = "Sie chatten mit einer KI."
    ref = build_disclosure_ref(text, "de-DE", channel="chat-ui")
    assert ref.disclosure_sha256_hex == hashlib.sha256(text.encode()).hexdigest()
    assert ref.language_tag == "de-DE"
    assert ref.disclosure_byte_length == len(text.encode())
