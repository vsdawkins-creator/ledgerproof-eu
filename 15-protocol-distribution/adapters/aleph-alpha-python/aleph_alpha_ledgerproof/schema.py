"""Receipt schemas with GDPR-aware validators.

Three schemas are exported:

* ``chatbot_session/v1``               — Article 50(1) natural-person interaction disclosure
* ``generated_content/v1``             — Article 50(2) synthetic-content marking
* ``on_prem_sovereign_deployment/v1``  — Article 50(1) variant for German / EU on-prem
  Aleph Alpha deployments. Captures hosting jurisdiction and operator attestation
  (strategic for BaFin / Bundesbank / BSI conversations).

GDPR notes
----------
None of these schemas accept raw prompts or completions. The wire payload only
ever carries *hashes* of the prompt / completion plus deployment metadata. This
keeps personal data out of the receipt itself and reduces the risk of the
receipt being reclassified as a personal-data processing record under GDPR.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


# --- Article 50 scope enum ---------------------------------------------------


class Article50Scope(str, Enum):
    """Sub-articles of EU AI Act Article 50 covered by this adapter."""

    PROVIDER_INTERACTION = "50(1)"
    DEPLOYER_GENERATED = "50(2)"
    DEEPFAKE_DISCLOSURE = "50(4)"


# --- Shared helpers ----------------------------------------------------------


_ISO_3166_ALPHA2 = re.compile(r"^[A-Z]{2}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _validate_hex64(value: str, field_name: str) -> str:
    if not _HEX64.match(value):
        raise ValueError(
            f"{field_name} must be a 64-char lowercase hex SHA-256 digest"
        )
    return value


def _validate_iso_alpha2(value: str) -> str:
    if not _ISO_3166_ALPHA2.match(value):
        raise ValueError(
            "jurisdiction must be ISO 3166-1 alpha-2 uppercase (e.g. 'DE', 'NL', 'FR')"
        )
    return value


class _BaseReceiptBody(BaseModel):
    """Shared fields. GDPR: hashes only — never raw content."""

    model_config = {"extra": "forbid"}

    schema_name: str = Field(..., description="Schema identifier, e.g. 'chatbot_session/v1'")
    article: Article50Scope = Field(..., description="EU AI Act Article 50 sub-article")
    prompt_sha256: str = Field(..., min_length=64, max_length=64)
    completion_sha256: str = Field(..., min_length=64, max_length=64)
    model: str = Field(..., min_length=1, max_length=200)
    model_version: Optional[str] = Field(default=None, max_length=200)
    ts_unix_ms: int = Field(..., ge=0)

    @field_validator("prompt_sha256", "completion_sha256")
    @classmethod
    def _check_hash(cls, v: str) -> str:
        return _validate_hex64(v, "hash")


# --- 50(1) chatbot session ---------------------------------------------------


class ChatbotSessionV1(_BaseReceiptBody):
    schema_name: Literal["chatbot_session/v1"] = "chatbot_session/v1"
    article: Literal[Article50Scope.PROVIDER_INTERACTION] = Article50Scope.PROVIDER_INTERACTION

    session_id_hash: str = Field(..., min_length=64, max_length=64)
    deployer_id: Optional[str] = Field(default=None, max_length=200)
    disclosure_shown: bool = Field(
        default=True,
        description="Whether an AI-interaction disclosure was presented to the user.",
    )

    @field_validator("session_id_hash")
    @classmethod
    def _hash_only(cls, v: str) -> str:
        return _validate_hex64(v, "session_id_hash")


# --- 50(2) generated content -------------------------------------------------


class GeneratedContentV1(_BaseReceiptBody):
    schema_name: Literal["generated_content/v1"] = "generated_content/v1"
    article: Literal[Article50Scope.DEPLOYER_GENERATED] = Article50Scope.DEPLOYER_GENERATED

    content_type: Literal["text", "summary", "translation", "code", "other"] = "text"
    marker_applied: bool = Field(
        default=False,
        description="Whether a machine-readable AI-generated marker was applied downstream.",
    )
    deployer_id: Optional[str] = Field(default=None, max_length=200)


# --- 50(1) variant: on-prem sovereign deployment -----------------------------


class OnPremSovereignDeploymentV1(_BaseReceiptBody):
    """On-premises sovereign deployment attestation.

    Strategic for German enterprise / BaFin-supervised institutions running
    Aleph Alpha Luminous models inside their own data centres. Captures
    hosting jurisdiction and operator identity so receipts form a verifiable
    chain proving an AI interaction never left a designated jurisdiction.
    """

    schema_name: Literal["on_prem_sovereign_deployment/v1"] = "on_prem_sovereign_deployment/v1"
    article: Literal[Article50Scope.PROVIDER_INTERACTION] = Article50Scope.PROVIDER_INTERACTION

    hosting_jurisdiction: str = Field(
        ...,
        description="ISO 3166-1 alpha-2 of the datacentre hosting the inference (e.g. 'DE').",
    )
    operator: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Legal name of the entity operating the on-prem deployment.",
    )
    sovereignty_attestation: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Operator-defined attestation token, e.g. 'on-prem-frankfurt-dc01'.",
    )
    data_residency_confirmed: bool = Field(default=True)
    egress_disabled: bool = Field(
        default=True,
        description="Operator asserts inbound/outbound egress to the public internet is disabled.",
    )

    @field_validator("hosting_jurisdiction")
    @classmethod
    def _jurisdiction(cls, v: str) -> str:
        return _validate_iso_alpha2(v.upper())


SCHEMA_REGISTRY = {
    "chatbot_session/v1": ChatbotSessionV1,
    "generated_content/v1": GeneratedContentV1,
    "on_prem_sovereign_deployment/v1": OnPremSovereignDeploymentV1,
}


def schema_for(name: str) -> type[_BaseReceiptBody]:
    if name not in SCHEMA_REGISTRY:
        raise KeyError(
            f"unknown schema {name!r}; supported: {sorted(SCHEMA_REGISTRY)}"
        )
    return SCHEMA_REGISTRY[name]
