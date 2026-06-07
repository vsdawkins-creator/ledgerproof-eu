"""
Receipt schemas for Article 50 evidence (Mistral adapter).

Three schemas:
  - chatbot_session/v1 — Article 50(1), covers direct chat interactions
  - generated_content/v1 — Article 50(2), covers synthetic content generation
  - eu_sovereign_ai_session/v1 — Article 50(1) variant capturing EU-sovereign AI
    provider attribution. Strategic positioning for Mistral as a French / EU
    headquartered model provider: receipts can record whether the inference
    happened in the EU, on EU-operated infrastructure, under EU jurisdiction.

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
    "eu_sovereign_ai_session/v1",
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
    """Reference to the AI system used (Mistral-side)."""

    provider: Literal["mistral"] = "mistral"
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
    """Tool / function-call binding (Mistral function calling)."""

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


class EuSovereigntyAttestation(_Base):
    """
    Optional EU-sovereign AI attestation block (eu_sovereign_ai_session/v1).

    Captures deployer-asserted facts about the residency, control plane, and
    legal jurisdiction of the AI inference. This is descriptive metadata, not
    a certification — see C1 disclaimer.
    """

    inference_region: Annotated[str, StringConstraints(min_length=2, max_length=16)]
    eu_data_residency: bool
    eu_operated_infrastructure: bool
    provider_eu_headquartered: bool = True  # default true for Mistral
    provider_legal_entity: Annotated[str, StringConstraints(max_length=128)] | None = None
    transfer_mechanism: Annotated[str, StringConstraints(max_length=64)] | None = None


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
    eu_sovereignty: EuSovereigntyAttestation | None = None
    tool_uses: list[ToolUseRef] = Field(default_factory=list)
    streaming: bool = False
    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-mistral"
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


def build_eu_sovereign_ai_session_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="eu_sovereign_ai_session/v1", **kwargs)
