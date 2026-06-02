"""Tests for receipt schemas and GDPR PII validation."""

import pytest

from ledgerproof_haystack.schema import (
    SCHEMAS,
    build_receipt,
    get_schema,
)

_HEX64 = "a" * 64


def test_all_schemas_registered():
    for sid in [
        "rag_pipeline_session/v1",
        "generated_content/v1",
        "haystack_node_receipt/v1",
        "editorial_pipeline_review/v1",
    ]:
        assert sid in SCHEMAS
        assert get_schema(sid).__name__.endswith("V1")


def test_get_schema_unknown():
    with pytest.raises(KeyError):
        get_schema("nope/v1")


def test_generated_content_v1_happy_path():
    r = build_receipt(
        "generated_content/v1",
        receipt_id="r1",
        deployer="acme-de",
        key_id="abcdef0123456789",
        content_hash=_HEX64,
        content_length=42,
        model_id="gpt-4o-mini",
        generator_class="OpenAIGenerator",
    )
    assert r.schema_id == "generated_content/v1"
    assert r.protocol == "lpr/1"


def test_rag_pipeline_session_v1_rejects_short_hash():
    with pytest.raises(Exception):
        build_receipt(
            "rag_pipeline_session/v1",
            receipt_id="r1",
            deployer="acme-de",
            key_id="abcdef0123456789",
            pipeline_name="rag",
            pipeline_hash="short",
            component_count=3,
            retrieved_doc_count=5,
            query_hash=_HEX64,
            answer_hash=_HEX64,
            model_id="gpt-4o-mini",
        )


def test_editorial_pipeline_review_requires_reviewer_when_reviewed():
    with pytest.raises(Exception):
        build_receipt(
            "editorial_pipeline_review/v1",
            receipt_id="r1",
            deployer="acme-de",
            key_id="abcdef0123456789",
            article_subject_hash=_HEX64,
            public_interest_category="news",
            human_editorial_review=True,
            reviewer_id=None,
            review_decision="published",
            pipeline_name="editorial",
            generation_hash=_HEX64,
        )


def test_editorial_pipeline_review_happy_path():
    r = build_receipt(
        "editorial_pipeline_review/v1",
        receipt_id="r1",
        deployer="acme-de",
        key_id="abcdef0123456789",
        article_subject_hash=_HEX64,
        public_interest_category="news",
        human_editorial_review=True,
        reviewer_id="editor-42",
        review_decision="published",
        pipeline_name="editorial",
        generation_hash=_HEX64,
    )
    assert r.reviewer_id == "editor-42"


def test_gdpr_pii_email_blocked_without_lawful_basis():
    with pytest.raises(Exception):
        build_receipt(
            "haystack_node_receipt/v1",
            receipt_id="r1",
            deployer="acme-de",
            key_id="abcdef0123456789",
            node_name="leaks-email-jane.doe@example.com-here",
            node_class="Bad",
            input_hash=_HEX64,
            output_hash=_HEX64,
            latency_ms=12.3,
        )


def test_gdpr_pii_allowed_with_lawful_basis():
    r = build_receipt(
        "haystack_node_receipt/v1",
        receipt_id="r1",
        deployer="acme-de",
        key_id="abcdef0123456789",
        gdpr_lawful_basis="art-6-1-b-contract",
        node_name="processes-jane.doe@example.com",
        node_class="OK",
        input_hash=_HEX64,
        output_hash=_HEX64,
        latency_ms=12.3,
    )
    assert r.gdpr_lawful_basis == "art-6-1-b-contract"


def test_deployer_required_non_empty():
    with pytest.raises(Exception):
        build_receipt(
            "generated_content/v1",
            receipt_id="r1",
            deployer="   ",
            key_id="abcdef0123456789",
            content_hash=_HEX64,
            content_length=1,
            model_id="x",
            generator_class="y",
        )
