"""Receipt schemas — Pydantic v2.

Four schemas tailored to xAI Grok deployment surfaces:

- `chatbot_session/v1`         — Article 50(1): natural person interacting with an AI system
- `generated_content/v1`       — Article 50(2): synthetically generated or manipulated content
- `realtime_data_inference/v1` — Article 50(1) variant capturing real-time data source
                                  attribution (Grok's distinctive X-platform integration);
                                  strategic for Article 50(4) public-interest text labeling
                                  when Grok's real-time web/X-data feature is used
- `vision_inference/v1`        — Article 50(2) variant for `grok-2-vision` image-input inference

GDPR discipline: receipts MUST NOT carry plaintext PII. We store hashes of
prompt/response, never raw text. The `user_pseudonym` field MUST be a hash,
opaque ID, or empty — validators reject anything that looks like a raw email
address.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


_EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class _ReceiptBase(BaseModel):
    """Common fields across all receipt schemas."""

    schema_id: str
    timestamp: str = Field(default_factory=_utc_now_iso)
    deployer_id: str
    model_provider: Literal["xai"] = "xai"
    model_id: str
    interaction_id: str
    prompt_sha256: str
    response_sha256: str
    user_pseudonym: str | None = None
    jurisdiction: str = "EU"
    extra: dict[str, Any] = Field(default_factory=dict)

    @field_validator("user_pseudonym")
    @classmethod
    def _no_raw_pii(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return v
        if _EMAIL_RE.search(v):
            raise ValueError(
                "user_pseudonym must not contain raw email addresses. "
                "Hash or pseudonymize first (GDPR Art. 5(1)(c) — data minimization)."
            )
        return v

    @field_validator("prompt_sha256", "response_sha256")
    @classmethod
    def _is_hex_sha256(cls, v: str) -> str:
        if len(v) != 64 or any(c not in "0123456789abcdef" for c in v.lower()):
            raise ValueError("must be a 64-char lowercase hex SHA-256")
        return v.lower()

    @field_validator("deployer_id")
    @classmethod
    def _is_urn(cls, v: str) -> str:
        if not v.startswith("urn:"):
            raise ValueError("deployer_id should be a URN (e.g. 'urn:eu:deployer:acme')")
        return v


class ChatbotSessionV1(_ReceiptBase):
    """Article 50(1): a natural person is interacting with an AI system."""

    schema_id: Literal["chatbot_session/v1"] = "chatbot_session/v1"
    article_basis: Literal["EU_AI_Act_Art_50_1"] = "EU_AI_Act_Art_50_1"
    disclosure_shown: bool = False


class GeneratedContentV1(_ReceiptBase):
    """Article 50(2): synthetically generated audio/image/video/text content."""

    schema_id: Literal["generated_content/v1"] = "generated_content/v1"
    article_basis: Literal["EU_AI_Act_Art_50_2"] = "EU_AI_Act_Art_50_2"
    content_modality: Literal["text", "image", "audio", "video"] = "text"
    machine_readable_marker: bool = True


class RealtimeDataInferenceV1(_ReceiptBase):
    """Article 50(1) variant — Grok's real-time data attribution.

    Captures whether the inference drew on live web / X-platform data, plus
    a hash of the source-attribution surface. Strategic for Article 50(4)
    public-interest text labeling: when Grok summarizes or paraphrases a
    real-time news / social-media surface, the receipt records the binding
    between prompt, attributed sources, and emitted answer.

    Note: `realtime_sources_sha256` is a SHA-256 over a deployer-chosen
    canonical representation of the source list (e.g. JSON-sorted array of
    URLs + capture timestamps). The adapter does NOT phone home to verify
    sources — that is the deployer's responsibility (constraint C4).
    """

    schema_id: Literal["realtime_data_inference/v1"] = "realtime_data_inference/v1"
    article_basis: Literal["EU_AI_Act_Art_50_1"] = "EU_AI_Act_Art_50_1"
    realtime_data_used: bool = False
    realtime_sources_sha256: str | None = None
    public_interest_text: bool = False

    @field_validator("realtime_sources_sha256")
    @classmethod
    def _maybe_hex_sha256(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if len(v) != 64 or any(c not in "0123456789abcdef" for c in v.lower()):
            raise ValueError("realtime_sources_sha256 must be 64-char lowercase hex SHA-256")
        return v.lower()


class VisionInferenceV1(_ReceiptBase):
    """Article 50(2) variant — Grok-2-vision image-input inference.

    `image_input_sha256` binds the receipt to the specific image(s) fed to
    the model (SHA-256 over the canonical-sorted concatenation of image
    bytes, or over the JSON-sorted array of remote image URLs). This makes
    the receipt actionable when the deployer is asked to prove which
    image triggered which model output.
    """

    schema_id: Literal["vision_inference/v1"] = "vision_inference/v1"
    article_basis: Literal["EU_AI_Act_Art_50_2"] = "EU_AI_Act_Art_50_2"
    content_modality: Literal["text", "image", "audio", "video"] = "text"
    image_input_sha256: str | None = None
    image_count: int = 0

    @field_validator("image_input_sha256")
    @classmethod
    def _maybe_hex_sha256(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if len(v) != 64 or any(c not in "0123456789abcdef" for c in v.lower()):
            raise ValueError("image_input_sha256 must be 64-char lowercase hex SHA-256")
        return v.lower()


SCHEMAS = {
    "chatbot_session/v1": ChatbotSessionV1,
    "generated_content/v1": GeneratedContentV1,
    "realtime_data_inference/v1": RealtimeDataInferenceV1,
    "vision_inference/v1": VisionInferenceV1,
}


def build_receipt(schema_id: str, **fields: Any) -> _ReceiptBase:
    """Construct a receipt by schema_id."""
    cls = SCHEMAS.get(schema_id)
    if cls is None:
        raise ValueError(
            f"Unknown schema_id={schema_id!r}. Known: {list(SCHEMAS)}"
        )
    return cls(**fields)
