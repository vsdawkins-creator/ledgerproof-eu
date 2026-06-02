"""
Receipt schemas for Article 50 evidence (AI21 adapter).

Four schemas:
  - chatbot_session/v1 — Article 50(1), covers direct chat interactions
  - generated_content/v1 — Article 50(2), covers synthetic content generation
  - long_context_inference/v1 — Article 50(1) variant capturing context-window
    utilization. AI21's Jamba 1.5 family ships up to 256k tokens of context;
    deployers exercising this surface (RAG over whole codebases, long legal
    review, multi-document analysis) get a dedicated schema that records the
    declared context length and effective token utilization.
  - jamba_hybrid_attribution/v1 — Article 50(1) variant capturing Mamba /
    Transformer hybrid architecture attestation. Jamba's hybrid SSM + attention
    architecture has different latency / throughput / memory characteristics
    than pure-Transformer models; this schema lets deployers record the
    architectural family of the model used, in case downstream conformity
    work needs that signal.

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
    "long_context_inference/v1",
    "jamba_hybrid_attribution/v1",
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
    """Reference to the AI system used (AI21-side)."""

    provider: Literal["ai21"] = "ai21"
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
    """Tool / function-call binding (AI21 function calling, OpenAI-compatible)."""

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


class LongContextAttestation(_Base):
    """
    Optional long-context attestation block (long_context_inference/v1).

    Captures declared and effective use of Jamba's long-context window.
    Descriptive metadata only — see C1 disclaimer.
    """

    declared_context_window: int = Field(
        ge=1,
        description="Model's declared maximum context length, e.g. 262144 for Jamba 1.5 Large.",
    )
    effective_input_tokens: int = Field(
        ge=0,
        description="Tokens actually consumed by the input on this call.",
    )
    long_context_workload: Annotated[str, StringConstraints(max_length=64)] | None = Field(
        default=None,
        description="Free-form workload tag (e.g. 'rag', 'legal-review', 'multi-doc-summary').",
    )
    truncation_applied: bool = False


class JambaHybridAttestation(_Base):
    """
    Optional Mamba / Transformer hybrid architecture attestation block
    (jamba_hybrid_attribution/v1).

    Captures the architectural family of the AI21 model used. Descriptive
    metadata only — this is NOT a certification of any model property, and
    AI21 Labs has not endorsed this schema.
    """

    architecture_family: Annotated[
        str, StringConstraints(min_length=1, max_length=64)
    ] = "mamba-transformer-hybrid"
    model_variant: Annotated[str, StringConstraints(min_length=1, max_length=64)]
    parameter_class: Annotated[str, StringConstraints(max_length=32)] | None = None
    attention_layer_ratio: Annotated[str, StringConstraints(max_length=32)] | None = Field(
        default=None,
        description="Optional human-readable summary of attention vs SSM layer ratio.",
    )


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
    long_context: LongContextAttestation | None = None
    jamba_hybrid: JambaHybridAttestation | None = None
    tool_uses: list[ToolUseRef] = Field(default_factory=list)
    streaming: bool = False
    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-ai21"
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


def build_long_context_inference_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="long_context_inference/v1", **kwargs)


def build_jamba_hybrid_attribution_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="jamba_hybrid_attribution/v1", **kwargs)
