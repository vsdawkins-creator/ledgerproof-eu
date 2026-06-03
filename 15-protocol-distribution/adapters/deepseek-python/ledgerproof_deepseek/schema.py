"""Receipt schemas — Pydantic v2.

Four schemas tailored to DeepSeek deployment surfaces:

- `chatbot_session/v1`     — Article 50(1): natural person interacting with an AI system
- `generated_content/v1`   — Article 50(2): synthetically generated or manipulated content
- `reasoning_trace/v1`     — Article 50(1) variant capturing `deepseek-reasoner` (R1)
                              chain-of-thought trace hash alongside the answer hash
- `code_generation/v1`     — Article 50(2) variant for `deepseek-coder` code-output
                              provenance binding

GDPR discipline: receipts MUST NOT carry plaintext PII. We store hashes of
prompt/response/reasoning, never raw text. The `user_pseudonym` field MUST be a
hash, opaque ID, or empty — validators reject anything that looks like a raw
email address. Same validator runs on `deployer_id` (which should be a URN, not
an email) and on `session_id` when populated.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


_EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _reject_email_shaped(value: str | None, field_name: str) -> str | None:
    if value is None or value == "":
        return value
    if _EMAIL_RE.search(value):
        raise ValueError(
            f"{field_name} must not contain raw email addresses. "
            "Hash or pseudonymize first (GDPR Art. 5(1)(c) — data minimization)."
        )
    return value


class _ReceiptBase(BaseModel):
    """Common fields across all receipt schemas."""

    schema_id: str
    timestamp: str = Field(default_factory=_utc_now_iso)
    deployer_id: str
    model_provider: Literal["deepseek"] = "deepseek"
    model_id: str
    interaction_id: str
    session_id: str | None = None
    prompt_sha256: str
    response_sha256: str
    user_pseudonym: str | None = None
    jurisdiction: str = "EU"
    extra: dict[str, Any] = Field(default_factory=dict)

    @field_validator("user_pseudonym")
    @classmethod
    def _user_pseudonym_no_pii(cls, v: str | None) -> str | None:
        return _reject_email_shaped(v, "user_pseudonym")

    @field_validator("session_id")
    @classmethod
    def _session_id_no_pii(cls, v: str | None) -> str | None:
        # GDPR: session_id should be an opaque correlation ID, not an email.
        return _reject_email_shaped(v, "session_id")

    @field_validator("prompt_sha256", "response_sha256")
    @classmethod
    def _is_hex_sha256(cls, v: str) -> str:
        if len(v) != 64 or any(c not in "0123456789abcdef" for c in v.lower()):
            raise ValueError("must be a 64-char lowercase hex SHA-256")
        return v.lower()

    @field_validator("deployer_id")
    @classmethod
    def _deployer_id_is_urn(cls, v: str) -> str:
        # deployer_id is a stable organisational identifier — must not be an email
        # (data minimization) and must be in URN form so it routes cleanly through
        # the Foundation's deployer registry.
        if _EMAIL_RE.search(v):
            raise ValueError(
                "deployer_id must not contain raw email addresses. "
                "Use a URN (e.g. 'urn:eu:deployer:acme')."
            )
        if not v.startswith("urn:"):
            raise ValueError(
                "deployer_id should be a URN (e.g. 'urn:eu:deployer:acme')"
            )
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
    content_modality: Literal["text", "image", "audio", "video", "code"] = "text"
    machine_readable_marker: bool = True


class ReasoningTraceV1(_ReceiptBase):
    """Article 50(1) variant — DeepSeek-R1 (`deepseek-reasoner`) chain-of-thought.

    `deepseek-reasoner` returns two fields on the assistant message:
    - `content`            — the final answer text
    - `reasoning_content`  — the chain-of-thought trace

    Both are AI-generated text. This schema binds the prompt to BOTH the final
    answer hash and a separate hash over the reasoning trace, so an auditor can
    verify a deployer's claim that "the trace surfaced to user X is the trace
    that produced answer Y" without the deployer disclosing the raw trace text
    (GDPR + commercial confidentiality).

    `reasoning_sha256` is optional — if the deployer's pipeline did not retain
    the trace, the field stays `None` and the receipt records only the final
    answer binding.
    """

    schema_id: Literal["reasoning_trace/v1"] = "reasoning_trace/v1"
    article_basis: Literal["EU_AI_Act_Art_50_1"] = "EU_AI_Act_Art_50_1"
    reasoning_sha256: str | None = None
    reasoning_token_count: int | None = None
    trace_surfaced_to_user: bool = False

    @field_validator("reasoning_sha256")
    @classmethod
    def _maybe_hex_sha256(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if len(v) != 64 or any(c not in "0123456789abcdef" for c in v.lower()):
            raise ValueError("reasoning_sha256 must be 64-char lowercase hex SHA-256")
        return v.lower()


class CodeGenerationV1(_ReceiptBase):
    """Article 50(2) variant — `deepseek-coder` code-output provenance.

    Code emitted by an AI system that is shipped into production, into a
    customer-visible artifact, or into a public repository is Article 50(2)
    "generated content." A verifiable provenance receipt is useful both for
    Article 50(2) compliance and for downstream supply-chain attestations
    (e.g. SLSA, in-toto).
    """

    schema_id: Literal["code_generation/v1"] = "code_generation/v1"
    article_basis: Literal["EU_AI_Act_Art_50_2"] = "EU_AI_Act_Art_50_2"
    content_modality: Literal["code"] = "code"
    programming_language: str | None = None
    machine_readable_marker: bool = True


SCHEMAS = {
    "chatbot_session/v1": ChatbotSessionV1,
    "generated_content/v1": GeneratedContentV1,
    "reasoning_trace/v1": ReasoningTraceV1,
    "code_generation/v1": CodeGenerationV1,
}


def build_receipt(schema_id: str, **fields: Any) -> _ReceiptBase:
    """Construct a receipt by schema_id."""
    cls = SCHEMAS.get(schema_id)
    if cls is None:
        raise ValueError(
            f"Unknown schema_id={schema_id!r}. Known: {list(SCHEMAS)}"
        )
    return cls(**fields)
