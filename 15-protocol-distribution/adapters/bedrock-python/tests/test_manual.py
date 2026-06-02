"""Manual emit_receipt + decorator + extraction helpers."""

from __future__ import annotations

import base64
import json

from ledgerproof_bedrock import (
    Ed25519Signer,
    QueueEmitter,
    emit_receipt,
    extract_assistant_text,
    extract_tool_uses,
    extract_user_message_text_from_converse,
    extract_user_message_text_from_invoke_body,
    lpr_track,
    make_eu_residency_attestation,
    verify,
)
from ledgerproof_bedrock.canonical import canonical_encode


def test_extract_assistant_text_claude_invoke_shape():
    resp = {"content": [{"type": "text", "text": "Hi"}, {"type": "text", "text": " there"}]}
    assert extract_assistant_text(resp) == "Hi there"


def test_extract_assistant_text_converse_shape():
    resp = {"output": {"message": {"content": [{"text": "Bonjour"}]}}}
    assert extract_assistant_text(resp) == "Bonjour"


def test_extract_assistant_text_llama():
    assert extract_assistant_text({"generation": "Salut"}) == "Salut"


def test_extract_assistant_text_titan():
    resp = {"results": [{"outputText": "Hallo"}]}
    assert extract_assistant_text(resp) == "Hallo"


def test_extract_assistant_text_mistral():
    resp = {"outputs": [{"text": "Ciao"}, {"text": "!"}]}
    assert extract_assistant_text(resp) == "Ciao!"


def test_extract_assistant_text_cohere():
    assert extract_assistant_text({"generations": [{"text": "Hola"}]}) == "Hola"


def test_extract_assistant_text_ai21():
    resp = {"completions": [{"data": {"text": "Hej"}}]}
    assert extract_assistant_text(resp) == "Hej"


def test_extract_assistant_text_none_safe():
    assert extract_assistant_text(None) is None
    assert extract_assistant_text(123) is None


def test_extract_tool_uses_converse():
    resp = {
        "output": {
            "message": {
                "content": [
                    {"text": "Let me look that up."},
                    {"toolUse": {"toolUseId": "tu-1", "name": "search", "input": {"q": "x"}}},
                ]
            }
        }
    }
    tools = extract_tool_uses(resp)
    assert len(tools) == 1
    assert tools[0].tool_name == "search"
    assert tools[0].tool_use_id == "tu-1"
    assert len(tools[0].input_sha256_hex) == 64


def test_extract_user_text_converse_messages():
    msgs = [
        {"role": "user", "content": [{"text": "first"}, {"text": "second"}]},
        {"role": "assistant", "content": [{"text": "reply"}]},
    ]
    assert extract_user_message_text_from_converse(msgs) == "first\nsecond"


def test_extract_user_text_invoke_body_claude():
    body = json.dumps(
        {"messages": [{"role": "user", "content": "hi there"}], "max_tokens": 5}
    )
    assert extract_user_message_text_from_invoke_body(body) == "hi there"


def test_extract_user_text_invoke_body_llama():
    body = json.dumps({"prompt": "Summarize this.", "max_gen_len": 50})
    assert extract_user_message_text_from_invoke_body(body) == "Summarize this."


def test_extract_user_text_invoke_body_titan():
    body = json.dumps({"inputText": "Generate something"})
    assert extract_user_message_text_from_invoke_body(body) == "Generate something"


def test_make_eu_residency_attestation_flags_eu_correctly():
    att = make_eu_residency_attestation("eu-west-1", sccs_in_place=True)
    assert att.eu_region is True
    assert att.attested_region == "eu-west-1"

    att2 = make_eu_residency_attestation("us-east-1")
    assert att2.eu_region is False


def test_emit_receipt_signs_and_verifies():
    captured = []
    signer = Ed25519Signer()
    response = {"output": {"message": {"content": [{"text": "Bonjour"}]}}}
    signed = emit_receipt(
        response,
        deployer_id="acme-eu",
        model_id="mistral.mistral-large-2402-v1:0",
        region="eu-west-1",
        user_message_text="salut",
        signer=signer,
        emitter=QueueEmitter(captured.append),
    )
    assert captured == [signed]
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_encode(signed["receipt"]), sig)
    assert signed["receipt"]["model"]["upstream_provider"] == "mistral"
    assert signed["receipt"]["model"]["region"] == "eu-west-1"


def test_lpr_track_sync_emits_on_call():
    captured = []

    @lpr_track(
        deployer_id="acme",
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        region="eu-central-1",
        user_message_kwarg="prompt",
        emitter=QueueEmitter(captured.append),
    )
    def call(prompt: str):
        return {"content": [{"type": "text", "text": "Hallo " + prompt}]}

    out = call(prompt="welt")
    assert out["content"][0]["text"] == "Hallo welt"
    assert len(captured) == 1
    r = captured[0]["receipt"]
    assert r["model"]["upstream_provider"] == "anthropic"
    assert r["model"]["region"] == "eu-central-1"


def test_lpr_track_emits_residency_when_provided():
    captured = []

    @lpr_track(
        deployer_id="acme",
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        region="eu-west-1",
        schema="eu_aws_data_residency/v1",
        residency={
            "attested_region": "eu-west-1",
            "eu_region": True,
            "cross_border_transfer": False,
        },
        emitter=QueueEmitter(captured.append),
    )
    def call():
        return {"content": [{"type": "text", "text": "ok"}]}

    call()
    r = captured[0]["receipt"]
    assert r["schema"] == "eu_aws_data_residency/v1"
    assert r["residency"]["eu_region"] is True
