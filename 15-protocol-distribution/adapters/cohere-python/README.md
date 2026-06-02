# ledgerproof-cohere

LedgerProof adapter for the [Cohere Python SDK](https://github.com/cohere-ai/cohere-python) (V2).

Emits **side-channel cryptographic transparency receipts** for AI-touched interactions, suitable as an evidence layer
for **EU AI Act Article 50** (transparency obligations for providers and deployers of AI systems).

This adapter works with anyone using the Cohere SDK directly, including:

- `cohere.ClientV2` / `cohere.AsyncClientV2`
- Cohere RAG pipelines using `Embed` + `Rerank` + grounded `chat()` (`rag_response/v1` receipts)
- Multi-language EU deployments where Article 50(5) requires disclosure in a language the recipient understands
  (`multilingual_disclosure/v1` receipts capturing the BCP-47 language tag and hash of the disclosure shown)

## Why this matters for EU enterprise

Cohere is the AI provider of choice for many Tier-1 EU enterprise RAG deployments — multilingual support across
DE/FR/IT/NL/ES, on-prem and private-cloud deployment options, and a Canadian (EU-friendly) data residency story.
This adapter is built around two surfaces that EU compliance teams care about most:

1. **Retrieval attestation** — When a grounded `chat()` call cites retrieved documents (Cohere Embed + Rerank
   pipeline), the `rag_response/v1` receipt binds the SHA-256 of each document and its rerank relevance score
   into the signed receipt. This lets a CRO/CCO answer the question *"can you prove the model saw exactly these
   sources and no others?"* with cryptographic evidence rather than logs.
2. **Multilingual disclosure binding** — Article 50(5) requires that the AI-interaction disclosure be made *"in
   a clear and distinguishable manner... in [the] official language of [the relevant Member State]"*. The
   `multilingual_disclosure/v1` receipt records the BCP-47 language tag and a hash of the exact disclosure
   string shown, so a deployer operating across DE / FR / IT can prove per-jurisdiction language compliance
   without storing the user's locale or other PII.

## 5-minute quickstart

```bash
pip install ledgerproof-cohere
export COHERE_API_KEY=...
```

```python
from ledgerproof_cohere import LedgerProofCohere, LogEmitter

client = LedgerProofCohere(
    deployer_id="acme-corp-eu",
    emitter=LogEmitter(),
)

response = client.chat(
    model="command-a-03-2025",
    messages=[{"role": "user", "content": "Hello"}],
)

print(response.message.content[0].text)
# Receipt has already been emitted to the side-channel.
```

The Cohere response object is returned **unchanged**. The receipt is emitted to the side channel only (C7).

## Three integration patterns

1. **Client wrapper** (recommended) — `LedgerProofCohere` wraps `cohere.ClientV2` and intercepts `chat()` /
   `chat_stream()`. Sync, async, streaming, RAG (`chat_with_retrieved_documents()`), and multilingual
   disclosure (`chat_with_disclosure()`) are all supported.
2. **Decorator** — `@lpr_track(deployer_id="...")` for user-defined functions that wrap Cohere calls. Supports
   declaring kwargs that hold retrieved documents or a disclosure ref for schema promotion.
3. **Manual emission** — `emit_receipt(response, deployer_id, regulatory_context)` for full control inside a
   custom orchestration layer (Embed-only flows, Classify pipelines, batch Rerank).

See `examples/` for runnable code:

- `examples/01_chat_v2_quickstart.py` — vanilla `ClientV2.chat()`
- `examples/02_rag_with_rerank.py` — Embed + Rerank + grounded chat with `rag_response/v1`
- `examples/03_multilingual_disclosure.py` — `multilingual_disclosure/v1` across DE / FR / IT

## Architectural discipline (C1–C8)

This adapter is implemented under the LedgerProof protocol's load-bearing constraints:

- **C1**: No claim of regulator endorsement. No claim of Article 40 presumption of conformity.
- **C4**: Local verification only. The adapter does **not** phone home to LedgerProof servers during normal operation.
- **C6**: Stream-aware signing. Streaming chats are signed using an incremental SHA-256 over `content-delta`
  text deltas; multibyte UTF-8 (German umlauts, French accents, etc.) is handled correctly.
- **C7**: Side-channel emission only. The adapter **cannot and does not modify** the Cohere response payload.

## GDPR posture

Receipts reference content by SHA-256 hash only. The adapter **does not store** raw prompts, raw responses, raw
retrieved-document text, or raw disclosure strings. Identifiers (`deployer_id`, `document_id`, `tool_call_id`)
are length-bounded and character-set-restricted (no free-form PII). The deployer is responsible for ensuring
the inputs they feed in (e.g. `document_id` values) do not themselves leak PII.

## Scope disclaimer

LedgerProof provides an **evidence layer for Article 50 transparency obligations only**.

It does **not** cover:

- Article 9 (risk management system)
- Article 10 (data and data governance)
- Article 13 (transparency and information to deployers)
- Article 15 (accuracy, robustness, and cybersecurity)
- Article 72 (post-market monitoring)

LedgerProof does **not** confer presumption of conformity under Article 40. LedgerProof is not endorsed by the
European Commission, the AI Office, any national competent authority, or Cohere Inc.

This adapter wraps the official Cohere Python SDK; it is not affiliated with Cohere Inc.

## License

Apache 2.0. Copyright 2026 LedgerProof Foundation (in formation: US 501(c)(3) Delaware + Dutch Stichting EU subsidiary).
