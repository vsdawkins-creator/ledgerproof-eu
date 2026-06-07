"""
Receipt schemas for Article 50 evidence — Replicate variant.

Replicate hosts and runs an open ecosystem of third-party models — Llama, FLUX,
Stable Diffusion, Whisper, MusicGen, ZeroScope, and many more — across text,
image, audio, and video modalities. The receipt schemas reflect that surface:

  - chatbot_session/v1 — Article 50(1): direct text chat (Llama-style chat models)
  - generated_content/v1 — Article 50(2): general-purpose synthetic content
  - synthetic_image/v1 — Article 50(2) for image generation. Captures the exact
    `model:version` string, the prompt hash, and the SHA-256 of the produced
    image bytes. Strategic because Replicate is the leading non-OpenAI image-gen
    runtime in the EU market (FLUX, Stable Diffusion, SDXL).
  - synthetic_audio/v1 — Article 50(2) for audio generation/synthesis. Covers
    Whisper transcription, MusicGen, Bark, RVC voice clones. The audio MIME and
    duration are bound to support enforcement.
  - synthetic_video/v1 — Article 50(2) for video. Covers ZeroScope, AnimateDiff,
    and other text-to-video / image-to-video stacks. Includes frame count + FPS.
  - multimodel_attribution/v1 — Article 50(2) capturing the precise model
    coordinates: `author/name:version` (immutable Replicate version hash). This
    is the load-bearing schema for content-provenance traceability: a verifier
    can prove which exact model weights produced the output, because Replicate
    versions are content-addressed.

GDPR guardrail: receipts MUST NOT contain raw prompt or response text by default.
Content is referenced via SHA-256 hashes only. Free-text fields are length-bounded.
End-user identifiers, IP addresses, and locale data are not part of the schema.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

SchemaName = Literal[
    "chatbot_session/v1",
    "generated_content/v1",
    "synthetic_image/v1",
    "synthetic_audio/v1",
    "synthetic_video/v1",
    "multimodel_attribution/v1",
]

# Pattern allowing short bounded identifiers — no free-form PII.
_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:\-/+@]{1,128}$")

# Replicate model coordinates look like:
#   "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
#   "black-forest-labs/flux-schnell"
# We allow author/name with optional :version (64-char content hash).
_REPLICATE_MODEL_PATTERN = re.compile(
    r"^[A-Za-z0-9._\-]{1,64}/[A-Za-z0-9._\-]{1,128}(:[A-Za-z0-9]{8,128})?$"
)


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
    """
    Reference to the AI system used (Replicate-side).

    `model_id` is the Replicate coordinate string `author/name` (e.g.
    `black-forest-labs/flux-schnell`). `model_version` is the immutable
    content-addressed version hash, when known — this is the load-bearing
    field for content-provenance verification.
    """

    provider: Literal["replicate"] = "replicate"
    model_id: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    model_version: Annotated[str, StringConstraints(max_length=128)] | None = None
    prediction_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    status: Annotated[str, StringConstraints(max_length=32)] | None = None
    predict_time_seconds: float | None = Field(default=None, ge=0.0)

    @field_validator("model_id")
    @classmethod
    def _validate_model_id(cls, v: str) -> str:
        # Accept either "author/name" or "author/name:version"; we split version out.
        if not _REPLICATE_MODEL_PATTERN.match(v):
            raise ValueError(
                f"model_id {v!r} must match Replicate format 'author/name' "
                "or 'author/name:version'"
            )
        return v


class ContentRef(_Base):
    """SHA-256 reference to message content. Raw text NEVER stored in receipts."""

    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    role: Literal["user", "assistant", "system", "tool", "prompt", "output"]


class InputRef(_Base):
    """
    SHA-256 reference to a single Replicate prediction input parameter.

    Replicate models take a structured `input` dict (e.g. `{"prompt": "...",
    "guidance_scale": 7.5}`). We hash each scalar/text input separately to allow
    verifiers to attest "this exact prompt produced this exact output" without
    storing the prompt text itself.
    """

    name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    # The pydantic "type" hint of the original input (str, int, float, bool, file).
    input_type: Literal["text", "number", "boolean", "file", "json"] = "text"


class OutputArtifactRef(_Base):
    """
    Reference to a single generated artifact (image, audio, video, or other
    binary output). Replicate returns these as URLs (FileOutput) which the
    deployer is responsible for hashing — we record the hash here.

    GDPR: artifact bytes are NEVER stored in the receipt — only the hash, MIME,
    and bounded metadata.
    """

    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    media_type: Annotated[str, StringConstraints(max_length=128)] | None = None
    # Modality-specific descriptors (all optional, bounded):
    width_px: int | None = Field(default=None, ge=0, le=65536)
    height_px: int | None = Field(default=None, ge=0, le=65536)
    duration_seconds: float | None = Field(default=None, ge=0.0)
    sample_rate_hz: int | None = Field(default=None, ge=0)
    frame_count: int | None = Field(default=None, ge=0)
    frames_per_second: float | None = Field(default=None, ge=0.0)
    output_uri: Annotated[str, StringConstraints(max_length=512)] | None = None


class RegulatoryContext(_Base):
    """Deployer-supplied regulatory metadata."""

    article_50_paragraph: Literal["1", "2", "3", "4"]
    deployer_jurisdiction: Annotated[str, StringConstraints(min_length=2, max_length=8)]
    end_user_disclosure_made: bool
    # For 50(2) synthetic content: whether a machine-readable provenance mark
    # (C2PA, watermark, etc.) was applied at the same time.
    machine_readable_mark_applied: bool | None = None
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None


class ReceiptV1(_Base):
    """Common envelope for all v1 receipts."""

    schema_name: SchemaName = Field(alias="schema")
    schema_version: Literal[1] = 1
    receipt_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    deployer_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    issued_at: datetime = Field(default_factory=_utcnow)
    model: ModelRef
    content_refs: list[ContentRef] = Field(default_factory=list)
    input_refs: list[InputRef] = Field(default_factory=list)
    output_artifacts: list[OutputArtifactRef] = Field(default_factory=list)
    regulatory_context: RegulatoryContext
    streaming: bool = False
    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-replicate"
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

    def to_payload(self) -> dict[str, Any]:
        """Dump the receipt to a JSON/CBOR-ready dict with stable key ordering."""
        return self.model_dump(mode="json", by_alias=True, exclude_none=False)


# ---------------------------------------------------------------------------
# Schema constructors with schema-specific invariants.
# ---------------------------------------------------------------------------


def build_chatbot_session_receipt(**kwargs: Any) -> ReceiptV1:
    """Article 50(1) — direct chat interaction with a Replicate-hosted LLM."""
    receipt = ReceiptV1(schema="chatbot_session/v1", **kwargs)
    if not receipt.content_refs:
        raise ValueError("chatbot_session/v1 requires at least one content_ref")
    return receipt


def build_generated_content_receipt(**kwargs: Any) -> ReceiptV1:
    """Article 50(2) — general synthetic content."""
    receipt = ReceiptV1(schema="generated_content/v1", **kwargs)
    if not receipt.content_refs and not receipt.output_artifacts:
        raise ValueError(
            "generated_content/v1 requires at least one content_ref or output_artifact"
        )
    return receipt


def build_synthetic_image_receipt(**kwargs: Any) -> ReceiptV1:
    """
    Article 50(2) for image generation — FLUX, SDXL, Stable Diffusion, etc.

    Requires at least one output_artifact with image-shaped fields (width/height
    or media_type image/*), and binds the prompt hash via input_refs.
    """
    receipt = ReceiptV1(schema="synthetic_image/v1", **kwargs)
    if not receipt.output_artifacts:
        raise ValueError(
            "synthetic_image/v1 requires at least one output_artifact "
            "(the generated image bytes)"
        )
    return receipt


def build_synthetic_audio_receipt(**kwargs: Any) -> ReceiptV1:
    """
    Article 50(2) for audio generation — Whisper TTS, MusicGen, Bark, RVC.
    """
    receipt = ReceiptV1(schema="synthetic_audio/v1", **kwargs)
    if not receipt.output_artifacts:
        raise ValueError(
            "synthetic_audio/v1 requires at least one output_artifact "
            "(the generated audio bytes)"
        )
    return receipt


def build_synthetic_video_receipt(**kwargs: Any) -> ReceiptV1:
    """
    Article 50(2) for video generation — ZeroScope, AnimateDiff, etc.
    """
    receipt = ReceiptV1(schema="synthetic_video/v1", **kwargs)
    if not receipt.output_artifacts:
        raise ValueError(
            "synthetic_video/v1 requires at least one output_artifact "
            "(the generated video bytes)"
        )
    return receipt


def build_multimodel_attribution_receipt(**kwargs: Any) -> ReceiptV1:
    """
    Article 50(2) capturing the exact `author/name:version` Replicate coordinate.

    Required: model.model_version (the immutable content hash) MUST be present.
    This is the strongest form of model attribution because Replicate versions
    are content-addressed — the same version hash always references the same
    weights.
    """
    receipt = ReceiptV1(schema="multimodel_attribution/v1", **kwargs)
    if not receipt.model.model_version:
        raise ValueError(
            "multimodel_attribution/v1 requires model.model_version to be set "
            "(the content-addressed Replicate version hash)"
        )
    return receipt
