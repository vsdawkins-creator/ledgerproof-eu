"""
Receipt schemas for Article 50 evidence (Qwen/DashScope adapter).

Four schemas:
  - chatbot_session/v1 — Article 50(1), covers direct chat interactions
  - generated_content/v1 — Article 50(2), covers synthetic content generation
  - multilingual_chinese_inference/v1 — Article 50(1) variant capturing
    Chinese-language disclosure facts + regional-endpoint routing for
    deployers using Qwen against Chinese-speaking end users or hybrid EU/CN
    audiences
  - cross_jurisdictional_routing/v1 — Article 50(1) variant capturing the
    deployer's choice of regional endpoint (Singapore / Hong Kong /
    international) to avoid mainland-China data residency

GDPR guardrail:
  - receipts MUST NOT contain raw prompt or response text by default; content is
    referenced via SHA-256 hashes only
  - free-text fields are length-bounded
  - identifier fields reject email-shaped strings (no PII leakage through
    deployer_id / user_session_id)
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

SchemaName = Literal[
    "chatbot_session/v1",
    "generated_content/v1",
    "multilingual_chinese_inference/v1",
    "cross_jurisdictional_routing/v1",
]

# Pattern allowing short bounded identifiers — no free-form PII.
_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:\-/+]{1,128}$")

# Crude but effective email shape detector. Reject anything that looks like
# an email address in identifier fields (GDPR direct-identifier guard).
_EMAIL_LIKE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _reject_email_shape(value: str, field_name: str) -> str:
    if _EMAIL_LIKE.match(value):
        raise ValueError(
            f"{field_name} {value!r} looks like an email address; "
            "use an opaque identifier instead — receipts must not carry direct "
            "personal identifiers (GDPR Art. 4(1) / Art. 5(1)(c) data minimisation)."
        )
    return value


class _Base(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class ModelRef(_Base):
    """Reference to the AI system used (Qwen-side)."""

    provider: Literal["qwen"] = "qwen"
    model_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    response_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    finish_reason: Annotated[str, StringConstraints(max_length=64)] | None = None
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)


class ContentRef(_Base):
    """SHA-256 reference to message content. Raw text NEVER stored in receipts."""

    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    role: Literal["user", "assistant", "system", "tool"]


class ToolUseRef(_Base):
    """Tool / function-call binding (Qwen function calling)."""

    tool_name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    tool_use_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    input_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    output_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None = None


class RegulatoryContext(_Base):
    """Deployer-supplied regulatory metadata."""

    article_50_paragraph: Literal["1", "2", "3", "4"]
    deployer_jurisdiction: Annotated[str, StringConstraints(min_length=2, max_length=8)]
    end_user_disclosure_made: bool
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None


# Endpoint-region literal — captures the realistic DashScope regional options.
EndpointRegion = Literal[
    "mainland-cn",
    "singapore",
    "hong-kong",
    "international",
    "unknown",
]


class ChineseInferenceAttestation(_Base):
    """
    Optional Chinese-origin AI inference attestation
    (multilingual_chinese_inference/v1).

    Captures deployer-asserted facts about Chinese-language Article 50 disclosure
    and the regional endpoint used to reach Qwen. This is descriptive metadata,
    not a certification — see C1 disclaimer.
    """

    chinese_disclosure_shown: bool
    chinese_disclosure_text_hash_sha256_hex: (
        Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None
    ) = None
    endpoint_region: EndpointRegion = "singapore"
    avoids_mainland_residency: bool = True
    provider_legal_entity: Annotated[str, StringConstraints(max_length=128)] | None = None


class CrossJurisdictionalRoute(_Base):
    """
    Optional cross-jurisdictional routing attestation
    (cross_jurisdictional_routing/v1).

    Captures the deployer's choice of regional endpoint and the cross-border
    transfer mechanism (if any) used. Useful for GDPR Schrems-II analysis
    documentation. Descriptive metadata only — not a regulatory finding.
    """

    endpoint_region: EndpointRegion
    endpoint_base_url: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    avoids_mainland_residency: bool
    transfer_mechanism: Annotated[str, StringConstraints(max_length=128)] | None = None
    provider_legal_entity: Annotated[str, StringConstraints(max_length=128)] | None = None
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None

    @field_validator("endpoint_base_url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("endpoint_base_url must start with http:// or https://")
        return v


class ReceiptV1(_Base):
    """Common envelope for all v1 receipts."""

    schema_name: SchemaName = Field(alias="schema")
    schema_version: Literal[1] = 1
    receipt_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    deployer_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    user_session_id: Annotated[str, StringConstraints(min_length=1, max_length=128)] | None = None
    issued_at: datetime = Field(default_factory=_utcnow)
    model: ModelRef
    content_refs: list[ContentRef]
    regulatory_context: RegulatoryContext
    chinese_inference: ChineseInferenceAttestation | None = None
    cross_jurisdictional_route: CrossJurisdictionalRoute | None = None
    tool_uses: list[ToolUseRef] = Field(default_factory=list)
    streaming: bool = False
    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-qwen"
    adapter_version: Annotated[str, StringConstraints(max_length=32)] = "0.1.0"

    @field_validator("deployer_id", "receipt_id")
    @classmethod
    def _validate_id_no_pii(cls, v: str, info) -> str:  # type: ignore[no-untyped-def]
        field_name = info.field_name
        _reject_email_shape(v, field_name)
        if not _ID_PATTERN.match(v):
            raise ValueError(
                f"{field_name}={v!r} contains disallowed characters; "
                "use only [A-Za-z0-9._:-/+] up to 128 chars"
            )
        return v

    @field_validator("user_session_id")
    @classmethod
    def _validate_optional_id_no_pii(cls, v: str | None, info) -> str | None:  # type: ignore[no-untyped-def]
        if v is None:
            return v
        field_name = info.field_name
        _reject_email_shape(v, field_name)
        if not _ID_PATTERN.match(v):
            raise ValueError(
                f"{field_name}={v!r} contains disallowed characters; "
                "use only [A-Za-z0-9._:-/+] up to 128 chars"
            )
        return v

    @field_validator("content_refs")
    @classmethod
    def _at_least_one_content_ref(cls, v: list[ContentRef]) -> list[ContentRef]:
        if not v:
            raise ValueError("receipt must reference at least one piece of content")
        return v

    def to_payload(self) -> dict[str, Any]:
        """Dump the receipt to a JSON/CBOR-ready dict with stable key ordering."""
        return self.model_dump(mode="json", by_alias=True, exclude_none=False)


def build_chatbot_session_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="chatbot_session/v1", **kwargs)


def build_generated_content_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="generated_content/v1", **kwargs)


def build_multilingual_chinese_inference_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="multilingual_chinese_inference/v1", **kwargs)


def build_cross_jurisdictional_routing_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="cross_jurisdictional_routing/v1", **kwargs)
