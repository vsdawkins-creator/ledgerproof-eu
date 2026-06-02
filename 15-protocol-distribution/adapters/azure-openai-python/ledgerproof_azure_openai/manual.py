"""Manual receipt emission — for users who want explicit control.

```python
from openai import AzureOpenAI
from ledgerproof_azure_openai import emit_receipt

client = AzureOpenAI(
    azure_endpoint="https://contoso-weu.openai.azure.com/",
    api_key="...",
    api_version="2024-08-01-preview",
)
resp = client.chat.completions.create(
    model="gpt4-prod", messages=[{"role": "user", "content": "hi"}]
)
emit_receipt(
    resp,
    deployer_id="urn:eu:deployer:contoso-bank",
    messages=[{"role": "user", "content": "hi"}],
    azure_endpoint="https://contoso-weu.openai.azure.com/",
    azure_deployment="gpt4-prod",
    api_version="2024-08-01-preview",
    regulatory_context={"schema": "azure_enterprise_session/v1"},
)
```
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from .canonical import canonical_encode
from .client_wrapper import _guess_region_from_endpoint
from .emitter import Emitter, LogEmitter
from .schema import build_receipt
from .signer import Ed25519Signer, Signer
from .version import __version__


_AZURE_PROVENANCE_SCHEMAS = {
    "azure_enterprise_session/v1",
    "azure_ad_authenticated_session/v1",
}


def _hash_messages(messages: list[dict[str, Any]] | None) -> str:
    if not messages:
        return hashlib.sha256(b"").hexdigest()
    payload = json.dumps(messages, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hash_response_text(response: Any) -> str:
    """SHA-256 over the concatenated assistant text from all choices."""
    parts: list[str] = []
    choices = getattr(response, "choices", None) or []
    for choice in choices:
        msg = getattr(choice, "message", None)
        if msg is None:
            continue
        content = getattr(msg, "content", None)
        if content:
            parts.append(content)
    return hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()


def emit_receipt(
    response: Any,
    deployer_id: str,
    *,
    messages: list[dict[str, Any]] | None = None,
    regulatory_context: dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    user_pseudonym: str | None = None,
    extra: dict[str, Any] | None = None,
    azure_endpoint: str | None = None,
    azure_deployment: str | None = None,
    azure_region: str | None = None,
    api_version: str | None = None,
    tenant_id_hash: str | None = None,
    subscription_id_hash: str | None = None,
    azure_ad_principal_hash: str | None = None,
) -> dict[str, Any]:
    """Build, sign, and emit a receipt for an already-completed Azure response.

    Returns the signed envelope dict so callers can also persist / inspect it.
    Does **not** modify `response`.
    """
    regulatory_context = dict(regulatory_context or {})
    schema_id = regulatory_context.get("schema", "chatbot_session/v1")

    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    model_id = getattr(response, "model", azure_deployment or "unknown")
    interaction_id = getattr(response, "id", None) or str(uuid.uuid4())

    fields: dict[str, Any] = dict(
        deployer_id=deployer_id,
        model_id=model_id,
        interaction_id=interaction_id,
        prompt_sha256=_hash_messages(messages),
        response_sha256=_hash_response_text(response),
        user_pseudonym=user_pseudonym or regulatory_context.get("user_pseudonym"),
        jurisdiction=regulatory_context.get("jurisdiction", "EU"),
        extra=extra or {},
    )

    if schema_id in _AZURE_PROVENANCE_SCHEMAS:
        endpoint = azure_endpoint or regulatory_context.get("azure_endpoint")
        if not endpoint:
            raise ValueError(
                f"Schema {schema_id!r} requires azure_endpoint."
            )
        fields["azure_endpoint"] = endpoint
        fields["azure_deployment"] = (
            azure_deployment
            or regulatory_context.get("azure_deployment")
            or model_id
        )
        fields["azure_region"] = (
            azure_region
            or regulatory_context.get("azure_region")
            or _guess_region_from_endpoint(endpoint)
        )
        fields["api_version"] = api_version or regulatory_context.get("api_version")
        tih = tenant_id_hash or regulatory_context.get("tenant_id_hash")
        if tih is not None:
            fields["tenant_id_hash"] = tih
        sih = subscription_id_hash or regulatory_context.get("subscription_id_hash")
        if sih is not None:
            fields["subscription_id_hash"] = sih
        if schema_id == "azure_ad_authenticated_session/v1":
            principal = (
                azure_ad_principal_hash
                or regulatory_context.get("azure_ad_principal_hash")
            )
            if not principal:
                raise ValueError(
                    "azure_ad_authenticated_session/v1 requires "
                    "azure_ad_principal_hash."
                )
            fields["azure_ad_principal_hash"] = principal
            if "azure_ad_principal_type" in regulatory_context:
                fields["azure_ad_principal_type"] = regulatory_context[
                    "azure_ad_principal_type"
                ]
            if "auth_method" in regulatory_context:
                fields["auth_method"] = regulatory_context["auth_method"]

    receipt = build_receipt(schema_id, **fields)
    receipt_dict = receipt.model_dump()
    canonical_bytes = canonical_encode(receipt_dict)
    signature = signer.sign(canonical_bytes)

    envelope = {
        "receipt": receipt_dict,
        "signature": signature.hex(),
        "signature_alg": "ed25519",
        "public_key": signer.public_key_bytes().hex(),
        "adapter": {"name": "ledgerproof-azure-openai", "version": __version__},
    }
    emitter.emit(envelope)
    return envelope
