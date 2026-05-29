# LPR v1.2 — Spec Freeze

**Purpose:** The first protocol evolution since v1.1 launch. v1.2 is **additive only** — no v1.1 receipt loses verifiability under a v1.2 reader. The release introduces the profile system that absorbs Code-of-Practice evolution and the lineage chain primitives that enable cross-receipt provenance.

**Owner:** Spec lead (hired by Day 60) + Founder
**Target freeze date:** Day 60 (August 24, 2026)
**Target production deployment:** Day 90 (September 23, 2026)
**Backwards-compat guarantee:** v1.1 readers ignore v1.2-only fields; v1.2 readers verify v1.1 receipts using v1.1 rules.

---

## What v1.2 adds

### 1. Profile system

A `profile` field is added to every receipt header. Values:

- `lpr.v1.1` (default for v1.1 receipts; v1.2 readers infer)
- `lpr.v1.2.baseline` (default for v1.2 receipts with no extension)
- `lpr.v1.2.code-of-practice.YYYY-MM` (when Code finalizes)
- `lpr.v1.2.dora-article-28` (for FSI customers signaling DORA-specific receipt content)
- `lpr.v1.2.iso-42001.A.6` (when the receipt is being issued specifically as A.6 evidence)

Profiles are **declarative**, not behavioral. A v1.2.baseline receipt and a v1.2.code-of-practice.2026-10 receipt have the same on-the-wire bytes for the fields they share; the profile string tells the reader which additional fields to expect.

Profile registry lives at `spec.ledgerproofhq.io/profiles/`. Each profile has:
- A canonical URL (immutable)
- A version
- A list of required fields
- A list of optional fields
- A mapping to one or more regulatory citations
- A deprecation policy

### 2. Lineage chain primitives

A `lineage` block is added to the receipt body. Structure:

```cbor
{
  "lineage": {
    "parent_receipts": [
      { "receipt_id": "...", "anchor_block": 850123, "relationship": "training_data" },
      { "receipt_id": "...", "anchor_block": 850124, "relationship": "model_version" },
      { "receipt_id": "...", "anchor_block": 850125, "relationship": "specification" }
    ]
  }
}
```

This is what enables ISO/IEC 42001 A.6.2.3 ("Documentation of AI system design and development") to claim Full coverage. The lineage chain is verifiable by walking parent receipts to their own anchors.

**Cycle protection:** Lineage chains must be DAGs. The receipt issuer signs the lineage; the verifier walks parents and rejects any cycle.

**Privacy:** Parent receipt IDs are content-addressed hashes, not URLs. They do not leak issuer identity unless the issuer has published the corresponding receipts.

### 3. Soft-delete semantics

Customers may request soft-delete of receipt metadata for GDPR Article 17 compliance. v1.2 formalizes the soft-delete posture:

- The Bitcoin anchor (Merkle root) is permanent.
- The metadata layer at the operator is deleted on request.
- The receipt's canonical CBOR is no longer retrievable from the operator.
- The verifier portal returns a `soft-deleted` indicator when a receipt ID is queried but no metadata is present, along with proof that an anchor at the claimed block height exists.

**Customer responsibility:** If a customer wants the original receipt content to remain available (e.g., for regulator examination), the customer is responsible for retaining a local copy before requesting soft-delete.

### 4. Cross-protocol bridge fields

Optional fields enable the receipt to carry attestations from other protocols:

- `c2pa_manifest_hash`: SHA-256 of an attached C2PA manifest
- `scitt_entry_id`: identifier from IETF SCITT (if the customer also publishes to an SCITT transparency service)
- `external_attestation_uri`: arbitrary URI for vendor-specific attestations

Verifier portal exposes these fields but does not validate them — third-party validators can be added by the Foundation Advisory Council.

### 5. Operator hints

Optional fields the operator can populate at issuance (not signed by the customer):

- `operator_anchor_pool`: which Bitcoin pool relayed the anchor
- `operator_region`: which region issued the receipt
- `operator_fingerprint`: hash of operator binary version

These are advisory only. The receipt's verifiability does not depend on them.

---

## What v1.2 does NOT change

- Receipt header format (issuer, signature, hash, timestamp, anchor)
- OP_RETURN format ("LPR1" + 32-byte Merkle root)
- Canonical CBOR encoding (RFC 8949)
- Ed25519 signature scheme
- RFC 6962 Merkle tree with domain separation
- Schema rejection of PII at parse time
- Verifier portal API surface (additive only)

These are deliberately frozen. Changing any of them requires v2.0.

---

## Migration path

| Customer state | Action |
|---|---|
| Issuing v1.1 receipts on SDK 1.1 | No action. v1.1 receipts continue to verify forever. |
| Wants to issue v1.2 receipts | Upgrade to SDK 1.2 (Day 90 release). Set profile in client constructor. |
| Wants to issue mixed (different profiles per workflow) | SDK 1.2 supports per-call profile override. |
| Has v1.1 receipts and wants to retroactively claim a v1.2 profile | Not possible. v1.1 receipts remain v1.1. Customers continue issuing v1.1 alongside new v1.2 receipts for as long as they wish. |

**SDK 1.2 supports issuing both v1.1 and v1.2 receipts from the same client.** Customers can adopt v1.2 per workflow without flag-day migrations.

---

## CI gates before freeze

- [ ] All v1.1 receipts in the production canonical set verify under a v1.2 reader (regression: 100K receipts sampled across all v1.1 issuers)
- [ ] Profile resolver behavior matches spec (table-driven tests covering all known profiles + unknown profile fallback)
- [ ] Lineage cycle detection passes (adversarial fixtures with crafted cycles)
- [ ] Soft-delete API returns correct anchor-proof + soft-delete indicator
- [ ] Cross-protocol fields validate format only (no semantic validation in baseline reader)
- [ ] Operator hint fields are explicitly excluded from the signed receipt body — CI verifies issuance never signs them

---

## IETF coordination

The v1.2 spec is published as IETF Internet-Draft `draft-dawkins-scitt-ai-article50-01` (revision -01 of the original).

**Submission timing:**
- Day 45: spec lead circulates revision-01 draft to SCITT working group
- Day 53: incorporate feedback
- Day 58: submit revision-01 to Datatracker
- Day 90: v1.2 deployed to production
- Day 120: revision-02 submitted with production deployment learnings

The IETF process moves slower than the production deployment. The Foundation maintains `spec.ledgerproofhq.io/lpr-1.2` as the canonical reference while the IETF process runs in parallel; if the WG requires substantive changes, the spec lead is authorized to revise without breaking v1.2 already deployed (additive changes only, profile-managed).

---

## Spec deliverables (Foundation publishes by Day 60)

- `spec.ledgerproofhq.io/lpr-1.2` — full spec text (Markdown source on GitHub Pages)
- `spec.ledgerproofhq.io/lpr-1.2/profiles/baseline.json` — baseline profile definition
- `spec.ledgerproofhq.io/lpr-1.2/diff-from-1.1.html` — annotated diff
- `spec.ledgerproofhq.io/lpr-1.2/migration-guide.md`
- `spec.ledgerproofhq.io/lpr-1.2/test-vectors.json` — reference vectors for v1.2 receipts
- Updated mapping documents (ISO/IEC 42001, NIST RMF, DORA Article 28) referencing v1.2 fields where applicable
- IETF revision-01 draft + Datatracker entry

---

## Open questions for spec lead to resolve before freeze

1. **Profile URI scheme.** Use `lpr.v1.2.<name>` (current proposal) or `https://spec.ledgerproofhq.io/profiles/v1.2/<name>` (full URI)? Trade-off: brevity vs. self-describing. **Recommend dotted name + canonical resolver at fixed URL.**
2. **Lineage relationship vocabulary.** Open-ended strings or controlled vocabulary? **Recommend controlled vocabulary for v1.2.baseline; profiles may extend.**
3. **Soft-delete cryptographic proof.** Should the operator return a signed soft-delete attestation, or is the absence of metadata + presence of anchor sufficient? **Recommend signed attestation; the regulator wants a trail of who deleted what when.**
4. **Cross-protocol bridge validation.** Should the verifier portal pull and validate the linked C2PA manifest? **Recommend no in v1.2; defer to a Foundation Advisory Council vote at Day 120.**
5. **Operator hint field stability.** Should operator hints be guaranteed stable across operator versions? **Recommend no; they are explicitly advisory and may change.**

Close all five by Day 45 so the freeze can happen on schedule.
