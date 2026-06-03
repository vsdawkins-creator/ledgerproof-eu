"""
Receipt schemas for Article 50 evidence (Codestral adapter, code-specific).

Four schemas:
  - chatbot_session/v1            — Article 50(1), code-chatbot interactions
  - generated_code/v1             — Article 50(2), synthetic code output
                                    carries language, line_count, has_security_pattern
  - fim_completion/v1             — Article 50(2), fill-in-the-middle code
                                    carries prefix/suffix hashes + middle hash
  - safety_critical_code_review/v1 — Article 50(4), editorial-control attestation
                                    when generated code passes documented human
                                    review before deployment

GDPR guardrails:
  - receipts MUST NOT contain raw prompt, suffix, generated code, or review notes;
    content is referenced via SHA-256 hashes only
  - free-text fields are length-bounded
  - identifier fields (deployer_id, user_session_id, reviewer_id) reject
    email-shaped strings (no direct-identifier leakage)
  - has_security_pattern is a single boolean — no CVE / line numbers / stack
    traces are carried in the receipt

C1 reminder:
  - These schemas do NOT confer any safety, security, or fitness-for-purpose
    certification of the reviewed code. They record deployer-asserted facts about
    a review step.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

SchemaName = Literal[
    "chatbot_session/v1",
    "generated_code/v1",
    "fim_completion/v1",
    "safety_critical_code_review/v1",
]

# Pattern allowing short bounded identifiers — no free-form PII.
_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:\-/+]{1,128}$")

# Crude but effective email shape detector. Reject anything that looks like
# an email address in identifier fields (GDPR direct-identifier guard).
_EMAIL_LIKE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

# Allowed programming language identifiers in generated_code receipts.
# Conservative whitelist; deployers may extend by setting `language="other"`
# and recording the actual language out-of-band.
_LANGUAGE_PATTERN = re.compile(r"^[a-z0-9+\-#]{1,32}$")


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
    """Reference to the AI system used (Codestral-side)."""

    provider: Literal["mistral-codestral"] = "mistral-codestral"
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
    role: Literal["user", "assistant", "system", "tool", "prefix", "suffix", "middle"]


class ToolUseRef(_Base):
    """Tool / function-call binding."""

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


class GeneratedCodeAttributes(_Base):
    """
    Code-specific metadata for generated_code/v1 and fim_completion/v1 schemas.

    All fields are deployer-asserted descriptive metadata. `has_security_pattern`
    is intentionally a single boolean — receipts do NOT carry CVE numbers,
    vulnerable line numbers, or any other detail that could leak source
    structure or facilitate attack-surface mapping.
    """

    language: Annotated[str, StringConstraints(min_length=1, max_length=32)] = "unknown"
    line_count: int = Field(ge=0, default=0)
    has_security_pattern: bool = False
    static_analyser: Annotated[str, StringConstraints(max_length=64)] | None = None

    @field_validator("language")
    @classmethod
    def _normalise_language(cls, v: str) -> str:
        v = v.lower()
        if v == "unknown" or v == "other":
            return v
        if not _LANGUAGE_PATTERN.match(v):
            raise ValueError(
                f"language {v!r} must match {_LANGUAGE_PATTERN.pattern} "
                "or be 'unknown' / 'other'"
            )
        return v


class FimPositions(_Base):
    """
    Position metadata for fill-in-the-middle completions.

    Hashes are stored on the parent receipt's content_refs (roles `prefix`,
    `suffix`, `middle`). This block only carries the byte lengths so the
    relative size of prefix/middle/suffix is auditable without the raw text.
    """

    prefix_byte_length: int = Field(ge=0)
    suffix_byte_length: int = Field(ge=0)
    middle_byte_length: int = Field(ge=0)


class SafetyCriticalReview(_Base):
    """
    Editorial-control attestation block for safety_critical_code_review/v1.

    Records the deployer-asserted fact that generated code passed a documented
    human review *before* deployment (Article 50(4) editorial-control carve-out).

    This is NOT a certification that the reviewed code is safe — it is evidence
    that a review step happened. Liability remains with the deployer.
    """

    reviewer_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    review_outcome: Literal["approved", "approved_with_changes", "rejected"]
    review_completed_at: datetime
    review_policy_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    deployed: bool = False
    deployment_target: Annotated[str, StringConstraints(max_length=128)] | None = None

    @field_validator("reviewer_id")
    @classmethod
    def _reviewer_id_no_pii(cls, v: str) -> str:
        _reject_email_shape(v, "reviewer_id")
        if not _ID_PATTERN.match(v):
            raise ValueError(
                f"reviewer_id={v!r} contains disallowed characters; "
                "use only [A-Za-z0-9._:-/+] up to 128 chars"
            )
        return v


class ReceiptV1(_Base):
    """Common envelope for all v1 Codestral receipts."""

    schema_name: SchemaName = Field(alias="schema")
    schema_version: Literal[1] = 1
    receipt_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    deployer_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    user_session_id: Annotated[str, StringConstraints(min_length=1, max_length=128)] | None = None
    issued_at: datetime = Field(default_factory=_utcnow)
    model: ModelRef
    content_refs: list[ContentRef]
    regulatory_context: RegulatoryContext
    code_attributes: GeneratedCodeAttributes | None = None
    fim_positions: FimPositions | None = None
    safety_review: SafetyCriticalReview | None = None
    tool_uses: list[ToolUseRef] = Field(default_factory=list)
    streaming: bool = False
    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-mistral-codestral"
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


def build_generated_code_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="generated_code/v1", **kwargs)


def build_fim_completion_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="fim_completion/v1", **kwargs)


def build_safety_critical_code_review_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="safety_critical_code_review/v1", **kwargs)
