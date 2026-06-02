"""Pydantic schema validation + GDPR safety."""

import pytest

from ledgerproof_semantic_kernel.schema import (
    SCHEMAS,
    AgentFunctionInvocationReceipt,
    AzureEnterpriseSessionReceipt,
    ChatbotSessionReceipt,
    GeneratedContentReceipt,
    get_schema,
)


GOOD_HASH = "a" * 64


def test_chatbot_session_minimum_valid():
    r = ChatbotSessionReceipt(
        run_id="r1",
        timestamp_utc="2026-06-02T00:00:00.000000Z",
        deployer_id="acme-001",
        transcript_sha256=GOOD_HASH,
        model_identifier="gpt-4o",
    )
    assert r.schema_id == "chatbot_session/v1"
    assert r.disclosure_shown is True


def test_generated_content_minimum_valid():
    r = GeneratedContentReceipt(
        run_id="r1",
        timestamp_utc="2026-06-02T00:00:00.000000Z",
        deployer_id="acme-001",
        transcript_sha256=GOOD_HASH,
        model_identifier="gpt-4o",
        content_type="text/plain",
    )
    assert r.schema_id == "generated_content/v1"


def test_agent_function_invocation_minimum_valid():
    r = AgentFunctionInvocationReceipt(
        run_id="r1",
        timestamp_utc="2026-06-02T00:00:00.000000Z",
        deployer_id="acme-001",
        transcript_sha256=GOOD_HASH,
        plugin_name="weather",
        function_name="get_weather",
        argument_names=["city"],
        is_auto_invoked=True,
    )
    assert r.is_auto_invoked is True
    assert r.argument_names == ["city"]


def test_azure_enterprise_session_minimum_valid():
    r = AzureEnterpriseSessionReceipt(
        run_id="r1",
        timestamp_utc="2026-06-02T00:00:00.000000Z",
        deployer_id="acme-001",
        transcript_sha256=GOOD_HASH,
        model_identifier="gpt-4o",
        tenant_id="00000000-0000-0000-0000-000000000000",
        subscription_scope="sub/00000000-0000-0000-0000-000000000000",
        deployment_region="westeurope",
    )
    assert r.schema_id == "azure_enterprise_session/v1"


def test_email_rejected_in_deployer_id():
    with pytest.raises(ValueError):
        ChatbotSessionReceipt(
            run_id="r1",
            timestamp_utc="2026-06-02T00:00:00.000000Z",
            deployer_id="alice@corp.example",
            transcript_sha256=GOOD_HASH,
            model_identifier="gpt-4o",
        )


def test_email_rejected_in_user_principal_id():
    with pytest.raises(ValueError):
        AzureEnterpriseSessionReceipt(
            run_id="r1",
            timestamp_utc="2026-06-02T00:00:00.000000Z",
            deployer_id="acme-001",
            transcript_sha256=GOOD_HASH,
            model_identifier="gpt-4o",
            tenant_id="t1",
            subscription_scope="s1",
            deployment_region="westeurope",
            user_principal_id="alice@corp.example",
        )


def test_bad_transcript_hash_rejected():
    with pytest.raises(ValueError):
        ChatbotSessionReceipt(
            run_id="r1",
            timestamp_utc="2026-06-02T00:00:00.000000Z",
            deployer_id="acme-001",
            transcript_sha256="not-a-hash",
            model_identifier="gpt-4o",
        )


def test_get_schema_unknown():
    with pytest.raises(ValueError):
        get_schema("does-not-exist/v9")


def test_all_schemas_registered():
    assert set(SCHEMAS) == {
        "chatbot_session/v1",
        "generated_content/v1",
        "agent_function_invocation/v1",
        "azure_enterprise_session/v1",
    }
