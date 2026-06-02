"""Schema validation, provider inference, EU region helpers."""

from __future__ import annotations

import pytest

from ledgerproof_bedrock.schema import (
    EU_AWS_REGIONS,
    ContentRef,
    DataResidencyAttestation,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    build_chatbot_session_receipt,
    build_cross_provider_receipt,
    build_eu_residency_receipt,
    build_generated_content_receipt,
    infer_provider,
    is_eu_region,
)


def _reg() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="DE",
        end_user_disclosure_made=True,
    )


def _content_refs() -> list[ContentRef]:
    return [
        ContentRef(sha256_hex="a" * 64, byte_length=10, role="user"),
        ContentRef(sha256_hex="b" * 64, byte_length=20, role="assistant"),
    ]


def test_infer_provider_known_prefixes():
    assert infer_provider("anthropic.claude-3-5-sonnet-20240620-v1:0") == "anthropic"
    assert infer_provider("meta.llama3-70b-instruct-v1:0") == "meta"
    assert infer_provider("mistral.mistral-large-2402-v1:0") == "mistral"
    assert infer_provider("amazon.titan-text-express-v1") == "amazon"
    assert infer_provider("cohere.command-r-v1:0") == "cohere"
    assert infer_provider("ai21.j2-ultra-v1") == "ai21"
    assert infer_provider("stability.stable-diffusion-xl-v1") == "stability"
    assert infer_provider("unknown-model") == "unknown"
    assert infer_provider("") == "unknown"


def test_is_eu_region():
    for region in ["eu-west-1", "eu-central-1", "eu-north-1", "eu-south-2"]:
        assert is_eu_region(region)
    assert not is_eu_region("us-east-1")
    assert not is_eu_region(None)
    assert not is_eu_region("")
    # EU_AWS_REGIONS sanity check.
    assert "eu-west-1" in EU_AWS_REGIONS


def test_receipt_serialises_with_schema_alias():
    r = build_chatbot_session_receipt(
        receipt_id="r-1",
        deployer_id="acme",
        model=ModelRef(
            upstream_provider="anthropic",
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            response_id="resp-1",
            region="eu-west-1",
        ),
        content_refs=_content_refs(),
        regulatory_context=_reg(),
    )
    payload = r.to_payload()
    assert payload["schema"] == "chatbot_session/v1"
    assert payload["schema_version"] == 1
    assert payload["model"]["provider"] == "bedrock"
    assert payload["model"]["upstream_provider"] == "anthropic"
    assert payload["model"]["region"] == "eu-west-1"


def test_cross_provider_schema_round_trips():
    r = build_cross_provider_receipt(
        receipt_id="r-2",
        deployer_id="acme",
        model=ModelRef(
            upstream_provider="meta",
            model_id="meta.llama3-70b-instruct-v1:0",
            response_id="resp-2",
            region="eu-central-1",
        ),
        content_refs=_content_refs(),
        regulatory_context=_reg(),
    )
    assert r.to_payload()["schema"] == "bedrock_cross_provider/v1"


def test_eu_residency_schema_with_attestation():
    att = DataResidencyAttestation(
        attested_region="eu-west-1",
        eu_region=True,
        cross_border_transfer=False,
        sccs_in_place=True,
    )
    r = build_eu_residency_receipt(
        receipt_id="r-3",
        deployer_id="acme",
        model=ModelRef(
            upstream_provider="anthropic",
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            response_id="resp-3",
            region="eu-west-1",
        ),
        content_refs=_content_refs(),
        regulatory_context=_reg(),
        residency=att,
    )
    payload = r.to_payload()
    assert payload["schema"] == "eu_aws_data_residency/v1"
    assert payload["residency"]["eu_region"] is True


def test_invalid_deployer_id_rejected():
    with pytest.raises(Exception):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="r-4",
            deployer_id="bad id with spaces",
            model=ModelRef(
                model_id="m",
                response_id="r",
            ),
            content_refs=_content_refs(),
            regulatory_context=_reg(),
        )


def test_receipt_requires_content_ref():
    with pytest.raises(Exception):
        ReceiptV1(
            schema="generated_content/v1",
            receipt_id="r-5",
            deployer_id="acme",
            model=ModelRef(model_id="m", response_id="r"),
            content_refs=[],
            regulatory_context=_reg(),
        )


def test_generated_content_schema():
    r = build_generated_content_receipt(
        receipt_id="r-6",
        deployer_id="acme",
        model=ModelRef(model_id="stability.stable-diffusion-xl-v1", response_id="r"),
        content_refs=_content_refs(),
        regulatory_context=_reg(),
    )
    assert r.to_payload()["schema"] == "generated_content/v1"
