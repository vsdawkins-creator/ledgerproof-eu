# Regulator Briefing — LedgerProof and Article 50

**Document version:** v1.0 (June 2026)
**Audience:** Regulator staff at EU Commission DG-CNECT, national AI competent authorities (BNetzA, AGCOM, CNIL, AP, etc.), and EU AI Office personnel
**Purpose:** A 4-page primer that a regulator reads in 10 minutes and walks away knowing exactly what LedgerProof is, what it is not, and how to verify a LedgerProof Receipt without trusting LedgerProof

**Distribution channel:** Direct outreach to named regulator-side contacts via Foundation-branded email (`registry@ledgerproofhq.io`), not founder-branded. Briefings happen on Foundation letterhead, not commercial letterhead.

---

## 1. What LedgerProof is

LedgerProof is an open cryptographic protocol that produces **regulator-verifiable receipts of AI-generated outputs**. The protocol is published as an IETF Internet-Draft (`draft-dawkins-scitt-ai-article50-00`, confirmed on Datatracker May 25, 2026) and is governed by the LedgerProof Foundation, a US 501(c)(3) in formation with Swiss Verein and Singapore non-profit twins planned for Q1 2027.

The protocol's design objective is a single property: **a regulator can verify that an AI output was disclosed in accordance with Article 50 without trusting any commercial party.** Verification uses public Bitcoin chain state, the published Ed25519 public keys of the receipt issuer, and the open IETF specification. No LedgerProof service or commercial relationship is on the verification path.

## 2. What LedgerProof is not

- **Not a Code of Practice.** The Code of Practice is the regulator's instrument. LedgerProof Receipts are evidence that fits inside whatever Code of Practice the Commission finalizes.
- **Not a closed standard.** Any organization may implement the receipt format from the IETF spec. Any organization may run an operator that issues receipts. The Foundation membership is the coordination layer, not a gating mechanism.
- **Not an AI safety tool.** LedgerProof does not measure AI risk, evaluate model behavior, or filter outputs. It records what happened, with cryptographic integrity, after the AI system has acted.
- **Not a regulatory advisor.** The Foundation does not interpret Article 50 obligations on behalf of any party. Mappings published by the Foundation are reference documents, not legal advice.

## 3. How a regulator verifies a LedgerProof Receipt

The verification flow is identical whether the regulator is examining a single receipt or an Audit-Ready Compliance Stamp PDF covering millions of receipts.

**Step 1 — Obtain the receipt or stamp.** From the regulated entity, in the entity's regular response to an information request.

**Step 2 — Verify the Ed25519 signature.** The receipt is signed by the issuer (typically the regulated entity itself, acting as Provider or Deployer under Article 25 of the AI Act). The public key is published in a DID document or in an eIDAS-qualified electronic seal. The signature can be verified with any standard cryptographic library.

**Step 3 — Verify the Bitcoin anchor.** The receipt includes a Bitcoin block height and a Merkle inclusion proof. The regulator queries any Bitcoin node (or any public block explorer) to fetch the block's OP_RETURN entry at the specified height, then re-computes the Merkle root from the receipt's leaf and inclusion path. If the recomputed root matches the OP_RETURN entry, the receipt is proven to have existed at or before the timestamp of the Bitcoin block.

**Step 4 — Verify the receipt's claim against Article 50.** The receipt declares which Article 50 sub-clause it satisfies and includes the fields required by that sub-clause (e.g., the disclosure language used for 50(1) chatbot disclosure, the labeling mechanism used for 50(2) synthetic media). The regulator confirms the declared sub-clause matches the actual obligation that applies to the output.

**Total verification time for a single receipt:** under 10 seconds with the public verifier portal at `verify.ledgerproofhq.io`; under 2 minutes with a regulator's own toolchain.

## 4. What the receipt contains (and what it does not)

**Contains:**
- Issuer DID and signature
- Output content hash (SHA-256)
- Output type classification (text, image, audio, video, decision)
- Article 50 sub-clause claim
- Timestamp (issued and anchored)
- Profile identifier (allows the receipt to evolve as the Code of Practice clarifies)
- Lineage chain reference (optional, links to upstream receipts for derived outputs)

**Does not contain:**
- The output content itself (only its hash)
- Personally identifiable information (the schema rejects email addresses, names, and other PII fields at parse time)
- Customer business data
- Model weights or training data
- Anything that would require GDPR data-subject consent to anchor publicly

The Bitcoin anchor stores only a 32-byte Merkle root prefixed with "LPR1" (36 bytes total). No customer-attributable data ever lands on the public chain.

## 5. GDPR posture

The Foundation has designed the protocol to be compatible with GDPR Article 17 (right to erasure) using **soft-delete semantics at the receipt layer.** When a Customer requests erasure of metadata associated with a specific output, the receipt's metadata is removed from the operator's database. The Bitcoin anchor remains — but the anchor alone is non-identifiable (a Merkle root with no resolvable mapping back to the individual).

The Foundation's view is that the soft-delete posture meets the spirit of GDPR Article 17 while preserving the immutability properties required for regulatory evidence. The Foundation acknowledges that this is a posture, not a settled legal question, and welcomes Data Protection Authority feedback.

## 6. How to engage the Foundation

| Reason | Channel |
|---|---|
| Request a regulator briefing | `registry@ledgerproofhq.io` |
| Submit feedback on the IETF draft | IETF SCITT working group; or `spec@ledgerproofhq.io` |
| Request access to the Foundation Canonical Registry | `registry@ledgerproofhq.io` |
| Report a vulnerability | `security@ledgerproofhq.io` (PGP key at `security.ledgerproofhq.io/pgp`) |
| Submit a Code of Practice consultation reference | `consultation@ledgerproofhq.io` |

The Foundation will respond to regulator inquiries within 2 business days. No commercial discussion happens through these channels.

## 7. Independence

The Foundation is structurally independent from LedgerProof Inc. (the Delaware commercial entity operating one of the receipt-issuing services). The Foundation owns the protocol specification, the canonical registry, and the trademark "LedgerProof." LedgerProof Inc. pays Foundation membership fees on the same terms available to any other operator.

The Foundation's governance is documented at `foundation.ledgerproofhq.io/governance`. The board includes three independent members. No commercial entity holds more than one board seat. Voting on protocol changes requires a two-thirds majority of independent members.

This document is published by the Foundation, not by LedgerProof Inc.

---

## Appendix A — Citations

- IETF Internet-Draft: `draft-dawkins-scitt-ai-article50-00` (Datatracker, May 25, 2026)
- Receipt specification: `spec.ledgerproofhq.io/lpr-1.1`
- Verifier source code: `github.com/ledgerproof/verifier` (Apache 2.0)
- Foundation governance: `foundation.ledgerproofhq.io/governance`
- ISO/IEC 42001 mapping: `spec.ledgerproofhq.io/mappings/iso-42001`

## Appendix B — Founder availability

The Foundation's founding chair, Veronica S. Dawkins, is available for regulator briefings in Brussels, Frankfurt, Paris, Amsterdam, or by video. Briefings are non-commercial; no sales conversation occurs in the same meeting. Request via `registry@ledgerproofhq.io`.
