# LedgerProof × eIDAS Compatibility Statement

**Document:** eIDAS Compatibility, v1.0
**Status:** Public statement
**Editor:** Veronica S. Dawkins, LedgerProof Foundation
**Date:** May 25, 2026
**Regulatory basis:** Regulation (EU) No 910/2014 (eIDAS) and Regulation (EU) 2024/1183 (eIDAS 2.0)

---

## 1 · Purpose

This document explains how LedgerProof Receipts (LPRs) interoperate with the EU eIDAS trust framework. It is intended for EU legal teams, qualified trust service providers (QTSPs), and compliance officers evaluating LPR as part of an eIDAS-aware document lifecycle.

**Bottom line:** LPRs are compatible with eIDAS qualified electronic seal verification workflows. LPRs do not replace qualified electronic seals issued by a QTSP — they complement them by providing a Bitcoin-anchored timestamp and integrity proof that survives independently of the QTSP's continued existence.

---

## 2 · Mapping LPR primitives to eIDAS

| eIDAS Concept | LPR Equivalent | Notes |
|---|---|---|
| **Qualified Electronic Seal** | LPR `signature` field (Ed25519, future PQC composite) | LPR signatures are cryptographically equivalent in strength; QTSP-issued seals provide additional regulatory standing |
| **Qualified Electronic Timestamp** | LPR `entry_timestamp` + Bitcoin anchor confirmation | Bitcoin anchor provides a tamper-evident timestamp independent of any TSA |
| **Qualified Trust Service Provider (QTSP)** | LedgerProof Foundation (calendar operator) | LedgerProof is not yet a QTSP; integration with QTSPs is supported via §4 below |
| **Trusted List (TL)** | LedgerProof operator key registry (`/v1/keys`) | Public list of operator verifying keys |
| **Legal validity (Art. 25 eIDAS)** | Receipt evidentiary weight | LPR receipts are admissible as electronic evidence; legal weight depends on jurisdiction and accompanying QTSP-issued elements |

---

## 3 · What LPR adds beyond eIDAS alone

A standard eIDAS qualified electronic seal proves:
- The document was sealed by a specific entity at a specific time
- The document has not been altered since sealing

The seal is verifiable as long as:
- The QTSP's signing certificate remains in a trusted list
- The QTSP's revocation infrastructure (CRL, OCSP) remains operational
- The QTSP itself remains in business

LPR adds a layer that does not depend on any QTSP's continued operation:
- The receipt hash is committed to the Bitcoin blockchain
- Verification requires only access to the Bitcoin chain, which exists independently of any commercial entity
- The receipt remains verifiable for as long as Bitcoin operates

For long-horizon document archives (>10 years), this matters. QTSPs go out of business. Trust lists evolve. Bitcoin's commitment is immutable and verifiable by anyone with a Bitcoin node, indefinitely.

---

## 4 · Joint LPR + QTSP workflow

For deployers seeking maximum legal robustness under eIDAS, LedgerProof recommends a joint workflow:

```
1. Document is finalized.
2. Deployer obtains a qualified electronic seal from a QTSP.
3. Deployer constructs an LPR receipt referencing the sealed document:
     - artifact_hash: SHA-256 of the sealed document
     - signature: Ed25519 signature by the deployer's LedgerProof key
     - content includes a reference to the QTSP seal identifier
4. LPR receipt is published and anchored to Bitcoin.
5. Verifier validates BOTH:
     a. The eIDAS qualified seal (using the QTSP's trust chain)
     b. The LPR receipt (using the Bitcoin anchor)
6. Both must pass for full joint validation.
```

In this workflow, the QTSP provides EU regulatory standing; LPR provides perpetual verifiability. Loss of either does not invalidate the other.

---

## 5 · eIDAS 2.0 considerations

Regulation (EU) 2024/1183 (eIDAS 2.0) introduces qualified electronic ledger services as a new trust service category. LedgerProof's architecture is conceptually aligned with the qualified electronic ledger model:

- Append-only, cryptographically verifiable records
- Independent verification not requiring QTSP cooperation
- Integration with qualified electronic seals and timestamps

LedgerProof Foundation intends to pursue qualification as a qualified electronic ledger service under eIDAS 2.0 once the European Commission's implementing acts under Article 45j are published. Target: 2027.

In the interim, LPR receipts remain compatible with the existing eIDAS framework as described in §2–§4 above.

---

## 6 · Article 50 + eIDAS combined compliance

For deployers subject to both EU AI Act Article 50 (machine-readable AI disclosure) and eIDAS qualified seal requirements (e.g., regulated financial disclosures, legal documents):

1. Generate AI content as usual.
2. Issue LPR `ai/article-50/v1` receipt satisfying Article 50(2).
3. Have the deployer's QTSP apply a qualified electronic seal to the final published document.
4. Optionally issue a follow-up LPR receipt referencing the QTSP-sealed document.
5. Publish the document with both:
   - LPR transparency_marker visible to humans and machines
   - QTSP qualified seal embedded per eIDAS standards

This combined approach satisfies both regulatory frameworks in a single auditable bundle.

---

## 7 · Verification API

LedgerProof's public verification endpoints work alongside eIDAS verification tools without modification:

- `GET /v1/verify/{receipt_id}` returns the LPR receipt for combined validation
- The receipt's `content` field may reference an external qualified seal identifier
- Verifiers using existing eIDAS tooling (e.g., the EU DSS library) can extend their verification to additionally consult the LPR API

A reference verifier integration is available at:
`https://github.com/vsdawkins-creator/ledgerproof-eidas-bridge`

Target availability: June 30, 2026.

---

## 8 · Limitations

This statement is technical, not legal. LedgerProof Foundation is not a qualified trust service provider as of the publication date of this document. Receipts issued by LedgerProof do not, on their own, constitute qualified electronic seals or qualified electronic timestamps within the meaning of eIDAS Articles 35 or 41 respectively.

Deployers requiring qualified elements MUST obtain them from a qualified trust service provider listed in an EU Member State's trusted list. LPR receipts complement, but do not replace, those elements.

---

## 9 · Contact

- eIDAS questions: eidas@ledgerproofhq.io
- QTSP partnerships: partnerships@ledgerproofhq.io
- Joint workflow assistance: support@ledgerproofhq.io

---

*LedgerProof Foundation · May 25, 2026*
*This document is published under CC BY 4.0.*
