# LedgerProof Founding Member Agreement — Template v1.0

**Status:** DRAFT — awaiting Cooley (Jodie Bourdet) review and revision before customer-facing distribution. Target completion: Tue Jun 2 EOD.
**Use:** This is the entire legal vehicle for the Founding Member cohort. Replaces the 30-Day Pilot SOW for this 14-day window. Designed to clear customer legal in 3–5 business days.

**Hard scope rule for Cooley:** if the final agreement exceeds 4 pages of printed text (excluding signature page and warrant attachment), the agreement has failed its purpose. Push back on additions; cut wherever possible.

---

# LEDGERPROOF FOUNDING MEMBER AGREEMENT

This Founding Member Agreement (the "**Agreement**") is entered into as of [DATE], 2026 (the "**Effective Date**") between **LedgerProof, Inc.**, a Delaware corporation ("**LedgerProof**") and **[CUSTOMER NAME]**, a [jurisdiction] [entity type] ("**Customer**"). LedgerProof and Customer each a "**Party**" and together the "**Parties**".

**Recitals.** LedgerProof has developed and operates the LedgerProof Protocol ("**LPR**"), an open IETF-tracked cryptographic protocol for evidence of AI-generated outputs, with reference operator service hosted in Frankfurt and a public verifier at `verify.ledgerproofhq.io`. The LedgerProof Foundation (currently in formation as a US 501(c)(3) public charity, with Swiss Verein and Singapore non-profit twin entities planned) governs the LPR specification, reference verifier, and conformance suite. Customer wishes to become a Founding Member of the LedgerProof commercial cohort prior to the LedgerProof public launch on July 6, 2026, on the terms set out below.

## 1 — Founding Member status

LedgerProof grants Customer the status of **Founding Member** of the LedgerProof launch cohort. The cohort is hard-capped at five (5) members; Founding Member status is no longer available for issuance after June 15, 2026.

Founding Member status entitles Customer to:
- The Service (defined in §2)
- The Advisory Council seat (defined in §3)
- The Reference Rights (defined in §4)
- The Price Lock (defined in §5)
- The Warrant (defined in §6)

## 2 — The Service

LedgerProof will provide Customer with access to the LedgerProof commercial service ("**the Service**"), consisting of:

1. **Protocol access.** Production-tier access to the LedgerProof Frankfurt EU operator running LPR v1.1+, with the Python SDK (`pip install ledgerproof`) and TypeScript SDK (`npm install @ledgerproof/sdk`), and direct API access at `api.ledgerproofhq.io`.

2. **Volume.** Up to one million (1,000,000) receipts issued per month under this Agreement at the Standard tier; ten million (10,000,000) receipts per month at the Anchor tier (overage at $0.001 per receipt above tier).

3. **Audit-Ready Compliance Stamp PDF.** Within thirty (30) days of the Effective Date, LedgerProof will deliver to Customer the first Audit-Ready Compliance Stamp PDF summarizing all receipts issued under this Agreement during that thirty-day period, mapped to EU AI Act Article 50 sub-clauses, ISO/IEC 42001 controls, and NIST AI RMF functions.

4. **Best-efforts SLO.** LedgerProof commits, on a best-efforts basis without contractual penalty, to: (a) receipt commitment latency at or below one (1) hour at the 99th percentile; (b) Bitcoin anchor confirmation within twenty-four (24) hours at the 99th percentile. SLO is published in real time at `status.ledgerproofhq.io` and anchored weekly. Hard SLO violations are disclosed in the same channel within 24 hours of detection.

5. **Data handling.** No content data leaves Customer's perimeter. The SDK computes SHA-256 hashes of Customer's AI-generated outputs locally; only the hash, non-PII metadata, and the LedgerProof Receipt structure are transmitted to the LedgerProof EU operator. The receipt schema rejects email addresses in policy-protected fields at parse time. GDPR Article 17 soft-delete is available via the procedure documented in the LedgerProof Privacy Policy.

## 3 — Advisory Council seat

Customer names one (1) executive (the "**Advisory Council Designee**") to serve on the LedgerProof Foundation Customer Advisory Council. The Advisory Council:
- Meets quarterly via video conference (one in-person meeting per year, at the Foundation's expense)
- Provides Customer input on protocol roadmap, regulation-mapping priorities, and Foundation transparency reporting
- Is distinct from the Foundation Board of Directors and the Technical Steering Committee
- Does not create any fiduciary, governance, or financial relationship with the Foundation
- Carries no voting authority on Foundation matters
- The seat commences upon the Foundation's receipt of its IRS 501(c)(3) determination letter (target: October 2026) or upon LedgerProof's earlier election

## 4 — Reference Rights

LedgerProof MAY name Customer as a "Founding Member" in:
- The LedgerProof public launch announcement on July 6, 2026, and subsequent launch-window communications (logo, quote pre-approved by Customer, role description pre-approved by Customer)
- LedgerProof's website (`ledgerproofhq.io`), case studies, investor materials, Foundation transparency reports
- Press inquiries to LedgerProof regarding the Founding Member cohort

Customer warrants that the executive named in §3 OR a duly authorized communications representative will provide one (1) approved quote and one (1) approved logo for use in the launch announcement within seven (7) calendar days of the Effective Date.

Customer may revoke Reference Rights for future communications on thirty (30) days' written notice; LedgerProof's use of Customer's name in materials already published or in good-faith production at the time of revocation continues.

## 5 — Fees and Price Lock

Customer will pay LedgerProof the annual fee for the Founding Member tier elected on the signature page:

- **Standard tier:** twenty-five thousand United States dollars ($25,000 USD) per year
- **Anchor tier:** fifty thousand United States dollars ($50,000 USD) per year

Each fee is payable annually in advance. First annual fee due within thirty (30) days of the Effective Date.

**Price Lock.** LedgerProof guarantees the annual fee for the tier elected will not increase for the first thirty-six (36) months from the Effective Date. After the initial 36-month period, LedgerProof may adjust the fee at renewal subject to commercial reasonableness and the published Foundation membership pricing schedule then in effect.

## 6 — Warrant

Concurrent with the execution of this Agreement, LedgerProof will deliver to Customer a warrant agreement (the "**Warrant**", attached as Schedule A) granting Customer the right to purchase shares of LedgerProof common stock equivalent to:
- **Standard tier:** zero point one zero percent (0.10%) of LedgerProof's fully-diluted capitalization as of the Effective Date
- **Anchor tier:** zero point two five percent (0.25%) of LedgerProof's fully-diluted capitalization as of the Effective Date

Warrant terms: exercisable at a strike price of $0.01 per share, four-year vest with one-year cliff, accelerated vesting on a change-of-control event of LedgerProof. Customer's failure to exercise within ten (10) years from the Effective Date causes the Warrant to lapse. The Warrant is fully assignable by Customer (subject to standard securities-law restrictions on private-company stock).

## 7 — Confidentiality

Each Party will hold the other Party's Confidential Information in confidence using the same degree of care it uses for its own confidential information, but no less than reasonable care. This obligation survives termination for three (3) years.

**Carve-out for the Founding Member cohort itself.** The fact of Customer's Founding Member status, the existence of this Agreement, and the existence of the Warrant ARE NOT Customer's Confidential Information. LedgerProof's right to publicly disclose Customer's Founding Member status per §4 controls.

## 8 — Warranties

LedgerProof represents and warrants that:
1. The Service, when used in accordance with LedgerProof's published documentation, will perform substantially as described in such documentation
2. LedgerProof maintains the security posture documented in `security.ledgerproofhq.io`, including the published Trail of Bits canonicalization audit (Jun 2026) and Latacora supply-chain review (Jul 2026)
3. LedgerProof has not received notice of any unauthorized disclosure of Customer Confidential Information by LedgerProof

Customer's exclusive remedy for any breach of the foregoing warranties is, at Customer's election, (a) a refund of the unused portion of the annual fee, or (b) thirty (30) days for LedgerProof to cure followed by Customer termination per §10.

**No certification of regulatory compliance.** LedgerProof does NOT warrant that the Service, by itself, makes Customer compliant with the EU AI Act, GDPR, DORA, MiFID II, ISO/IEC 42001, NIST AI RMF, or any other regulation. The Service provides cryptographic evidence layer; regulatory compliance is the joint responsibility of Customer's compliance program and Customer's interpretation of applicable law.

## 9 — Liability

EXCEPT FOR BREACH OF CONFIDENTIALITY OBLIGATIONS, GROSS NEGLIGENCE, OR WILLFUL MISCONDUCT, EACH PARTY'S CUMULATIVE LIABILITY UNDER THIS AGREEMENT IS LIMITED TO THE ANNUAL FEE PAID OR PAYABLE FOR THE THEN-CURRENT YEAR. IN NO EVENT WILL EITHER PARTY BE LIABLE FOR LOST PROFITS, LOST DATA, OR INDIRECT, CONSEQUENTIAL, INCIDENTAL, OR PUNITIVE DAMAGES.

## 10 — Term and Termination

This Agreement commences on the Effective Date and continues for three (3) years (the "Initial Term"), automatically renewing for successive one-year terms unless either Party gives written notice of non-renewal at least sixty (60) days before the then-current term ends.

Either Party may terminate this Agreement for material breach on thirty (30) days' written notice if the breach is not cured during the notice period. Upon termination:
- Customer's Founding Member status, Advisory Council seat, and Warrant survive only if termination is by Customer for LedgerProof's uncured material breach.
- The Price Lock terminates.
- Reference Rights survive only for Customer materials already published.
- The Warrant vesting accelerates by twelve months on termination by LedgerProof without cause.

## 11 — Governing law and dispute resolution

This Agreement is governed by the laws of the State of Delaware, USA, without reference to its conflict-of-laws principles. Any dispute arising under this Agreement is subject to the exclusive jurisdiction of the federal and state courts located in New Castle County, Delaware. The Parties waive any objection to venue or jurisdiction in those courts.

## 12 — Entire agreement; modifications

This Agreement (including Schedule A, the Warrant) constitutes the entire agreement between the Parties with respect to the Founding Member status. No other agreement (including any LedgerProof or Customer general terms and conditions referenced in any quote, invoice, purchase order, or click-through) applies unless explicitly incorporated here by signed amendment. This Agreement may be amended only by a writing signed by both Parties.

---

## Signature page

| LedgerProof, Inc. (Delaware) | [Customer Name] |
|---|---|
| | |
| __________________________ | __________________________ |
| Veronica S. Dawkins, Founder & CEO | [Authorized Signatory] |
| Date: _______________________ | Date: _______________________ |

**Tier elected (check one):**
- [ ] Standard ($25,000/year; 1M receipts/month; 0.10% warrant)
- [ ] Anchor ($50,000/year; 10M receipts/month; 0.25% warrant)

**Advisory Council Designee:** ____________________________________

**Customer billing contact:** _____________________________________

**Customer technical contact:** ___________________________________

---

## Schedule A — Warrant Agreement

[Cooley standard early-stage warrant template, customized for the percentage and tier per §6. Three to five pages. Drafted by Jodie Bourdet within 48 hours of engagement.]

---

## Drafting notes for Cooley

1. The 4-page maximum for the body of this agreement (excluding signature page and Schedule A) is non-negotiable. If a section needs to grow, another section needs to shrink.

2. The "No certification of regulatory compliance" warranty in §8 is load-bearing. Customer counsel will try to soften it; LedgerProof's position is that the protocol is the evidence layer, not the compliance certification. Hold the line.

3. The Reference Rights in §4 are the actual commercial value of the agreement to LedgerProof. Customer counsel will try to make these revocable on shorter notice; we are willing to extend the cure period for breach of reference but not to make the rights cancellable at-will during the launch window (June 15–July 13).

4. The carve-out in §7 (Founding Member status is NOT Customer's Confidential Information) is what makes the press release possible. Critical.

5. The Warrant at §6 should be on Cooley's standard early-stage warrant template; Schedule A should be the warrant itself, not a separate signed agreement. This is to keep the deal a one-document execution.

6. The Foundation Advisory Council in §3 should be referenced by name only; the Foundation itself is in formation and the Customer Advisory Council charter has not yet been ratified. Defer charter detail to a Foundation publication; the agreement only commits LedgerProof to honor the seat assignment.

7. The customer types most likely to redline this agreement: mid-market FSI (will want indemnification language; we hold the line at the §9 liability cap), AI scaleups (will accept this template essentially as-is), media GCs (will want stronger press-coordination language; we accept reasonable amendments to §4 detailing the launch-window press process).
