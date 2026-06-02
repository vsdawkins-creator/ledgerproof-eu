"""Manual emit_receipt() tests including Azure provenance routing."""

from __future__ import annotations

import hashlib
import queue
from types import SimpleNamespace

import pytest

from ledgerproof_azure_openai import QueueEmitter, emit_receipt


_TENANT_HASH = hashlib.sha256(b"t").hexdigest()
_PRINCIPAL_HASH = hashlib.sha256(b"p").hexdigest()


def _fake_resp(text: str = "hello", id_: str = "chatcmpl-1"):
    msg = SimpleNamespace(role="assistant", content=text)
    choice = SimpleNamespace(index=0, message=msg, finish_reason="stop")
    return SimpleNamespace(id=id_, model="gpt-4o-2024-08-06", choices=[choice])


def test_emit_receipt_baseline():
    q: queue.Queue = queue.Queue()
    env = emit_receipt(
        _fake_resp(),
        deployer_id="urn:eu:deployer:contoso-bank",
        messages=[{"role": "user", "content": "hi"}],
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["schema_id"] == "chatbot_session/v1"
    assert q.get_nowait() == env


def test_emit_receipt_azure_enterprise_requires_endpoint():
    with pytest.raises(ValueError):
        emit_receipt(
            _fake_resp(),
            deployer_id="urn:eu:deployer:contoso-bank",
            messages=[{"role": "user", "content": "hi"}],
            regulatory_context={"schema": "azure_enterprise_session/v1"},
            # no azure_endpoint
        )


def test_emit_receipt_azure_enterprise_happy_path():
    q: queue.Queue = queue.Queue()
    env = emit_receipt(
        _fake_resp(),
        deployer_id="urn:eu:deployer:contoso-bank",
        messages=[{"role": "user", "content": "hi"}],
        regulatory_context={"schema": "azure_enterprise_session/v1"},
        azure_endpoint="https://contoso-frc.openai.azure.com/",
        azure_deployment="gpt4-prod",
        api_version="2024-08-01-preview",
        tenant_id_hash=_TENANT_HASH,
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["azure_region"] == "francecentral"
    assert env["receipt"]["azure_deployment"] == "gpt4-prod"
    assert env["receipt"]["tenant_id_hash"] == _TENANT_HASH


def test_emit_receipt_azure_ad_requires_principal():
    with pytest.raises(ValueError):
        emit_receipt(
            _fake_resp(),
            deployer_id="urn:eu:deployer:contoso-bank",
            messages=[{"role": "user", "content": "hi"}],
            regulatory_context={
                "schema": "azure_ad_authenticated_session/v1",
                "azure_endpoint": "https://contoso-weu.openai.azure.com/",
            },
        )


def test_emit_receipt_azure_ad_happy_path():
    q: queue.Queue = queue.Queue()
    env = emit_receipt(
        _fake_resp(),
        deployer_id="urn:eu:deployer:contoso-bank",
        messages=[{"role": "user", "content": "hi"}],
        regulatory_context={
            "schema": "azure_ad_authenticated_session/v1",
            "azure_endpoint": "https://contoso-weu.openai.azure.com/",
            "api_version": "2024-08-01-preview",
            "azure_ad_principal_type": "service_principal",
            "auth_method": "azure_ad_token",
        },
        azure_deployment="gpt4-prod",
        azure_ad_principal_hash=_PRINCIPAL_HASH,
        emitter=QueueEmitter(q),
    )
    assert env["receipt"]["azure_ad_principal_hash"] == _PRINCIPAL_HASH
    assert env["receipt"]["azure_ad_principal_type"] == "service_principal"
