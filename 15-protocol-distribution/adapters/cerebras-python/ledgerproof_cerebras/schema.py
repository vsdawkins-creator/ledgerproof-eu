"""Receipt schemas for LedgerProof-Cerebras.

Each schema is a versioned Pydantic model that, once validated, becomes the
canonical body of a transparency receipt. GDPR validators enforce that only
hashed or pseudonymous identifiers reach a receipt — never raw personal data.
"""

from __future__ import annotations

import hashlib
import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ReceiptSchemaName(str, Enum):
    CHATBOT_SESSION_V1 = "chatbot_session/v1"
    GENERATED_CONTENT_V1 = "generated_content/v1"
    WAFER_SCALE_INFERENCE_V1 = "wafer_scale_inference/v1"
    REASONING_DISTILLED_V1 = "reasoning_distilled/v1"


class GDPRValidationError(ValueError):
    """Raised when a field that should be hashed/pseudonymised contains
    apparently raw personal data."""


_HASH_PREFIX_RE = re.compile(r"^(sha256|sha3-256|blake2b):[0-9a-fA-F]{32,128}$")
_EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def validate_gdpr_safe(value: Optional[str], *, field_name: str) -> Optional[str]:
    """Reject obviously raw personal data in receipt identifier fields.

    Permits: None, empty string, or a prefixed hash like 'sha256:abc...'.
    Rejects: bare email addresses or long unhashed strings.
    """
    if value is None or value == "":
        return value
    if _HASH_PREFIX_RE.match(value):
        return value
    if _EMAIL_RE.search(value):
        raise GDPRValidationError(
            f"Field {field_name!r} appears to contain a raw email. "
            "Hash it first (e.g. 'sha256:<hex>')."
        )
    if len(value) > 64 and " " in value:
        raise GDPRValidationError(
            f"Field {field_name!r} looks like free-form personal data. "
            "Hash or pseudonymise before placing it in a receipt."
        )
    return value


def hash_str(text: str, algo: str = "sha256") -> str:
    """Convenience helper to produce a GDPR-safe identifier."""
    h = hashlib.new(algo, text.encode("utf-8")).hexdigest()
    return f"{algo}:{h}"


class _ReceiptBase(BaseModel):
    schema_name: ReceiptSchemaName
    model: str = Field(..., description="Cerebras model identifier")
    provider: str = Field(default="cerebras")
    timestamp_unix_ms: int = Field(..., description="Receipt creation time, ms since epoch")
    deployer_id: str = Field(..., description="Deployer identifier (Article 3(4))")

    model_config = {"extra": "forbid"}


class ChatbotSessionV1(_ReceiptBase):
    """Article 50(1) — natural-person interaction with an AI chatbot."""

    schema_name: ReceiptSchemaName = ReceiptSchemaName.CHATBOT_SESSION_V1
    subject_id_hash: Optional[str] = Field(
        default=None,
        description="Pseudonymous identifier for the natural person (hashed).",
    )
    session_id_hash: Optional[str] = None
    prompt_hash: Optional[str] = None
    completion_hash: Optional[str] = None
    disclosure_shown: bool = Field(
        default=False,
        description="Whether the Article 50(1) AI-interaction disclosure was shown.",
    )

    @field_validator("subject_id_hash", "session_id_hash", "prompt_hash", "completion_hash")
    @classmethod
    def _gdpr(cls, v, info):
        return validate_gdpr_safe(v, field_name=info.field_name)


class GeneratedContentV1(_ReceiptBase):
    """Article 50(2) — synthetic content marking."""

    schema_name: ReceiptSchemaName = ReceiptSchemaName.GENERATED_CONTENT_V1
    content_hash: str = Field(..., description="Hash of the generated artefact.")
    content_type: str = Field(default="text", description="text | audio | image | video")
    marking_method: Optional[str] = Field(
        default=None, description="e.g. 'visible-label', 'c2pa', 'watermark'"
    )

    @field_validator("content_hash")
    @classmethod
    def _hash_required(cls, v):
        if not _HASH_PREFIX_RE.match(v):
            raise GDPRValidationError(
                "content_hash must be a prefixed hash, e.g. 'sha256:<hex>'."
            )
        return v


class WaferScaleInferenceV1(_ReceiptBase):
    """Cerebras-specific 50(1) variant capturing CS-3 wafer-scale performance.

    Attestation surface for the differentiating ultra-low-latency profile of
    the Cerebras CS-3 wafer-scale engine. The deployer attests to observed
    inference latency, tokens/sec throughput, and token-accounting figures.
    """

    schema_name: ReceiptSchemaName = ReceiptSchemaName.WAFER_SCALE_INFERENCE_V1
    inference_latency_ms: float = Field(..., ge=0)
    tokens_per_second: Optional[float] = Field(default=None, ge=0)
    prompt_tokens: Optional[int] = Field(default=None, ge=0)
    completion_tokens: Optional[int] = Field(default=None, ge=0)
    total_tokens: Optional[int] = Field(default=None, ge=0)
    hardware_class: str = Field(
        default="wafer-scale",
        description="Free-form hardware-class attribution (e.g. 'wafer-scale').",
    )
    prompt_hash: Optional[str] = None
    completion_hash: Optional[str] = None

    @field_validator("prompt_hash", "completion_hash")
    @classmethod
    def _gdpr(cls, v, info):
        return validate_gdpr_safe(v, field_name=info.field_name)


class ReasoningDistilledV1(_ReceiptBase):
    """50(1) variant for distilled reasoning models.

    Targets `deepseek-r1-distill-*`, `qwen3-*-thinking`, and similar
    chain-of-thought-style distilled models hosted on Cerebras. Captures
    the reasoning-trace token usage alongside the final completion so a
    deployer can attest to the cost surface of a reasoning interaction
    while still hashing the trace itself (never the raw text).
    """

    schema_name: ReceiptSchemaName = ReceiptSchemaName.REASONING_DISTILLED_V1
    reasoning_tokens: Optional[int] = Field(default=None, ge=0)
    completion_tokens: Optional[int] = Field(default=None, ge=0)
    prompt_tokens: Optional[int] = Field(default=None, ge=0)
    total_tokens: Optional[int] = Field(default=None, ge=0)
    inference_latency_ms: Optional[float] = Field(default=None, ge=0)
    reasoning_trace_hash: Optional[str] = Field(
        default=None,
        description="Hash of the reasoning/thinking trace (if surfaced).",
    )
    prompt_hash: Optional[str] = None
    completion_hash: Optional[str] = None
    disclosure_shown: bool = Field(
        default=False,
        description="Whether the Article 50(1) AI-interaction disclosure was shown.",
    )

    @field_validator(
        "reasoning_trace_hash", "prompt_hash", "completion_hash"
    )
    @classmethod
    def _gdpr(cls, v, info):
        return validate_gdpr_safe(v, field_name=info.field_name)


SCHEMA_REGISTRY = {
    ReceiptSchemaName.CHATBOT_SESSION_V1: ChatbotSessionV1,
    ReceiptSchemaName.GENERATED_CONTENT_V1: GeneratedContentV1,
    ReceiptSchemaName.WAFER_SCALE_INFERENCE_V1: WaferScaleInferenceV1,
    ReceiptSchemaName.REASONING_DISTILLED_V1: ReasoningDistilledV1,
}


def resolve_schema(name: str | ReceiptSchemaName) -> type[_ReceiptBase]:
    if isinstance(name, str):
        name = ReceiptSchemaName(name)
    return SCHEMA_REGISTRY[name]
