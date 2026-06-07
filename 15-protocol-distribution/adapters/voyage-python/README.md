# ledgerproof-voyage

LedgerProof adapter for the [Voyage AI Python SDK](https://github.com/voyage-ai/voyageai-python) (embeddings + rerank).

Emits **side-channel cryptographic transparency receipts** that capture the upstream retrieval evidence
(embeddings, rerank scores) feeding a downstream chatbot, suitable as an evidence layer for the
**EU AI Act Article 50** RAG pipeline scenario.

This adapter is **not endorsed by Voyage AI** or MongoDB. It wraps the official `voyageai` SDK; it is not
affiliated with Voyage AI Inc. or MongoDB Inc.

## Why an embeddings adapter for an Article 50 protocol?

Voyage AI is **upstream RAG infrastructure**. Calls to `voyageai.Client.embed()` and
`voyageai.Client.rerank()` are **not themselves** direct Article 50(1) "AI system intended to interact
directly with natural persons" surfaces — they are retrieval-side substrate.

But they are the **evidence trail** for any RAG pipeline whose downstream chatbot output **is** under
Article 50. When a regulator (or an internal auditor, or a litigant) asks the load-bearing question
*"what sources did the model see, and how did they get there?"*, the answer is a chain:

```
user query
  -> Voyage embed(query)              [embedding_inference/v1]
  -> Voyage embed(documents)          [embedding_inference/v1]
  -> ANN retrieval (vector DB)        [out of scope]
  -> Voyage rerank(query, candidates) [rerank_inference/v1]
  -> downstream chatbot turn          [bound by rag_pipeline_evidence/v1]
```

This adapter signs each link of that chain locally (constraint C4) so the full provenance is verifiable
offline from the stored signed receipts. The downstream chatbot turn is captured by the matching
LedgerProof chat adapter (`ledgerproof-openai`, `ledgerproof-anthropic`, `ledgerproof-cohere`, etc.) and
both are stitched together by a `rag_pipeline_evidence/v1` envelope.

This positioning matters because **most Tier-1 EU enterprise AI deployments under Article 50 enforcement
(2 August 2026) are RAG-shaped**, and the regulator's first incident-response question is invariably
"what evidence does the model have?". A signed Voyage embedding + rerank receipt is the cryptographic
answer.

## 5-minute quickstart

```bash
pip install ledgerproof-voyage
export VOYAGE_API_KEY=...
```

```python
from voyage_ledgerproof import LedgerProofVoyage, LogEmitter

client = LedgerProofVoyage(
    deployer_id="acme-corp-eu",
    emitter=LogEmitter(),
)

result = client.embed(
    texts=["Article 50 transparency obligations apply from 2 August 2026."],
    model="voyage-3-large",
    input_type="document",
)

print(result.embeddings[0][:4], "...")
# Receipt has already been emitted to the side-channel.
```

The Voyage `EmbeddingsObject` is returned **unchanged**. The receipt is emitted to the side channel only
(C7).

## Three schemas

| Schema | Article 50 mapping | What it binds |
| --- | --- | --- |
| `embedding_inference/v1` | Supporting infrastructure | per-input SHA-256, per-vector SHA-256, vector dim, model_id, input_type |
| `rerank_inference/v1` | Supporting infrastructure | query SHA-256, per-candidate SHA-256, relevance scores, post-rerank order, model_id |
| `rag_pipeline_evidence/v1` | Article 50(1) variant | upstream embed + rerank receipt hashes -> downstream chat receipt hash + user query hash |

`embedding_inference/v1` and `rerank_inference/v1` carry
`regulatory_context.article_50_paragraph = "supporting"` — they are not Article 50(1) artefacts in
themselves. `rag_pipeline_evidence/v1` carries `"1"` because that is the regulated user-facing turn.

## Three integration patterns

1. **Client wrapper** (recommended) — `LedgerProofVoyage` wraps `voyageai.Client` and intercepts
   `embed()` and `rerank()`. Sync and async (`LedgerProofAsyncVoyage`) supported.
2. **Decorator** — `@lpr_track_embed(deployer_id=..., model=...)` and
   `@lpr_track_rerank(deployer_id=..., model=...)` for user-defined functions wrapping Voyage calls.
3. **Manual emission** — `emit_embedding_receipt(...)`, `emit_rerank_receipt(...)`, and
   `emit_rag_pipeline_receipt(...)` for full control inside a custom RAG orchestration layer.

See `examples/`:

- `examples/01_voyage_embed_quickstart.py` — vanilla `embed()`
- `examples/02_voyage_rerank.py` — `rerank()` with relevance-score binding
- `examples/03_rag_pipeline_evidence.py` — full embed -> rerank -> (downstream chat stub) -> `rag_pipeline_evidence/v1`

## Architectural discipline (C1–C8)

This adapter is implemented under the LedgerProof protocol's load-bearing constraints:

- **C1**: **No claim of regulator endorsement. No claim of Article 40 presumption of conformity. Not
  endorsed by Voyage AI Inc. or MongoDB Inc.** This adapter wraps the official Voyage Python SDK; it is
  not affiliated with either company.
- **C4**: Local verification only. The adapter does **not** phone home to LedgerProof servers during
  normal operation. Signed receipts verify offline given the public key.
- **C6**: Stream-aware signing primitives are exposed for downstream chat adapters. Voyage's own surfaces
  (`embed`, `rerank`) are non-streaming today.
- **C7**: Side-channel emission only. The adapter **cannot and does not modify** the Voyage response
  payload. The `EmbeddingsObject` / `RerankingObject` is returned unchanged.

## GDPR posture

Receipts reference content by SHA-256 hash only. The adapter **does not store**:

- raw input texts to `embed()`
- raw document text fed to `rerank()`
- raw embedding vectors (the vector is canonicalized to big-endian float64 and hashed; the hash is
  stored, not the vector)
- raw user queries fed into the downstream chatbot

Identifiers (`deployer_id`, `document_id`, `tool_call_id`) are length-bounded and character-set-
restricted (no free-form PII). The deployer is responsible for ensuring the inputs they feed in
(e.g. `document_id` values) do not themselves leak PII.

## Vector canonicalization

Embedding vectors are canonicalized to **IEEE-754 big-endian float64** byte strings before hashing. This
is portable across machines, Python versions, and operating systems. A verifier with the original vector
can recompute `SHA-256(canonicalize_vector(vector))` and compare to `vector_sha256_hex` in the receipt.

Voyage exposes `output_dtype=` for higher-precision dtypes (`int8`, `uint8`, `binary`, `ubinary`); the
adapter records the requested `output_dtype` on `VoyageModelRef.output_dtype` for transparency, but
always canonicalizes through float64 for one stable wire format.

## Scope disclaimer

LedgerProof provides an **evidence layer for Article 50 transparency obligations only**.

It does **not** cover:

- Article 9 (risk management system)
- Article 10 (data and data governance)
- Article 13 (transparency and information to deployers)
- Article 15 (accuracy, robustness, and cybersecurity)
- Article 72 (post-market monitoring)

LedgerProof does **not** confer presumption of conformity under Article 40. LedgerProof is not endorsed
by the European Commission, the AI Office, any national competent authority, **Voyage AI Inc., or
MongoDB Inc.**

This adapter wraps the official `voyageai` Python SDK; it is not affiliated with Voyage AI Inc. or
MongoDB Inc.

## License

Apache 2.0. Copyright 2026 LedgerProof Foundation (in formation: US 501(c)(3) Delaware + Dutch Stichting
EU subsidiary).
