"""Schema validation tests (incl. GDPR-flavoured constraints)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ledgerproof_aleph_alpha.schema import (
    Article50Scope,
    ChatbotSessionV1,
    GeneratedContentV1,
    OnPremSovereignDeploymentV1,
    schema_for,
)


_HASH = "0" * 64


def test_chatbot_session_minimal_ok():
    body = ChatbotSessionV1(
        prompt_sha256=_HASH,
        completion_sha256=_HASH,
        model="luminous-base",
        ts_unix_ms=1,
        session_id_hash=_HASH,
    )
    assert body.article is Article50Scope.PROVIDER_INTERACTION
    assert body.disclosure_shown is True


def test_generated_content_minimal_ok():
    body = GeneratedContentV1(
        prompt_sha256=_HASH,
        completion_sha256=_HASH,
        model="luminous-supreme",
        ts_unix_ms=1,
    )
    assert body.content_type == "text"
    assert body.marker_applied is False


def test_on_prem_sovereign_ok():
    body = OnPremSovereignDeploymentV1(
        prompt_sha256=_HASH,
        completion_sha256=_HASH,
        model="luminous-supreme-control",
        ts_unix_ms=1,
        hosting_jurisdiction="DE",
        operator="Acme Bank AG",
        sovereignty_attestation="on-prem-frankfurt-dc01",
    )
    assert body.hosting_jurisdiction == "DE"
    assert body.egress_disabled is True


def test_jurisdiction_must_be_iso_alpha2():
    with pytest.raises(ValidationError):
        OnPremSovereignDeploymentV1(
            prompt_sha256=_HASH,
            completion_sha256=_HASH,
            model="luminous-supreme-control",
            ts_unix_ms=1,
            hosting_jurisdiction="Germany",
            operator="X",
            sovereignty_attestation="y",
        )


def test_hash_must_be_64_hex():
    with pytest.raises(ValidationError):
        GeneratedContentV1(
            prompt_sha256="not-a-hash",
            completion_sha256=_HASH,
            model="luminous-base",
            ts_unix_ms=1,
        )


def test_schema_for_registry():
    assert schema_for("chatbot_session/v1") is ChatbotSessionV1
    assert schema_for("generated_content/v1") is GeneratedContentV1
    assert schema_for("on_prem_sovereign_deployment/v1") is OnPremSovereignDeploymentV1
    with pytest.raises(KeyError):
        schema_for("does/not/exist")


def test_extra_fields_forbidden_keeps_payload_minimal():
    """GDPR: no raw PII leaks through arbitrary extras."""
    with pytest.raises(ValidationError):
        GeneratedContentV1(
            prompt_sha256=_HASH,
            completion_sha256=_HASH,
            model="luminous-base",
            ts_unix_ms=1,
            user_email="alice@example.com",  # type: ignore[call-arg]
        )
