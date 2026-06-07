"""
Receipt schemas for Article 50 evidence (Fireworks AI adapter).

Four schemas:
  - chatbot_session/v1 — Article 50(1), covers direct chat interactions
  - generated_content/v1 — Article 50(2), covers synthetic content generation
  - open_model_hosted/v1 — Article 50(1) variant capturing the underlying
    open-model provider attribution. Fireworks AI hosts open-weights models
    built by other organisations (Meta Llama, Mistral, Qwen / Alibaba,
    DeepSeek, Black Forest Labs / FLUX, Fireworks-built FireFunction, ...).
    For accurate Article 50 evidence, the deployer often wants the receipt
    to record BOTH the upstream model provider AND the hosting attribution
    (Fireworks).
  - flux_image_generation/v1 — Article 50(2) for FLUX image models served
    by Fireworks. Captures prompt SHA-256 and per-image output SHA-256.

GDPR guardrail:
  - receipts MUST NOT contain raw prompt or response text by default; content is
    referenced via SHA-256 hashes only
  - free-text fields are length-bounded
  - identifier fields reject email-shaped strings (no PII leakage through
    deployer_id / user_session_id)
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

SchemaName = Literal[
    "chatbot_session/v1",
    "generated_content/v1",
    "open_model_hosted/v1",
    "flux_image_generation/v1",
]

# Pattern allowing short bounded identifiers — no free-form PII.
_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:\-/+]{1,128}$")

# Crude but effective email shape detector. Reject anything that looks like
# an email address in identifier fields (GDPR direct-identifier guard).
_EMAIL_LIKE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _reject_email_shape(value: str, field_name: str) -> str:
    if _EMAIL_LIKE.match(value):
        raise ValueError(
            f"{field_name} {value!r} looks like an email address; "
            "use an opaque identifier instead — receipts must not carry direct "
            "personal identifiers (GDPR Art. 4(1) / Art. 5(1)(c) data minimisation)."
        )
    return value


class _Base(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class ModelRef(_Base):
    """Reference to the AI system used (Fireworks-side)."""

    provider: Literal["fireworks"] = "fireworks"
    model_id: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    response_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    finish_reason: Annotated[str, StringConstraints(max_length=64)] | None = None
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)


class ContentRef(_Base):
    """SHA-256 reference to message content. Raw text NEVER stored in receipts."""

    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    role: Literal["user", "assistant", "system", "tool", "image"]


class ToolUseRef(_Base):
    """Tool / function-call binding (Fireworks function calling on OpenAI-compatible shape)."""

    tool_name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    tool_use_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    input_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    output_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None = None


class RegulatoryContext(_Base):
    """Deployer-supplied regulatory metadata."""

    article_50_paragraph: Literal["1", "2", "3", "4"]
    deployer_jurisdiction: Annotated[str, StringConstraints(min_length=2, max_length=8)]
    end_user_disclosure_made: bool
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None


# Known underlying open-model families that Fireworks hosts. Extend over time;
# unknown values are allowed via the catch-all string field (we don't gate the
# protocol on Fireworks's catalogue).
OpenModelFamily = Literal[
    "llama",
    "llama-vision",
    "mistral",
    "mixtral",
    "qwen",
    "qwen-vision",
    "deepseek",
    "deepseek-r1",
    "gemma",
    "phi",
    "yi",
    "firefunction",
    "flux",
    "stable-diffusion",
    "other",
]

OpenModelProvider = Literal[
    "meta",
    "mistral-ai",
    "alibaba-qwen",
    "deepseek",
    "google",
    "microsoft",
    "01-ai",
    "fireworks",
    "black-forest-labs",
    "stability-ai",
    "other",
]


class OpenModelAttribution(_Base):
    """
    Open-model attribution block (open_model_hosted/v1).

    Records which organisation built the underlying open-weights model and which
    organisation served it. This is descriptive metadata — see C1 disclaimer.
    Fireworks AI is NOT endorsed by, affiliated with, or certified by this
    adapter; "fireworks" here is a factual hosting attribution string only.
    """

    underlying_model_family: OpenModelFamily | Annotated[
        str, StringConstraints(min_length=1, max_length=64)
    ]
    underlying_model_provider: OpenModelProvider | Annotated[
        str, StringConstraints(min_length=1, max_length=64)
    ]
    host_provider: Literal["fireworks"] = "fireworks"
    model_license: Annotated[str, StringConstraints(max_length=128)] | None = None
    weights_origin: Annotated[str, StringConstraints(max_length=256)] | None = None
    inference_region: Annotated[str, StringConstraints(max_length=32)] | None = None


class ReceiptV1(_Base):
    """Common envelope for all v1 receipts."""

    schema_name: SchemaName = Field(alias="schema")
    schema_version: Literal[1] = 1
    receipt_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    deployer_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    user_session_id: Annotated[str, StringConstraints(min_length=1, max_length=128)] | None = None
    issued_at: datetime = Field(default_factory=_utcnow)
    model: ModelRef
    content_refs: list[ContentRef]
    regulatory_context: RegulatoryContext
    open_model: OpenModelAttribution | None = None
    tool_uses: list[ToolUseRef] = Field(default_factory=list)
    streaming: bool = False
    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-fireworks"
    adapter_version: Annotated[str, StringConstraints(max_length=32)] = "0.1.0"

    @field_validator("deployer_id", "receipt_id")
    @classmethod
    def _validate_id_no_pii(cls, v: str, info) -> str:  # type: ignore[no-untyped-def]
        field_name = info.field_name
        _reject_email_shape(v, field_name)
        if not _ID_PATTERN.match(v):
            raise ValueError(
                f"{field_name}={v!r} contains disallowed characters; "
                "use only [A-Za-z0-9._:-/+] up to 128 chars"
            )
        return v

    @field_validator("user_session_id")
    @classmethod
    def _validate_optional_id_no_pii(cls, v: str | None, info) -> str | None:  # type: ignore[no-untyped-def]
        if v is None:
            return v
        field_name = info.field_name
        _reject_email_shape(v, field_name)
        if not _ID_PATTERN.match(v):
            raise ValueError(
                f"{field_name}={v!r} contains disallowed characters; "
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
        return self.model_dump(mode="json", by_alias=True, exclude_none=False)


def build_chatbot_session_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="chatbot_session/v1", **kwargs)


def build_generated_content_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="generated_content/v1", **kwargs)


def build_open_model_hosted_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="open_model_hosted/v1", **kwargs)


def build_flux_image_generation_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="flux_image_generation/v1", **kwargs)


# ---------------------------------------------------------------------------
# Best-effort: infer (family, provider) from a Fireworks model_id string.
# Strictly heuristic. Deployers can always override via OpenModelAttribution.
# Fireworks model IDs are typically:
#   accounts/fireworks/models/llama-v3p1-70b-instruct
#   accounts/fireworks/models/mixtral-8x22b-instruct
#   accounts/fireworks/models/qwen2p5-72b-instruct
#   accounts/fireworks/models/deepseek-r1
#   accounts/fireworks/models/firefunction-v2
#   accounts/fireworks/models/flux-1-schnell-fp8
# ---------------------------------------------------------------------------

_INFERENCE_RULES: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (re.compile(r"llama.*vision", re.I), "llama-vision", "meta"),
    (re.compile(r"llama-?v?\d", re.I), "llama", "meta"),
    (re.compile(r"llama", re.I), "llama", "meta"),
    (re.compile(r"mixtral", re.I), "mixtral", "mistral-ai"),
    (re.compile(r"mistral", re.I), "mistral", "mistral-ai"),
    (re.compile(r"qwen.*vl", re.I), "qwen-vision", "alibaba-qwen"),
    (re.compile(r"qwen", re.I), "qwen", "alibaba-qwen"),
    (re.compile(r"deepseek.*r1", re.I), "deepseek-r1", "deepseek"),
    (re.compile(r"deepseek", re.I), "deepseek", "deepseek"),
    (re.compile(r"gemma", re.I), "gemma", "google"),
    (re.compile(r"phi-?\d", re.I), "phi", "microsoft"),
    (re.compile(r"yi-", re.I), "yi", "01-ai"),
    (re.compile(r"firefunction", re.I), "firefunction", "fireworks"),
    (re.compile(r"flux", re.I), "flux", "black-forest-labs"),
    (re.compile(r"stable-?diffusion|playground|sdxl", re.I), "stable-diffusion", "stability-ai"),
)


def infer_open_model_attribution(model_id: str) -> OpenModelAttribution | None:
    """
    Best-effort inference of underlying open-model family + provider from a
    Fireworks model_id. Returns None if we cannot identify the upstream model.

    This is heuristic — deployers building Article 50 receipts SHOULD pass an
    explicit OpenModelAttribution. The inferred value is offered as a default
    so the open_model_hosted/v1 schema can be used without ceremony.
    """
    if not model_id:
        return None
    # Strip Fireworks account-path prefix to make matches cleaner.
    tail = model_id.rsplit("/", 1)[-1]
    for pattern, family, provider in _INFERENCE_RULES:
        if pattern.search(tail) or pattern.search(model_id):
            return OpenModelAttribution(
                underlying_model_family=family,  # type: ignore[arg-type]
                underlying_model_provider=provider,  # type: ignore[arg-type]
            )
    return None
