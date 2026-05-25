# LedgerProof — GDPR Architecture and Data Processing Agreement Template

**Version:** 1.0 Draft
**Date:** May 2026
**Author:** LedgerProof Foundation
**Legal disclaimer:** This document is provided for informational purposes only. It does not constitute legal advice. Deployers should consult qualified legal counsel regarding their GDPR obligations.

---

## Part A — GDPR Privacy Architecture

### A.1 · The architectural guarantee

LedgerProof receipts are designed so that **no personal data is required in, or derivable from, any on-chain record**. The Bitcoin OP_RETURN anchor contains only a 32-byte Merkle root and a 4-byte prefix. The Merkle root is a hash of hashes — it contains no data that can be reversed to reveal any personal information.

The LPR receipt itself (stored in the off-chain calendar operator database) contains:

| Field | Contains personal data? | Notes |
|---|---|---|
| `receipt_id` | No | Random UUID v7 |
| `trace_id` | No | Random UUID v7 |
| `timestamp_ns / timestamp_iso` | No | Unix timestamp in nanoseconds |
| `artifact.content_hash` | Depends — see A.2 | SHA-256 of the document |
| `artifact.content_type` | No | MIME type string |
| `authorship.actor_id` | Depends — see A.3 | AI model identifier or human identifier |
| `authorship.actor_assertion` | Potentially — see A.3 | Deployer-provided string |
| `eu_ai_act_50.deployer_id` | No (legal entity) | Business registration number |
| `eu_ai_act_50.deployer_name` | No (legal entity) | Organization name |
| `anchor.*` | No | Bitcoin transaction data |
| `signature.*` | No | Cryptographic key material |

The artifact itself (the document, image, or other content) is **never** transmitted to or stored by LedgerProof. Only the SHA-256 hash is submitted.

### A.2 · Is a content hash personal data under GDPR?

This is a live legal question. The European Data Protection Board's draft guidelines on blockchain processing (April 2025) distinguish between:

- Hashes of **arbitrary content**: not personal data per se
- Hashes of **content that is uniquely associated with an identifiable individual**: potentially personal data if the hash can be used, in combination with other data, to single out a natural person

LedgerProof's position, consistent with the EDPB draft guidance:

**In most enterprise deployment scenarios, an LPR receipt does not contain personal data.** The `content_hash` is a SHA-256 hash. SHA-256 is a one-way function — the hash cannot be reversed to recover the document content. Without access to the original document AND a list of candidate documents to hash-match against, the content_hash is not re-identifiable.

**However,** deployers should assess their specific context. If the document being anchored is itself uniquely associated with an identified natural person (e.g., a health record identified by patient ID, a legal filing identified by a named individual), and if an adversary could obtain the original document through other means, the deployer should treat the content_hash as potentially personal data in that context and apply appropriate safeguards.

**Practical mitigation:** For high-sensitivity documents containing personal data, deployers SHOULD pre-process the document to produce a canonical form that removes or pseudonymizes direct identifiers before computing the content_hash. The LPR receipt then anchors the pseudonymized form.

### A.3 · `authorship.actor_id` and personal data

When `actor_type = "HUMAN"`, the `actor_id` field may contain an email address, employee ID, or other personal identifier. This constitutes personal data under GDPR. Deployers MUST either:

1. Use a pseudonym or internal identifier that does not directly identify a natural person, OR
2. Ensure that the off-chain receipt store (calendar operator) is configured as a data processor under a DPA, and that the deployer has a lawful basis for processing the personal identifier

When `actor_type = "AI_MODEL"`, `actor_id` is a model identifier (e.g., `openai/gpt-4o/2024-11-20`) — this is not personal data.

For EU AI Act Article 50 receipts, the `deployer_id` and `deployer_name` refer to a legal entity, not a natural person, and are therefore not personal data under GDPR.

### A.4 · Data subject rights

**Right to erasure (Article 17 GDPR):** The on-chain Bitcoin anchor cannot be erased — Bitcoin transactions are permanent by design. However, the anchor contains no personal data (it is a Merkle root). The off-chain receipt record CAN be deleted from LedgerProof's calendar operator database in response to a valid Article 17 request.

Important: deleting the off-chain receipt record means that the Bitcoin anchor can no longer be verified through LedgerProof's infrastructure (the Merkle inclusion proof is lost). The Bitcoin transaction itself remains on the blockchain. A deleted receipt cannot be used to prove anything — the absence of the proof record effectively nullifies the receipt's evidentiary value.

**Right of access (Article 15 GDPR):** Deployers who have submitted receipts containing personal data in `actor_id` or similar fields can request a copy of all receipts associated with their API key. Contact: privacy@ledgerproofhq.io.

**Right to rectification (Article 16 GDPR):** Receipts cannot be modified (this is by design — modification would destroy their evidentiary value). If an error occurred in the personal data included in a receipt, the deployer may issue a new receipt with corrected data and chain it to the original receipt (`chain.prev_receipt_hash`), effectively creating an amendment record.

**Data portability (Article 20 GDPR):** All receipts can be exported in their canonical CBOR or JSON form upon request. Contact: privacy@ledgerproofhq.io.

### A.5 · Data storage and retention

| Data | Location | Retention | GDPR role |
|---|---|---|---|
| Receipt CBOR | Off-chain calendar operator database | Default: 25 years (configurable) | Processor |
| Bitcoin anchor | Bitcoin blockchain (public, permanent) | Permanent | Not applicable (public record) |
| API authentication logs | LedgerProof infrastructure | 12 months | Processor |
| Verifier query logs | LedgerProof infrastructure | 30 days | Processor |
| Deployer account data | LedgerProof account system | Duration of account + 2 years | Controller |

---

## Part B — Data Processing Agreement Template

*The following is a template DPA for use between LedgerProof, Inc. (as Data Processor) and an enterprise deployer (as Data Controller). This template must be reviewed by qualified legal counsel before execution.*

---

### DATA PROCESSING AGREEMENT

**Between:**

**[DEPLOYER NAME]**, a company organized under the laws of [jurisdiction], with registered address at [address], VAT number [number] ("**Controller**")

**and**

**LedgerProof, Inc.**, a Delaware corporation with registered address at [LedgerProof registered address] ("**Processor**")

*Each a "Party", together the "Parties".*

**Effective date:** [date]

---

#### Article 1 — Definitions

1.1 "**Services**" means the LedgerProof receipt issuance, anchoring, and verification services accessed via api.ledgerproofhq.io and verify.ledgerproofhq.io.

1.2 "**Personal Data**" has the meaning given in Article 4(1) GDPR.

1.3 "**Processing**" has the meaning given in Article 4(2) GDPR.

1.4 "**Applicable Data Protection Law**" means the EU General Data Protection Regulation (Regulation (EU) 2016/679), the UK Data Protection Act 2018, and any applicable national implementing legislation.

1.5 Terms not otherwise defined herein shall have the meanings given in GDPR.

---

#### Article 2 — Subject matter and details of processing

2.1 **Subject matter:** The Processor provides receipt issuance and verification services to the Controller in connection with the Controller's use of AI systems generating documents requiring Article 50 transparency marking.

2.2 **Duration:** The term of the Master Services Agreement between the Parties, plus the retention period specified in Article 5 of this DPA.

2.3 **Nature and purpose of processing:** Receipt issuance (creating and storing LPR receipts referencing hashes of Controller-generated documents); verification (responding to queries about receipt validity); anchoring (recording Merkle roots on the Bitcoin blockchain).

2.4 **Type of personal data:** As determined by the Controller's configuration; may include: document content hashes (where the Controller determines the hash constitutes personal data), authorship identifiers (where the Controller uses human actor IDs), and API authentication identifiers.

2.5 **Categories of data subjects:** Employees of the Controller or third parties whose data appears in AI-generated documents anchored by the Controller.

2.6 **Controller's instructions:** The Controller instructs the Processor to process Personal Data solely as required to provide the Services, as further specified in the Processor's documentation (docs.ledgerproofhq.io).

---

#### Article 3 — Processor obligations

3.1 The Processor shall process Personal Data only on documented instructions from the Controller.

3.2 The Processor shall ensure that persons authorized to process the Personal Data have committed themselves to confidentiality.

3.3 The Processor shall implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including:
  - Encryption of Personal Data at rest (AES-256) and in transit (TLS 1.3)
  - Access controls limiting Personal Data access to authorized personnel
  - Regular security assessments of the Services
  - Incident response procedures meeting GDPR Article 33 notification timelines

3.4 The Processor shall not engage any sub-processor without prior general or specific written authorization from the Controller. Current sub-processors are listed at: ledgerproofhq.io/sub-processors

3.5 The Processor shall assist the Controller in responding to requests from data subjects exercising their rights under Chapter III of GDPR.

3.6 The Processor shall delete or return all Personal Data to the Controller upon termination of the Services, at the Controller's choice, and delete existing copies unless required to retain them by Union or Member State law.

3.7 The Processor shall make available to the Controller all information necessary to demonstrate compliance with GDPR Article 28 and allow for and contribute to audits conducted by the Controller.

---

#### Article 4 — Controller obligations

4.1 The Controller warrants that it has a lawful basis for processing the Personal Data submitted to the Services.

4.2 The Controller warrants that it has provided appropriate privacy notices to data subjects whose Personal Data may be included in receipts.

4.3 The Controller is responsible for assessing whether the `artifact.content_hash` of any document constitutes Personal Data in the specific context of the deployment and for configuring the Services accordingly.

4.4 The Controller shall not submit to the Services any Personal Data that is not necessary for the purpose of AI content provenance documentation.

---

#### Article 5 — Data retention and deletion

5.1 Off-chain receipt records: retained for 25 years from issuance date by default. The Controller may request deletion of specific receipt records at any time by contacting privacy@ledgerproofhq.io, subject to Article A.4 of the LedgerProof GDPR Architecture document.

5.2 On-chain Bitcoin anchor records: permanently retained on the Bitcoin blockchain. These records contain only Merkle roots and the LPR1 prefix — no Personal Data.

5.3 Upon termination of Services: the Processor shall delete all off-chain receipt data associated with the Controller's account within 30 days of written termination notice, unless the Controller requests retention under a data escrow arrangement.

---

#### Article 6 — International transfers

6.1 The Processor's primary calendar operator is hosted in [EU region — Frankfurt/Amsterdam, Fly.io]. Processing of EU data subjects' Personal Data shall be conducted within the EU/EEA unless the Controller specifically configures a non-EU calendar operator.

6.2 Any transfer of Personal Data outside the EU/EEA shall be governed by appropriate safeguards as required by GDPR Chapter V, including Standard Contractual Clauses where applicable.

---

#### Article 7 — Liability and indemnification

7.1 Each Party shall be liable for the damage caused by processing that infringes Applicable Data Protection Law in accordance with GDPR Article 82.

7.2 The Processor shall be exempt from liability if it proves that it is not in any way responsible for the event giving rise to the damage.

---

#### Article 8 — Contact details

Privacy contact for the Processor: privacy@ledgerproofhq.io
Data Protection Officer (if appointed): dpo@ledgerproofhq.io

---

*Signature block — [Controller authorized representative] / [LedgerProof, Inc. authorized representative]*

---

*LedgerProof Foundation · GDPR Architecture v1.0 Draft · May 2026*
*This is a template document. It has not been reviewed by legal counsel. Do not execute without qualified legal review.*
