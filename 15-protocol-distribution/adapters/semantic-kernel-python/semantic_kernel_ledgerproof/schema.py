"""Pydantic v2 schemas for LedgerProof transparency receipts.

Four schema variants for Semantic Kernel-shaped workloads:

  * chatbot_session/v1             -> Article 50(1) chatbot interaction
  * generated_content/v1           -> Article 50(2) AI-generated content
  * agent_function_invocation/v1   -> Article 50(1) variant capturing
                                      kernel-function calls in agentic
                                      / auto-function-calling workflows
  * azure_enterprise_session/v1    -> Article 50(1) variant capturing
                                      Azure tenant attribution (tenant id,
                                      subscription scope, region) for
                                      enterprise compliance teams

GDPR safety: validators on `deployer_id`, `tenant_id`, `user_principal_id`,
and `subscription_scope` reject obvious email-shaped strings. These fields
should hold opaque pseudonymous identifiers, not personal data.
"""

from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _reject_email_shaped(value: str, field_name: str) -> str:
    if _EMAIL_RE.match(value.strip()):
        raise ValueError(
            f"GDPR safety: {field_name!r} appears to be an email address. "
            "Use a pseudonymous identifier instead."
        )
    return value


class _BaseReceipt(BaseModel):
    """Common header fields for all receipt variants."""

    schema_id: str = Field(..., description="Receipt schema, e.g. 'chatbot_session/v1'")
    run_id: str = Field(..., description="Unique run identifier (UUID string)")
    timestamp_utc: str = Field(..., description="ISO-8601 UTC timestamp")
    deployer_id: str = Field(
        ...,
        description="Pseudonymous deployer identifier. MUST NOT be an email.",
        min_length=1,
        max_length=256,
    )
    transcript_sha256: str = Field(
        ...,
        description="Hex-encoded SHA-256 of the canonicalized transcript",
        pattern=r"^[0-9a-f]{64}$",
    )

    @field_validator("deployer_id")
    @classmethod
    def _check_deployer(cls, v: str) -> str:
        return _reject_email_shaped(v, "deployer_id")


class ChatbotSessionReceipt(_BaseReceipt):
    """Article 50(1): user was interacting with an AI system."""

    schema_id: Literal["chatbot_session/v1"] = "chatbot_session/v1"
    model_identifier: str = Field(..., description="Model name/version")
    disclosure_shown: bool = Field(
        True, description="Whether AI-interaction disclosure was shown to the user"
    )


class GeneratedContentReceipt(_BaseReceipt):
    """Article 50(2): content was generated or substantially modified by AI."""

    schema_id: Literal["generated_content/v1"] = "generated_content/v1"
    model_identifier: str
    content_type: str = Field(..., description="MIME-ish content type, e.g. 'text/markdown'")
    machine_readable_mark: bool = Field(
        True,
        description="True if the output carries a machine-readable provenance mark",
    )


class AgentFunctionInvocationReceipt(_BaseReceipt):
    """Article 50(1) variant: kernel function invoked inside an agentic flow.

    Captures the *fact* that an LLM-driven agent called a named function in a
    Semantic Kernel plugin. Argument *names* are recorded (not values), so
    user-supplied data does not leak into the receipt.
    """

    schema_id: Literal["agent_function_invocation/v1"] = "agent_function_invocation/v1"
    plugin_name: str = Field(..., max_length=256)
    function_name: str = Field(..., max_length=256)
    argument_names: list[str] = Field(
        default_factory=list,
        description="Names of arguments passed. Values are NOT recorded.",
    )
    is_auto_invoked: bool = Field(
        False, description="True if invoked by SK auto-function-calling agent"
    )
    model_identifier: str = Field("unknown", description="Model that triggered the call")


class AzureEnterpriseSessionReceipt(_BaseReceipt):
    """Article 50(1) variant with Azure tenant attribution for enterprise audit.

    Enables Microsoft enterprise compliance teams to bind a receipt to the
    Azure Entra ID tenant + subscription scope that hosted the AI system.
    Fields are pseudonymous identifiers — tenant GUIDs and subscription IDs
    are opaque, not personal data.
    """

    schema_id: Literal["azure_enterprise_session/v1"] = "azure_enterprise_session/v1"
    model_identifier: str
    tenant_id: str = Field(..., max_length=128, description="Azure Entra ID tenant GUID")
    subscription_scope: str = Field(
        ..., max_length=256, description="Azure subscription / management group scope"
    )
    deployment_region: str = Field(
        ..., max_length=64, description="Azure region, e.g. 'westeurope'"
    )
    user_principal_id: Optional[str] = Field(
        None,
        max_length=256,
        description="OPTIONAL pseudonymous principal id. MUST NOT be a UPN/email.",
    )
    disclosure_shown: bool = True

    @field_validator("tenant_id")
    @classmethod
    def _check_tenant(cls, v: str) -> str:
        return _reject_email_shaped(v, "tenant_id")

    @field_validator("subscription_scope")
    @classmethod
    def _check_sub(cls, v: str) -> str:
        return _reject_email_shaped(v, "subscription_scope")

    @field_validator("user_principal_id")
    @classmethod
    def _check_upn(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _reject_email_shaped(v, "user_principal_id")


SCHEMAS: dict[str, type[_BaseReceipt]] = {
    "chatbot_session/v1": ChatbotSessionReceipt,
    "generated_content/v1": GeneratedContentReceipt,
    "agent_function_invocation/v1": AgentFunctionInvocationReceipt,
    "azure_enterprise_session/v1": AzureEnterpriseSessionReceipt,
}


def get_schema(schema_id: str) -> type[_BaseReceipt]:
    """Look up a schema class by its identifier."""
    try:
        return SCHEMAS[schema_id]
    except KeyError as exc:
        raise ValueError(
            f"Unknown receipt schema: {schema_id!r}. Known: {sorted(SCHEMAS)}"
        ) from exc
