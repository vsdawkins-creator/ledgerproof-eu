"""
LPR API — Pydantic request/response models.

All models are validated before reaching business logic. No raw dicts
reach the database or signing layer.
"""
from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ActorType(str, Enum):
    HUMAN = "HUMAN"
    AI_MODEL = "AI_MODEL"
    HYBRID = "HYBRID"
    INSTITUTION = "INSTITUTION"


class AnchorStatus(str, Enum):
    PENDING = "PENDING"
    ANCHORED = "ANCHORED"
    FAILED = "FAILED"


class ContentCategory(str, Enum):
    SYNTHETIC_TEXT = "SYNTHETIC_TEXT"
    SYNTHETIC_IMAGE = "SYNTHETIC_IMAGE"
    SYNTHETIC_AUDIO = "SYNTHETIC_AUDIO"
    SYNTHETIC_VIDEO = "SYNTHETIC_VIDEO"
    DEEPFAKE = "DEEPFAKE"
    SYNTHETIC_MULTIMODAL = "SYNTHETIC_MULTIMODAL"
    AI_ASSISTED_DOCUMENT = "AI_ASSISTED_DOCUMENT"


class JurisdictionProfile(str, Enum):
    EU_AI_ACT_50_V1 = "EU-AI-ACT-50-v1"
    SCITT_V1 = "SCITT-v1"


# ---------------------------------------------------------------------------
# EU AI Act Article 50 sub-model
# ---------------------------------------------------------------------------

class EUAIAct50(BaseModel):
    """EU AI Act Article 50 transparency metadata.

    Required when jurisdiction_profile = "EU-AI-ACT-50-v1".
    See LPR-1.0-SPECIFICATION.md §8.5 and 12-eu-compliance/01-EU-AI-ACT-50-PROFILE.md.
    """
    profile_version: str = Field(default="EU-AI-ACT-50-v1", frozen=True)
    ai_system_id: str = Field(
        ...,
        description="Identifier of the AI system — e.g. openai/gpt-4o/2024-11-20",
        max_length=512,
    )
    ai_system_version: Optional[str] = Field(
        default=None,
        max_length=256,
    )
    deployer_id: str = Field(
        ...,
        description="Legal entity ID: EUID, LEI, VAT number, or DID. NOT a natural-person ID.",
        max_length=256,
    )
    deployer_name: str = Field(
        ...,
        description="Organization name of the deployer.",
        max_length=512,
    )
    deployer_country: str = Field(
        ...,
        description="ISO 3166-1 alpha-2 country code of the deployer.",
        min_length=2,
        max_length=2,
    )
    content_category: ContentCategory
    transparency_marker: str = Field(
        default="LPR-EU-AI-ACT-50",
        frozen=True,
    )
    enforcement_date: str = Field(default="2026-08-02", frozen=True)
    supervisory_authority: Optional[str] = Field(
        default=None,
        description="Optional: name of the relevant national supervisory authority.",
        max_length=512,
    )

    @field_validator("deployer_country")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        if not v.isupper() or not v.isalpha() or len(v) != 2:
            raise ValueError(
                f"deployer_country must be an ISO 3166-1 alpha-2 code (e.g. DE, FR, NL). Got: {v!r}"
            )
        return v

    @field_validator("deployer_id")
    @classmethod
    def no_natural_person_id(cls, v: str) -> str:
        """Reject obvious natural-person identifiers (email addresses)."""
        if re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError(
                "deployer_id must be a legal entity identifier (EUID, LEI, VAT, DID), "
                "not an email address. GDPR: natural-person identifiers require a DPA."
            )
        return v


# ---------------------------------------------------------------------------
# Receipt issuance request
# ---------------------------------------------------------------------------

class ReceiptRequest(BaseModel):
    """Body of POST /receipts."""

    # Artifact
    content_hash: str = Field(
        ...,
        description="Hex-encoded SHA-256 hash of the artifact (64 hex chars).",
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
    )
    content_type: str = Field(
        ...,
        description="MIME type of the artifact.",
        max_length=256,
    )
    content_bytes: int = Field(
        ...,
        ge=1,
        description="Size of the artifact in bytes.",
    )

    # Authorship
    actor_type: ActorType
    actor_id: str = Field(
        ...,
        description="AI model ID or pseudonymous human/institutional identifier.",
        max_length=512,
    )
    actor_assertion: str = Field(
        ...,
        description="Human-readable assertion about what was attested.",
        max_length=2048,
    )
    tool_chain: list[dict[str, str]] = Field(
        default_factory=list,
        description="Ordered list of tools/models used to produce the artifact.",
    )

    # Chain
    prev_receipt_id: Optional[str] = Field(
        default=None,
        description="UUID of the preceding receipt in this authorial chain.",
    )

    # Profile selection
    jurisdiction_profile: Optional[JurisdictionProfile] = Field(
        default=None,
        description="Optional jurisdiction-specific profile to apply.",
    )

    # EU AI Act Article 50 extension
    eu_ai_act_50: Optional[EUAIAct50] = Field(
        default=None,
        description="Required when jurisdiction_profile = EU-AI-ACT-50-v1.",
    )

    @field_validator("content_hash")
    @classmethod
    def validate_hex(cls, v: str) -> str:
        try:
            bytes.fromhex(v)
        except ValueError:
            raise ValueError("content_hash must be a valid 64-character hex string")
        return v.lower()

    @model_validator(mode="after")
    def eu_profile_requires_eu_extension(self) -> "ReceiptRequest":
        if (
            self.jurisdiction_profile == JurisdictionProfile.EU_AI_ACT_50_V1
            and self.eu_ai_act_50 is None
        ):
            raise ValueError(
                "eu_ai_act_50 is required when jurisdiction_profile = EU-AI-ACT-50-v1"
            )
        return self

    @model_validator(mode="after")
    def human_actor_id_warning(self) -> "ReceiptRequest":
        """Warn if actor_type=HUMAN and actor_id looks like a direct personal identifier."""
        if self.actor_type == ActorType.HUMAN:
            if re.match(r"^[^@]+@[^@]+\.[^@]+$", self.actor_id):
                raise ValueError(
                    "actor_type=HUMAN with an email address in actor_id constitutes "
                    "personal data under GDPR. Use a pseudonymous identifier or an "
                    "internal employee ID. If personal data processing is required, "
                    "ensure a Data Processing Agreement is in place and set "
                    "gdpr_personal_data_acknowledged=true."
                )
        return self


# ---------------------------------------------------------------------------
# Batch issuance
# ---------------------------------------------------------------------------

class BatchReceiptRequest(BaseModel):
    """Body of POST /receipts/batch. Max 1000 receipts per batch."""

    receipts: list[ReceiptRequest] = Field(
        ...,
        min_length=1,
        max_length=1000,
    )


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class AnchorInfo(BaseModel):
    substrate: str
    merkle_leaf_hash: str  # hex
    anchor_status: AnchorStatus
    btc_txid: Optional[str] = None
    btc_block_height: Optional[int] = None
    merkle_path: Optional[list[str]] = None  # hex-encoded path nodes
    anchored_at: Optional[datetime] = None


class ReceiptResponse(BaseModel):
    receipt_id: str
    trace_id: str
    timestamp_ns: int
    timestamp_iso: str
    lpr_version: int = 1
    profile: Optional[str] = None
    jurisdiction_profile: Optional[str] = None

    # Artifact (echoed back for confirmation)
    content_hash: str
    content_type: str
    content_bytes: int

    # Authorship (echoed)
    actor_type: str
    actor_id: str

    # Signing
    signer_pubkey: str  # hex-encoded Ed25519 public key

    # Anchor
    anchor: AnchorInfo

    # EU extension (echoed if submitted)
    eu_ai_act_50: Optional[dict[str, Any]] = None

    # Verification URL
    verify_url: str


class ProofResponse(BaseModel):
    receipt_id: str
    leaf_hash: str  # hex
    leaf_index: int
    tree_size: int
    proof_path: list[str]  # hex-encoded sibling hashes
    merkle_root: str  # hex
    btc_txid: str
    btc_block_height: int
    verification_url: str


class HealthResponse(BaseModel):
    status: str
    region: str
    lpr_version: str
    pending_receipts: int
    last_anchor_time: Optional[datetime]
    last_anchor_txid: Optional[str]
    last_anchor_block: Optional[int]
    hot_wallet_balance_sats: Optional[int]
    db_ok: bool
    btc_node_ok: bool


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
