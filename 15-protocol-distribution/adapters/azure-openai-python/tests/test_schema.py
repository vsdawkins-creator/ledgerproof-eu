"""Schema validation tests — including Azure-specific schemas + GDPR validators."""

import hashlib

import pytest
from pydantic import ValidationError

from ledgerproof_azure_openai.schema import (
    AzureAdAuthenticatedSessionV1,
    AzureEnterpriseSessionV1,
    ChatbotSessionV1,
    GeneratedContentV1,
    build_receipt,
)


_PROMPT_HASH = hashlib.sha256(b"hi").hexdigest()
_RESPONSE_HASH = hashlib.sha256(b"hello").hexdigest()
_TENANT_HASH = hashlib.sha256(b"tenant-guid").hexdigest()
_SUB_HASH = hashlib.sha256(b"subscription-guid").hexdigest()
_PRINCIPAL_HASH = hashlib.sha256(b"principal-oid").hexdigest()


def _base_fields(**overrides):
    fields = dict(
        deployer_id="urn:eu:deployer:contoso-bank",
        model_id="gpt4-prod",
        interaction_id="chatcmpl-123",
        prompt_sha256=_PROMPT_HASH,
        response_sha256=_RESPONSE_HASH,
    )
    fields.update(overrides)
    return fields


def _azure_fields(**overrides):
    fields = _base_fields(
        azure_endpoint="https://contoso-weu.openai.azure.com/",
        azure_deployment="gpt4-prod",
        azure_region="westeurope",
        api_version="2024-08-01-preview",
    )
    fields.update(overrides)
    return fields


# ---------------------------------------------------------------------------
# Baseline 50(1) + 50(2)
# ---------------------------------------------------------------------------


def test_chatbot_session_v1_happy_path():
    r = ChatbotSessionV1(**_base_fields())
    assert r.schema_id == "chatbot_session/v1"
    assert r.article_basis == "EU_AI_Act_Art_50_1"
    assert r.model_provider == "azure-openai"


def test_generated_content_v1_happy_path():
    r = GeneratedContentV1(**_base_fields(), content_modality="image")
    assert r.schema_id == "generated_content/v1"
    assert r.content_modality == "image"


# ---------------------------------------------------------------------------
# GDPR validators on user_pseudonym
# ---------------------------------------------------------------------------


def test_user_pseudonym_rejects_raw_email():
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(user_pseudonym="alice@example.com"))


def test_user_pseudonym_rejects_raw_ipv4():
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(user_pseudonym="user-192.168.1.42"))


def test_user_pseudonym_rejects_raw_phone():
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(user_pseudonym="caller +33 6 12 34 56 78"))


def test_user_pseudonym_accepts_hash():
    r = ChatbotSessionV1(
        **_base_fields(user_pseudonym=hashlib.sha256(b"alice").hexdigest())
    )
    assert r.user_pseudonym is not None


# ---------------------------------------------------------------------------
# Base validators
# ---------------------------------------------------------------------------


def test_invalid_prompt_hash_rejected():
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(prompt_sha256="not-a-hash"))


def test_deployer_id_must_be_urn():
    with pytest.raises(ValidationError):
        ChatbotSessionV1(**_base_fields(deployer_id="contoso-bank"))


# ---------------------------------------------------------------------------
# Azure enterprise session
# ---------------------------------------------------------------------------


def test_azure_enterprise_session_happy_path():
    r = AzureEnterpriseSessionV1(
        **_azure_fields(
            tenant_id_hash=_TENANT_HASH, subscription_id_hash=_SUB_HASH
        )
    )
    assert r.schema_id == "azure_enterprise_session/v1"
    assert r.azure_region == "westeurope"
    assert r.tenant_id_hash == _TENANT_HASH


def test_azure_endpoint_must_be_https_azure():
    with pytest.raises(ValidationError):
        AzureEnterpriseSessionV1(
            **_azure_fields(azure_endpoint="http://example.com/")
        )


def test_raw_tenant_guid_rejected():
    raw_guid = "12345678-1234-1234-1234-123456789abc"
    with pytest.raises(ValidationError) as exc:
        AzureEnterpriseSessionV1(**_azure_fields(tenant_id_hash=raw_guid))
    assert "Hash" in str(exc.value) or "hash" in str(exc.value)


def test_non_hex_tenant_hash_rejected():
    with pytest.raises(ValidationError):
        AzureEnterpriseSessionV1(**_azure_fields(tenant_id_hash="not-a-sha256"))


# ---------------------------------------------------------------------------
# Azure AD authenticated session
# ---------------------------------------------------------------------------


def test_azure_ad_authenticated_session_happy_path():
    r = AzureAdAuthenticatedSessionV1(
        **_azure_fields(
            azure_ad_principal_hash=_PRINCIPAL_HASH,
            azure_ad_principal_type="managed_identity",
            auth_method="managed_identity",
        )
    )
    assert r.azure_ad_principal_hash == _PRINCIPAL_HASH
    assert r.azure_ad_principal_type == "managed_identity"


def test_azure_ad_authenticated_session_rejects_raw_oid():
    raw_guid = "12345678-1234-1234-1234-123456789abc"
    with pytest.raises(ValidationError):
        AzureAdAuthenticatedSessionV1(
            **_azure_fields(azure_ad_principal_hash=raw_guid)
        )


def test_azure_ad_authenticated_session_requires_principal_hash():
    with pytest.raises(ValidationError):
        AzureAdAuthenticatedSessionV1(**_azure_fields())


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


def test_build_receipt_dispatch_azure_enterprise():
    r = build_receipt(
        "azure_enterprise_session/v1",
        **_azure_fields(tenant_id_hash=_TENANT_HASH),
    )
    assert isinstance(r, AzureEnterpriseSessionV1)


def test_build_receipt_unknown_schema():
    with pytest.raises(ValueError):
        build_receipt("nope/v1", **_base_fields())
