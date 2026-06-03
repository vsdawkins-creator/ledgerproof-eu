"""Schema validation, provider inference, EU region helpers, Granite detection."""

from __future__ import annotations

import pytest

from ledgerproof_watsonx.schema import (
    EU_WATSONX_REGIONS,
    ContentRef,
    DataResidencyAttestation,
    ModelRef,
    OpenWeightsAttestation,
    ReceiptV1,
    RegulatoryContext,
    build_chatbot_session_receipt,
    build_eu_residency_receipt,
    build_generated_content_receipt,
    build_granite_open_model_receipt,
    infer_provider,
    is_eea_or_adjacent,
    is_eu_region,
    is_granite_open_model,
    region_from_watsonx_url,
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
    assert infer_provider("ibm/granite-3-8b-instruct") == "ibm"
    assert infer_provider("meta-llama/llama-3-1-70b-instruct") == "meta"
    assert infer_provider("mistralai/mistral-large") == "mistral"
    assert infer_provider("google/flan-ul2") == "google"
    assert infer_provider("unknown-thing") == "unknown"
    assert infer_provider("") == "unknown"


def test_is_granite_open_model():
    assert is_granite_open_model("ibm/granite-3-8b-instruct")
    assert is_granite_open_model("ibm/granite-13b-chat-v2")
    assert is_granite_open_model("ibm/granite-20b-code-instruct")
    assert is_granite_open_model("IBM/GRANITE-3.1-8B-INSTRUCT")  # case-insensitive
    assert not is_granite_open_model("meta-llama/llama-3-1-70b-instruct")
    assert not is_granite_open_model("ibm/slate-30m-english-rtrvr")
    assert not is_granite_open_model("")


def test_is_eu_region_strict_eu_only():
    # eu-de = EU (Frankfurt) → True
    assert is_eu_region("eu-de")
    # eu-gb = post-Brexit UK → NOT EU
    assert not is_eu_region("eu-gb")
    assert not is_eu_region("us-south")
    assert not is_eu_region(None)
    assert not is_eu_region("")
    assert "eu-de" in EU_WATSONX_REGIONS


def test_is_eea_or_adjacent_includes_uk():
    assert is_eea_or_adjacent("eu-de")
    assert is_eea_or_adjacent("eu-gb")
    assert not is_eea_or_adjacent("us-south")


def test_region_from_watsonx_url():
    assert region_from_watsonx_url("https://eu-de.ml.cloud.ibm.com") == "eu-de"
    assert region_from_watsonx_url("https://us-south.ml.cloud.ibm.com/v1/x") == "us-south"
    assert region_from_watsonx_url("https://example.com") is None
    assert region_from_watsonx_url(None) is None


def test_receipt_serialises_with_schema_alias():
    r = build_chatbot_session_receipt(
        receipt_id="r-1",
        deployer_id="acme",
        model=ModelRef(
            upstream_provider="ibm",
            model_id="ibm/granite-3-8b-instruct",
            response_id="resp-1",
            region="eu-de",
            project_id="11111111-2222-3333-4444-555555555555",
            is_open_weights=True,
        ),
        content_refs=_content_refs(),
        regulatory_context=_reg(),
    )
    payload = r.to_payload()
    assert payload["schema"] == "chatbot_session/v1"
    assert payload["schema_version"] == 1
    assert payload["model"]["provider"] == "watsonx"
    assert payload["model"]["upstream_provider"] == "ibm"
    assert payload["model"]["region"] == "eu-de"
    assert payload["model"]["project_id"] == "11111111-2222-3333-4444-555555555555"
    assert payload["model"]["is_open_weights"] is True


def test_eu_residency_schema_with_attestation():
    att = DataResidencyAttestation(
        attested_region="eu-de",
        eu_region=True,
        cross_border_transfer=False,
        sccs_in_place=True,
        tenant_id="acme-de-tenant-hash",
    )
    r = build_eu_residency_receipt(
        receipt_id="r-3",
        deployer_id="acme",
        model=ModelRef(
            upstream_provider="ibm",
            model_id="ibm/granite-3-8b-instruct",
            response_id="resp-3",
            region="eu-de",
            project_id="11111111-2222-3333-4444-555555555555",
        ),
        content_refs=_content_refs(),
        regulatory_context=_reg(),
        residency=att,
    )
    payload = r.to_payload()
    assert payload["schema"] == "eu_data_residency/v1"
    assert payload["residency"]["eu_region"] is True
    assert payload["residency"]["tenant_id"] == "acme-de-tenant-hash"


def test_granite_open_model_schema():
    ow = OpenWeightsAttestation(
        model_family="ibm-granite",
        license_spdx="Apache-2.0",
        weights_url="https://huggingface.co/ibm-granite/granite-3.0-8b-instruct",
        reproducible=True,
    )
    r = build_granite_open_model_receipt(
        receipt_id="r-4",
        deployer_id="acme",
        model=ModelRef(
            upstream_provider="ibm",
            model_id="ibm/granite-3-8b-instruct",
            response_id="resp-4",
            region="eu-de",
            is_open_weights=True,
        ),
        content_refs=_content_refs(),
        regulatory_context=_reg(),
        open_weights=ow,
    )
    payload = r.to_payload()
    assert payload["schema"] == "granite_open_model/v1"
    assert payload["open_weights"]["license_spdx"] == "Apache-2.0"


def test_invalid_deployer_id_rejected():
    with pytest.raises(Exception):
        ReceiptV1(
            schema="chatbot_session/v1",
            receipt_id="r-x",
            deployer_id="bad id with spaces",
            model=ModelRef(model_id="m", response_id="r"),
            content_refs=_content_refs(),
            regulatory_context=_reg(),
        )


def test_invalid_project_id_rejected():
    with pytest.raises(Exception):
        ModelRef(
            model_id="ibm/granite-3-8b-instruct",
            response_id="r",
            project_id="not a uuid!",
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
        model=ModelRef(model_id="ibm/granite-3-8b-instruct", response_id="r"),
        content_refs=_content_refs(),
        regulatory_context=_reg(),
    )
    assert r.to_payload()["schema"] == "generated_content/v1"
