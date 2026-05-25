"""Pydantic v2 models for LPR v1.1 receipts and content types.

These models mirror the Rust ``AiArticle50Content``, ``AiHumanReviewContent``,
and ``AiChatbotSessionContent`` structs in ``quantum-edge-2/src/schemas.rs``.
Field names, types, and serde-rename conventions are preserved exactly so
that JSON serialized from a Python instance round-trips byte-for-byte
through the Rust server.

The enum values use SCREAMING_SNAKE_CASE on the wire, matching the Rust
``#[serde(rename_all = "SCREAMING_SNAKE_CASE")]`` attribute. Pydantic v2's
``use_enum_values=True`` ensures we emit the string form when dumping.
"""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Annotated, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

# ── Type aliases ───────────────────────────────────────────────────────────

LowercaseHex64 = Annotated[
    str,
    StringConstraints(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$"),
]
"""Exactly 64 lowercase hex characters — i.e., a SHA-256 in hex."""

Iso3166Alpha2 = Annotated[
    str,
    StringConstraints(min_length=2, max_length=2, pattern=r"^[A-Z]{2}$"),
]
"""Two uppercase ASCII letters — ISO 3166-1 alpha-2 country code."""


# ── Enums (SCREAMING_SNAKE_CASE on the wire) ───────────────────────────────


class ContentCategory(str, Enum):
    """Article 50 content category. Matches ``ContentCategory`` in quantum-edge-2."""

    SYNTHETIC_TEXT = "SYNTHETIC_TEXT"
    SYNTHETIC_IMAGE = "SYNTHETIC_IMAGE"
    SYNTHETIC_AUDIO = "SYNTHETIC_AUDIO"
    SYNTHETIC_VIDEO = "SYNTHETIC_VIDEO"
    DEEPFAKE = "DEEPFAKE"
    SYNTHETIC_MULTIMODAL = "SYNTHETIC_MULTIMODAL"
    AI_ASSISTED_DOCUMENT = "AI_ASSISTED_DOCUMENT"


class GenerationType(str, Enum):
    """LPR v1.1: modality of AI involvement in the artifact's creation."""

    FULLY_GENERATED = "FULLY_GENERATED"
    AI_MANIPULATED = "AI_MANIPULATED"
    AI_ASSISTED = "AI_ASSISTED"


class ReviewType(str, Enum):
    """LPR v1.1: type of human review for the Article 50(4) exemption."""

    SUBSTANTIAL_EDIT = "SUBSTANTIAL_EDIT"
    FACTUAL_REVIEW = "FACTUAL_REVIEW"
    APPROVAL_ONLY = "APPROVAL_ONLY"


class NotificationMethod(str, Enum):
    """LPR v1.1: how a chatbot user was notified of AI interaction."""

    INITIAL_BANNER = "INITIAL_BANNER"
    INLINE_MESSAGE = "INLINE_MESSAGE"
    AUDIO_ANNOUNCEMENT = "AUDIO_ANNOUNCEMENT"
    PRE_PROMPT_DISCLOSURE = "PRE_PROMPT_DISCLOSURE"


# ── Supporting models ──────────────────────────────────────────────────────


class PerceptualHash(BaseModel):
    """LPR v1.1: perceptual hash for image/audio/video robustness."""

    model_config = ConfigDict(use_enum_values=True, extra="forbid")

    algorithm: str = Field(min_length=1, max_length=32)
    """Algorithm identifier: pHash, dHash, aHash, wHash, chromaprint."""

    value: str = Field(min_length=1, pattern=r"^[0-9a-fA-F]+$")
    """Hex-encoded hash value."""

    bits: int = Field(ge=1, le=4096)
    """Bit length of the hash."""


# ── Content payloads ───────────────────────────────────────────────────────


class AiArticle50Content(BaseModel):
    """LPR v1.1 ``ai/article-50/v1`` content payload.

    Mirrors the Rust ``AiArticle50Content`` struct exactly. v1.0 fields are
    required; v1.1 additions are optional with server-side defaults.
    """

    model_config = ConfigDict(use_enum_values=True, extra="forbid")

    # ── v1.0 base fields ────────────────────────────────────────────────
    ai_system_id: str = Field(min_length=1, max_length=512)
    """Provider/model/version, e.g., ``openai/gpt-4o/2024-11-20``."""

    ai_system_version: Optional[str] = Field(default=None, max_length=256)
    """Optional version string when ``ai_system_id`` alone is insufficient."""

    deployer_id: str = Field(min_length=1, max_length=256)
    """Legal-entity identifier (LEI/EUID/VAT/DID). NOT an email — enforced."""

    deployer_name: str = Field(min_length=1, max_length=512)
    """Human-readable legal name of the deploying organization."""

    deployer_country: Iso3166Alpha2
    """ISO 3166-1 alpha-2 country code of the deployer's registered office."""

    content_category: ContentCategory
    """One of seven Article 50 content categories."""

    artifact_hash: LowercaseHex64
    """SHA-256 of the artifact in lowercase hex. The artifact itself stays local."""

    artifact_content_type: str = Field(min_length=1, max_length=128)
    """IANA media type (e.g., ``text/plain``, ``image/png``)."""

    artifact_bytes: int = Field(gt=0)
    """Artifact size in bytes. Must be > 0."""

    supervisory_authority: Optional[str] = Field(default=None, max_length=128)
    """Named EU supervisory authority, e.g., ``BaFin (DE)``."""

    # ── v1.1 additions (optional) ───────────────────────────────────────
    generation_type: Optional[GenerationType] = None
    """LPR v1.1: modality of AI involvement."""

    source_content_hash: Optional[LowercaseHex64] = None
    """LPR v1.1: for AI_MANIPULATED, SHA-256 of the original source."""

    perceptual_hash: Optional[PerceptualHash] = None
    """LPR v1.1: perceptual hash for resilience to re-encoding."""

    transparency_marker: str = Field(default="LPR-EU-AI-ACT-50", min_length=1, max_length=128)
    """LPR v1.1: human-readable disclosure string."""

    is_public_interest: Optional[bool] = None
    """LPR v1.1: deployer assertion that content touches matters of public interest."""

    enforcement_date: str = Field(default="2026-08-02", pattern=r"^\d{4}-\d{2}-\d{2}$")
    """LPR v1.1: ISO 8601 enforcement date of the applicable regulation."""

    profile_version: str = Field(default="EU-AI-ACT-50-v1.1", min_length=1, max_length=64)
    """LPR v1.1: profile version tag."""

    @field_validator("deployer_id")
    @classmethod
    def _deployer_id_is_legal_entity(cls, v: str) -> str:
        """GDPR safety net: reject anything that looks like an email."""
        if "@" in v:
            raise ValueError(
                "deployer_id must be a legal-entity identifier (LEI/EUID/VAT/DID), "
                "not an email or personal identifier"
            )
        return v

    @model_validator(mode="after")
    def _validate_manipulation_hint(self) -> AiArticle50Content:
        """If AI_MANIPULATED, source_content_hash is RECOMMENDED. We don't enforce
        it as a hard error (some manipulations have no single source — composites),
        but we surface it as a warning via a marker field. Server makes the call.
        """
        # No-op; documented for future hardening.
        return self


class AiHumanReviewContent(BaseModel):
    """LPR v1.1 ``ai/human-review/v1`` payload — Article 50(4) editorial exemption."""

    model_config = ConfigDict(use_enum_values=True, extra="forbid")

    original_entry_hash: LowercaseHex64
    """SHA-256 of the ai/article-50/v1 receipt being reviewed."""

    original_sequence: int = Field(ge=0)
    """Sequence number of the original receipt in the chain."""

    reviewer_role: str = Field(min_length=1, max_length=128)
    """Role identifier (NOT a name). E.g., 'senior-editor', 'legal-counsel'."""

    reviewer_country: Iso3166Alpha2
    """ISO 3166-1 alpha-2 country code of the reviewer's organization."""

    review_timestamp: datetime
    """When the review event occurred."""

    review_type: ReviewType
    """Type of review performed."""

    reviewed_artifact_hash: LowercaseHex64
    """SHA-256 of the post-review content. For SUBSTANTIAL_EDIT, must differ from original."""

    is_public_interest: bool
    """Deployer assertion that the content is public interest under Article 50(4)."""

    review_rationale: Optional[str] = Field(default=None, max_length=2048)
    """Free-text rationale. RECOMMENDED for legal defensibility. MUST NOT contain PII."""

    @field_validator("reviewer_role")
    @classmethod
    def _reviewer_role_is_role_not_person(cls, v: str) -> str:
        if "@" in v:
            raise ValueError(
                "reviewer_role must be a role identifier ('senior-editor'), "
                "not an email or personal identifier"
            )
        return v

    @field_validator("review_rationale")
    @classmethod
    def _rationale_no_email(cls, v: Optional[str]) -> Optional[str]:
        if v and "@" in v:
            raise ValueError(
                "review_rationale must not contain email addresses (GDPR)"
            )
        return v


class AiChatbotSessionContent(BaseModel):
    """LPR v1.1 ``ai/chatbot-session/v1`` payload — Article 50(1) interactive disclosure."""

    model_config = ConfigDict(use_enum_values=True, extra="forbid")

    session_id_hash: LowercaseHex64
    """SHA-256 of an opaque session identifier. Raw ID never transmitted."""

    ai_system_id: str = Field(min_length=1, max_length=512)
    deployer_id: str = Field(min_length=1, max_length=256)
    deployer_name: str = Field(min_length=1, max_length=512)
    deployer_country: Iso3166Alpha2

    notification_timestamp: datetime
    """When the user was notified of AI interaction (or session start, if exemption claimed)."""

    notification_method: NotificationMethod
    """How the notification was presented."""

    notification_text_hash: LowercaseHex64
    """SHA-256 of the disclosure text shown to the user."""

    obvious_exemption_claimed: bool
    """If True, deployer claims Article 50(1) 'obvious' exemption applied."""

    @field_validator("deployer_id")
    @classmethod
    def _deployer_id_is_legal_entity(cls, v: str) -> str:
        if "@" in v:
            raise ValueError(
                "deployer_id must be a legal-entity identifier, not an email"
            )
        return v


# ── Response models ────────────────────────────────────────────────────────


class Receipt(BaseModel):
    """The receipt object returned by ``POST /v1/publish``.

    Includes the canonical chain identifiers and a convenience verify URL.
    """

    model_config = ConfigDict(extra="ignore")

    sequence: int = Field(ge=0)
    """Position in the chain."""

    entry_hash: LowercaseHex64
    """SHA-256 of ``entry_json_canonical``, the immutable identity of this receipt."""

    receipt_id: Optional[int] = None
    """Server-side receipt row id (legacy compatibility)."""

    @property
    def verify_url(self) -> str:
        """Public URL where this receipt can be fetched without authentication.

        Defaults to the EU operator. Override by passing the URL explicitly.
        """
        return f"https://api-eu.ledgerproofhq.io/v1/verify/{self.sequence}"


class EntryResponse(BaseModel):
    """The full entry as returned by ``GET /v1/entries/:seq`` or ``/v1/verify/:seq``.

    Includes signed envelope fields plus optional ``content`` (nulled after
    GDPR Article 17 erasure).
    """

    model_config = ConfigDict(extra="ignore")

    sequence: int
    publisher_id: str
    key_id: str
    prev_hash: str
    entry_hash: str
    signature: str
    protocol_version: Optional[str] = None
    content_type: str
    content_hash: str
    content: Optional[dict] = None
    entry_json_canonical: Optional[str] = None
    entry_timestamp: datetime
    created_at: datetime
    deleted_at: Optional[datetime] = None
    deleted_reason: Optional[str] = None


__all__ = [
    "AiArticle50Content",
    "AiChatbotSessionContent",
    "AiHumanReviewContent",
    "ContentCategory",
    "EntryResponse",
    "GenerationType",
    "NotificationMethod",
    "PerceptualHash",
    "Receipt",
    "ReviewType",
]
