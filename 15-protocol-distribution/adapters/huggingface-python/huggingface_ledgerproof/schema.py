"""Receipt schemas — Pydantic v2.

Four schemas, one per Hugging Face Article 50 scenario:

- `chatbot_session/v1`       — Article 50(1): natural person interacting with an AI system
- `generated_content/v1`     — Article 50(2): synthetically generated or manipulated content
- `eu_open_model_hosted/v1`  — Article 50(1) variant capturing Hugging Face hosting +
                               open-model attribution (EU AI sovereignty story)
- `local_inference/v1`       — Article 50(1) variant for self-hosted Transformers
                               pipelines (captures host environment for on-prem compliance)

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
    model_provider: Literal["huggingface"] = "huggingface"
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


class EUOpenModelHostedV1(_ReceiptBase):
    """Article 50(1) — Hugging Face hosted inference of an open / open-weights model.

    Captures the hosting platform (Hugging Face Inference API), the EU AI
    sovereignty attribution (Hugging Face HQ in Paris/NYC), and the open-model
    license, where known. Strategic for deployers who want their receipts to
    reflect that inference ran on EU-headquartered infrastructure against
    auditable open weights.
    """

    schema_id: Literal["eu_open_model_hosted/v1"] = "eu_open_model_hosted/v1"
    article_basis: Literal["EU_AI_Act_Art_50_1"] = "EU_AI_Act_Art_50_1"
    hosting_platform: Literal["huggingface_inference_api"] = "huggingface_inference_api"
    hosting_provider_hq: str = "Paris/NYC"
    model_license: str | None = None
    open_weights: bool = True


class LocalInferenceV1(_ReceiptBase):
    """Article 50(1) — self-hosted Transformers pipeline inference.

    Captures the host environment (hostname, framework, device) so on-prem
    deployers can demonstrate the inference ran inside their controlled
    perimeter — no third-party hosted call was involved.
    """

    schema_id: Literal["local_inference/v1"] = "local_inference/v1"
    article_basis: Literal["EU_AI_Act_Art_50_1"] = "EU_AI_Act_Art_50_1"
    host_environment: dict[str, Any] = Field(default_factory=dict)
    framework: Literal["transformers"] = "transformers"
    device: str | None = None
    task: str | None = None


SCHEMAS = {
    "chatbot_session/v1": ChatbotSessionV1,
    "generated_content/v1": GeneratedContentV1,
    "eu_open_model_hosted/v1": EUOpenModelHostedV1,
    "local_inference/v1": LocalInferenceV1,
}


def build_receipt(schema_id: str, **fields: Any) -> _ReceiptBase:
    """Construct a receipt by schema_id."""
    cls = SCHEMAS.get(schema_id)
    if cls is None:
        raise ValueError(
            f"Unknown schema_id={schema_id!r}. Known: {list(SCHEMAS)}"
        )
    return cls(**fields)
