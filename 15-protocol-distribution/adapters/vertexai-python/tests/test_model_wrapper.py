"""GenerativeModel wrapper + chat wrapper tests, with mocked vertexai."""
from __future__ import annotations

import vertexai

from ledgerproof_vertexai import LedgerProofGenerativeModel, configure


def test_generate_content_emits_receipt_and_does_not_modify_response(configured):
    vertexai.init(project="acme-eu", location="europe-west4")
    model = LedgerProofGenerativeModel(
        "gemini-2.0-flash-001", lpr_schema="generated_content/v1"
    )
    resp = model.generate_content("Hello?")
    # C7: response unchanged
    assert resp.text == "vertex-says:Hello?"

    assert len(configured) == 1
    env = configured[0]
    assert env["protocol"] == "lpr/0.1"
    payload = env["payload"]
    assert payload["vertex"]["project"] == "acme-eu"
    assert payload["vertex"]["location"] == "europe-west4"
    assert payload["vertex"]["region_of_inference_attestation"] == "EU/NL"
    assert payload["schema"] == "generated_content/v1"
    assert payload["article_50_paragraph"] == "50(2)"


def test_eu_data_residency_schema_emits_region(configured):
    vertexai.init(project="bank-de", location="europe-west3")
    model = LedgerProofGenerativeModel(
        "gemini-2.0-flash-001", lpr_schema="eu_data_residency/v1"
    )
    model.generate_content("Was ist DORA?")
    payload = configured[0]["payload"]
    assert payload["schema"] == "eu_data_residency/v1"
    assert payload["vertex"]["location"] == "europe-west3"
    assert payload["vertex"]["region_of_inference_attestation"] == "EU/DE"
    assert payload["article_50_paragraph"] == "50(1)"


def test_streaming_does_not_mutate_chunks(configured):
    vertexai.init(project="p", location="europe-west4")
    model = LedgerProofGenerativeModel("gemini-2.0-flash-001")
    chunks = list(model.generate_content("Stream please.", stream=True))
    # C7: chunks are exactly what the underlying SDK produced.
    assert all(hasattr(c, "text") for c in chunks)
    # Receipt is emitted after the stream finishes.
    assert len(configured) == 1
    assert configured[0]["payload"]["schema"] == "generated_content/v1"


def test_chat_session_emits_one_receipt_per_turn(configured):
    vertexai.init(project="p", location="europe-west4")
    model = LedgerProofGenerativeModel("gemini-2.0-flash-001")
    chat = model.start_chat()
    chat.send_message("hi")
    chat.send_message("again")
    assert len(configured) == 2
    p0 = configured[0]["payload"]
    p1 = configured[1]["payload"]
    assert p0["schema"] == "chatbot_session/v1"
    assert p0["turn_index"] == 0
    assert p1["turn_index"] == 1
    assert p0["session_id"] == p1["session_id"]


def test_emitter_requires_deployer_id():
    vertexai.init(project="p", location="europe-west4")
    # Not calling configure(): no deployer_id → wrapper must swallow,
    # response must still be returned (C7).
    model = LedgerProofGenerativeModel("gemini-2.0-flash-001")
    resp = model.generate_content("hello")
    assert resp.text == "vertex-says:hello"
