"""Manual emit_receipt + decorator + extraction helpers."""

from __future__ import annotations

import base64
import json

from ledgerproof_watsonx import (
    Ed25519Signer,
    QueueEmitter,
    emit_receipt,
    extract_assistant_text,
    extract_tool_uses,
    extract_user_message_text,
    extract_user_prompt_from_generate,
    lpr_track,
    make_eu_residency_attestation,
    make_granite_attestation,
    verify,
)
from ledgerproof_watsonx.canonical import canonical_encode


def test_extract_assistant_text_chat_shape():
    resp = {
        "choices": [
            {"message": {"role": "assistant", "content": "Hallo Welt"}, "finish_reason": "stop"}
        ]
    }
    assert extract_assistant_text(resp) == "Hallo Welt"


def test_extract_assistant_text_chat_block_list_shape():
    resp = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "Bon"}, {"type": "text", "text": "jour"}],
                }
            }
        ]
    }
    assert extract_assistant_text(resp) == "Bonjour"


def test_extract_assistant_text_generate_text():
    assert extract_assistant_text({"generated_text": "Salut"}) == "Salut"


def test_extract_assistant_text_generate_text_results():
    resp = {"results": [{"generated_text": "Hallo"}, {"generated_text": " du"}]}
    assert extract_assistant_text(resp) == "Hallo du"


def test_extract_assistant_text_none_safe():
    assert extract_assistant_text(None) is None
    assert extract_assistant_text(123) is None


def test_extract_tool_uses_chat_shape():
    resp = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": "search", "arguments": '{"q":"x"}'},
                        }
                    ],
                }
            }
        ]
    }
    tools = extract_tool_uses(resp)
    assert len(tools) == 1
    assert tools[0].tool_name == "search"
    assert tools[0].tool_use_id == "call_1"
    assert len(tools[0].input_sha256_hex) == 64


def test_extract_user_message_text_chat():
    msgs = [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "reply"},
        {"role": "user", "content": [{"text": "second"}]},
    ]
    assert extract_user_message_text(msgs) == "first\nsecond"


def test_extract_user_prompt_from_generate():
    assert extract_user_prompt_from_generate("hello") == "hello"
    assert extract_user_prompt_from_generate(["a", "b"]) == "a\nb"


def test_make_eu_residency_attestation_flags_eu_correctly():
    att = make_eu_residency_attestation(
        "eu-de", project_id="11111111-2222", tenant_id="t-hash", sccs_in_place=True
    )
    assert att.eu_region is True
    assert att.attested_region == "eu-de"
    assert att.tenant_id == "t-hash"

    # eu-gb is NOT EU post-Brexit
    att_gb = make_eu_residency_attestation("eu-gb")
    assert att_gb.eu_region is False

    # us-south is obviously not EU
    att_us = make_eu_residency_attestation("us-south")
    assert att_us.eu_region is False


def test_make_granite_attestation_defaults_hf_url():
    att = make_granite_attestation(model_id="ibm/granite-3-8b-instruct")
    assert att.license_spdx == "Apache-2.0"
    assert att.model_family == "ibm-granite"
    assert att.weights_url and "huggingface.co" in att.weights_url


def test_emit_receipt_signs_and_verifies():
    captured = []
    signer = Ed25519Signer()
    response = {
        "id": "chatcmpl-abc",
        "model": "ibm/granite-3-8b-instruct",
        "choices": [
            {"message": {"role": "assistant", "content": "Bonjour"}, "finish_reason": "stop"}
        ],
        "usage": {"prompt_tokens": 4, "completion_tokens": 1},
    }
    signed = emit_receipt(
        response,
        deployer_id="acme-eu",
        model_id="ibm/granite-3-8b-instruct",
        region="eu-de",
        project_id="11111111-2222-3333-4444-555555555555",
        user_message_text="salut",
        signer=signer,
        emitter=QueueEmitter(captured.append),
    )
    assert captured == [signed]
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical_encode(signed["receipt"]), sig)
    r = signed["receipt"]
    assert r["model"]["upstream_provider"] == "ibm"
    assert r["model"]["region"] == "eu-de"
    assert r["model"]["is_open_weights"] is True
    assert r["model"]["input_tokens"] == 4
    assert r["model"]["output_tokens"] == 1


def test_emit_receipt_granite_schema_auto_fills_attestation():
    captured = []
    response = {"choices": [{"message": {"content": "hi"}}]}
    signed = emit_receipt(
        response,
        deployer_id="acme",
        model_id="ibm/granite-3-8b-instruct",
        schema="granite_open_model/v1",
        emitter=QueueEmitter(captured.append),
    )
    r = signed["receipt"]
    assert r["schema"] == "granite_open_model/v1"
    assert r["open_weights"]["license_spdx"] == "Apache-2.0"


def test_lpr_track_sync_emits_on_call():
    captured = []

    @lpr_track(
        deployer_id="acme",
        model_id="ibm/granite-3-8b-instruct",
        region="eu-de",
        project_id="11111111-2222-3333-4444-555555555555",
        user_message_kwarg="prompt",
        emitter=QueueEmitter(captured.append),
    )
    def call(prompt: str):
        return {"choices": [{"message": {"content": "Hallo " + prompt}}]}

    out = call(prompt="welt")
    assert out["choices"][0]["message"]["content"] == "Hallo welt"
    assert len(captured) == 1
    r = captured[0]["receipt"]
    assert r["model"]["upstream_provider"] == "ibm"
    assert r["model"]["region"] == "eu-de"
    assert r["model"]["project_id"] == "11111111-2222-3333-4444-555555555555"


def test_lpr_track_emits_residency_when_provided():
    captured = []

    @lpr_track(
        deployer_id="acme",
        model_id="ibm/granite-3-8b-instruct",
        region="eu-de",
        schema="eu_data_residency/v1",
        residency={
            "attested_region": "eu-de",
            "eu_region": True,
            "cross_border_transfer": False,
            "tenant_id": "acme-hash",
        },
        emitter=QueueEmitter(captured.append),
    )
    def call():
        return {"choices": [{"message": {"content": "ok"}}]}

    call()
    r = captured[0]["receipt"]
    assert r["schema"] == "eu_data_residency/v1"
    assert r["residency"]["eu_region"] is True
    assert r["residency"]["tenant_id"] == "acme-hash"
