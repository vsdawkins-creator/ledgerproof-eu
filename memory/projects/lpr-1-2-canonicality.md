# LPR 1.2 — Canonicality Annex

**Status:** Spec annex drafted May 26, 2026; implementation tickets ready
**Target ratification:** Q3 2026 (Sept 30) — 22 weeks from seed close
**Spec file:** `04-lpr-spec/LPR-1.2-CANONICALITY-ANNEX.md`
**Tickets file:** `04-lpr-spec/LPR-1.2-IMPLEMENTATION-TICKETS.md`

## What it adds (4 mechanisms)

### Mechanism 3 — Lineage chains (NEW)
- Optional fields: `previous_receipt_id`, `chain_root_id`, `lineage_position`, `supersedes`
- Identity delegations via `IdentityDelegation` entry kind
- 6 normative validation rules (predecessor existence, anchor status, identity, lineage arithmetic, chain root, linearity)
- 3 chain-walk endpoints: history, forward, canonical head
- 8 error codes LPR1200–LPR1208
- Linear chains only in v1.2 — branching deferred to v1.3

### Mechanism 4 — Multi-modal similarity hashing (NEW for text/audio/video/code)
- `similarity_hashes` map: tlsh-1, ssdeep-1, phash-1 (existing), audio-fp-1, video-kf-1, code-ast-1
- TLSH for text (LPR 1.2 §4.3)
- Brute-force scan acceptable up to 1M receipts; HNSW index when scale demands
- POST /v1/similarity/search endpoint
- Similarity Algorithm Registry at spec.ledgerproofhq.io/registry/similarity
- 3 error codes LPR1210–LPR1212

### Mechanism 5 — Witness attestation (NEW)
- New entry kind `attestation/v1`
- 6 registered types: co-sign, witness, notary, regulator, publisher, received
- Anchored in same Merkle tree as fresh entries
- Revocation via `attestation_revocation/v1`
- 6 error codes LPR1220–LPR1225

### Layer 3 — Canonical Registry + Foundation Arbitration (NEW)
- `canonical_claim/v1`, `canonical_dispute/v1`, `arbitration_resolution/v1` entry kinds
- 30-day dispute window after claim anchor
- 30-day arbitration window after dispute
- FROST-Ed25519 threshold signatures (default 3-of-5)
- Foundation Arbitration Panel resolutions are themselves anchored receipts
- 7 error codes LPR1230–LPR1236

## Code scaffolding shipped (post-close pickup)

### Migrations
- `migrations/0042_canonicality.sql` — all new columns + tables
- `migrations/0042_canonicality_rollback.sql` — clean rollback
- `migrations/0043_revocation_list.sql` — RRL for Unstoppable Priority 2

### Rust crates (in `ledgerproof-platform`)
- `crates/ledgerproof-api/src/validators/{chain,similarity,attestation,canonical}.rs` — 4 validators with full LPR12XX_ error codes
- `crates/ledgerproof-api/src/routes/{chains,attestations,canonical}.rs` — route stubs with TODO references to ticket numbers
- `crates/ledgerproof-frost/` — out-of-tree FROST-Ed25519 crate (Cargo.toml + 5 files)
- `crates/ledgerproof-substrate/` — out-of-tree multi-substrate crate
- `crates/UNSTOPPABLE-SCAFFOLDING-README.md` — contractor pickup guide

### SDK stubs
- `sdks/python/src/ledgerproof/v12.py` — Python method signatures with docstrings
- `sdks/typescript/src/v12.ts` — TypeScript types and interface

### CI/CD
- `.github/workflows/release-slsa.yml` — SLSA L3 + Sigstore + recursive LPR self-anchoring

## 33 tickets across 5 phases

| Phase | Tickets | Weeks |
|---|---|---|
| Phase 0 — Foundation (spec freeze, migration, OpenAPI, regression corpus) | 4 | 1-2 |
| Phase 1 — Lineage chains | 7 | 3-6 |
| Phase 2 — Text similarity (TLSH) | 5 | 7-9 |
| Phase 3 — Audio/Video/Code similarity | 4 | 10-13 |
| Phase 4 — Witness attestation | 4 | 14-17 |
| Phase 5 — Canonical Registry + Arbitration | 6 | 18-22 |
| Release | 3 | parallel |

Wall-clock with 3-engineer team: **13 weeks**.

## Critical backward-compat contract
Every v1.0/v1.1 receipt MUST verify byte-identically under v1.2. Enforced via:
- All new columns nullable
- All new fields OPTIONAL in CBOR
- Canonical bytes for v1.0/1.1 receipts unchanged
- 1,000-receipt frozen regression corpus in CI

## Cross-mechanism precedence (LPR 1.2 §7.1)
When determining canonical receipt, precedence order:
1. Foundation Arbitration Resolution (overrides all)
2. Uncontested canonical claim (>30d, no dispute)
3. Lineage chain head
4. Attestation graph weight (notary/regulator/publisher > co-sign)
5. First-anchor wins (Bitcoin block height)

Verifier UI MUST display the precedence reason.
