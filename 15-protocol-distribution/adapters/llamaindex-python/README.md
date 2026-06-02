# ledgerproof-llamaindex

LedgerProof callback handler for [LlamaIndex](https://www.llamaindex.ai/). Emits cryptographically signed, Bitcoin-anchorable **EU AI Act Article 50 transparency receipts** for RAG queries, chat sessions, and agent workflows — without modifying your LlamaIndex response payload.

> **Status:** v0.1.0 — MVP. APIs may change before v1.0.

---

## What this is

LedgerProof is an open cryptographic protocol that:

1. Emits a signed receipt for every AI-touched interaction.
2. Batches receipts into a Merkle tree.
3. Anchors the tree root to Bitcoin via OP_RETURN.
4. Verifies offline from Bitcoin chain + protocol public key + receipt alone.

This package wires LedgerProof into LlamaIndex via the standard `CallbackManager` interface. Receipts emit to a **side channel** (log, queue, or webhook) — your LLM/RAG response is byte-for-byte unchanged.

## What this is NOT

Read this carefully before deploying.

- **No claim of regulator endorsement.** Neither the EU AI Office, ENISA, nor any Member State authority has endorsed this adapter or the LedgerProof protocol.
- **No Article 40 presumption of conformity.** LedgerProof is not a harmonised standard. Use of this adapter does not create a presumption of conformity with the AI Act.
- **Scope is narrow.** This adapter provides an **evidence layer for Article 50** (transparency obligations for providers and deployers of certain AI systems). It does NOT cover:
  - Article 9 (risk management system)
  - Article 10 (data and data governance)
  - Article 13 (transparency and provision of information to deployers)
  - Article 15 (accuracy, robustness, cybersecurity)
  - Article 72 (post-market monitoring)
- **No LlamaIndex Inc. affiliation.** This is an independent integration. LlamaIndex is a registered trademark of LlamaIndex, Inc.

## Install

```bash
pip install ledgerproof-llamaindex
```

For the RAG examples:

```bash
pip install "ledgerproof-llamaindex[examples]"
```

## 5-minute quickstart (RAG)

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.callbacks import CallbackManager

from ledgerproof_llamaindex import LedgerProofCallbackHandler
from ledgerproof_llamaindex.emitter import LogEmitter
from ledgerproof_llamaindex.signer import Ed25519Signer

handler = LedgerProofCallbackHandler(
    deployer_id="acme-bank-eu",
    signer=Ed25519Signer.ephemeral(),  # production: HSM-backed
    emitter=LogEmitter(),
    article="50(1)",  # disclosure: user interacting with AI
)
Settings.callback_manager = CallbackManager([handler])

docs = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(docs)
query_engine = index.as_query_engine()

response = query_engine.query("What is the refund policy?")
print(response)  # response payload is UNCHANGED
# Receipt has been emitted to the configured side channel.
```

## C1–C8 protocol discipline

This adapter respects the LedgerProof protocol invariants:

| Invariant | Enforcement here |
|---|---|
| **C1** No regulator-endorsement claims | Documented above; no marketing copy in code paths |
| **C4** Local verification only | Adapter never phones home to LedgerProof servers in normal operation |
| **C6** Stream-aware signing | Transcript hash committed on event-start, signed on event-end. Streaming bodies are not buffered |
| **C7** Side-channel emission | The LlamaIndex response object is never mutated. Receipts emit to log/queue/webhook only |

## Emitters

```python
from ledgerproof_llamaindex.emitter import LogEmitter, WebhookEmitter, QueueEmitter

LogEmitter()                                    # writes JSON to a Python logger
WebhookEmitter("https://receipts.acme.eu/v1")   # POSTs canonical CBOR
QueueEmitter(my_queue)                          # puts onto any queue.Queue
```

## Receipt schemas

- `rag_chatbot_session/v1` — Article 50(1) RAG chatbot disclosure with retrieval-context hash.
- `generated_content/v1` — Article 50(2) generated-content marking.
- `rag_synthesized_response/v1` — Article 50(1) synthesized response with source attribution.

See `ledgerproof_llamaindex/schema.py`.

## Production hardening checklist

The MVP ships with **ephemeral** signing keys. Before production:

- [ ] Replace `Ed25519Signer.ephemeral()` with HSM-backed key (AWS KMS / GCP Cloud HSM / on-prem Luna).
- [ ] Move from `LogEmitter` to `QueueEmitter` or `WebhookEmitter` with retry + dead-letter.
- [ ] Configure your Merkle-batcher + Bitcoin anchorer (separate service; not part of this adapter).
- [ ] Run GDPR DPIA on `deployer_id` and any `subject_pseudonym` fields.
- [ ] Pin `ledgerproof-llamaindex` and `llama-index-core` versions in your lockfile.

## License

Apache License 2.0. See `LICENSE`.

## Foundation

LedgerProof is stewarded by the **LedgerProof Foundation** — a US 501(c)(3) Delaware non-profit (in formation) with a Dutch Stichting EU subsidiary (in formation). The protocol specification and reference adapters are open-source.

Contact: engineering@ledgerproof.org
