"""
Receipt schemas for Article 50 evidence (Gemini / Google AI variant).

Four schemas:
  - chatbot_session/v1 — Article 50(1), direct chat interactions
  - generated_content/v1 — Article 50(2), synthetic content generation
  - multimodal_generation/v1 — Article 50(2) variant, captures input
    modality types (text/image/audio/video) for transparency on multimodal
    generation contexts
  - gemini_function_call/v1 — Article 50(1) variant for tool-use /
    function-call invocations through the Gemini SDK

GDPR guardrail: receipts MUST NOT contain raw prompt or response text by
default. Content is referenced via SHA-256 hashes only. Free-text fields are
length-bounded. Identifier validators reject email-shaped strings to discourage
embedding personal data.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

SchemaName = Literal[
    "chatbot_session/v1",
    "generated_content/v1",
    "multimodal_generation/v1",
    "gemini_function_call/v1",
]

# Pattern allowing short bounded identifiers — no free-form PII.
_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:\-/+]{1,128}$")

# Used by GDPR guard validators on deployer_id / session_id.
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

Modality = Literal["text", "image", "audio", "video", "file"]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class _Base(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class ModelRef(_Base):
    """Reference to the AI system used (Gemini-side)."""

    provider: Literal["google-ai"] = "google-ai"
    model_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    response_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    finish_reason: Annotated[str, StringConstraints(max_length=64)] | None = None
    prompt_token_count: int | None = Field(default=None, ge=0)
    candidates_token_count: int | None = Field(default=None, ge=0)
    total_token_count: int | None = Field(default=None, ge=0)


class ContentRef(_Base):
    """SHA-256 reference to message content. Raw text NEVER stored in receipts."""

    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    role: Literal["user", "model", "system", "tool"]
    modality: Modality = "text"


class FunctionCallRef(_Base):
    """Tool / function-call binding for gemini_function_call receipts."""

    function_name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    args_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    response_sha256_hex: (
        Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None
    ) = None


class RegulatoryContext(_Base):
    """Deployer-supplied regulatory metadata."""

    article_50_paragraph: Literal["1", "2", "3", "4"]
    deployer_jurisdiction: Annotated[str, StringConstraints(min_length=2, max_length=8)]
    end_user_disclosure_made: bool
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None


def _reject_emails(value: str, field_name: str) -> str:
    if _EMAIL_PATTERN.match(value):
        raise ValueError(
            f"{field_name} {value!r} looks like an email address; "
            "GDPR guard rejects email-shaped identifiers to discourage "
            "embedding personal data in receipts"
        )
    if not _ID_PATTERN.match(value):
        raise ValueError(
            f"{field_name} {value!r} contains disallowed characters; "
            "use only [A-Za-z0-9._:-/+] up to 128 chars"
        )
    return value


class ReceiptV1(_Base):
    """Common envelope for all v1 Gemini receipts."""

    schema_name: SchemaName = Field(alias="schema")
    schema_version: Literal[1] = 1
    receipt_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    deployer_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    session_id: (
        Annotated[str, StringConstraints(min_length=1, max_length=128)] | None
    ) = None
    issued_at: datetime = Field(default_factory=_utcnow)
    model: ModelRef
    content_refs: list[ContentRef]
    regulatory_context: RegulatoryContext
    function_calls: list[FunctionCallRef] = Field(default_factory=list)
    input_modalities: list[Modality] = Field(default_factory=lambda: ["text"])
    streaming: bool = False
    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-google-ai"
    adapter_version: Annotated[str, StringConstraints(max_length=32)] = "0.1.0"

    @field_validator("deployer_id")
    @classmethod
    def _validate_deployer_id(cls, v: str) -> str:
        return _reject_emails(v, "deployer_id")

    @field_validator("session_id")
    @classmethod
    def _validate_session_id(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _reject_emails(v, "session_id")

    @field_validator("receipt_id")
    @classmethod
    def _validate_receipt_id(cls, v: str) -> str:
        if not _ID_PATTERN.match(v):
            raise ValueError(
                f"receipt_id {v!r} contains disallowed characters; "
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
        return self.model_dump(mode="json", by_alias=True)


def build_chatbot_session_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="chatbot_session/v1", **kwargs)


def build_generated_content_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="generated_content/v1", **kwargs)


def build_multimodal_generation_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="multimodal_generation/v1", **kwargs)


def build_function_call_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="gemini_function_call/v1", **kwargs)
