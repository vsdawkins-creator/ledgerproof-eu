# Post-Quantum Migration — v0.1 Design Document

**Purpose:** The cryptographic primitives in LPR v1.x are NIST-standardized but classical. NIST PQC standards are finalized (ML-KEM, ML-DSA, SLH-DSA); the migration window before quantum-relevant attacks is uncertain but bounded. We must publish a migration plan that survives Series A scrutiny and IETF Working Group adoption.

**Owner:** Spec Lead + external cryptography researcher (consultant by Day 120; hire by Day 180)
**Target publication:** Day 120 (October 2026)
**Target v2.0 protocol release with PQ primitives:** Q4 2028 (well ahead of NIST 2030 guidance for hybrid migration)
**Disclaimer:** v0.1 — this is a design doc for review, not a deployment plan

---

## Threat model

| Threat | Time horizon | Mitigation timeline |
|---|---|---|
| Cryptographically relevant quantum computer (CRQC) emerges | 2030–2040 (uncertain) | v2.0 with PQ signatures, 2028 |
| "Harvest now, decrypt later" against signing keys | Present-day risk | Signatures don't reveal long-term secrets; lower priority than KEM |
| "Harvest now, decrypt later" against confidential channels | Present-day risk | TLS migration to ML-KEM hybrid — Day 180 design, 2027 deployment |
| Signature forgery on retroactive receipts | Post-CRQC | Bitcoin anchor provides timestamp; receipts predating CRQC cannot be retroactively forged with valid anchor |

The receipt protocol's threat model is dominated by **signature forgery after the issuance window has closed**. Ed25519 in LPR v1.x is signing each receipt at issuance time and anchoring to Bitcoin. A CRQC could in principle forge new receipts post-quantum, but those receipts would not have valid Bitcoin anchors at their claimed issuance time. The Bitcoin anchor provides timestamping that survives quantum break.

The receipt protocol's confidentiality threat model is minimal — receipts carry only hashes and metadata, no confidential content. So KEM migration is less urgent for our protocol than for protocols that carry secrets.

---

## Migration approach — hybrid signatures in v2.0

LPR v2.0 receipts carry **two signatures** per issuance:
1. Ed25519 (classical) — preserves verifiability under v1.x readers (via downgrade compatibility)
2. ML-DSA-65 (post-quantum) — the future-proof signature

Verifier must verify both. Failure of either signature invalidates the receipt.

Wire format change:
- v1.x receipt body: `{ ..., "signature": <ed25519> }`
- v2.0 receipt body: `{ ..., "signatures": { "ed25519": <bytes>, "ml-dsa-65": <bytes> } }`

The `"signature"` field at the v1.x location is removed in v2.0. v1.x readers do not verify v2.0 receipts; this is the only point where strict backwards-compat breaks. Customers who need both classical-reader and PQ-reader compatibility issue receipts in both formats during the transition window.

---

## Primitive selection

| Operation | v1.x | v2.0 candidate | Rationale |
|---|---|---|---|
| Receipt signing | Ed25519 | ML-DSA-65 (FIPS 204) | NIST-standardized; balanced size + signing speed |
| Receipt hash | SHA-256 | SHA-256 | Symmetric primitives unaffected by quantum at relevant key sizes |
| Merkle tree leaf hash | SHA-256 | SHA-256 | Same |
| Merkle tree node hash | SHA-256 | SHA-256 | Same |
| CBOR encoding | RFC 8949 | RFC 8949 | Encoding unaffected |
| Bitcoin anchor format | "LPR1" + 32-byte Merkle root | "LPR2" + 32-byte Merkle root | Prefix bump signals v2.0 receipts in anchor stream |
| Operator HSM signing | Ed25519 software | ML-DSA-65 in HSM | HSM vendor support timeline drives this |
| TLS for SDK→operator | Classical | Hybrid ECDH+ML-KEM | When TLS 1.3 hybrid is widely supported (~2027) |

**Notable absences:**
- We do not migrate to a NIST-PQC stateful hash-based signature (e.g., XMSS, LMS). Stateful signatures are operationally fragile and a poor fit for a distributed receipt system.
- We do not migrate to SLH-DSA (SPHINCS+). Signatures are too large (~17 KB) for receipt-rate volumes.
- We do not migrate to Falcon (ML-DSA's competitor). Floating-point implementations are hazardous; ML-DSA-65 is preferred.

---

## Receipt size impact

| Field | v1.x | v2.0 | Delta |
|---|---|---|---|
| Receipt body (excluding signature) | ~3 KB | ~3 KB | 0 |
| Ed25519 signature | 64 bytes | 64 bytes | 0 (still present in v2.0) |
| ML-DSA-65 signature | 0 | ~3.3 KB | +3.3 KB |
| Receipt total | ~3.1 KB | ~6.4 KB | ~2x |

A 2x receipt size increase has cost implications:
- Storage at the operator: ~2x cost
- Network egress for SDK calls: ~2x
- Stamp PDF generation: receipt count limits per stamp may halve

This is acceptable. Storage and network are cheap; receipt volume is not the constraint.

---

## Migration timeline

| Date | Action |
|---|---|
| Day 120 (Oct 2026) | v0.1 design doc published; community review begins |
| Day 180 (Dec 2026) | v0.2 doc with community feedback; presented at Series A as forward visibility |
| Q1 2027 | v0.3 doc with primitive selection finalized; IETF WG presentation |
| Q3 2027 | LPR v2.0-draft published on spec.ledgerproofhq.io; reference implementation begins |
| Q1 2028 | LPR v2.0-rc; alpha SDK; conformance suite extended |
| Q3 2028 | LPR v2.0 stable; SDK 2.0 release; commercial operator supports both v1.x and v2.0 |
| 2028–2030 | Dual-issuance window: customers may issue both v1.x and v2.0 receipts; verifier supports both |
| 2030+ | New customers default to v2.0; v1.x remains supported indefinitely for receipt verification (read-only) |

**Critical constraint:** v1.x receipts already issued must remain verifiable forever. The verifier never deprecates v1.x support. This is non-negotiable — the Bitcoin anchor's value depends on the receipt being verifiable in perpetuity.

---

## Bitcoin anchor compatibility

Both v1.x and v2.0 receipts anchor to the same Bitcoin chain. The OP_RETURN payload format remains 36 bytes. The prefix changes:

- v1.x: `"LPR1"` (4 bytes) + 32-byte Merkle root
- v2.0: `"LPR2"` (4 bytes) + 32-byte Merkle root

Receipts of mixed versions can be batched into the same Merkle root; the Merkle root commits to all leaves regardless of version. The prefix in OP_RETURN signals the verifier which receipt-format-version applies to the leaves in that batch.

**Implication:** the verifier must walk the Merkle tree using version-aware leaf decoding. Spec'd in v2.0.

---

## Cost model

| Cost item | One-time | Recurring |
|---|---|---|
| External cryptography review (3 reviewers) | $90K | — |
| HSM with ML-DSA support (Yubico FIPS 4 / AWS CloudHSM) | $25K | $12K/year |
| Library implementation (Go + Python + TS + Java) | $60K (Founder + Sr. engineer) | — |
| Conformance suite extension | $40K | — |
| Performance benchmarking | $20K | — |
| Foundation board review + IETF coordination | $30K | — |
| **Total cost-to-v2.0** | **~$265K** | **~$12K/year ongoing** |

These costs are part of the Series A use of funds (the 10% R&D allocation).

---

## What v0.1 of this doc commits to

1. **NIST-standardized primitives only.** No proprietary or non-NIST candidates.
2. **Hybrid signatures in v2.0.** Both classical and PQ signatures present; either failure invalidates.
3. **Append-only protocol evolution.** v1.x receipts verify forever; v2.0 is additive (with the noted signature-field change).
4. **Public, IETF-tracked process.** v0.2 and beyond presented to the IETF SCITT WG.
5. **Foundation governance.** Migration decisions go through Foundation board approval, not founder fiat.
6. **No rushed timeline.** 2028 deployment is well ahead of any plausible CRQC threat. We do not rush.

## What v0.1 does NOT commit to

1. A specific HSM vendor (selection at Day 180)
2. Final library choices (depends on PQ library maturity in each language)
3. Bitcoin anchor format beyond the prefix-bump (research continues on whether to add explicit version field)
4. Migration tooling for self-hosted operators (Foundation will publish reference implementation; ops responsibility remains with self-hosters)

---

## Open questions for v0.2

1. **Hybrid signature scheme structure.** Concatenation, nested, or interleaved? Recommend nested with explicit identifiers.
2. **Anchor batching across version boundaries.** Same Merkle tree or separate? Recommend same.
3. **Operator signing key custody during migration.** Two HSMs (classical + PQ) or single multi-algorithm HSM? Recommend single multi-algorithm where vendor supports.
4. **Customer migration assistance.** What tooling does the Foundation publish to help customers detect v1.x → v2.0 readiness in their integrations? Recommend a `lpr-pq-readiness-scanner` CLI tool, shipped with SDK 2.0.
5. **PQ migration of TLS to operator.** Track separately or bundle with receipt-format migration? Recommend track separately; the timelines do not align.

## Companion documents to publish

- Technical FAQ for customers (1-pager): "What does PQ mean for me?"
- Regulator briefing addendum: "How LedgerProof addresses post-quantum cryptographic transition"
- Foundation board paper: "PQ migration governance and cost model"
- IETF presentation slides (for the SCITT WG)
