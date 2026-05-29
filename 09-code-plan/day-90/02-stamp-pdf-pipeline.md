# Audit-Ready Compliance Stamp PDF — Production Pipeline

**Purpose:** Productionize the Stamp PDF generation pipeline so monthly stamps for all paying customers generate automatically by Day 90. The pipeline must hit the design-spec target of <8 seconds end-to-end for stamps covering up to 10M receipts.

**Owner:** Web Engineering Consultant (Day 30 hire) → Founder for sign-off
**Spec reference:** [Stamp PDF Design Spec](../../08-gtm/day-30/03-compliance-stamp-pdf-design-spec.md)
**Target GA:** Day 90

---

## Pipeline stages

```
1. Trigger
   ├── Scheduled (monthly, per customer)
   └── On-demand (Customer API call)
        │
        ▼
2. Receipt enumeration
   ├── Query receipt store for [start, end]
   └── Stream-iterate; never load all in memory
        │
        ▼
3. Merkle tree construction (stamp-scoped)
   ├── RFC 6962 with domain separation
   └── Output: stamp Merkle root (32 bytes)
        │
        ▼
4. Coverage analysis
   ├── Count per Article 50 sub-clause
   ├── Count per ISO/IEC 42001 control
   ├── Count per NIST AI RMF function
   ├── Count per DORA Article 28 element
   └── Identify exceptions (missed SLOs, soft-deletes, key rotations)
        │
        ▼
5. Stamp CBOR construction
   ├── Canonical CBOR encoding (RFC 8949)
   └── Stamp ID = UUIDv4
        │
        ▼
6. Foundation signing
   ├── Ed25519 signature over canonical CBOR
   └── Foundation stamp signing key (HSM-backed Day 120+)
        │
        ▼
7. PDF rendering
   ├── LaTeX template at pipeline.ledgerproofhq.io/stamp.tex
   └── Tectonic for deterministic rendering
        │
        ▼
8. Foundation Canonical Registry publication
   ├── Stamp CBOR pushed to registry
   └── Permalink generated
        │
        ▼
9. Delivery
   ├── Customer dashboard download
   ├── Email to designated stamp recipients
   └── Optional: webhook to customer's GRC system
```

---

## Latency budget (target: 8s end-to-end for 10M receipts)

| Stage | Target | Strategy |
|---|---|---|
| Trigger to enumeration start | 100ms | Pre-warmed worker pool |
| Receipt enumeration (10M) | 2.5s | Postgres index on (customer_id, issued_at); parallel cursors |
| Merkle tree construction | 2s | SIMD-accelerated SHA-256; rayon parallel batching |
| Coverage analysis | 1s | Aggregations pre-computed by issuance-time triggers; final rollup only |
| CBOR construction + signing | 100ms | Constant-time work; pre-computed encoder |
| PDF rendering | 1.5s | Tectonic; template pre-compiled |
| Registry publication | 200ms | Async; does not block customer response |
| Delivery | 600ms | Async email send |
| **Total wall-clock** | **~8s** | Stages 5-9 can pipeline in parallel where possible |

For stamps covering 100M+ receipts, the target slips to ~30s; documented in customer-facing SLA.

---

## Architecture

**Workers:** Stamp pipeline runs in a dedicated worker pool (Fly Machines, autoscaled). Decoupled from operator receipt-issuance path. A spike in stamp generation never affects receipt issuance latency.

**Storage:** Stamp CBOR + rendered PDF stored in S3-compatible object storage with versioning. Stamps are immutable once published; corrections are issued as new stamps with `supersedes` field pointing to the prior stamp ID.

**Caching:** Coverage analysis aggregations cached at the per-customer-per-day grain. A monthly stamp pulls 30 days of pre-aggregated data and rolls up — most of the work is already done by the time the stamp triggers.

**Idempotency:** Stamp generation is idempotent on (customer_id, coverage_start, coverage_end). Re-running produces the same stamp ID, same Merkle root, byte-identical PDF — unless underlying receipts have been soft-deleted in the interim, in which case the new stamp has a different ID and a `supersedes` reference.

---

## Reference stamp (live demo)

A reference stamp covering the Foundation's own AI usage (its public communications, regulator briefings, Foundation-issued receipts) is published at `verify.ledgerproofhq.io/stamp/example`. Updated monthly. This is the dogfood artifact every customer sees before signing.

The reference stamp demonstrates:
- All eight regulation rows populated (Article 50, ISO 42001, NIST RMF, DORA)
- One exception row showing a soft-delete (intentionally created for demo)
- The QR code resolves correctly
- The PDF renders identically across viewers
- The verifier portal verifies in <10 seconds

If the reference stamp ever fails verification, that is a P0 incident.

---

## Customer co-branding pipeline

Production-tier and above customers may add their own logo to the PDF (replacing the QR code position in the top-right; QR moves to footer-center).

Co-branding workflow:
1. Customer submits logo + signed co-branding agreement via dashboard
2. Foundation reviews logo for legal use (CCBY, customer mark policy, etc.) — 5 business day turnaround
3. Logo approved → stored in stamp-pipeline asset bucket
4. Subsequent stamps for that customer render with the logo

**Critical constraint:** Customer logos NEVER appear on the Foundation's own letterhead artifacts (e.g., the reference stamp, regulator briefings). Co-branding is strictly per-customer-stamp.

---

## Stamp formats produced (all from same canonical CBOR)

1. **PDF (A4 portrait)** — the primary artifact
2. **PDF (US Letter)** — secondary, generated on-demand
3. **HTML rendering** — embedded in customer dashboard
4. **JSON-LD machine-readable** — for customer GRC system ingestion
5. **CBOR canonical** — the cryptographic source of truth

All five are byte-equivalent at the cryptographic layer (same Merkle root, same Foundation signature). Rendering differences are presentational only.

---

## Failure modes

| Failure | Impact | Mitigation |
|---|---|---|
| Coverage period contains 0 receipts | Stamp generates with "No receipts in period" notice | Acceptable; customer dashboard surfaces clearly |
| Coverage period spans operator regions | Receipts from all regions included; receipt IDs disambiguate | Pipeline handles natively |
| Foundation signing key rotation mid-period | Stamp signed with both keys; rotation timestamp noted | Documented in footer band |
| Customer soft-deleted receipts during period | Stamp shows `[N] of [M] (M-N soft-deleted)`; exception block lists deletions | Spec-compliant; design-spec covers this |
| Postgres unavailable during enumeration | Stamp generation deferred; retry queue holds for 24h | Customer alerted if stamp delayed >2h beyond scheduled time |
| Bitcoin RPC unavailable during anchor verification | Anchor verification deferred; stamp generates with `anchor_verification_pending` field | Verified when RPC recovers; stamp updated with verification timestamp |
| PDF rendering fails | Customer notified; founder paged | Manual stamp generation as backup |

---

## Customer dashboard surface

A new "Compliance Stamps" section in the customer dashboard, shipped by Day 90:

- List of past stamps with status, coverage period, receipt count
- Download in any of the 5 formats
- Schedule configuration (monthly default; weekly or quarterly options)
- On-demand stamp trigger
- Co-branding configuration
- Recipient list for email delivery
- Webhook configuration for GRC system integration

---

## Pre-launch gates

- [ ] Reference stamp generates and verifies in CI (every commit)
- [ ] Load test: 100 concurrent stamp generations, each covering 10M receipts, complete within 60s p95
- [ ] PDF deterministic rendering: same input → byte-identical PDF across two render hosts
- [ ] CBOR canonical encoding: same input → byte-identical CBOR
- [ ] Customer-facing API documented at docs.ledgerproofhq.io/stamps
- [ ] At least 3 pilot customers have received a manually-generated stamp before automatic generation switches on
- [ ] Foundation signing key custody documented and reviewed by security advisor
- [ ] HSM integration design doc (not necessarily integrated by Day 90, but designed)

---

## Open questions

1. **Stamp signing key custody.** Software key OK for Day 90; HSM-backed by Day 120 (committed). Should it be a Foundation-owned HSM or LedgerProof Inc.-owned with Foundation oversight? **Recommend Foundation-owned HSM at Day 120.**
2. **PDF localization.** German, French, Spanish, Italian — when? **Recommend translation pipeline at Day 120; first translation shipped Day 150.**
3. **Stamp issuance for self-hosted operator customers.** Can a customer running the reference operator issue stamps signed by the Foundation? **No — Foundation signing is reserved for Foundation-operated stamps. Self-hosters issue stamps signed by themselves under the reference template. Documented.**
4. **Historical stamp revalidation.** If a customer requests a stamp for a period 6 months ago, do we generate it? **Yes, provided receipts in that period are still retained. Aggregations may need on-demand recompute.**
