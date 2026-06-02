"""Receipt schemas — Pydantic v2 — Azure OpenAI flavor.

Four schemas, mapped to Article 50 scenarios + Azure-specific provenance:

- `chatbot_session/v1`               — Article 50(1): natural person interacting with an AI system
- `generated_content/v1`             — Article 50(2): synthetic/manipulated content
- `azure_enterprise_session/v1`      — Article 50(1) variant capturing Azure deployment + region +
                                       tenant + subscription provenance (recommended for FSI)
- `azure_ad_authenticated_session/v1`— Article 50(1) variant binding a hashed Azure AD principal

GDPR discipline:
  - Receipts MUST NOT carry plaintext PII.
  - `user_pseudonym` rejects raw email / IP / phone patterns.
  - `tenant_id_hash`, `subscription_id_hash`, `azure_ad_principal_hash` must be
    64-char hex SHA-256. Raw GUIDs are rejected — even an Azure tenant GUID is
    indirectly identifying and is subject to data-minimisation under GDPR Art.
    5(1)(c).
  - `azure_endpoint` is allowed because the resource URL is publicly inferable
    from the deployment-region pair and does not constitute personal data.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


_EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_hex64(v: str) -> bool:
    return bool(_HEX64_RE.match(v.lower()))


class _ReceiptBase(BaseModel):
    """Common fields across all Azure OpenAI receipt schemas."""

    schema_id: str
    timestamp: str = Field(default_factory=_utc_now_iso)
    deployer_id: str
    model_provider: Literal["azure-openai"] = "azure-openai"
    model_id: str
    interaction_id: str
    prompt_sha256: str
    response_sha256: str
    user_pseudonym: str | None = None
    jurisdiction: str = "EU"
    extra: dict[str, Any] = Field(default_factory=dict)

    @field_validator("user_pseudonym")
    @classmethod
    def _no_raw_pii(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return v
        if _EMAIL_RE.search(v):
            raise ValueError(
                "user_pseudonym must not contain raw email addresses. "
                "Hash or pseudonymize first (GDPR Art. 5(1)(c))."
            )
        if _IPV4_RE.search(v):
            raise ValueError(
                "user_pseudonym must not contain raw IPv4 addresses. "
                "Hash first (GDPR Art. 5(1)(c))."
            )
        if _PHONE_RE.search(v):
            raise ValueError(
                "user_pseudonym must not contain raw phone numbers. "
                "Hash first (GDPR Art. 5(1)(c))."
            )
        return v

    @field_validator("prompt_sha256", "response_sha256")
    @classmethod
    def _is_hex_sha256(cls, v: str) -> str:
        if len(v) != 64 or any(c not in "0123456789abcdef" for c in v.lower()):
            raise ValueError("must be a 64-char lowercase hex SHA-256")
        return v.lower()

    @field_validator("deployer_id")
    @classmethod
    def _is_urn(cls, v: str) -> str:
        if not v.startswith("urn:"):
            raise ValueError(
                "deployer_id should be a URN (e.g. 'urn:eu:deployer:contoso-bank')"
            )
        return v


# ---------------------------------------------------------------------------
# Article 50(1) baseline
# ---------------------------------------------------------------------------


class ChatbotSessionV1(_ReceiptBase):
    """Article 50(1): a natural person is interacting with an AI system."""

    schema_id: Literal["chatbot_session/v1"] = "chatbot_session/v1"
    article_basis: Literal["EU_AI_Act_Art_50_1"] = "EU_AI_Act_Art_50_1"
    disclosure_shown: bool = False


# ---------------------------------------------------------------------------
# Article 50(2): synthetic content
# ---------------------------------------------------------------------------


class GeneratedContentV1(_ReceiptBase):
    """Article 50(2): synthetically generated audio/image/video/text content."""

    schema_id: Literal["generated_content/v1"] = "generated_content/v1"
    article_basis: Literal["EU_AI_Act_Art_50_2"] = "EU_AI_Act_Art_50_2"
    content_modality: Literal["text", "image", "audio", "video"] = "text"
    machine_readable_marker: bool = True


# ---------------------------------------------------------------------------
# Azure enterprise session — strategic schema for FSI customers
# ---------------------------------------------------------------------------


class _AzureProvenanceMixin(BaseModel):
    """Fields capturing Azure-specific deployment provenance."""

    azure_endpoint: str  # e.g. https://contoso-weu.openai.azure.com/
    azure_deployment: str  # customer-chosen deployment name (not OpenAI model id)
    azure_region: str | None = None  # e.g. "westeurope", "francecentral"
    api_version: str | None = None  # e.g. "2024-08-01-preview"
    tenant_id_hash: str | None = None
    subscription_id_hash: str | None = None

    @field_validator("azure_endpoint")
    @classmethod
    def _endpoint_shape(cls, v: str) -> str:
        if not (v.startswith("https://") and ".openai.azure.com" in v):
            raise ValueError(
                "azure_endpoint must be an https Azure OpenAI resource URL "
                "(e.g. https://<resource>.openai.azure.com/)"
            )
        return v

    @field_validator("tenant_id_hash", "subscription_id_hash")
    @classmethod
    def _must_be_hashed(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return v
        if _GUID_RE.match(v):
            raise ValueError(
                "Raw Azure GUID detected. Hash with SHA-256 first (GDPR Art. "
                "5(1)(c) — data minimisation). Use "
                "hashlib.sha256(guid.encode()).hexdigest()."
            )
        if not _is_hex64(v):
            raise ValueError(
                "tenant_id_hash / subscription_id_hash must be 64-char lowercase "
                "hex SHA-256."
            )
        return v.lower()


class AzureEnterpriseSessionV1(_ReceiptBase, _AzureProvenanceMixin):
    """Article 50(1) variant binding full Azure deployment provenance.

    This is the schema you almost certainly want for an EU bank / insurer /
    asset manager running production Azure OpenAI workloads. It captures:

    - which Azure resource (endpoint URL → region)
    - which customer-named deployment (e.g. `gpt4-prod` vs `gpt4-shadow`)
    - which API version (preview vs GA)
    - which tenant + subscription, both hashed for GDPR

    Together, those answer "who, where, on whose contract" without leaking
    raw Azure identifiers.
    """

    schema_id: Literal["azure_enterprise_session/v1"] = "azure_enterprise_session/v1"
    article_basis: Literal["EU_AI_Act_Art_50_1"] = "EU_AI_Act_Art_50_1"
    disclosure_shown: bool = False


# ---------------------------------------------------------------------------
# Azure AD authenticated session
# ---------------------------------------------------------------------------


class AzureAdAuthenticatedSessionV1(_ReceiptBase, _AzureProvenanceMixin):
    """Article 50(1) variant when Azure AD (Entra ID) authentication is used.

    Captures a SHA-256 hash of the principal object ID (managed identity,
    service principal, or user OID). Binding the *hashed* OID lets auditors
    later prove a specific managed identity invoked a specific deployment
    without exposing the raw OID, which under EU guidance is treated as
    personal data when it identifies a natural-person user.
    """

    schema_id: Literal["azure_ad_authenticated_session/v1"] = (
        "azure_ad_authenticated_session/v1"
    )
    article_basis: Literal["EU_AI_Act_Art_50_1"] = "EU_AI_Act_Art_50_1"
    azure_ad_principal_hash: str
    azure_ad_principal_type: Literal[
        "user", "service_principal", "managed_identity", "unknown"
    ] = "unknown"
    auth_method: Literal["azure_ad_token", "managed_identity", "default_credential"] = (
        "azure_ad_token"
    )

    @field_validator("azure_ad_principal_hash")
    @classmethod
    def _principal_hash_shape(cls, v: str) -> str:
        if _GUID_RE.match(v):
            raise ValueError(
                "Raw Azure AD object ID detected. Hash with SHA-256 first."
            )
        if not _is_hex64(v):
            raise ValueError(
                "azure_ad_principal_hash must be 64-char lowercase hex SHA-256."
            )
        return v.lower()


SCHEMAS = {
    "chatbot_session/v1": ChatbotSessionV1,
    "generated_content/v1": GeneratedContentV1,
    "azure_enterprise_session/v1": AzureEnterpriseSessionV1,
    "azure_ad_authenticated_session/v1": AzureAdAuthenticatedSessionV1,
}


def build_receipt(schema_id: str, **fields: Any) -> _ReceiptBase:
    """Construct a receipt by schema_id."""
    cls = SCHEMAS.get(schema_id)
    if cls is None:
        raise ValueError(
            f"Unknown schema_id={schema_id!r}. Known: {list(SCHEMAS)}"
        )
    return cls(**fields)
