# EU AI Act Code of Practice — Signatory Application Package

**Applicant:** LedgerProof Foundation
**Contact:** Veronica S. Dawkins, Founder/Editor — founder@ledgerproofhq.io
**Date:** May 25, 2026
**Target submission:** EU AI Office, by June 1, 2026

---

## 0 · Cover note

LedgerProof Foundation hereby applies to become a signatory to the General-Purpose AI Code of Practice (and the forthcoming Article 50 Code of Practice once finalized) under Regulation (EU) 2024/1689.

We are a technical-infrastructure provider whose sole product addresses Article 50 transparency obligations. Our deployment is live in Frankfurt, our protocol is open and IETF-submitted, and we believe LedgerProof Receipts (LPRs) are the most directly applicable existing implementation of the "machine-readable format" requirement of Article 50(2).

This package contains:
1. Applicant profile and qualifications
2. Technical evidence of capability
3. Code of Practice alignment statement
4. Commitments we are prepared to make as a signatory
5. Requested attachments

---

## 1 · Applicant profile

**Organization:** LedgerProof Foundation (formation in progress, Delaware non-profit; EU establishment via wholly-owned subsidiary planned for Q4 2026)

**Founder/Editor:** Veronica S. Dawkins

**Mission:** Develop and steward an open protocol for cryptographic provenance receipts for AI-generated content, anchored to the Bitcoin blockchain, addressing transparency obligations under EU AI Act Article 50 and analogous regulations in other jurisdictions.

**Operational status (as of May 25, 2026):**
- Live EU production deployment at `https://api-eu.ledgerproofhq.io` (Frankfurt, Fly.io)
- Health endpoint returns `{"status":"ok","db":"ok"}`
- 70 days ahead of the August 2, 2026 Article 50 enforcement date
- Three real Bitcoin mainnet pre-launch demonstration anchors (May 6, May 13, May 18, 2026)
- Open-source reference implementation at `github.com/vsdawkins-creator/ledgerproof-platform`
- IETF draft submitted: `draft-dawkins-scitt-ai-article50-00`

**Public launch:** July 6, 2026

---

## 2 · Technical capability evidence

### 2.1 Article 50 sub-obligation coverage

LedgerProof Receipt v1.1 (the production deployment) provides machine-readable cryptographic receipts for the following Article 50 sub-obligations:

| Sub-obligation | LPR v1.1 Content Type | Live? |
|---|---|---|
| 50(1) Interactive AI disclosure | `ai/chatbot-session/v1` | ✅ schema live, SDK in progress |
| 50(2) Synthetic media marking | `ai/article-50/v1` | ✅ live in production |
| 50(3) Biometric/emotion recognition | (out of scope — GDPR-sensitive) | n/a |
| 50(4) Public-interest text + human review exemption | `ai/article-50/v1` + `ai/human-review/v1` | ✅ schema live, SDK in progress |

To our knowledge, LedgerProof v1.1 is the only open protocol providing receipts for all three of these sub-obligations in machine-readable form.

### 2.2 Architectural properties relevant to Article 50

| Property | Requirement | LPR Implementation |
|---|---|---|
| Machine-readable format | Article 50(2) | JSON + CBOR canonical encoding, IANA media type registration requested |
| Effective | Article 50(2) | SHA-256 content hash + Ed25519 signature; cryptographically tamper-evident |
| Interoperable | Article 50(2) | Open IETF profile, C2PA assertion mapping, eIDAS-compatible |
| Robust | Article 50(2) | Bitcoin blockchain anchoring; survives any single party's failure |
| Reliable | Article 50(2) | Append-only ledger semantics, RFC 6962 Merkle tree construction |
| Clear and distinguishable manner | Article 50(1)/(4) | `transparency_marker` field with default value `"LPR-EU-AI-ACT-50"` |

### 2.3 GDPR safety architecture

LPRs are designed for GDPR compatibility:
- The content itself is **never** transmitted to or stored by LedgerProof — only a SHA-256 hash
- `deployer_id` MUST be a legal-entity identifier (LEI, EUID, VAT, DID); natural-person identifiers are rejected at validation
- `reviewer_role` (in human-review receipts) MUST be a role identifier, not a person's name
- GDPR Article 17 erasure is supported via soft-delete: content fields are nulled while preserving chain integrity (entry_hash, signature, prev_hash)
- Documented in companion specification `12-eu-compliance/03-GDPR-ARCHITECTURE-AND-DPA.md`

### 2.4 Standards engagement

- **IETF SCITT working group:** Draft `draft-dawkins-scitt-ai-article50-00` submitted May 2026
- **C2PA:** Assertion specification (`org.ledgerproof.receipt.v1`) prepared for CAWG submission
- **eIDAS:** Compatibility statement published; QTSP partnership track underway
- **CEN/CENELEC AI Act standardization:** LedgerProof Foundation requests observer status in relevant TC working groups

---

## 3 · Code of Practice alignment statement

LedgerProof Foundation reviewed the second draft of the General-Purpose AI Code of Practice (March 5, 2026) and the published technical guidance from the EU AI Office. We affirm alignment with the following Code positions:

**Multi-layered marking:** The Code's "defence-in-depth combination of watermarking, metadata identifiers, cryptographic provenance and fingerprinting" position is correct. LedgerProof Receipts provide the **cryptographic provenance** layer of this multi-layered approach. We endorse and complement:
- C2PA / Content Credentials for in-file metadata
- SynthID and similar invisible watermarking for content-bound marking
- Perceptual fingerprinting (which we additionally support natively via the `perceptual_hash` field)

LedgerProof Receipts are **additive** to these techniques, not a replacement for any of them. We do not seek to be designated as a singular solution.

**Presumption of conformity:** We understand that signatories receive a presumption of conformity with Article 50 obligations. We commit to producing technical guidance, reference implementations, and integration support to ensure that our protocol can be invoked by other signatories' implementations and that no signatory using LPR receipts in the prescribed manner faces uncertainty about their compliance status.

---

## 4 · Commitments we are prepared to make as a signatory

If admitted as a signatory, LedgerProof Foundation commits to:

1. **Maintain the LPR v1.1 specification as an open standard** under permissive license (CC BY 4.0 for specifications, Apache 2.0 for reference implementations).

2. **Operate the EU production deployment** at `api-eu.ledgerproofhq.io` with:
   - 99.5% target availability
   - EU data residency (Frankfurt region)
   - Public verification endpoint at no cost to verifiers

3. **Provide no-cost reference SDKs** in Python, Node.js, and Rust by July 6, 2026.

4. **Maintain a public verifier** at `verify.ledgerproofhq.io` accessible without authentication.

5. **Publish quarterly transparency reports** including: receipts issued, anchors confirmed, erasure requests processed, key rotations performed.

6. **Federate the calendar operator network**: actively support and recognize independent operators running LPR-compliant calendar services, including operators run by competitors. The protocol explicitly contemplates multiple operators; we will not act in restraint of trade.

7. **Participate constructively in the Code of Practice working group**, including providing technical experts at no cost to the AI Office for working sessions on machine-readable marking.

8. **Implement updates to align with binding CEN/CENELEC technical standards** under the EU AI Act's standardization mandate, within 90 days of standard publication.

9. **Pursue qualification as a qualified electronic ledger service** under eIDAS 2.0 once Article 45j implementing acts are published (target: 2027).

10. **Refrain from anti-competitive practices**: LPR will be free to verify, free to read the specification, and free to operate compatible calendars. Commercial pricing applies only to high-volume publishing customers.

---

## 5 · Requested attachments

The following documents are available for the AI Office's review:

- `04-lpr-spec/LPR-1.0-SPECIFICATION.md` — base protocol specification
- `04-lpr-spec/LPR-1.1-SPECIFICATION.md` — Article 50 expansion
- `04-lpr-spec/IETF-DRAFT-DAWKINS-SCITT-AI-ARTICLE50-00.txt` — IETF Internet-Draft
- `04-lpr-spec/C2PA-ASSERTION-SPEC.md` — C2PA assertion mapping
- `12-eu-compliance/01-EU-AI-ACT-50-PROFILE.md` — Article 50 compliance profile
- `12-eu-compliance/03-GDPR-ARCHITECTURE-AND-DPA.md` — GDPR architecture
- `12-eu-compliance/07-EIDAS-COMPATIBILITY.md` — eIDAS compatibility statement
- `13-api-backend/CONTRACTOR-AUDIT-MAY24.md` — independent senior Rust audit
- Production endpoint: `https://api-eu.ledgerproofhq.io/v1/health`
- Public verifier (current): `https://verify.ledgerproofhq.io/`
- Open-source repo: `https://github.com/vsdawkins-creator/ledgerproof-eu`

---

## 6 · Next steps requested

1. Acknowledgment of receipt
2. Assignment of a working group contact
3. Invitation to participate in remaining Code of Practice consultation sessions
4. Guidance on the technical track for signatory status (timeline, criteria, formal review)

We are available for technical presentations or working sessions in Brussels, by video, or at any forthcoming AI Office workshop. Lead time of one week is sufficient for travel logistics.

---

## 7 · Submission target

Application package to be submitted by:

- **Primary:** EU AI Office contact form (`https://digital-strategy.ec.europa.eu/en/policies/ai-office`)
- **Secondary:** Direct email to the Code of Practice secretariat (TBD — confirm via AI Office)
- **Backup:** Postal submission to:
  > European AI Office
  > Directorate-General for Communications Networks, Content and Technology (DG CONNECT)
  > European Commission
  > 200 Rue de la Loi, 1049 Brussels, Belgium

Veronica to confirm correct postal address and current secretariat contact before sending.

---

## 8 · Cover letter (separate, send with package)

> **Subject:** Application to become a signatory — EU AI Act Code of Practice — LedgerProof Foundation
>
> Dear AI Office,
>
> LedgerProof Foundation respectfully submits its application to become a signatory to the EU AI Act Code(s) of Practice with particular focus on Article 50 transparency obligations.
>
> We are a technical-infrastructure provider with a live EU production deployment (Frankfurt) and an open-protocol implementation that, to our knowledge, is the only existing open standard providing machine-readable cryptographic compliance records for Article 50(1), 50(2), and 50(4) sub-obligations.
>
> Our protocol is Bitcoin-anchored, IETF-submitted, complementary to C2PA, and compatible with eIDAS qualified trust services. Our reference deployment has been live for over two months and demonstrates conformance with the multi-layered marking approach endorsed in the second-draft Code of Practice.
>
> We seek signatory status not for commercial advantage but to ensure that the Code of Practice's machine-readable provenance requirements have a working, open, fully-implemented reference available to all participants. Our commitments are described in the attached application package.
>
> We would welcome a working session with the relevant Code of Practice secretariat at your earliest convenience.
>
> Respectfully,
>
> Veronica S. Dawkins
> Founder & Editor
> LedgerProof Foundation
> founder@ledgerproofhq.io
> +1 (xxx) xxx-xxxx
>
> Attachments: Application package (this document) and supporting specifications

---

*LedgerProof Foundation · May 25, 2026 · Application package, v1.0*
