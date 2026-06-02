"""03 — EU-region deployment with data-residency posture.

This is the canonical pattern for a European bank, insurer, or asset manager
running Azure OpenAI under EU data-residency obligations. It:

  - Pins a specific EU region (West Europe / North Europe / France Central /
    Sweden Central / Switzerland North / Italy North / Germany West Central).
  - Emits `azure_enterprise_session/v1` receipts binding the endpoint,
    deployment, region, api_version, and hashed tenant + subscription.
  - Disposes the response unchanged (C7); receipts go to a side-channel sink
    (here LogEmitter; in production a webhook / Event Hubs / Service Bus).

CAVEAT (C1):
  Emitting receipts is NOT a substitute for completing your own ROPA,
  Article 35 DPIA, DORA TLPT obligations, or your AI Act Article 9 risk-
  management documentation. LedgerProof produces tamper-evident transparency
  evidence; it does not certify your overall AI Act posture and is not a
  harmonised standard under Article 40.

Run:
    export AZURE_OPENAI_API_KEY=...
    python examples/03_eu_region_deployment.py
"""

from __future__ import annotations

import hashlib
import os

from ledgerproof_azure_openai import LedgerProofAzureOpenAI, WebhookEmitter

EU_REGION_ENDPOINTS = {
    # Map of canonical EU region -> illustrative resource-name pattern.
    # Replace with your actual resource URL.
    "westeurope": "https://contoso-weu.openai.azure.com/",
    "northeurope": "https://contoso-neu.openai.azure.com/",
    "francecentral": "https://contoso-frc.openai.azure.com/",
    "swedencentral": "https://contoso-swc.openai.azure.com/",
    "switzerlandnorth": "https://contoso-swn.openai.azure.com/",
    "italynorth": "https://contoso-itn.openai.azure.com/",
    "germanywestcentral": "https://contoso-gwc.openai.azure.com/",
}


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> None:
    # 1. Pick an EU region. Default to West Europe.
    region = os.environ.get("AZURE_OPENAI_REGION", "westeurope")
    if region not in EU_REGION_ENDPOINTS:
        raise SystemExit(
            f"Refusing to proceed: {region} is not in the EU residency allow-list. "
            f"Pick one of: {sorted(EU_REGION_ENDPOINTS)}"
        )
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", EU_REGION_ENDPOINTS[region])

    # 2. Emit receipts to your internal audit-ingest webhook (illustrative).
    emitter = WebhookEmitter(
        url=os.environ.get(
            "LPR_RECEIPT_WEBHOOK", "https://audit.contoso.example/lpr/v1/receipts"
        ),
        timeout=2.0,
    )

    # 3. Hash provenance identifiers up front — never let raw GUIDs reach the
    #    receipt builder. Schema validators will reject them anyway.
    tenant_id = os.environ.get(
        "AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000"
    )
    subscription_id = os.environ.get(
        "AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000"
    )

    client = LedgerProofAzureOpenAI(
        deployer_id="urn:eu:deployer:contoso-bank",
        azure_endpoint=endpoint,
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", "dummy"),
        api_version="2024-08-01-preview",
        emitter=emitter,
        regulatory_context={
            "schema": "azure_enterprise_session/v1",
            "jurisdiction": "EU",
            "azure_endpoint": endpoint,
            "azure_region": region,
            "api_version": "2024-08-01-preview",
            "tenant_id_hash": _hash(tenant_id),
            "subscription_id_hash": _hash(subscription_id),
        },
    )

    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt4-prod")
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a regulated-banking assistant operating in the EU. "
                    "Decline anything not appropriate for an FSI assistant."
                ),
            },
            {"role": "user", "content": "Summarise DORA Article 28 in one sentence."},
        ],
    )

    print(f"[region={region}] Assistant:", response.choices[0].message.content)


if __name__ == "__main__":
    main()
