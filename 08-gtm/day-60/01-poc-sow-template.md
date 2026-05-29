# 30-Day Pilot Statement of Work — Template

**Document version:** v1.0 (June 2026)
**Purpose:** Drop-in SOW for the LedgerProof 30-Day Pilot. Designed to clear enterprise procurement WITHOUT requiring a Master Services Agreement (MSA), legal committee review, or security review beyond what is included in this SOW.

---

# LEDGERPROOF — 30-DAY PILOT
**Statement of Work**

This Statement of Work ("**SOW**") is entered into as of [DATE], 2026 (the "**Effective Date**") between **LedgerProof, Inc.**, a Delaware corporation with offices at [Wilmington, DE address] ("**LedgerProof**") and **[CUSTOMER NAME]**, a [jurisdiction] [entity type] with offices at [address] ("**Customer**"). LedgerProof and Customer each a "**Party**" and together the "**Parties**".

## 1 — Pilot scope

LedgerProof will deploy the LedgerProof Software Development Kit (the "**SDK**") into a single, bounded AI workflow operated by Customer (the "**Pilot Pipeline**"). The Pilot Pipeline is described in Schedule A. The deployment will produce LedgerProof Receipts (as defined in the LedgerProof Receipt Specification version 1.1, available at `spec.ledgerproofhq.io`) covering AI-generated outputs of the Pilot Pipeline during the Pilot Period.

## 2 — Pilot period

The Pilot Period is thirty (30) calendar days beginning on the Effective Date. The Pilot Period may be extended by written agreement of both Parties for one additional thirty (30) day period without modification to the fee in Section 5.

## 3 — Deliverables

LedgerProof will deliver to Customer:

1. **Integration support** to install the SDK into the Pilot Pipeline within five (5) business days of the Effective Date.
2. **Daily receipt collection** during the Pilot Period, anchored to Bitcoin mainnet via LedgerProof's EU operator (Frankfurt).
3. **An Audit-Ready Compliance Stamp PDF** delivered to Customer on Day 30, summarizing the receipts collected during the Pilot Period, mapping the receipts to applicable EU AI Act Article 50 sub-clauses, ISO/IEC 42001 controls, and NIST AI RMF functions.
4. **A Pilot Readout Report** delivered to Customer on Day 30, including: technical integration findings, latency observations, customer-success notes, and recommended path-to-production-deployment.
5. **A live verifier portal** at `pilot.ledgerproofhq.io/{customer-slug}` accessible to authorized Customer personnel throughout the Pilot Period.

## 4 — Success criteria

The Pilot is deemed successful if all of the following are achieved by Day 30:

1. **Technical:** Latency overhead added by the SDK does not exceed fifty (50) milliseconds at the 99th percentile across the Pilot Pipeline.
2. **Operational:** The LedgerProof EU operator maintains 99.5% or better availability during the Pilot Period.
3. **Compliance:** The Audit-Ready Compliance Stamp PDF is delivered on or before Day 30.
4. **Receipt integrity:** 100% of AI-generated outputs of the Pilot Pipeline during the Pilot Period are anchored to Bitcoin mainnet within the SLO defined in Schedule B.

If all four criteria are met, the Pilot is deemed successful. If any criterion is not met, the Parties will negotiate in good faith. Customer is entitled to a 100% refund of the Pilot Fee if technical criterion (1) or operational criterion (2) is not met.

## 5 — Fees

The total fee for the Pilot (the "**Pilot Fee**") is **twenty-five thousand United States dollars ($25,000 USD)**, payable as follows:

- $12,500 due on the Effective Date
- $12,500 due on Day 30 upon delivery of the Audit-Ready Compliance Stamp PDF and the Pilot Readout Report

The Pilot Fee is **100% creditable** against any LedgerProof annual subscription contract signed by Customer within sixty (60) days following the end of the Pilot Period.

## 6 — Data handling and privacy

1. **No content data leaves Customer's perimeter.** The SDK computes SHA-256 hashes of Customer's AI-generated content locally. Only the resulting hash, non-PII metadata, and the LedgerProof Receipt are transmitted to the LedgerProof EU operator. Original content (audio, images, video, text, documents) is never transmitted, stored, or processed by LedgerProof.
2. **GDPR compliance.** LedgerProof's data processing role under GDPR Article 28 is governed by the LedgerProof Data Processing Addendum, attached as Schedule C.
3. **Erasure.** Customer may request erasure of metadata associated with any LedgerProof Receipt at any time via the procedure in the LedgerProof Privacy Policy. Erasure does not affect the Bitcoin anchor, which only contains a Merkle root and no Customer-attributable data.
4. **Pilot data retention.** Upon the end of the Pilot Period, all metadata stored by LedgerProof associated with the Pilot will be retained for ninety (90) days for Customer's verification needs and then erased, unless Customer signs an annual subscription contract.

## 7 — Confidentiality

Each Party will hold the other Party's Confidential Information in confidence using the same degree of care it uses for its own confidential information, but no less than reasonable care. This obligation survives termination of this SOW for three (3) years.

## 8 — Warranties

LedgerProof represents and warrants that:

1. The SDK, when deployed in accordance with LedgerProof's published documentation, will perform substantially as described in such documentation during the Pilot Period.
2. LedgerProof has not been notified of any unauthorized disclosure of Customer Confidential Information by LedgerProof.
3. LedgerProof maintains the security posture documented in Schedule D, including SOC 2 Type 1 attestation [attached / in progress with delivery date attached].

Customer's exclusive remedy for any breach of the foregoing warranties is a refund of the Pilot Fee.

## 9 — Limitations of liability

EXCEPT FOR BREACH OF CONFIDENTIALITY OBLIGATIONS OR GROSS NEGLIGENCE, EACH PARTY'S CUMULATIVE LIABILITY UNDER THIS SOW IS LIMITED TO THE PILOT FEE PAID OR PAYABLE. IN NO EVENT WILL EITHER PARTY BE LIABLE FOR LOST PROFITS, LOST DATA, OR INDIRECT, CONSEQUENTIAL, INCIDENTAL, OR PUNITIVE DAMAGES.

## 10 — Termination

Either Party may terminate this SOW for any reason on ten (10) days' written notice. Upon termination, Customer is entitled to a prorated refund of the Pilot Fee for any portion of the Pilot Period not yet elapsed, and LedgerProof will deliver an interim Audit-Ready Compliance Stamp PDF reflecting receipts collected through the termination date.

## 11 — Governing law

This SOW is governed by the laws of [the State of Delaware, USA] OR [Customer-preferred jurisdiction — to be agreed on the cover page].

## 12 — Entire agreement

This SOW, together with its Schedules, constitutes the entire agreement between the Parties with respect to the Pilot. No other agreement (including any LedgerProof or Customer general terms and conditions referenced in any quote, invoice, purchase order, or click-through) applies unless explicitly incorporated here by signed amendment.

---

**[CUSTOMER SIGNATURE BLOCK]**

**[LEDGERPROOF SIGNATURE BLOCK]**

---

# SCHEDULE A — Pilot Pipeline Definition

**Pilot Pipeline:** [Specific AI workflow, e.g., "Customer's internal HR resume-screening AI tool, accessed via Workday Recruiting"]

**Estimated daily output volume:** [N] AI-generated decisions per day
**Estimated 30-day total volume:** [N × 30]
**Integration touchpoint:** [Specific API or webhook in the Pilot Pipeline where the LedgerProof SDK will be installed]
**Technical owner at Customer:** [Name, title, email]
**Compliance owner at Customer:** [Name, title, email]

# SCHEDULE B — SLOs

**Receipt issuance latency (P99):** 200 ms
**Bitcoin anchor SLO:** Within 24 hours of receipt issuance, 99% of the time
**Operator availability:** 99.5%

# SCHEDULE C — Data Processing Addendum

Standard LedgerProof DPA (current version available at `legal.ledgerproofhq.io/dpa`). Customer-specific amendments may be appended.

# SCHEDULE D — Security Posture

- SOC 2 Type 1 [attached / scheduled for completion by Day 60]
- SOC 2 Type 2 in progress, scheduled for completion by Day 270
- ISO 27001 in progress, scheduled for completion by Day 360
- Penetration test by [Trail of Bits / NCC Group] scheduled for completion by Day 90
- Cryptographic primitives: SHA-256, Ed25519, RFC 6962 Merkle, canonical CBOR (RFC 8949). All NIST-standardized.
- EU data residency: All Customer metadata processed and stored within the European Union (Fly.io Frankfurt). No transfer to third countries.
