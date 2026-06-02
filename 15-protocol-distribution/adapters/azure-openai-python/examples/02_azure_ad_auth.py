"""02 — Azure AD (Entra ID) authentication with managed identity.

Demonstrates:
  - Using DefaultAzureCredential + bearer-token provider for keyless auth.
  - Emitting an `azure_ad_authenticated_session/v1` receipt that binds a
    SHA-256 hash of the managed identity's principal OID (not the raw OID).
  - Capturing tenant + subscription provenance (also hashed).

WHY THE HASHING DISCIPLINE:
  Azure tenant GUIDs and AAD object IDs are treated as personal data under
  EU guidance when they identify a natural person. Hashing them lets you
  prove WHICH managed identity invoked the model without leaking the raw
  identifier into the audit log. This is GDPR Art. 5(1)(c) — data
  minimisation — applied to the audit trail itself.

Run:
    az login   # or run from within a managed-identity-enabled compute resource
    python examples/02_azure_ad_auth.py
"""

from __future__ import annotations

import hashlib
import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from ledgerproof_azure_openai import LedgerProofAzureOpenAI


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> None:
    endpoint = os.environ.get(
        "AZURE_OPENAI_ENDPOINT", "https://contoso-weu.openai.azure.com/"
    )
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt4-prod")

    # Step 1: standard Azure AD bearer-token provider.
    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(
        credential, "https://cognitiveservices.azure.com/.default"
    )

    # Step 2: gather provenance. In production these come from
    # IDENTITY_ENDPOINT / IMDS / your config, NOT hardcoded.
    tenant_id = os.environ.get(
        "AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000"
    )
    subscription_id = os.environ.get(
        "AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000"
    )
    principal_oid = os.environ.get(
        "AZURE_PRINCIPAL_OID", "11111111-1111-1111-1111-111111111111"
    )

    client = LedgerProofAzureOpenAI(
        deployer_id="urn:eu:deployer:contoso-bank",
        azure_endpoint=endpoint,
        azure_ad_token_provider=token_provider,
        api_version="2024-08-01-preview",
        regulatory_context={
            "schema": "azure_ad_authenticated_session/v1",
            "azure_endpoint": endpoint,
            "api_version": "2024-08-01-preview",
            # All identifiers are hashed BEFORE landing in the receipt.
            "tenant_id_hash": _hash(tenant_id),
            "subscription_id_hash": _hash(subscription_id),
            "azure_ad_principal_hash": _hash(principal_oid),
            "azure_ad_principal_type": "managed_identity",
            "auth_method": "default_credential",
        },
    )

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "user", "content": "Confirm you are running under AAD auth."},
        ],
    )

    print("Assistant:", response.choices[0].message.content)


if __name__ == "__main__":
    main()
