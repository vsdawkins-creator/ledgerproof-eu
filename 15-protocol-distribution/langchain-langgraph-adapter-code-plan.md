# LangChain / LangGraph Adapter — Full Code Build-Out Plan

**Document version**: v1.0
**Drafted**: Tuesday June 2, 2026
**Owner**: Veronica → Senior Protocol Engineer (target hire Jul 13)
**Operating reference**: `14-seed-close-pack/04-atomic-explosion-master-plan.md`
**Brand-discipline references**: C2, C4, C6, C7 from `ops-state.json`
**Target ship dates**: MVP v0.1 by Jun 27 (pre-launch); v1.0 by Aug 2 (Article 50 enforcement); v1.1 by Sep 30

---

## Why this exists

LangChain is the de-facto LLM orchestration framework. LangSmith is its commercial observability platform. They cover Articles 9 / 12 / 13 / 14 / 15 / 72 of the EU AI Act through internal observability primitives. They **structurally cannot** cover Article 50 because their evidence chain terminates inside the auditee's perimeter and Article 50 obligations are owed to externals — natural persons and supervisory authorities.

This adapter is the integration that sits between LangChain's orchestration plane and LedgerProof's evidence plane. It emits an LPR (LedgerProof Protocol) receipt at every Article 50 trigger point in a LangChain pipeline — chatbot disclosure, synthetic-content generation, human-in-the-loop editorial review — without modifying the response payload (C7), without requiring per-request HSM signing (C6), and without phoning home to LedgerProof Inc. (C4).

It is the single highest-leverage piece of code in the Aug 2 roadmap because every existing LangSmith customer becomes a potential LedgerProof co-deployment with one import statement.

---

## Architectural design — six load-bearing decisions

| # | Decision | Why | C-reference |
|---|----------|-----|-------------|
| 1 | **LangChain callback handler + LangGraph node middleware (dual-target)** | LangChain has migrated to LangGraph for production agents; callback handlers are legacy. Both surfaces must be supported. Targeting only callbacks ships against last-generation architecture. | C7 |
| 2 | **Side-channel receipt emission (queue / webhook / log) — NOT response-payload modification** | LangChain callback handlers are side-effect-only. They cannot modify the response. Receipts must emit to a separate channel (configurable: in-process queue, Kafka, AWS SQS, webhook, file log). | C7 |
| 3 | **Stream-aware signing (commit on stream-start, sign on stream-end) — NOT body buffering** | LangChain pipelines stream tokens. Buffering the full response to sign it adds 50-200ms p99 latency and breaks streaming UX. Commit a transcript hash on stream-start; sign the completed receipt on stream-end. | C6 |
| 4 | **Merkle-batch signing — NOT per-request HSM** | HSM per-signature latency is 5-50ms. At AI inference rates (100-10,000 req/s) this is prohibitive. Batch N receipts into a Merkle tree per anchoring window (default 60 min, configurable to 10 min); HSM signs the root once; individual receipts include inclusion proofs. | C6 |
| 5 | **Local verification only — LedgerProof nodes are optional convenience** | The adapter must NOT phone home to LedgerProof Inc. infrastructure during normal operation. Verification of any emitted receipt requires only the Bitcoin chain, the published protocol public key, and the receipt itself. | C4 |
| 6 | **Partnership-first, framework-fork-fallback** | Approach LangChain Inc. as integration partner via Harrison Chase / BD outreach. If declined, ship as community integration outside main; pursue LlamaIndex Inc. partnership as primary alternate. | C3, KS7 |

---

## Package architecture

### Python package: `ledgerproof-langchain`

**Distribution**: PyPI under `ledgerproof-langchain`
**License**: Apache 2.0
**Repo**: `github.com/ledgerproof/ledgerproof-langchain`
**Python compatibility**: 3.10+
**Dependencies**:
- `ledgerproof >= 1.1.1rc0` (the core SDK; not yet GA — adapter co-releases with core)
- `langchain-core >= 0.3.0`
- `langgraph >= 0.2.0` (only if LangGraph node middleware is imported)
- `cryptography >= 41.0` (Ed25519)
- `cbor2 >= 5.0` (canonical encoding)
- `requests >= 2.31` (optional — for webhook side-channel)
- `aiokafka >= 0.10` (optional — for Kafka side-channel)
- `boto3 >= 1.34` (optional — for AWS SQS side-channel)

**Directory layout**:
```
ledgerproof-langchain/
├── README.md                      — 10-min quickstart + production deployment notes
├── LICENSE                        — Apache 2.0
├── pyproject.toml                 — package metadata + dependencies
├── ledgerproof_langchain/
│   ├── __init__.py
│   ├── callback_handler.py        — LedgerProofCallbackHandler (BaseCallbackHandler subclass)
│   ├── langgraph_middleware.py    — node decorator for LangGraph state machines
│   ├── schema.py                  — LPR canonical schemas (chatbot_session, generated_content, human_review)
│   ├── transcript_hasher.py       — incremental SHA-256 for streaming responses
│   ├── batcher.py                 — Merkle-batch accumulator with configurable window
│   ├── signer.py                  — Ed25519 signer; HSM-backed if configured
│   ├── emitter.py                 — side-channel adapter (queue / webhook / log / SIEM)
│   ├── verifier.py                — local-only verification (no network)
│   ├── config.py                  — config schema (env vars + YAML + Python)
│   └── exceptions.py              — typed errors
├── examples/
│   ├── 01_chatbot_quickstart.py        — 5-min chatbot session disclosure example
│   ├── 02_synthetic_content.py         — Article 50(2) generated-content receipt
│   ├── 03_langgraph_editorial.py       — Article 50(4) human-review editorial workflow
│   ├── 04_streaming_chat.py            — stream-aware signing demonstration
│   ├── 05_production_hsm.py            — production deployment with AWS CloudHSM
│   └── 06_siem_export.py               — Splunk + Datadog + Vanta side-channel
├── tests/
│   ├── conftest.py
│   ├── test_callback_handler.py
│   ├── test_langgraph_middleware.py
│   ├── test_canonical_encoding.py      — cross-language conformance (matches Python core SDK)
│   ├── test_merkle_batch.py
│   ├── test_streaming_consistency.py
│   ├── test_no_network_during_verify.py — load-bearing: verification must NOT make any network call
│   └── conformance/
│       └── test_vectors_v1_1.json       — protocol conformance vectors
├── docs/
│   ├── index.md
│   ├── quickstart.md                   — 10-min walkthrough
│   ├── production_deployment.md        — HSM, anchoring pipeline, side-channel choices
│   ├── article_50_mapping.md           — which receipt schema maps to which Article 50 subsection
│   ├── api_reference.md                — generated from docstrings
│   ├── faq.md                          — including "what about LangSmith?"
│   └── migration_from_langsmith.md     — for teams already on LangSmith
└── .github/
    ├── workflows/
    │   ├── ci.yml                       — tests + conformance + lint
    │   ├── release.yml                  — PyPI publish + SLSA L3 provenance
    │   └── conformance.yml              — daily run against latest core SDK
    └── ISSUE_TEMPLATE/
```

### TypeScript package: `@ledgerproof/langchain`

**Distribution**: npm under `@ledgerproof/langchain`
**License**: Apache 2.0
**Repo**: `github.com/ledgerproof/ledgerproof-langchain-js`
**Node compatibility**: 20+ (Node 22 preferred)
**Mirror of Python package** — same architecture, idiomatic TypeScript.

Key differences:
- Uses `@langchain/core ^0.3.0` and `@langchain/langgraph ^0.2.0`
- Uses `@noble/ed25519@2.3.0` (NOT 3.x — pinned per master plan)
- Uses `@noble/hashes@1.8.0` (pinned)
- ESM-first with CJS compatibility shim

---

## Phase 1 — MVP shipped by Friday June 27 (pre-launch)

**Goal**: A working callback handler that emits an LPR receipt to a configurable side channel on stream-end of any LangChain LLM call. No HSM. No batching. No LangGraph yet. Just the minimum demonstrable code that lets V attach the working adapter to her partnership outreach to Harrison Chase the same week.

### Deliverables

1. **`ledgerproof_langchain.callback_handler.LedgerProofCallbackHandler`** — subclass of `BaseCallbackHandler`. Implements `on_llm_start` (capture transcript hash + context), `on_llm_end` (finalize receipt + sign + emit). Sign with an ephemeral Ed25519 key for the MVP (HSM in Phase 4).

2. **`schema.py`** — one schema only: `chatbot_session/v1` covering Article 50(1) disclosure event. Fields: `interaction_id`, `model_id`, `prompt_hash`, `response_hash`, `disclosure_text_hash`, `deployer_id`, `timestamp_ns`, `regulatory_context`, `langchain_run_id`. GDPR safety: schema validator rejects email-shaped values in `deployer_id` and `disclosure_text_hash` is a hash, not the text itself.

3. **`emitter.py`** — three side-channel implementations: `LogEmitter` (writes JSON-lines to a configurable file path), `WebhookEmitter` (POSTs to a URL), `QueueEmitter` (puts to an in-process `queue.Queue`).

4. **`examples/01_chatbot_quickstart.py`** — minimal demonstration:
   ```python
   from langchain_anthropic import ChatAnthropic
   from ledgerproof_langchain import LedgerProofCallbackHandler

   handler = LedgerProofCallbackHandler(
       deployer_id="acme-corp-prod",
       regulatory_context="eu-ai-act-article-50-1",
       emit_to="webhook",
       webhook_url="https://siem.acme.com/ai-receipts",
   )

   llm = ChatAnthropic(model="claude-opus-4-1", callbacks=[handler])
   response = llm.invoke("Hello, are you an AI?")
   # Receipt emitted to https://siem.acme.com/ai-receipts on stream-end
   ```

5. **Test suite**: 12 unit tests covering callback firing, canonical encoding determinism, signature verification, side-channel emission, GDPR validator rejection, no-network-during-verify, and stream-aware hash consistency.

6. **README.md** with the 5-minute quickstart + the C1-C8 discipline statement (specifically: no claim of Article 9/10/13/15/72 coverage; no claim of regulator endorsement; no presumption of conformity).

7. **PyPI release `0.1.0`** + GitHub release tagged `v0.1.0` + SLSA L3 provenance via `slsa-github-generator`.

### Out of scope for Phase 1

- LangGraph node middleware (Phase 2)
- HSM signing (Phase 4)
- Merkle batching (Phase 2)
- TypeScript adapter (Phase 3)
- SIEM-specific connectors beyond generic webhook (Phase 3)
- Production verification CLI (Phase 4)

### Owner + schedule

**Owner**: Veronica directly (with senior protocol engineer interview help)
**Engineering hours**: ~25 hours over 3 days (Wed Jun 18 – Fri Jun 20 OR Mon Jun 23 – Wed Jun 25, depending on seed-close timing)
**Reviewer**: Mathias Lafeldt (existing ops contractor) or one of the senior protocol engineer interview candidates as a paid trial task

### Success criteria

- Working `pip install ledgerproof-langchain==0.1.0` on a fresh venv
- Quickstart runs end-to-end on Python 3.11 with `langchain-anthropic`, `langchain-openai`, and `langchain-mistralai`
- A receipt emitted by the MVP can be verified offline using the core `ledgerproof` Python SDK
- README + quickstart pass V's pre-publish C1-C8 discipline check
- GitHub repo public under the Foundation org by Sat Jun 28

---

## Phase 2 — LangGraph node middleware + Merkle batching (Jun 28 – Jul 18)

**Goal**: LangGraph support (the current LangChain production surface) + asynchronous Merkle-batch signing that handles production AI inference rates without per-request HSM cost.

### Deliverables

1. **`ledgerproof_langchain.langgraph_middleware.lpr_receipt_node`** — a LangGraph node decorator that wraps any node and emits an LPR receipt on resume edge. Specifically targets the `human_review` resume edge for Article 50(4) editorial-control receipt, but works on any node.

   ```python
   from langgraph.graph import StateGraph
   from ledgerproof_langchain import lpr_receipt_node

   workflow = StateGraph(AgentState)

   @lpr_receipt_node(
       schema="human_review/v1",
       deployer_id="acme-corp-prod",
   )
   def editorial_review(state):
       # Human pauses here, reviews, sets state['editor_approval'] = True
       return state

   workflow.add_node("editorial_review", editorial_review)
   # On resume, an LPR receipt is emitted recording: reviewer_role, review_rationale_hash, decision, timestamp.
   ```

2. **`batcher.py`** — `MerkleBatcher` class that accumulates receipts over a configurable time window (default 60 min) OR a configurable size threshold (default 1000 receipts), whichever comes first. On flush, builds Merkle tree, signs root with Ed25519, emits individual receipts with inclusion proofs.

3. **Three new schemas**:
   - `generated_content/v1` — Article 50(2) machine-readable marking of synthetic content
   - `human_review/v1` — Article 50(4) editorial-control event
   - `disclosure_assertion/v1` — Article 50(1) end-user notification recorded at the orchestration layer rather than at the LLM call

4. **`examples/03_langgraph_editorial.py`** — full LangGraph state machine with `interrupt` + `lpr_receipt_node` + side-channel emission. Demonstrates the Article 50(4) editorial-control exception workflow end-to-end.

5. **Conformance test vectors** — JSON file with N test cases. Each case: input → expected canonical bytes → expected hash. The adapter's tests verify it produces the same hashes as the core Python SDK and the Rust `quantum-edge-2` reference implementation. Cross-language conformance test.

6. **Async batching tests** — verify that under load (1k req/s simulated), the batcher does not lose receipts, does not exceed memory bounds, and flushes on window-close even under low load.

7. **PyPI release `0.2.0`** + GitHub release.

### Owner + schedule

**Owner**: Senior Protocol Engineer (starting Jul 13 per master plan)
**Engineering hours**: ~80 hours over 3 weeks (Jul 13 – Aug 1)
**Reviewer**: Veronica + Foundation Technical Steering Committee (when seated)

### Success criteria

- LangGraph editorial-review example runs end-to-end including a human pause + resume
- Merkle batcher handles 1k req/s without dropping receipts in stress test
- Cross-language conformance: same input → same canonical hash in Python adapter, Python core SDK, Rust quantum-edge-2
- GitHub releases public by Aug 1
- Senior protocol engineer signs off

---

## Phase 3 — TypeScript adapter + SIEM connectors (Aug 1 – Aug 31)

**Goal**: Bring TypeScript / JavaScript LangChain users into scope (the larger of the two LangChain ecosystems). Ship pre-built SIEM side-channel connectors so enterprise deployers don't have to build their own webhook + parsing layer.

### Deliverables

1. **`@ledgerproof/langchain` npm package** — TypeScript port of the Python package. Identical API surface, idiomatic TS. ESM-first.

2. **SIEM connectors** — drop-in side-channel emitters for the six most common enterprise SIEM/compliance platforms:
   - `SplunkHECEmitter` — HTTP Event Collector format
   - `DatadogLogsEmitter` — Datadog logs intake API
   - `ElasticECSEmitter` — Elastic Common Schema-formatted events
   - `ServiceNowGRCEmitter` — ServiceNow GRC integration via REST API
   - `VantaEmitter` — Vanta audit-event API
   - `DrataEmitter` — Drata control-evidence API

3. **`examples/06_siem_export.py`** updated to demonstrate all six SIEM connectors with sample configurations.

4. **Browser-side verifier integration** — receipt emitted by the adapter is verifiable by the existing `verify.ledgerproofhq.io` portal. Add a "verify in browser" link to the receipt that points the regulator at the portal pre-populated with the receipt.

5. **PyPI release `0.3.0`** + npm release `0.3.0` + GitHub release.

### Owner + schedule

**Owner**: Senior Protocol Engineer + Foundation DevRel contractor (target hire Aug 15)
**Engineering hours**: ~120 hours over 4 weeks (Aug 1 – Aug 28)

### Success criteria

- TypeScript adapter works in a fresh `npm install @ledgerproof/langchain@0.3.0` project
- All six SIEM connectors verified end-to-end with each platform's free-tier or trial environment
- Browser verifier portal round-trip works for any receipt emitted by either Python or TypeScript adapter

---

## Phase 4 — Production HSM hardening (Sep 1 – Sep 30)

**Goal**: Make the adapter production-grade for regulated enterprises. HSM-backed signing keys, anchoring-pipeline integration, full operational tooling.

### Deliverables

1. **HSM backends** (pluggable via `signer.py` interface):
   - `AWSCloudHSMSigner` — Amazon CloudHSM via PKCS#11
   - `AzureDedicatedHSMSigner` — Azure Dedicated HSM via PKCS#11
   - `ThalesLunaSigner` — Thales Luna Network HSM via PKCS#11
   - `YubiHSM2Signer` — YubiHSM 2 for smaller deployments
   - `LocalKeyfileSigner` — for development; explicitly NOT production

2. **Anchoring pipeline integration** — adapter emits batched signed receipts to an anchoring service (either Foundation-operated reference anchor at `anchor.ledgerproofhq.io` OR a self-hosted anchor binary the deployer runs). Includes RBF (Replace-By-Fee) handling and OpenTimestamps fallback.

3. **Production CLI** — `ledgerproof-langchain verify` command for offline verification of a receipt against a local Bitcoin block-header snapshot. Demonstrates the "no LedgerProof in the path" property.

4. **Monitoring + observability hooks** — Prometheus metrics for receipt-emission rate, batch-flush latency, HSM signing latency, side-channel delivery success/failure. Grafana dashboard template.

5. **PyPI release `1.0.0`** + npm release `1.0.0` + GitHub release (GA — out of pre-release).

### Owner + schedule

**Owner**: Senior Protocol Engineer + Foundation Security Advisor (existing fractional)
**Engineering hours**: ~100 hours over 4 weeks

### Success criteria

- Adapter runs in production at one Founding Member deployment under HSM-backed signing
- Anchor pipeline integration verified: receipts emitted by the adapter are anchored to Bitcoin within the configured window
- Production CLI verifies receipts offline against Bitcoin headers without any network call to LedgerProof
- 1.0.0 release published

---

## Phase 5 — LangChain Hub listing + community engagement (Oct 1 – Dec 31)

**Goal**: Sustained adoption. Move from "we built it" to "LangChain devs use it."

### Deliverables

1. **LangChain Hub listing** — submit the adapter as an official LangChain integration. Coordinate with LangChain DevRel for placement in the integrations directory and the Cookbook.

2. **LangChain Cookbook PR** — submit a worked example to the official LangChain Cookbook repo. Example covers Article 50(1) chatbot disclosure + Article 50(4) editorial review in a single LangGraph application.

3. **Joint blog post with LangChain** — co-authored content "The Article 50 evidentiary stack: LangChain + LedgerProof." Published on both blogs.

4. **Reference architecture documents** — three: (a) RAG chatbot with Article 50(1) compliance; (b) AI marketing-content generation with Article 50(2) compliance; (c) AI-generated journalism with Article 50(4) editorial-control compliance.

5. **Conference engagement** — LangChain Interrupt conference 2027 talk submission (if conference exists). Backup: PyCon EU 2027 talk on regulatory-compliance integration patterns for LLM frameworks.

6. **Foundation-funded contributor program** — small grant ($1-5K) per accepted contribution to the adapter from external developers. Builds community ownership beyond Foundation-employed engineers.

### Owner + schedule

**Owner**: Foundation DevRel (full-time hire by Aug 15) + Foundation Executive Director (Aug 1) for institutional engagement
**Hours**: ongoing, ~20-30 hours/week from DevRel through end of year

### Success criteria

- LangChain Hub listing approved and live
- Cookbook PR merged
- Joint blog post published
- 50+ GitHub stars on the adapter repo by end of year
- 3+ external contributors with merged PRs by end of year
- 5+ Founding Member deployments using the adapter in production by end of year

---

## Maintenance + governance model

### Foundation owns the spec; Inc. maintains the adapter

- The adapter's canonical schemas (`chatbot_session/v1`, `generated_content/v1`, etc.) are part of the LPR specification, governed by the Foundation
- The adapter implementation lives in a LedgerProof Inc.-maintained repo (Foundation transferable if/when Foundation operational capacity scales)
- External contributions welcomed under CLA (Contributor License Agreement) that allows Foundation transfer

### Versioning policy

- Adapter version follows semver: `MAJOR.MINOR.PATCH`
- Adapter compatibility matrix published in each release: which LPR protocol version, which LangChain version, which LangGraph version
- Breaking changes only on major version bumps; deprecation warnings for at least one minor cycle
- Backwards-compatibility commitment: any receipt produced by adapter `1.x` remains verifiable by `2.x` and later

### Release cadence

- Patch releases: as needed for bug fixes
- Minor releases: monthly during 1.x; quarterly thereafter
- Major releases: aligned with LPR protocol major versions

### CI/CD

- GitHub Actions for tests, lint, conformance
- Release provenance via `slsa-github-generator` at SLSA L3
- Conformance test vectors auto-run daily against latest core SDK
- Dependabot for dependency updates with auto-merge for non-breaking changes

---

## Dependencies + critical-path risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| LangChain Inc. declines partnership (KS7) | Medium | Ship as community integration; pursue LlamaIndex Inc. as primary alternate; community-driven adoption still possible |
| Senior protocol engineer hire slips past Jul 13 | Medium | Phase 1 MVP V drives directly; Phase 2 can absorb 2-week slip without breaking Aug 2; Phase 3+ slips proportionally |
| LangChain API breaking changes during build-out | Low-Medium | Pin to `langchain-core ^0.3` in `pyproject.toml`; compatibility matrix published per release |
| LangGraph migration ahead of our Phase 2 ship | Low | LangGraph is already production for LangChain users; we're tracking the existing surface, not chasing |
| Foundation-Inc IP license not finalized | Medium (KS2 / KS3 cascade) | Phase 1 publishes under Inc. license; Phase 2+ transfers to Foundation under perpetual royalty-free irrevocable terms |
| Cross-language conformance gap with quantum-edge-2 Rust impl | Medium | LPR-ERRATA-001 lessons learned; conformance test vectors run daily in CI; deterministic encoding is the load-bearing property |
| Production HSM integration takes longer than Phase 4 window | Medium | AWS CloudHSM + YubiHSM2 first (most accessible); Azure + Thales as Q4 work if needed |

---

## Adapter feature → Article 50 sub-obligation mapping

This is the partnership-pitch artifact. When V emails Harrison Chase, this table is the one-page diagram attached.

| Article 50 sub-obligation | LangChain primitive | LedgerProof adapter receipt schema | Evidence type |
|---------------------------|---------------------|----------------------------------|---------------|
| **50(1)** Direct user disclosure | `BaseCallbackHandler.on_llm_start` (capture disclosure context) | `chatbot_session/v1` | Signed receipt of disclosure assertion at session start |
| **50(2)** Synthetic content marking | `BaseCallbackHandler.on_llm_end` (capture generated content hash) | `generated_content/v1` | Out-of-band receipt that the content was AI-generated; content-hash binding |
| **50(3)** Emotion recognition / biometric categorization | `BaseCallbackHandler.on_llm_start` (capture system-class metadata) | `emotion_classification/v1` (v1.2 schema, post-launch) | Signed assertion of system class |
| **50(4)** Deepfake / public-interest text + editorial control | `LangGraph.interrupt` + `lpr_receipt_node` on resume edge | `human_review/v1` | Editorial-control receipt naming the reviewer + decision |
| **50(6)** Manner of disclosure (clear, distinguishable, accessible) | LangChain UI integration patterns | Disclosure_text_hash field in `chatbot_session/v1` | Hash of the actual disclosure shown to the user |

---

## Distribution targets

| Channel | Phase ship | Owner |
|---------|-----------|-------|
| PyPI: `ledgerproof-langchain` | Phase 1 (0.1.0) | Veronica → Senior Eng |
| npm: `@ledgerproof/langchain` | Phase 3 (0.3.0) | Senior Eng |
| GitHub: `ledgerproof/ledgerproof-langchain` (Python) | Phase 1 | Veronica |
| GitHub: `ledgerproof/ledgerproof-langchain-js` (TypeScript) | Phase 3 | Senior Eng |
| LangChain Hub | Phase 5 | DevRel + LangChain BD |
| LangChain Cookbook | Phase 5 | DevRel |
| Documentation site at `ledgerproofhq.io/developers/langchain` | Phase 1 (stub) → Phase 5 (full) | Veronica → DevRel |

---

## Open questions for V before Phase 1 starts

1. **Package name**: `ledgerproof-langchain` (Python) and `@ledgerproof/langchain` (npm) — confirm naming. Foundation org name on npm: do we have `@ledgerproof` reserved yet, or use `@ledgerproof-foundation`?
2. **Repo ownership**: Foundation GitHub org `ledgerproof` or Inc. GitHub org? Recommendation: Foundation owns, Inc. is contributor with CLA.
3. **First Founding Member co-pilot**: which Founding Member commits to running the adapter in production first? If Klarna or Adyen, the adapter has to support Anthropic + OpenAI + Mistral as Phase 1 LLM providers. If Riot, Anthropic + OpenAI only is acceptable for Phase 1.
4. **Phase 1 MVP timeline**: do you drive it personally Wed Jun 18 – Fri Jun 20 (pre-seed-close-pressure), OR wait for Senior Protocol Engineer start Jul 13 and ship MVP Jul 14-16? Recommendation: drive personally if seed-close conversations allow; the LangChain partnership conversation is materially stronger with working code attached.
5. **HSM-backend priority**: AWS CloudHSM first OR YubiHSM 2 first for Phase 4? Recommendation: YubiHSM 2 because more accessible for development and most Founding Members will start small.

---

## Success metric for the entire build-out

By Dec 31, 2026, the answer to the question *"Is LangChain integrated with LedgerProof yet?"* is **yes**.

- LangChain Hub listing live
- Cookbook PR merged
- Joint blog post published
- ≥5 Founding Member deployments running adapter in production
- ≥50 GitHub stars
- ≥3 external contributors with merged PRs
- Adapter version 1.0.0 GA

When all six land, the question stops being *"are LedgerProof and LangChain complementary?"* and becomes *"why isn't every Article 50 deployer using both?"* That's the inflection.
