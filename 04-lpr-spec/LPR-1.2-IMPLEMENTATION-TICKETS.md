# LPR 1.2 — Implementation Tickets (GitHub-ready)

This document is structured so each `### Ticket` block can be copy-pasted directly into a GitHub issue. Issue numbering is illustrative; assign real numbers at creation time.

**Milestones:**
- `v1.2-phase-0` (weeks 1–2): Foundation work
- `v1.2-phase-1` (weeks 3–6): Lineage chains
- `v1.2-phase-2` (weeks 7–9): Text similarity
- `v1.2-phase-3` (weeks 10–13): Audio/video/code similarity
- `v1.2-phase-4` (weeks 14–17): Witness attestation
- `v1.2-phase-5` (weeks 18–22): Canonical Registry + arbitration

**Labels:** `area:rust-core`, `area:api`, `area:sdk-python`, `area:sdk-typescript`, `area:verifier-ui`, `area:spec`, `area:devops`, `priority:p0`, `priority:p1`.

---

## PHASE 0 — Foundation

### Ticket 1 — Freeze LPR 1.2 spec annex
**Milestone:** v1.2-phase-0
**Labels:** area:spec, priority:p0
**Effort:** 1 week

Lock the LPR 1.2 Canonicality Annex (`04-lpr-spec/LPR-1.2-CANONICALITY-ANNEX.md`). Distribute to external cryptographer review. Incorporate feedback. Tag `lpr-1.2-draft-rc1`.

**Acceptance criteria:**
- [ ] External cryptographer review (Trail of Bits / NCC / Cure53 / Cas Cremers) returns sign-off or actionable feedback
- [ ] All `[TBD]` placeholders resolved
- [ ] CBOR schema validates against test vectors
- [ ] Tagged release `lpr-1.2-draft-rc1`

---

### Ticket 2 — Schema migration 0042: canonicality columns + new tables
**Milestone:** v1.2-phase-0
**Labels:** area:rust-core, area:devops, priority:p0
**Effort:** 3 days
**Blocked by:** #1

Author `migrations/0042_canonicality.sql` adding:
- `entries.previous_receipt_id`, `entries.chain_root_id`, `entries.lineage_position`, `entries.supersedes`
- `identity_delegations` table
- `similarity_index` table
- `attestations` table
- `canonical_claims` table
- `foundation_resolutions` table

**Acceptance criteria:**
- [ ] Migration applies cleanly on a snapshot of production data
- [ ] All new columns are nullable / have safe defaults
- [ ] sqlx offline metadata regenerated (`cargo sqlx prepare`)
- [ ] Rollback path documented

---

### Ticket 3 — OpenAPI 3.1 specification update
**Milestone:** v1.2-phase-0
**Labels:** area:api, area:spec, priority:p1
**Effort:** 4 days
**Blocked by:** #1

Update `04-lpr-spec/openapi-v1.2.yaml` with every new endpoint and schema. Generate ReDoc-rendered preview.

**Acceptance criteria:**
- [ ] All 14 new endpoints documented
- [ ] All request/response schemas defined
- [ ] Example payloads for each endpoint
- [ ] Renders cleanly in ReDoc
- [ ] OpenAPI lint clean

---

### Ticket 4 — Backward-compatibility regression corpus
**Milestone:** v1.2-phase-0
**Labels:** area:rust-core, area:devops, priority:p0
**Effort:** 3 days
**Blocked by:** #1

Capture 1,000 v1.0/v1.1 receipts from production. Snapshot them. Add a CI test that re-canonicalizes each under v1.2 code and asserts byte-identical canonical output.

**Acceptance criteria:**
- [ ] `tests/regression/v1_compat_corpus.json` checked in (gzipped)
- [ ] `cargo test --release v1_compat` runs in CI on every PR
- [ ] Documented in `CONTRIBUTING.md` how to add new corpus entries

---

## PHASE 1 — Lineage chains (Mechanism 3)

### Ticket 5 — Extend `LprEntry` Rust struct with lineage fields
**Milestone:** v1.2-phase-1
**Labels:** area:rust-core, priority:p0
**Effort:** 2 days
**Blocked by:** #2

Add four OPTIONAL fields to `LprEntry` in `crates/ledgerproof-api/src/models/entry.rs`:
- `previous_receipt_id: Option<Uuid>`
- `chain_root_id: Option<Uuid>`
- `lineage_position: Option<u32>`
- `supersedes: Option<bool>`

Extend canonicalizer in `crates/ledgerproof-api/src/canonical.rs` to handle them per LPR 1.2 §3.1.

**Acceptance criteria:**
- [ ] All four fields serialize/deserialize via serde + serde-cbor
- [ ] Canonical bytes for v1.1 receipts (without these fields) unchanged
- [ ] Unit tests cover present/absent permutations
- [ ] Regression corpus from #4 still passes

---

### Ticket 6 — Implement chain validator
**Milestone:** v1.2-phase-1
**Labels:** area:rust-core, priority:p0
**Effort:** 5 days
**Blocked by:** #5

Create `crates/ledgerproof-api/src/validators/chain.rs` enforcing LPR 1.2 §3.3 (six validation rules) and §3.5 (delegations).

**Acceptance criteria:**
- [ ] All 8 error codes (`LPR1200`–`LPR1207`) return correctly
- [ ] Same-issuer succession passes
- [ ] Delegated succession passes when delegation valid
- [ ] Branch attempt rejected with `LPR1205_BRANCH_NOT_ALLOWED`
- [ ] Test coverage ≥ 95%

---

### Ticket 7 — Chain-walk API endpoints
**Milestone:** v1.2-phase-1
**Labels:** area:api, priority:p1
**Effort:** 3 days
**Blocked by:** #6

Implement three endpoints in `crates/ledgerproof-api/src/routes/chains.rs`:
- `GET /v1/chains/{receipt_id}/history`
- `GET /v1/chains/{chain_root_id}/forward`
- `GET /v1/chains/{chain_root_id}/canonical`

**Acceptance criteria:**
- [ ] All three endpoints return per LPR 1.2 §3.6
- [ ] Anchor status included in every receipt entry
- [ ] Identity verification status included
- [ ] Pagination supported (`?after=` cursor) for chains >100 entries
- [ ] Rate-limited per existing tower-governor config

---

### Ticket 8 — Identity delegation API + entry kind
**Milestone:** v1.2-phase-1
**Labels:** area:api, area:rust-core, priority:p1
**Effort:** 4 days
**Blocked by:** #5

Implement `identity_delegation/v1` entry kind and `POST /v1/delegations` endpoint per LPR 1.2 §3.5.

**Acceptance criteria:**
- [ ] Delegation entries anchored like ordinary LPR entries
- [ ] Delegation validation enforces scope.expires_at
- [ ] Chain validator (#6) consults delegations correctly
- [ ] Tests cover expired / revoked / scope-mismatch cases

---

### Ticket 9 — Python SDK lineage support
**Milestone:** v1.2-phase-1
**Labels:** area:sdk-python, priority:p1
**Effort:** 3 days
**Blocked by:** #7

Add to `sdks/python/src/ledgerproof/`:
- `client.publish_v1_1(content, previous_receipt_id=..., supersedes=...)`
- `client.get_chain_history(receipt_id)`
- `client.delegate_chain(chain_root_id, delegate_did, expires_at)`

**Acceptance criteria:**
- [ ] Methods documented with examples
- [ ] Async variants for each
- [ ] Live integration tests against staging
- [ ] Type stubs (`.pyi`) updated

---

### Ticket 10 — TypeScript SDK lineage support
**Milestone:** v1.2-phase-1
**Labels:** area:sdk-typescript, priority:p1
**Effort:** 3 days
**Blocked by:** #7

Add to `sdks/typescript/src/`:
- `client.publishV1_1({ content, previousReceiptId?, supersedes? })`
- `client.getChainHistory(receiptId)`
- `client.delegateChain({ chainRootId, delegateDid, expiresAt })`

**Acceptance criteria:**
- [ ] Methods exported from `@ledgerproof/sdk`
- [ ] TypeScript types complete
- [ ] Vitest unit tests
- [ ] Browser + Node + edge runtime smoke tests

---

### Ticket 11 — Verifier UI: chain history rendering
**Milestone:** v1.2-phase-1
**Labels:** area:verifier-ui, priority:p1
**Effort:** 5 days
**Blocked by:** #7

Update browser extensions (Chrome/Firefox/Safari) and `verify.ledgerproofhq.io` to render chain history:
- "Version N of M in chain by [issuer]"
- "View history" expandable timeline
- Orphan warning when a receipt references unknown predecessor

**Acceptance criteria:**
- [ ] Chrome / Firefox / Safari extensions updated
- [ ] Web verifier UI updated
- [ ] Embedded badge shows version number
- [ ] Accessibility (WCAG 2.1 AA) preserved
- [ ] Cross-browser visual regression tests pass

---

## PHASE 2 — Text similarity (Mechanism 4 partial)

### Ticket 12 — `ledgerproof-similarity` Rust crate
**Milestone:** v1.2-phase-2
**Labels:** area:rust-core, priority:p0
**Effort:** 4 days

Create new crate `crates/ledgerproof-similarity/`:
- `pub trait SimilarityHasher` with `hash(&self, content: &[u8]) -> SimHash`
- `pub trait SimilarityComparer` with `distance(&self, a: &SimHash, b: &SimHash) -> u32`
- Impls for TLSH, ssdeep, pHash

**Acceptance criteria:**
- [ ] TLSH wrapper over `tlsh` crate
- [ ] pHash wrapper over `img_hash` crate
- [ ] ssdeep wrapper
- [ ] Test vectors from LPR 1.2 §10
- [ ] Documented API

---

### Ticket 13 — Similarity indexer
**Milestone:** v1.2-phase-2
**Labels:** area:rust-core, area:api, priority:p0
**Effort:** 4 days
**Blocked by:** #12, #2

Background indexer in `crates/ledgerproof-api/src/services/similarity_indexer.rs` that computes and stores similarity hashes for every new entry.

**Acceptance criteria:**
- [ ] Computes hashes based on `content_type`
- [ ] Inserts into `similarity_index` table
- [ ] Idempotent
- [ ] Backfill command for existing entries
- [ ] Metrics exported

---

### Ticket 14 — Similarity search API
**Milestone:** v1.2-phase-2
**Labels:** area:api, priority:p1
**Effort:** 3 days
**Blocked by:** #13

Implement `POST /v1/similarity/search` per LPR 1.2 §4.4. Enhance `GET /v1/verify/{id}` to include `similar_receipts` array (up to 5).

**Acceptance criteria:**
- [ ] Brute-force TLSH scan with threshold filter
- [ ] Response time < 200ms for 1M-receipt index
- [ ] Pagination supported
- [ ] Rate-limited

---

### Ticket 15 — SDK auto-similarity-hashing (Python + TS)
**Milestone:** v1.2-phase-2
**Labels:** area:sdk-python, area:sdk-typescript, priority:p1
**Effort:** 4 days
**Blocked by:** #14

SDKs auto-compute similarity hashes client-side based on `content_type`.

**Acceptance criteria:**
- [ ] Python TLSH via `tlsh-python`
- [ ] TypeScript TLSH via `tlsh-js` (or pure-TS port)
- [ ] Pre-publish hook computes hashes
- [ ] Opt-out via `compute_similarity_hashes=False`

---

### Ticket 16 — Verifier UI: similarity warnings
**Milestone:** v1.2-phase-2
**Labels:** area:verifier-ui, priority:p1
**Effort:** 4 days
**Blocked by:** #14

Update verifiers to render the four states from LPR 1.2 §4.5.

**Acceptance criteria:**
- [ ] Orange warning badge for "different issuer + earlier anchor"
- [ ] Click-through diff viewer for text content
- [ ] Similarity confidence percentage displayed
- [ ] Visual regression tests pass

---

## PHASE 3 — Audio / Video / Code similarity

### Ticket 17 — Audio fingerprinting integration
**Milestone:** v1.2-phase-3
**Labels:** area:rust-core, priority:p1
**Effort:** 5 days
**Blocked by:** #12

Wrap `chromaprint` (via subprocess or FFI) in `ledgerproof-similarity` crate. Add `audio-fp-1` algorithm.

**Acceptance criteria:**
- [ ] Fingerprints 60s audio in < 2s
- [ ] Cross-format consistency (wav, mp3, ogg, m4a)
- [ ] Distance function reflects acoustic similarity
- [ ] Test vectors

---

### Ticket 18 — Video keyframe pHash extraction
**Milestone:** v1.2-phase-3
**Labels:** area:rust-core, priority:p1
**Effort:** 5 days
**Blocked by:** #12

Extract keyframes via `ffmpeg-next`, compute pHash per frame. Add `video-kf-1` algorithm.

**Acceptance criteria:**
- [ ] 10-minute video processed in < 30s
- [ ] Keyframe count proportional to video length
- [ ] Pairwise pHash matching with majority-vote
- [ ] Cross-codec consistency

---

### Ticket 19 — Code AST fingerprinting via tree-sitter
**Milestone:** v1.2-phase-3
**Labels:** area:rust-core, priority:p2
**Effort:** 4 days
**Blocked by:** #12

Use `tree-sitter` to parse and canonicalize AST. Add `code-ast-1` algorithm. Support Python, TypeScript, Rust, Go, Java initially.

**Acceptance criteria:**
- [ ] AST canonicalization stable across formatting changes
- [ ] Identifier renames don't change hash (alpha-renaming)
- [ ] Comment changes don't change hash
- [ ] Test corpus of 100 (original, refactored) pairs

---

### Ticket 20 — Verifier UI: multi-modal similarity rendering
**Milestone:** v1.2-phase-3
**Labels:** area:verifier-ui, priority:p2
**Effort:** 4 days
**Blocked by:** #17, #18, #19

Render similarity warnings appropriately for audio, video, code content types.

**Acceptance criteria:**
- [ ] Audio: waveform comparison preview
- [ ] Video: keyframe gallery diff
- [ ] Code: side-by-side syntax-highlighted diff
- [ ] Mobile-responsive

---

## PHASE 4 — Witness attestation (Mechanism 5)

### Ticket 21 — Attestation entry kind + Merkle batching
**Milestone:** v1.2-phase-4
**Labels:** area:rust-core, priority:p0
**Effort:** 4 days
**Blocked by:** #2

Add `Attestation` entry kind in Rust core. Extend Merkle batcher in `crates/ledgerproof-anchor/src/builder.rs` to include attestations as leaves alongside entries.

**Acceptance criteria:**
- [ ] `Attestation` canonicalizes per LPR 1.2 §5.1
- [ ] Anchored in same Merkle tree as entries
- [ ] Inclusion proof generation works
- [ ] Backward-compat preserved

---

### Ticket 22 — Attestation submission + listing API
**Milestone:** v1.2-phase-4
**Labels:** area:api, priority:p1
**Effort:** 3 days
**Blocked by:** #21

Implement endpoints per LPR 1.2 §5.5:
- `POST /v1/attestations`
- `GET /v1/receipts/{id}/attestations`
- `GET /v1/receipts/{id}/attestations/all`
- `POST /v1/attestations/{id}/revoke`

**Acceptance criteria:**
- [ ] All 6 error codes (`LPR1220`–`LPR1225`) return correctly
- [ ] Duplicate prevention works
- [ ] Revocation by non-author returns `LPR1225`
- [ ] Revoked attestations included only in `/all` endpoint

---

### Ticket 23 — SDK attestation methods (Python + TS)
**Milestone:** v1.2-phase-4
**Labels:** area:sdk-python, area:sdk-typescript, priority:p1
**Effort:** 3 days
**Blocked by:** #22

Add `attest_receipt(...)` and `revoke_attestation(...)` to both SDKs.

**Acceptance criteria:**
- [ ] Signs canonical attestation payload with provided key
- [ ] All 6 attestation types supported
- [ ] Live integration tests against staging

---

### Ticket 24 — Verifier UI: attestation graph
**Milestone:** v1.2-phase-4
**Labels:** area:verifier-ui, priority:p1
**Effort:** 5 days
**Blocked by:** #22

Render attestation graph for any receipt. Show attestor identity, type, timestamp, revocation status.

**Acceptance criteria:**
- [ ] Visual graph (D3 or similar) for receipts with 3+ attestations
- [ ] Simple list view for ≤2 attestations
- [ ] Identity verification level shown for each attestor
- [ ] Revoked attestations rendered with strikethrough

---

## PHASE 5 — Canonical Registry + Foundation Arbitration (Layer 3)

### Ticket 25 — FROST-Ed25519 threshold signature module
**Milestone:** v1.2-phase-5
**Labels:** area:rust-core, priority:p0
**Effort:** 6 days
**Blocked by:** #2

New crate `crates/ledgerproof-frost/` implementing FROST-Ed25519 per LPR 1.2 §6.7. Use `frost-ed25519` crate as base.

**Acceptance criteria:**
- [ ] Key generation (DKG) for 5 participants
- [ ] Threshold signing (3-of-5)
- [ ] Aggregated signature verifies against group public key as ordinary Ed25519
- [ ] HSM integration points documented
- [ ] Test vectors

---

### Ticket 26 — Canonical claim / dispute / resolution entry kinds
**Milestone:** v1.2-phase-5
**Labels:** area:rust-core, priority:p0
**Effort:** 5 days
**Blocked by:** #21, #25

Implement three new entry kinds per LPR 1.2 §6.2–6.4.

**Acceptance criteria:**
- [ ] All three canonicalize correctly
- [ ] Anchored as ordinary entries
- [ ] State machine: `asserted` → `disputed` → `resolved` enforced
- [ ] 30-day windows enforced

---

### Ticket 27 — Canonical Registry API
**Milestone:** v1.2-phase-5
**Labels:** area:api, priority:p0
**Effort:** 4 days
**Blocked by:** #26

Implement endpoints per LPR 1.2 §6.8.

**Acceptance criteria:**
- [ ] All 7 error codes (`LPR1230`–`LPR1236`) return correctly
- [ ] FROST signature verification at `/resolve`
- [ ] Threshold check
- [ ] Audit trail of all panel member signatures

---

### Ticket 28 — Foundation Arbitration Panel UI
**Milestone:** v1.2-phase-5
**Labels:** area:verifier-ui, priority:p1
**Effort:** 10 days
**Blocked by:** #27

Internal app at `arbitration.ledgerproof-foundation.org`. Auth via board-member DIDs. Evidence viewer. FROST partial-signing flow.

**Acceptance criteria:**
- [ ] Board-member DID authentication
- [ ] Open disputes dashboard
- [ ] Evidence panel: lineage, attestations, similarity, identity certs
- [ ] Partial-signature submission UI
- [ ] Aggregation UI
- [ ] Audit log of all panel actions

---

### Ticket 29 — Verifier UI: canonicality badges
**Milestone:** v1.2-phase-5
**Labels:** area:verifier-ui, priority:p1
**Effort:** 4 days
**Blocked by:** #27

Add canonicality state badges to all verifier surfaces per LPR 1.2 §6.5.

**Acceptance criteria:**
- [ ] Green ✅ `canonical_upheld` / `canonical_uncontested`
- [ ] Yellow ⚠️ `disputed` with countdown timer
- [ ] Red ❌ `canonical_overturned`
- [ ] Neutral `no_clear_canonical`
- [ ] Click-through to dispute resolution page

---

### Ticket 30 — SDK canonical claim methods
**Milestone:** v1.2-phase-5
**Labels:** area:sdk-python, area:sdk-typescript, priority:p2
**Effort:** 3 days
**Blocked by:** #27

Expose claim/dispute creation in SDKs.

**Acceptance criteria:**
- [ ] `claim_canonical(receipt_id, statement, evidence)`
- [ ] `dispute_claim(claim_id, competing_receipt_id, rationale)`
- [ ] Both Python and TypeScript

---

## RELEASE — v1.2-rc1 → v1.2-stable

### Ticket 31 — Documentation: LPR 1.2 launch
**Milestone:** v1.2-release
**Labels:** area:docs, priority:p0
**Effort:** 5 days
**Blocked by:** all phases complete

Update `docs.ledgerproofhq.io` with:
- v1.2 overview page
- Migration guide for SDK users
- Tutorial: building a chain
- Tutorial: requesting an attestation
- Tutorial: filing a canonical claim
- Updated API reference

**Acceptance criteria:**
- [ ] All five pages live
- [ ] Tutorials runnable against staging
- [ ] No broken links
- [ ] Reviewed by senior-technical-writer

---

### Ticket 32 — External security audit (LPR 1.2 scope)
**Milestone:** v1.2-release
**Labels:** area:security, priority:p0
**Effort:** 6 weeks (external)
**Blocked by:** all phases complete

Engage Trail of Bits / NCC / Cure53 for audit of LPR 1.2 spec + reference implementations.

**Acceptance criteria:**
- [ ] Engagement letter signed
- [ ] Audit complete
- [ ] All HIGH and CRITICAL findings remediated
- [ ] Audit report published

---

### Ticket 33 — Press: LPR 1.2 announcement
**Milestone:** v1.2-release
**Labels:** area:marketing, priority:p2
**Effort:** 3 days

Coordinate with PR. Blog post, IETF announcement, C2PA coalition update.

---

## Summary

**Total: 33 tickets across 5 phases + release.**

| Phase | Tickets | Estimated effort |
|---|---|---|
| Phase 0 — Foundation | 4 | 2 weeks |
| Phase 1 — Lineage chains | 7 | 4 weeks |
| Phase 2 — Text similarity | 5 | 3 weeks |
| Phase 3 — Multi-modal similarity | 4 | 4 weeks |
| Phase 4 — Attestation | 4 | 4 weeks |
| Phase 5 — Canonical Registry | 6 | 5 weeks |
| Release | 3 | parallel |
| **Total elapsed** | **33** | **22 weeks** |

With a 3-engineer team (1 Rust core, 1 SDK + UI, 1 DevOps/test) running in parallel, **wall-clock = 13 weeks**.

Target ship: Q3 2026 end (Sept 30).

---

*End of v1.2 Implementation Tickets.*
