"""Schema validation tests, including GDPR deployer_id validator."""
from __future__ import annotations

import pytest

from ledgerproof_vertexai.schema import (
    SCHEMA_NAMES,
    VertexContext,
    build_receipt_payload,
)


def _vc() -> VertexContext:
    return VertexContext(
        project="p",
        location="europe-west4",
        model="gemini-2.0-flash-001",
        region_of_inference_attestation="EU/NL",
    )


def test_all_schemas_listed():
    assert "chatbot_session/v1" in SCHEMA_NAMES
    assert "generated_content/v1" in SCHEMA_NAMES
    assert "eu_data_residency/v1" in SCHEMA_NAMES
    assert "gemini_function_call/v1" in SCHEMA_NAMES


def test_eu_data_residency_payload_captures_region():
    payload = build_receipt_payload(
        "eu_data_residency/v1",
        deployer_id="urn:lpr:deployer:acme",
        occurred_at="2026-06-01T12:00:00Z",
        vertex=_vc(),
        input_digest="a" * 64,
        output_digest="b" * 64,
    )
    assert payload["vertex"]["location"] == "europe-west4"
    assert payload["vertex"]["region_of_inference_attestation"] == "EU/NL"
    assert payload["article_50_paragraph"] == "50(1)"


def test_generated_content_50_2():
    payload = build_receipt_payload(
        "generated_content/v1",
        deployer_id="urn:lpr:deployer:x",
        occurred_at="2026-06-01T00:00:00Z",
        vertex=_vc(),
        input_digest="0" * 64,
        output_digest="1" * 64,
    )
    assert payload["article_50_paragraph"] == "50(2)"


def test_chatbot_session_requires_session_id():
    with pytest.raises(Exception):
        build_receipt_payload(
            "chatbot_session/v1",
            deployer_id="urn:lpr:deployer:x",
            occurred_at="2026-06-01T00:00:00Z",
            vertex=_vc(),
            # missing session_id / turn_index
            input_digest="0" * 64,
            output_digest="1" * 64,
        )


@pytest.mark.parametrize(
    "bad",
    [
        "alice@example.com",  # email
        "Alice Smith",  # whitespace / full name
        "",  # empty
        "x" * 300,  # too long
    ],
)
def test_gdpr_rejects_pii_deployer_id(bad: str):
    with pytest.raises(Exception):
        build_receipt_payload(
            "generated_content/v1",
            deployer_id=bad,
            occurred_at="2026-06-01T00:00:00Z",
            vertex=_vc(),
            input_digest="0" * 64,
            output_digest="1" * 64,
        )


def test_gdpr_accepts_urn_deployer_id():
    payload = build_receipt_payload(
        "generated_content/v1",
        deployer_id="urn:lpr:deployer:acme-bank-de",
        occurred_at="2026-06-01T00:00:00Z",
        vertex=_vc(),
        input_digest="0" * 64,
        output_digest="1" * 64,
    )
    assert payload["deployer_id"].startswith("urn:lpr:")


def test_unknown_schema_rejected():
    with pytest.raises(ValueError):
        build_receipt_payload(
            "made_up/v9",
            deployer_id="urn:lpr:deployer:x",
            occurred_at="2026-06-01T00:00:00Z",
            vertex=_vc(),
        )
