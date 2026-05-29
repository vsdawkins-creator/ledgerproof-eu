# LPR v2.0 — Post-Quantum RFC (Series A Window Draft)

**Purpose:** The Series A audience expects forward visibility on protocol evolution. By Day 180, we publish the LPR v2.0 RFC — the cryptographic-migration plan, not yet implemented, but committed and IETF-tracked. Series A leads see a credible 18-month roadmap; the broader IETF SCITT community sees a real engineering proposal.

**Owner:** Spec Lead + Cryptography Researcher (consulting from Day 120; full hire by Day 180)
**Published as:** `draft-dawkins-scitt-ai-article50-v2-00` on IETF Datatracker
**Publication target:** Day 175 (so it's live before Series A diligence calls begin)
**Implementation target:** Q3 2028 stable

This document is the **public RFC text outline**, not the design rationale (that lives in [Day 120 PQ migration v0.1](../day-120/01-pq-migration-v0.1.md)).

---

## Abstract

LedgerProof Receipt v2.0 introduces post-quantum cryptographic signatures alongside classical Ed25519 signatures, enabling forward-secure attestation under both current and quantum-relevant threat models. v2.0 maintains backwards-compatibility for receipt verification (v1.x receipts remain verifiable under v2.0 readers) and forward-compatibility for receipt anchoring (v2.0 receipts anchor to Bitcoin mainnet via the same Merkle-tree-anchored OP_RETURN mechanism as v1.x).

---

## Document structure

The RFC text follows IETF Internet-Draft conventions. Section outline:

### 1. Introduction
1.1. Motivation: NIST PQC standardization (FIPS 203, 204, 205)
1.2. Relationship to LPR v1.x
1.3. Conventions and definitions

### 2. Threat model
2.1. Cryptographically-relevant quantum computer (CRQC) emergence
2.2. Harvest-now-decrypt-later considerations
2.3. Signature forgery against historical receipts
2.4. Out-of-scope threats

### 3. Receipt format
3.1. Receipt structure (delta from v1.x)
3.2. The `signatures` block (hybrid: Ed25519 + ML-DSA-65)
3.3. Profile system (carried forward from v1.2)
3.4. Lineage chains (carried forward)
3.5. Cross-protocol bridge fields (carried forward)

### 4. Cryptographic primitives
4.1. ML-DSA-65 selection rationale (FIPS 204)
4.2. Hash function selection (SHA-256 retained)
4.3. Symmetric primitives (unchanged)
4.4. Hybrid signature construction
4.5. Key management considerations

### 5. Backwards compatibility
5.1. v1.x receipt verification under v2.0 readers
5.2. The `signature` field removal and migration path
5.3. Mixed-version Merkle trees
5.4. Mixed-version Bitcoin anchors

### 6. Bitcoin anchoring
6.1. OP_RETURN format: `"LPR2" || merkle_root_32` (36 bytes)
6.2. Mixed-version anchor batching
6.3. Anchor verification under v2.0 readers
6.4. Anchor verification of v1.x receipts under v2.0 readers

### 7. Profile system in v2.0
7.1. Profile identifier scheme
7.2. Backwards-compatible profile evolution
7.3. v2.0 profiles for forward-looking regulatory regimes

### 8. Verifier semantics
8.1. Dual-signature verification requirements
8.2. Failure modes
8.3. Verifier reference implementation

### 9. Implementation guidance
9.1. Library selection per language
9.2. Performance characteristics
9.3. HSM integration patterns
9.4. Key rotation procedures

### 10. Security considerations
10.1. Hybrid signature security argument
10.2. Side-channel considerations
10.3. Implementation pitfalls
10.4. GDPR Article 17 compatibility (carried forward)

### 11. IANA considerations
11.1. Profile registry
11.2. Signature algorithm identifiers

### 12. References
12.1. Normative (FIPS 204, RFC 8949, RFC 6962, BIP 152)
12.2. Informative (NIST PQC migration guidance, EU AI Act, ISO/IEC 42001)

### Appendix A — Test vectors
### Appendix B — Migration playbook for v1.x deployments
### Appendix C — Cryptographic agility considerations for v3.x

---

## Key normative requirements

| Requirement | Statement |
|---|---|
| MUST | v2.0 receipts include both Ed25519 and ML-DSA-65 signatures |
| MUST | Verifier verify both signatures; either failure invalidates |
| MUST | v2.0 readers verify v1.x receipts using v1.x rules |
| MUST NOT | v2.0 readers verify v2.0 receipts with only one of the two signatures present |
| MUST | Bitcoin anchor OP_RETURN prefix be `"LPR2"` for v2.0-receipt-bearing anchors |
| MAY | A single Merkle tree batch contain mixed v1.x and v2.0 receipts |
| MUST | Mixed batches use a single OP_RETURN prefix; if any v2.0 receipt is present, prefix is `"LPR2"` |
| SHOULD | Implementations use NIST-standardized PQ libraries only |
| SHOULD | Operators use HSM-backed signing keys for ML-DSA-65 |
| MAY | Customers issue both v1.x and v2.0 receipts during the migration window |

---

## What's explicitly out of scope for v2.0

- KEM migration (TLS-layer): tracked separately in `draft-dawkins-tls-lpr-pq-00`
- Multi-chain anchoring (Ethereum, Solana, etc.): backlog research, not v2.0
- Stateful PQ signatures (XMSS, LMS): rejected for protocol; not revisited
- SLH-DSA (SPHINCS+) signatures: rejected for production due to signature size
- Anchor format extensions beyond the prefix byte change: rejected to preserve OP_RETURN parsability

---

## IETF presentation plan

- **Day 175** — RFC published on Datatracker; announced to SCITT WG mailing list
- **IETF 119 (March 2027)** — Spec Lead presents v2.0 at SCITT WG meeting
- **IETF 120 (July 2027)** — Adoption call expected
- **IETF 121 (November 2027)** — WG draft milestone
- **IESG review** — 2028
- **RFC publication** — late 2028 or early 2029

The IETF timeline is independent of the implementation timeline. We ship v2.0 in production in Q3 2028 even if RFC publication trails.

---

## Coordination with the broader IETF SCITT ecosystem

LPR v2.0 is co-positioned with the IETF SCITT WG's own PQ work. We have submitted comments on:
- SCITT envelope's compatibility with hybrid signatures
- COSE signing algorithm identifiers for ML-DSA-65 (CBOR Object Signing and Encryption)
- The SCITT transparency service signature algorithms

Where our LPR v2.0 work and SCITT WG work converge, we will adopt SCITT's choices to maintain ecosystem coherence.

---

## What this RFC publication signals at Series A

1. **Cryptographic seriousness.** The Series A audience reads a published IETF Internet-Draft on PQ migration as evidence that the protocol is being maintained at the level of seriousness regulators expect.
2. **Forward visibility.** The 2028 implementation timeline gives the Series A audience confidence that the protocol's roadmap is committed, not vaporware.
3. **Foundation governance in action.** The RFC is authored under Foundation auspices, not LedgerProof Inc.'s. This visible separation matters for the diligence narrative.
4. **No flag-day migration.** Customers can adopt v2.0 per-workflow, not all-or-nothing. This de-risks the migration story for enterprise procurement.

---

## Pre-publication gates

- [ ] Cryptography Researcher sign-off on primitive selections
- [ ] External cryptography review by at least one independent reviewer
- [ ] IETF Internet-Draft tooling tested (xml2rfc, idnits, etc.)
- [ ] Spec Lead briefed the SCITT WG chairs informally on the publication
- [ ] Foundation board approval (consent-agenda item; substantive review at next quarterly)
- [ ] Test vectors generated and verified against a reference implementation
- [ ] Companion technical FAQ for customers ready to publish same day
- [ ] Series A deck slide on PQ updated to reference the published draft

---

## What this draft is NOT

- Not a deployment commitment for any date earlier than Q3 2028
- Not a deprecation announcement for v1.x (v1.x receipts remain valid forever)
- Not a binding standard yet (still an Internet-Draft, not an RFC)
- Not the only acceptable PQ migration for the protocol — the Foundation board may revise based on IETF WG feedback before implementation begins
