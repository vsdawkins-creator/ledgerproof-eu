"""Receipt schemas — Pydantic v2.

Three schemas, one per Article 50 scenario:

- `chatbot_session/v1`  — Article 50(1): natural person interacting with an AI system
- `generated_content/v1` — Article 50(2): synthetically generated or manipulated content
- `assistant_response/v1` — Article 50(1) with assistant_id binding for OpenAI Assistants API

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
    model_provider: Literal["openai"] = "openai"
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


class AssistantResponseV1(_ReceiptBase):
    """Article 50(1) — variant binding an OpenAI Assistants API `assistant_id`."""

    schema_id: Literal["assistant_response/v1"] = "assistant_response/v1"
    article_basis: Literal["EU_AI_Act_Art_50_1"] = "EU_AI_Act_Art_50_1"
    assistant_id: str
    thread_id: str | None = None
    run_id: str | None = None


SCHEMAS = {
    "chatbot_session/v1": ChatbotSessionV1,
    "generated_content/v1": GeneratedContentV1,
    "assistant_response/v1": AssistantResponseV1,
}


def build_receipt(schema_id: str, **fields: Any) -> _ReceiptBase:
    """Construct a receipt by schema_id."""
    cls = SCHEMAS.get(schema_id)
    if cls is None:
        raise ValueError(
            f"Unknown schema_id={schema_id!r}. Known: {list(SCHEMAS)}"
        )
    return cls(**fields)
