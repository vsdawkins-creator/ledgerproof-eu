# ledgerproof-azure-openai

LedgerProof adapter for the **Azure OpenAI Python SDK**. Emits signed,
side-channel transparency receipts aligned with **EU AI Act Article 50**.

This package targets Tier-1 European enterprise deployers of Azure OpenAI —
banks, insurers, asset managers, and other regulated entities running GPT-4o /
GPT-4 / o-series deployments in EU Azure regions (West Europe, North Europe,
France Central, Sweden Central, Switzerland North, Italy North, Germany West
Central) under data-residency obligations.

## Discipline (please read)

This adapter is engineered against four hard constraints. They are not
marketing copy — they are the reason this package can exist at all.

- **C1 — No regulator endorsement, no Article 40 presumption.**
  LedgerProof is **not** a harmonised standard. Emitting these receipts does
  **not** confer Article 40 presumption of conformity with the EU AI Act and
  is **not** an attestation from the European Commission, the EU AI Office,
  any national competent authority, or any EU institution.
- **C1 — No Microsoft / Azure endorsement.**
  LedgerProof is **not** endorsed by, certified by, affiliated with, or in any
  way blessed by Microsoft Corporation or Microsoft Azure. "Azure OpenAI" is a
  Microsoft trademark used here solely under nominative fair use to identify
  the SDK this adapter wraps.
- **C4 — Local verification only.**
  Receipts are verified against the deployer's published signing key. No
  Foundation oracle, no phone-home, no remote attestation server is consulted
  at runtime.
- **C6 — Stream-aware signing.**
  Streaming responses are hashed incrementally as chunks arrive; the receipt is
  emitted only when the stream is fully drained, so the response hash always
  binds the *complete* assistant output.
- **C7 — Side-channel emission only.**
  The Azure OpenAI response object is returned to your code **byte-identical**.
  Receipts go to a logger, webhook, queue, or Event Hubs / Service Bus sink —
  never into the response payload, never into the response stream.

## Why a separate package for Azure OpenAI?

Azure OpenAI is *operationally* a different product from OpenAI even though it
ships the same `openai` Python SDK. Enterprise compliance teams need the
receipt to bind the **Azure-specific provenance** that determines who is
responsible for the inference and where the data resided:

- `azure_endpoint` — the region-specific resource URL (e.g.
  `https://contoso-weu.openai.azure.com/`) which encodes the Azure region of
  the deployment, and therefore the data-residency claim.
- `azure_deployment` — the **customer-chosen deployment name**, which is *not*
  the same as the underlying OpenAI model name (e.g. deployment `gpt4-prod`
  pointing at model `gpt-4o-2024-08-06`).
- `api_version` — Azure exposes preview and GA API versions independently of
  OpenAI; the receipt binds the exact API surface the call hit.
- Optional `tenant_id`, `subscription_id` — for enterprise attribution under
  the customer's own Azure tenant. **Hashed before emission.**
- Optional `azure_ad_principal_hash` — when Azure AD authentication is used,
  the receipt can bind a hash of the principal identity (object ID), proving
  *which managed identity* invoked the model without exposing the raw ID.

These bind together to answer the only question a GC or CRO actually cares
about during an Article 50 inquiry: *"who invoked which model, in which
region, under which API contract, on whose behalf — and prove it."*

## Install

```bash
pip install ledgerproof-azure-openai
```

Optional extras:

```bash
pip install "ledgerproof-azure-openai[keyvault]"   # Azure Key Vault signer stub
pip install "ledgerproof-azure-openai[test]"
```

## 30-second quickstart

```python
from ledgerproof_azure_openai import LedgerProofAzureOpenAI

client = LedgerProofAzureOpenAI(
    deployer_id="urn:eu:deployer:contoso-bank",
    azure_endpoint="https://contoso-weu.openai.azure.com/",
    api_key="...",
    api_version="2024-08-01-preview",
    regulatory_context={
        "schema": "azure_enterprise_session/v1",
        "jurisdiction": "EU",
        "azure_region": "westeurope",
    },
)

resp = client.chat.completions.create(
    model="gpt4-prod",   # NB: Azure "model" is the deployment name
    messages=[{"role": "user", "content": "Hello"}],
)

# `resp` is the standard openai.types.chat.ChatCompletion — unchanged.
# A signed receipt was emitted on the side channel.
```

## EU region positioning

Azure OpenAI in EU regions is one of the most common procurement-approved
inference paths for European banks, insurers, and asset managers. Deploying
**both** in an EU region **and** emitting Article 50 receipts is the
defensible posture under:

- **EU AI Act Art. 50** — transparency obligations on deployers of GPAI
  systems (chatbots, generative content).
- **GDPR Art. 5(1)(c)** — data minimisation; receipts store *hashes*, never
  raw prompts or responses.
- **DORA** — operational resilience evidence for ICT third-party risk;
  receipts are tamper-evident audit records.
- **EBA / ECB guidance on AI in banking** — explainability, traceability,
  and human-oversight evidence.

See `examples/03_eu_region_deployment.py` for the West Europe / North Europe /
France Central pattern.

## What ships in v0.1 (MVP)

- `LedgerProofAzureOpenAI` — sync wrapper around `openai.AzureOpenAI`.
- `LedgerProofAsyncAzureOpenAI` — async wrapper.
- `@lpr_track(...)` — decorator for any function returning an Azure OpenAI
  `ChatCompletion`.
- `emit_receipt(response, ...)` — manual emission for explicit callers.
- Four receipt schemas (Pydantic v2):
  - `chatbot_session/v1` — Article 50(1) baseline.
  - `generated_content/v1` — Article 50(2) (text / image / audio / video).
  - `azure_enterprise_session/v1` — captures Azure deployment name, endpoint
    region, tenant ID hash, subscription ID hash. **Recommended for
    enterprise customers.**
  - `azure_ad_authenticated_session/v1` — captures Azure AD principal hash
    when bearer-token auth is used.
- Stream-aware SHA-256 hashing of assistant content.
- Ed25519 ephemeral signer + `AzureKeyVaultSigner` stub for v0.2.
- `LogEmitter`, `WebhookEmitter`, `QueueEmitter` side-channel sinks.
- GDPR validators: rejects raw emails / IPs / phone numbers in
  `user_pseudonym`; rejects unhashed tenant/subscription IDs.

## What is NOT in v0.1

- Azure Event Hubs / Service Bus emitters (planned v0.2).
- Concrete Azure Key Vault signing (stubbed; concrete impl v0.2).
- Microsoft Entra ID role-claim binding (planned v0.3).
- DALL-E / Whisper / TTS endpoints (chat completions only in MVP).

## License

Apache-2.0. Foundation-stewarded.
