# Cloud Connector Spec — Bedrock, Azure OpenAI, Vertex AI, OpenAI, Anthropic

**Purpose:** Pre-built integrations between LedgerProof SDKs and the major AI inference platforms. Customers should not write integration glue; they should `import` it. By Day 90, six connector packages ship with full coverage.

**Owner:** Product Engineer + DevRel (Day 120)
**Target:** Day 90 alpha for all six; Day 120 1.0 stable

---

## Connector inventory

| Connector | Python package | TS package | Pattern |
|---|---|---|---|
| OpenAI | `ledgerproof-openai` | `@ledgerproof/openai` | Wrap `openai.ChatCompletion.create` and friends |
| Anthropic | `ledgerproof-anthropic` | `@ledgerproof/anthropic` | Wrap `anthropic.Messages.create` |
| Azure OpenAI | `ledgerproof-azure-openai` | `@ledgerproof/azure-openai` | Wrap Azure-specific SDK |
| AWS Bedrock | `ledgerproof-bedrock` | `@ledgerproof/bedrock` | Wrap `boto3.client('bedrock-runtime')` |
| Google Vertex AI | `ledgerproof-vertex` | `@ledgerproof/vertex` | Wrap `google.cloud.aiplatform` |
| LangChain (cross-cutting) | `langchain-ledgerproof` (existing) | `@ledgerproof/langchain` | Callback handler + chain builder |

Each is a thin layer (< 500 lines) that:
1. Computes the receipt's `output_hash` over the model response
2. Classifies the receipt's Article 50 sub-clause based on output type
3. Populates `system_metadata` with the model deployment context
4. Calls the LedgerProof SDK to issue the receipt
5. Returns the original model response unchanged

The connectors are **zero-impact** on the model API surface — drop-in replacements for the SDK imports.

---

## Connector pattern (canonical example: OpenAI)

```python
# Before
from openai import OpenAI
client = OpenAI(api_key=...)
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)

# After
from ledgerproof_openai import OpenAI  # wraps openai.OpenAI
client = OpenAI(
    api_key=...,
    ledgerproof_client=ledgerproof.Client(api_key=...),
    article50_subclause="50(1)",  # or "auto" — see below
)
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)
# Receipt issued in the background; receipt_id available on response.ledgerproof.receipt_id
```

The `response` object retains the OpenAI SDK's exact return shape, with a `.ledgerproof` attribute added.

### `article50_subclause="auto"` behavior

Auto-classification rules (sequential):
1. If the response is structured chat that includes a user-facing reply → `50(1)` chatbot disclosure
2. If the response includes image, audio, or video generation → `50(2)` synthetic media labeling
3. If the response is text generation likely to be public-facing → `50(4)` AI-generated text labeling
4. Otherwise → unclassified; receipt still issues but with `article50_subclause=null`

Auto-classification is conservative — it errs toward `50(1)` for ambiguous cases. Customers may override per-call.

---

## Per-connector specifics

### `ledgerproof-openai`

Supports:
- `chat.completions.create` (sync + async + streaming)
- `images.generate` → automatically classified as 50(2)
- `audio.speech.create` → 50(2)
- `embeddings.create` → no receipt by default (embeddings are not Article-50 outputs); opt-in via flag

Streaming responses: receipt is issued at stream completion, not per chunk. The final receipt's `output_hash` covers the assembled content.

### `ledgerproof-anthropic`

Supports:
- `messages.create` (sync + async + streaming)
- Tool-use responses: receipt covers the full tool-augmented response, including tool calls and results
- `messages.batches.create` (Anthropic Batch API): receipts issued per completed batch entry

### `ledgerproof-azure-openai`

Supports:
- All OpenAI capabilities via Azure
- Auto-population of `system_metadata.deployment` with the Azure deployment ID
- Special handling for Microsoft Purview integration (emits Purview lineage events)

### `ledgerproof-bedrock`

Supports:
- `invoke_model` for all Bedrock-hosted models (Claude, Llama, Mistral, Cohere, Stability)
- Model identifier auto-extracted to `system_metadata.model_arn`
- AWS SigV4 auth preserved through wrapper

### `ledgerproof-vertex`

Supports:
- Gemini 1.5/2.0 generation
- Vertex AI Prediction custom-model endpoints
- Generative AI Studio outputs
- Workspace Add-on (Docs/Sheets/Slides/Gmail Gemini calls) via separate sub-package

### `langchain-ledgerproof` 1.2

- Backwards-compatible with 1.1 callback handler API
- Adds `chain.with_ledgerproof(client, **opts)` builder method (LCEL-friendly)
- Integrates with LangSmith: receipt_id attached to LangSmith trace metadata
- New v1.2 profile support: chains can declare their profile per-step
- Async + sync paths

---

## Packaging and release

Each connector lives in its own repo:
- `github.com/ledgerproof/ledgerproof-openai-py`
- `github.com/ledgerproof/ledgerproof-openai-ts`
- ... etc.

All are Apache 2.0. SBOM published per release. Connectors depend on the base SDK with version pin `>=1.1,<2.0`.

**Release cadence:** Major version locked to base SDK major. Connectors track minor releases of the upstream model SDK (e.g., `ledgerproof-openai` minor release follows OpenAI SDK minor release with ≤ 2-week lag).

---

## Marketplace integration

These connectors are what the AWS / Azure / GCP marketplace listings reference. The "30-minute time to first receipt" claim depends on them. The marketplace starter kits import these connectors as their integration shape.

The Azure listing's Microsoft Purview integration callout depends specifically on `ledgerproof-azure-openai` emitting Purview events. That code path must be the highest-tested.

---

## Pre-1.0 gates

- [ ] Each connector has live API integration tests run nightly in CI (cost budget: ~$200/month total)
- [ ] Each connector's docs include a 50-line working example
- [ ] Auto-classification rules documented with a decision flowchart
- [ ] Each connector's auto-issued receipts verified by the verifier portal in CI
- [ ] LangChain matrix tests pass against the 3 most recent minor versions
- [ ] Streaming response receipt issuance tested for partial-stream-failure scenarios
- [ ] Per-connector benchmark: p99 overhead measured and posted in connector README

---

## Open questions

1. **OpenTelemetry integration.** Should connectors emit OTel spans by default? **Recommend opt-in flag; default off to avoid surprising customers' tracing pipelines.**
2. **Tool-use receipt semantics.** When an Anthropic response includes tool calls, does each tool result get its own receipt? **Recommend no for v1.0 — one receipt covers the full tool-augmented response. Sub-receipts for tool results land in v2.0.**
3. **Embedding receipt opt-in.** Default is no receipt for embeddings. Is there a customer that needs them? **No customer ask so far. Stay opt-in.**
4. **Bedrock Knowledge Bases integration.** Bedrock KB retrievals are technically AI-touched. Receipt or not? **Recommend receipt at KB-augmented inference time, not at retrieval. Document.**
5. **Connector for AI agent frameworks (CrewAI, AutoGen, etc.).** Out of scope for Day 90. **Revisit at Day 180 based on customer demand.**
