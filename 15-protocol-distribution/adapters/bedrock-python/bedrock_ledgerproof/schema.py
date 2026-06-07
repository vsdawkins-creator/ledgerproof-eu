"""
Receipt schemas for AWS Bedrock invocations under EU AI Act Article 50.

Bedrock is a multi-provider AI gateway, so the schema set here is richer than
single-provider adapters:

  - chatbot_session/v1 — Article 50(1), direct chat interactions
  - generated_content/v1 — Article 50(2), synthetic content generation
  - bedrock_cross_provider/v1 — Article 50(1) variant that captures provider
    attribution (anthropic / meta / mistral / amazon / cohere / ai21 / stability)
    plus the Bedrock region. Critical for multi-provider deployers because the
    deployer's Article 50 obligations may differ subtly per upstream provider.
  - eu_aws_data_residency/v1 — Article 50(1) variant for EU regions specifically
    (eu-west-1, eu-central-1, eu-north-1, eu-south-1, eu-west-2, eu-west-3,
    eu-central-2, eu-south-2). Records explicit residency attestation: the
    inference happened in an EU region and customer prompt/response bytes did
    not cross the region boundary.

GDPR guardrail: receipts MUST NOT contain raw prompt or response text by default.
Content is referenced via SHA-256 hashes only. Free-text fields are length-bounded.
ARN-shaped IDs are allowed in the identifier regex (colons are permitted).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

SchemaName = Literal[
    "chatbot_session/v1",
    "generated_content/v1",
    "bedrock_cross_provider/v1",
    "eu_aws_data_residency/v1",
]

# Bedrock model IDs and ARNs use a fairly wide character set:
#   anthropic.claude-3-5-sonnet-20240620-v1:0
#   arn:aws:bedrock:eu-west-1:123456789012:foundation-model/...
_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:\-/+@]{1,256}$")

# Known Bedrock model-ID prefixes → provider attribution.
# We do not endorse any provider; this is a structural classification.
_PROVIDER_PREFIXES = {
    "anthropic": "anthropic",
    "meta": "meta",
    "mistral": "mistral",
    "amazon": "amazon",
    "cohere": "cohere",
    "ai21": "ai21",
    "stability": "stability",
}

# EU regions for the eu_aws_data_residency schema.
EU_AWS_REGIONS = frozenset(
    {
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "eu-central-1",
        "eu-central-2",
        "eu-north-1",
        "eu-south-1",
        "eu-south-2",
    }
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def infer_provider(model_id: str) -> str:
    """Best-effort: pull the provider prefix from a Bedrock modelId."""
    if not model_id:
        return "unknown"
    head = model_id.split(".", 1)[0].lower()
    # Handle inference-profile ARNs which start with arn:aws:bedrock:...
    if head.startswith("arn:"):
        # Try to find a provider prefix later in the ARN.
        for prefix in _PROVIDER_PREFIXES:
            if f"/{prefix}." in model_id.lower() or f":{prefix}." in model_id.lower():
                return _PROVIDER_PREFIXES[prefix]
        return "unknown"
    return _PROVIDER_PREFIXES.get(head, "unknown")


def is_eu_region(region: str | None) -> bool:
    return bool(region) and region in EU_AWS_REGIONS


class _Base(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class ModelRef(_Base):
    """Reference to the AI system used (Bedrock-side)."""

    provider: Annotated[str, StringConstraints(min_length=1, max_length=32)] = "bedrock"
    upstream_provider: Annotated[str, StringConstraints(min_length=1, max_length=32)] = "unknown"
    model_id: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    response_id: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    region: Annotated[str, StringConstraints(min_length=1, max_length=32)] | None = None
    stop_reason: Annotated[str, StringConstraints(max_length=64)] | None = None
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)


class ContentRef(_Base):
    """SHA-256 reference to message content. Raw text NEVER stored in receipts."""

    sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    byte_length: int = Field(ge=0)
    role: Literal["user", "assistant", "system", "tool"]


class ToolUseRef(_Base):
    """Tool call binding for agent-style receipts (Bedrock Converse tool_use)."""

    tool_name: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    tool_use_id: Annotated[str, StringConstraints(min_length=1, max_length=256)]
    input_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    output_sha256_hex: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None = None


class RegulatoryContext(_Base):
    """Deployer-supplied regulatory metadata."""

    article_50_paragraph: Literal["1", "2", "3", "4"]
    deployer_jurisdiction: Annotated[str, StringConstraints(min_length=2, max_length=8)]
    end_user_disclosure_made: bool
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None


class DataResidencyAttestation(_Base):
    """
    Self-attestation by the deployer that the Bedrock call ran in an EU region.

    LedgerProof does NOT verify this against AWS; it records the deployer's
    own attestation alongside the region pulled from the boto3 client config.
    The verifier compares `attested_region` with `model.region` to catch drift.
    """

    attested_region: Annotated[str, StringConstraints(min_length=2, max_length=32)]
    eu_region: bool
    cross_border_transfer: bool = False
    sccs_in_place: bool | None = None  # Standard Contractual Clauses
    notes: Annotated[str, StringConstraints(max_length=512)] | None = None

    @field_validator("attested_region")
    @classmethod
    def _normalize_region(cls, v: str) -> str:
        return v.strip().lower()


class ReceiptV1(_Base):
    """Common envelope for all v1 receipts."""

    schema_name: SchemaName = Field(alias="schema")
    schema_version: Literal[1] = 1
    receipt_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    deployer_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    issued_at: datetime = Field(default_factory=_utcnow)
    model: ModelRef
    content_refs: list[ContentRef]
    regulatory_context: RegulatoryContext
    tool_uses: list[ToolUseRef] = Field(default_factory=list)
    streaming: bool = False
    residency: DataResidencyAttestation | None = None
    adapter: Annotated[str, StringConstraints(max_length=64)] = "ledgerproof-bedrock"
    adapter_version: Annotated[str, StringConstraints(max_length=32)] = "0.1.0"

    @field_validator("deployer_id", "receipt_id")
    @classmethod
    def _validate_id(cls, v: str) -> str:
        if not _ID_PATTERN.match(v):
            raise ValueError(
                f"identifier {v!r} contains disallowed characters; "
                "use only [A-Za-z0-9._:-/+@] up to 256 chars"
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


def build_cross_provider_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="bedrock_cross_provider/v1", **kwargs)


def build_eu_residency_receipt(**kwargs: Any) -> ReceiptV1:
    return ReceiptV1(schema="eu_aws_data_residency/v1", **kwargs)
