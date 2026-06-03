"""
Receipt schemas for Article 50 evidence.

Four schemas:
  - chatbot_session/v1 — Article 50(1), direct chat / assistant interactions.
  - generated_content/v1 — Article 50(2), synthetic content generation.
  - multimodal_native_inference/v1 — Article 50(1) variant that captures mixed
    text/image/audio/video INPUTS in a single receipt. Reka models are
    multimodal-native, so a single inference may bind several input modalities
    simultaneously; the receipt records each modality as a separate ContentRef.
  - video_understanding/v1 — Article 50(1) for video-input inferences. Strategic
    surface for Article 50(4) public-interest video labeling once the upstream
    inference is bound to a downstream provenance pipeline. THIS RECEIPT DOES
    NOT BY ITSELF CONSTITUTE 50(4) COMPLIANCE; it is an evidence-layer hash
    binding of the inference event, nothing more.

GDPR guardrails:
  - Receipts MUST NOT contain raw prompt or response text by default. Content
    is referenced via SHA-256 hashes only.
  - Receipts MUST NOT contain raw media bytes. Media is referenced via
    SHA-256 hashes plus MIME type and byte length.
  - Free-text fields are length-bounded.
  - Identifier fields use a strict character pattern that prevents free-form PII.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

SchemaName = Literal[
    "chatbot_session/v1",
    "generated_content/v1",
    "multimodal_native_inference/v1",
    "video_understanding/v1",
]

# Pattern allowing short bounded identifiers — no free-form PII.
_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:\-/+@]{1,128}$")

# Allowed modality tags for multimodal receipts.
Modality = Literal["text", "image", "audio", "video"]

# Allowed MIME-type top-level categories for media refs.
_MIME_PATTERN = re.compile(r"^[a-z]+/[A-Za-z0-9.+\-]+$")


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
    """Reference to the AI system used (Reka-side)."""

    provider: Literal["reka"] = "reka"
    model_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    response_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    finish_reason: Annotated[str, StringConstraints(max_length=64)] | None = None
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)


class ContentRef(_Base):
    """SHA-256 reference to message content. Raw text NEVER stored in receipts."""

    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    role: Literal["user", "assistant", "system", "tool"]
    modality: Modality = "text"
    mime_type: Annotated[str, StringConstraints(max_length=128)] | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    # Optional GDPR-safe descriptor: pixel dims for images, sample rate for audio, etc.
    # Free-text bounded; deployers SHOULD NOT include PII here.
    media_descriptor: Annotated[str, StringConstraints(max_length=128)] | None = None

    @field_validator("mime_type")
    @classmethod
    def _validate_mime(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not _MIME_PATTERN.match(v):
            raise ValueError(
                f"mime_type {v!r} is not a well-formed RFC 6838 type/subtype value"
            )
        return v


class MediaRef(_Base):
    """
    Hash reference to an input media artefact (image, audio clip, video).

    Used by multimodal_native_inference/v1 and video_understanding/v1 to bind
    the inference to the exact bytes that were submitted to Reka, without
    storing the bytes themselves (GDPR Art. 5(1)(c) data minimisation).
    """

    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    modality: Modality
    mime_type: Annotated[str, StringConstraints(min_length=3, max_length=128)]
    # Bounded descriptors. Examples: "1920x1080", "16kHz_mono", "30fps_h264".
    descriptor: Annotated[str, StringConstraints(max_length=128)] | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    source_uri_sha256_hex: (
        Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None
    ) = None

    @field_validator("mime_type")
    @classmethod
    def _validate_mime(cls, v: str) -> str:
        if not _MIME_PATTERN.match(v):
            raise ValueError(
                f"mime_type {v!r} is not a well-formed RFC 6838 type/subtype value"
            )
        return v


class ToolUseRef(_Base):
    """Tool call binding for agent-style receipts."""

    tool_name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    tool_use_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    input_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    output_sha256_hex: (
        Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None
    ) = None


class RegulatoryContext(_Base):
    """Deployer-supplied regulatory metadata."""

    article_50_paragraph: Literal["1", "2", "3", "4"]
    deployer_jurisdiction: Annotated[str, StringConstraints(min_length=2, max_length=8)]
    end_user_disclosure_made: bool
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None


class ReceiptV1(_Base):
    """Common envelope for all v1 receipts."""

    schema_name: SchemaName = Field(alias="schema")
    schema_version: Literal[1] = 1
    receipt_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    deployer_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    issued_at: datetime = Field(default_factory=_utcnow)
    model: ModelRef
    content_refs: list[ContentRef]
    media_refs: list[MediaRef] = Field(default_factory=list)
    regulatory_context: RegulatoryContext
    tool_uses: list[ToolUseRef] = Field(default_factory=list)
    input_modalities: list[Modality] = Field(default_factory=lambda: ["text"])
    streaming: bool = False
    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-reka"
    adapter_version: Annotated[str, StringConstraints(max_length=32)] = "0.1.0"

    @field_validator("deployer_id", "receipt_id")
    @classmethod
    def _validate_id(cls, v: str) -> str:
        if not _ID_PATTERN.match(v):
            raise ValueError(
                f"identifier {v!r} contains disallowed characters; "
                "use only [A-Za-z0-9._:-/+@] up to 128 chars"
            )
        return v

    @field_validator("content_refs")
    @classmethod
    def _at_least_one_content_ref(cls, v: list[ContentRef]) -> list[ContentRef]:
        if not v:
            raise ValueError("receipt must reference at least one piece of content")
        return v

    @field_validator("input_modalities")
    @classmethod
    def _modalities_nonempty_and_unique(cls, v: list[Modality]) -> list[Modality]:
        if not v:
            raise ValueError("input_modalities must contain at least one modality")
        if len(set(v)) != len(v):
            raise ValueError("input_modalities must not contain duplicates")
        return v

    def to_payload(self) -> dict[str, Any]:
        """Dump the receipt to a JSON/CBOR-ready dict with stable key ordering."""
        return self.model_dump(mode="json", by_alias=True)


def build_chatbot_session_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="chatbot_session/v1", **kwargs)


def build_generated_content_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="generated_content/v1", **kwargs)


def build_multimodal_native_inference_receipt(**kwargs: Any) -> ReceiptV1:
    """
    Article 50(1) variant capturing mixed text/image/audio/video INPUTS.

    Use when a single Reka inference combines two or more input modalities
    (e.g. a chat turn that includes a screenshot plus a spoken question).
    """
    kwargs.setdefault("input_modalities", ["text"])
    return ReceiptV1(schema="multimodal_native_inference/v1", **kwargs)


def build_video_understanding_receipt(**kwargs: Any) -> ReceiptV1:
    """
    Article 50(1) for video-input inferences.

    Strategic surface for downstream Article 50(4) public-interest video
    labeling workflows. NOTE: this receipt alone does NOT discharge 50(4)
    obligations — it is an evidence-layer binding of the inference event.
    """
    kwargs.setdefault("input_modalities", ["video"])
    return ReceiptV1(schema="video_understanding/v1", **kwargs)
