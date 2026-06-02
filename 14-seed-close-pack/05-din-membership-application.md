# DIN SME Membership Application Briefing

**Filing entity**: LedgerProof Foundation (US 501(c)(3) in formation, Delaware; fiscal sponsorship by New Venture Fund through Q4 2026)
**Membership tier sought**: Mitgliedschaft KMU (SME / Small-and-Medium-Enterprise tier), DIN e.V., Berlin
**Primary delegate**: Veronica S. Dawkins, Founder, LedgerProof Inc.; Director, LedgerProof Foundation (in formation)
**Secondary delegate**: Foundation Executive Director (TBC, Aug 1, 2026 start)
**Technical advisor (Foundation-side, JTC 21 matters)**: Sebastian Hallensleben (subject to acceptance, see Part A §5)
**Target filing window**: Wednesday, June 3, 2026 (first draft) → Monday, June 15, 2026 (file)
**Kill-switch tripwire**: KS4 — if not filed by June 21, 2026, switch to AFNOR (France) or NEN (Netherlands) and absorb a 4-week standards-path slip
**Master-plan reference**: `14-seed-close-pack/04-atomic-explosion-master-plan.md`, T+5, T+15
**Owner**: Veronica
**Review cadence**: Daily during filing window; weekly thereafter until DIN confirmation receipt

---

## Part A — Internal Strategy Briefing

### A.1 Why DIN membership matters (and why now)

The EU AI Act ("Regulation (EU) 2024/1689") becomes binding for Article 50 transparency obligations on **August 2, 2026** — 62 days from today. Article 40 of the AI Act establishes a **presumption of conformity** for AI systems that comply with **harmonized standards** (hENs) published in the *Official Journal of the European Union* under standardisation request **M/593** (the Commission's request to CEN and CENELEC of May 22, 2023, on AI safety, transparency, robustness, governance, and conformity assessment). Those harmonized standards are developed by **CEN-CENELEC Joint Technical Committee 21 (JTC 21) — "Artificial Intelligence"**.

DIN — *Deutsches Institut für Normung e.V.* — is the German national member body of CEN and CENELEC. National member bodies are the only route through which a non-government entity participates in JTC 21 work. There is no direct "JTC 21 membership" available to a US foundation, an open-source consortium, or a startup. You must mirror your participation through a national member body. The two viable national mirror routes for LedgerProof Foundation are:

1. **DIN** (Germany) via its mirror committee NA 043-01-42 AA "Künstliche Intelligenz" — the largest, most active JTC 21 national mirror, and the one Sebastian Hallensleben (CEN-CENELEC JTC 21 rapporteur for trustworthiness) chairs key working groups within.
2. **AFNOR** (France) via CN/IA, or **NEN** (Netherlands) via NEN AI working groups — both maintain JTC 21 national mirrors but with smaller delegations and weaker rapporteur leverage.

DIN is the right primary path. AFNOR and NEN are the KS4 fallback.

What DIN membership directly buys us:

- **Standing to attend NA 043-01-42 AA mirror committee meetings** (3-4 per year, Berlin/online), where the German position on JTC 21 documents is formed before each JTC 21 plenary.
- **Right to submit New Work Item Proposals (NWIPs)** through the German delegation. A non-member cannot submit an NWIP. An NWIP is the only mechanism by which we get LedgerProof Protocol (LPR) considered as a candidate work item in JTC 21.
- **Read access to in-progress JTC 21 working drafts** before they are public. This is operationally critical: without it, we are responding to harmonized-standard language six to twelve months after it has hardened.
- **Voting weight on German national positions** at JTC 21, proportional to delegation size and tier. SME tier confers a single delegate vote at NA 043-01-42 AA meetings, which is sufficient for our purposes.
- **Eligibility to be nominated to expert delegations** that attend JTC 21 plenaries directly — this is the path by which Hallensleben and Hauser actually participate.

### A.2 Correction discipline (C1 — read this every time)

**DIN membership does NOT confer presumption of conformity. JTC 21 participation does NOT confer presumption of conformity. Co-authoring a CEN-CENELEC technical specification does NOT confer presumption of conformity.** Only an Article 40 harmonized standard (hEN), published in the *OJEU* with citation under M/593 (or its successor mandate), confers the Article 40 presumption.

Article 95 of the AI Act establishes **voluntary codes of conduct** for general-purpose AI providers. Compliance with a voluntary code is a **reputational and supervisory signal** — it tells the AI Office and the national competent authority that a provider is acting in good faith. It does **not** create a legal presumption of conformity with Article 50 transparency obligations or with any other operative provision.

Every paragraph of Part B and every external-facing statement about DIN membership must respect this distinction. We are filing to **participate in the harmonized-standards development process** with the **intention** that work items we contribute to may, over a multi-year horizon, ripen into hENs cited in the *OJEU*. We are not filing because membership confers any legal benefit on LedgerProof users today.

### A.3 SME tier vs full corporate membership

DIN offers several membership tiers. The relevant ones:

| Tier | Approximate annual fee | Voting weight | Right to submit NWIP | Mirror-committee participation |
|---|---|---|---|---|
| Mitgliedschaft KMU (SME) | €3,000–€5,000 | 1 vote per delegate seat | Yes | Yes |
| Mitgliedschaft (Standard corporate) | €15,000–€30,000+ | Larger delegations possible | Yes | Yes, broader |
| Fördermitgliedschaft (Sponsoring) | €50,000+ | Same as standard | Yes | Yes, plus visibility | 

The SME tier is the right choice because:

1. **Eligibility**: The Foundation, post-formation, will sit at a US 501(c)(3) with budgeted Y1 expenses in the low single-digit millions of dollars (per `14-seed-close-pack/01-cfo-24-month-model.md`). It comfortably qualifies as an SME under DIN's revenue threshold (the threshold is set at the entity level, not the affiliated commercial entity).
2. **Optics**: A small open-protocol non-profit applying as an SME reads as authentic. The same Foundation applying as a sponsoring member would read as a US startup buying its way into the German standards process, which is precisely the read we cannot afford to give Hallensleben, Hauser, or the DIN secretariat.
3. **Cost discipline**: The Foundation's Y1 operating budget allocates approximately **$48K/year to standards participation** (DIN + AFNOR + BSI fees + JTC 21 participation costs, per `14-seed-close-pack/01-cfo-24-month-model.md`). SME tier fits inside that envelope and leaves room for AFNOR and BSI parallel memberships in Y2.
4. **Functional parity**: SME tier grants the same NWIP authority and the same mirror-committee participation as Standard corporate tier. The Foundation does not need more votes. It needs a credible seat and a credible delegate.

Decision: file as SME. Upgrade to Standard if Foundation revenues materially exceed the SME threshold at Y2 budget review, or if JTC 21 work load justifies a multi-delegate seat.

### A.4 Why Foundation files, not Inc.

This is the load-bearing decision and the one most often gotten wrong by startup founders.

**LedgerProof Foundation files. LedgerProof Inc. does not.**

Reasons:

1. **Standards bodies will not accept a venture-backed corporation as a credible steward of an open protocol they may eventually harmonize.** DIN's mirror-committee chairs and Hallensleben specifically will read an Inc. application as a vendor lobbying for its commercial advantage. They will read a Foundation application as a public-interest entity contributing to the process. Same protocol; different credibility.
2. **The dual-entity structure was designed precisely for this asymmetry** (per `04-atomic-explosion-master-plan.md` §3). The Foundation holds the protocol IP under an Apache 2.0 / open license and runs the spec process. Inc. operates the hosted commercial services around it. Regulators, standards bodies, and journalists engage with the Foundation. Customers and investors engage with Inc.
3. **Conflict-of-interest disclosure is cleaner from the Foundation side.** Veronica's dual role as Director (Foundation) and Founder/CEO (Inc.) must be disclosed in the DIN application. From the Foundation, this is a routine sponsor-relationship disclosure. From Inc., it would be a flag.
4. **Letterhead discipline scales beyond this filing.** Every subsequent regulator-facing artifact — AI Office briefing notes, EU AI Board correspondence, ENISA technical inputs, national competent authority engagements (BaFin, ACPR, AFM) — flows from the Foundation. Establishing that pattern on this filing makes the next twenty cleaner.

Operational mechanics: the Foundation is in formation. Articles of Incorporation will be filed in Delaware before June 15, 2026 (per Cooley engagement letter and the Adler & Colvin retainer pending sign at master-plan T+0). IRS Form 1023 follows on the standard 90-day cycle. **In the interim, the Foundation operates under fiscal sponsorship from New Venture Fund.** The DIN application will state this fiscal-sponsorship arrangement explicitly. DIN accepts fiscally-sponsored entities for membership; the sponsoring 501(c)(3) provides the audited financial-history substitute that DIN's membership review requires.

### A.5 Sponsorship and co-applicant strategy

DIN does not formally require sponsorship for SME membership, but the SME application materially benefits from named inside-DIN supporters. The three target sponsors:

**Sebastian Hallensleben** — Head of Digitalisation and AI at VDE / DKE, CEN-CENELEC JTC 21 rapporteur on trustworthiness and transparency, leads NA 043-01-42 AA AK Trustworthiness. He is the single most consequential inside-DIN ally we can recruit. He is also the IETF-adjacent figure most likely to recognize SCITT alignment (see Birkholz introduction, master-plan T+11). **Warm-intro route**: Henk Birkholz (Fraunhofer SIT, IETF SCITT WG co-chair) → Hallensleben. Birkholz has direct working relationship through ENISA trustworthy-AI work. Email request goes out **Monday, June 8, 2026** (master-plan T+8). Specific ask: 30-minute call by June 12; sponsorship letter for DIN application by June 14; ongoing role as **Foundation-side technical advisor on JTC 21 matters** (unpaid; Foundation advisory role, with conflict disclosure if he also advises commercial competitors).

**Andreas Hauser** — Director, AI Quality and Safety, TÜV SÜD. He is the German notified-body voice on AI conformity assessment and chairs working groups on AI testing methodology within DIN mirror activities. He is the inside-DIN voice who can validate that LPR's verification model (local Merkle proof + Ed25519 + Bitcoin anchor — see C4 in master-plan §2) is consistent with the conformity-assessment patterns notified bodies will be asked to apply. **Warm-intro route**: through Hallensleben once we have him, or independently through Cooley's Frankfurt office (Adam Ross relationship via Munich Re due-diligence work). Email request goes out **Monday, June 8, 2026**. Specific ask: 30-minute call by June 12; technical-credibility letter (1 paragraph) by June 14.

**Sebastiano Toffaletti** — Secretary General, European DIGITAL SME Alliance. Brussels-based. Long-running advocacy voice for SME representation in EU standards processes. He does not sit at DIN; he sits adjacent to it, with reputation and convening power across all CEN-CENELEC national bodies. His value is **defensive**: a letter from DIGITAL SME Alliance endorsing our SME-tier application is the most credible response to any DIN reviewer who looks at a US-affiliated foundation and wonders whether SME-tier qualification is being gamed. **Warm-intro route**: through Maxime Bezombes (DG-CNECT) or independently through DIGITAL SME's open-source-software working group. Email request goes out **Monday, June 8, 2026** (master-plan T+8, `Hallensleben + Toffaletti warm-intro requests`). Specific ask: written endorsement letter by June 14.

All three are listed in the Real-10 contact map in `04-atomic-explosion-master-plan.md` §2.

If we secure two of three by June 14, file on June 15 as planned. If we secure only one, file on June 15 anyway and add the second-and-third endorsement as a supplemental submission within the 30-day post-filing window DIN allows for completeness materials. **Do not delay the filing for sponsorship completeness — KS4 bites first.**

### A.6 Timeline

| Date | Action | Owner | Output |
|---|---|---|---|
| Wed Jun 3, 2026 | First draft of application complete (Part B of this document) | Veronica | Draft .docx + .md in repo |
| Thu Jun 4, 2026 | Adler & Colvin review of Foundation-formation references in draft | Veronica + Adler & Colvin | Redlines |
| Fri Jun 5, 2026 | German-language translation request to Sprachdienst (recommended: Lionbridge Legal or Acolad Legal, Frankfurt office) | Veronica + ops contractor | Translation engagement letter |
| Mon Jun 8, 2026 | Sponsorship outreach to Hallensleben, Hauser, Toffaletti | Veronica | Email + log entries |
| Wed Jun 10, 2026 | Revision pass incorporating sponsor feedback and translation review | Veronica | v0.2 |
| Fri Jun 12, 2026 | Sponsor calls completed; written endorsements received (target 2 of 3) | Veronica | PDFs in repo |
| Sun Jun 14, 2026 | Final review with Adler & Colvin; financial annexes finalized; signature block prepared | Veronica + Adler & Colvin | v1.0 ready to file |
| **Mon Jun 15, 2026** | **File DIN SME membership application** (master-plan T+15) | Veronica | DIN application receipt; ops-state.json updated |
| Jun 22, 2026 | Acknowledgment-of-receipt expected from DIN secretariat | DIN | Tracking number |
| Jul–Aug 2026 | DIN membership review (typical 6–8 weeks) | DIN | Membership decision |
| Aug 1–15, 2026 | Membership confirmation target (before Article 50 enforcement Aug 2) | DIN | Confirmation letter |
| Aug–Sep 2026 | First NA 043-01-42 AA mirror-committee meeting attendance (calendar-dependent) | Veronica + Foundation ED | Meeting minutes |
| Q3 2026 | First NWIP draft prepared; submission via German delegation | Veronica + Hallensleben advisory | NWIP draft, see `14-seed-close-pack/07-jtc21-nwip-outline.md` |

### A.7 Budget

| Line item | Y1 | Y2 |
|---|---|---|
| DIN SME membership fee | €4,000 | €4,000 |
| AFNOR membership fee (Y2 if standards path expands) | — | €5,000 |
| BSI membership fee (Y2 if UK retained scope) | — | £3,500 |
| German-language Sprachdienst (initial translation + ongoing) | €3,500 | €6,000 |
| JTC 21 + NA 043-01-42 AA travel (4 meetings × €1,500 avg) | €6,000 | €8,000 |
| Document fees, working-draft access | €1,500 | €2,000 |
| Foundation ED + Veronica working-time allocation (notional, 15% of two FTEs) | — (cash-equivalent allocated in Foundation budget) | — |
| **Total cash** | **~€15,000** | **~€25,500** |

This is consistent with the $48K Y1 standards-participation envelope in `01-cfo-24-month-model.md`.

### A.8 Risks, kill switches, and branch logic

**Primary kill switch: KS4** — DIN application not filed by **June 21, 2026**. Trip conditions: filing slip past June 21 caused by (a) sponsorship outreach failure with no path to filing without sponsors, (b) Foundation formation legal blocker (Adler & Colvin redline cycle stalls), (c) translation delay, or (d) Veronica calendar collision.

**Branch action if KS4 trips:**

1. Pivot primary national-body application to **AFNOR (France)** within 5 business days. AFNOR application materials are similar; the existing draft of Part B can be repurposed with substitution of AFNOR-specific fields, CN/IA mirror committee references, and French-language translation. Sponsorship pivot: target Maxime Bezombes (DG-CNECT) and Winston Maxwell (Hogan Lovells Paris, AI Act commentator) as French-side sponsors.
2. Hold **NEN (Netherlands)** as secondary backup if AFNOR also stalls. NEN's AI mirror committee is smaller and more nimble; NEN application processing has historically been the fastest of the three.
3. Absorb the 4-week schedule slip per `04-atomic-explosion-master-plan.md` §CB4. Update `lpr-status.json` standards milestones to reflect AFNOR confirmation target of **early September 2026** rather than mid-August.
4. The "DIN member, JTC 21 active" line drops from the press kit and is replaced with "national-body member, JTC 21 mirror participation" — less crisp but technically equivalent.

**Secondary risks:**

- **Hallensleben declines sponsorship**: file without him; pursue him as a Foundation Technical Advisory Board member on a longer timeline; backstop with Henk Birkholz as IETF SCITT WG signal of credibility.
- **Foundation formation Articles of Incorporation slip past June 15**: file the DIN application under the New Venture Fund fiscal-sponsorship cover with explicit statement that the Foundation is in formation; submit the formed-entity Articles as supplemental materials within 30 days.
- **DIN secretariat queries SME qualification given affiliated commercial entity (Inc.)**: respond with the dual-entity structural documents (IP license, governance separation memorandum). Adler & Colvin has these templates.
- **C8 — customer-ownership optics**: irrelevant to DIN application substantively, but DIN reviewers may search the founder's public commercial relationships. Specific Strategic Beta Partner arrangements (per master-plan T+4) should not be foregrounded in DIN materials regardless of customer identity. The US/EU counterweight anchor commitments (in window per C8) are the appropriate public-facing partner references.

---

## Part B — DIN SME Membership Application Content Draft

> **Note to filer**: The content below is drafted in English. German-language equivalents for the most load-bearing paragraphs (B.1, B.7, B.8) are provided in §B.9 for Sprachdienst review. DIN accepts English-language applications from international applicants; a German-language summary cover letter is conventionally appended and is included as §B.9.

### B.1 Applicant identification and organization profile

**Applicant**: LedgerProof Foundation
**Legal form**: United States 501(c)(3) tax-exempt non-profit corporation (Delaware), in formation as of the filing date. Fiscal sponsorship through Q4 2026 by New Venture Fund, a U.S. 501(c)(3) public charity (EIN 20-5806345).
**Registered address**: [Adler & Colvin registered agent address, San Francisco, California — final address inserted at filing]
**European correspondence address**: c/o [European Counsel TBC — preferred: Cooley LLP, Frankfurt am Main]
**Date of formation**: Articles of Incorporation filed in Delaware on or before June 15, 2026.
**Tax-exempt status**: IRS Form 1023 filing in progress; recognition pending. During the recognition period, the Foundation operates under fiscal sponsorship as noted above.
**Affiliation disclosure**: The Foundation has a defined structural relationship with LedgerProof Inc., a Delaware C-corporation that licenses the LedgerProof Protocol from the Foundation under an arms-length agreement and operates hosted commercial services around the protocol. The Foundation governs the open protocol specification and standards process. LedgerProof Inc. has no governance role at the Foundation; the Foundation's board includes independent directors representing public-interest, technical, and academic constituencies (composition finalized at formation).

**Mission**: The Foundation exists to develop, maintain, and steward open cryptographic protocols that allow operators of AI systems to produce tamper-evident, locally verifiable records of AI-system inputs and outputs, in service of regulatory transparency obligations including those established by Regulation (EU) 2024/1689 ("EU AI Act"), and analogous obligations under emerging US, UK, and Asia-Pacific AI-governance regimes.

**Funding model**: The Foundation is funded by (i) royalty-style protocol licensing fees from commercial implementers, (ii) targeted grants from public-interest funders, and (iii) member contributions from participating organizations. The Foundation does not accept funding sources that compromise its protocol-neutrality posture.

**Governance**: A board of directors of no fewer than three and no more than nine members, with a majority of independent directors not affiliated with any commercial implementer. Standing committees include a Technical Steering Committee responsible for protocol specification, a Standards Engagement Committee responsible for relationships with bodies including DIN, CEN-CENELEC, ISO/IEC, IETF, and ETSI, and an Audit Committee responsible for financial controls and the Foundation's IRS Form 990 reporting obligations.

### B.2 Technical expertise statement

The LedgerProof Protocol ("LPR") is a cryptographic record-keeping specification that produces a **locally verifiable tamper-evident record** for each AI-system input/output pair. The technical primitives are well-established and standards-based:

- **SHA-256** hashing per FIPS 180-4 for content commitments.
- **Ed25519** signatures per RFC 8032 for operator-attested provenance.
- **RFC 6962-style Merkle trees** for batching and inclusion-proof generation. Merkle batching is operationally necessary to keep HSM signing latency tractable for high-throughput inference workloads (per architectural correction C6: stream-aware signing with N requests → 1 HSM signature).
- **Bitcoin OP_RETURN anchoring** of periodic Merkle roots for global, decentralized, tamper-evident timestamping. The anchoring cadence is configurable; operational defaults publish a root every approximately ten minutes during steady-state operation.
- **Verification is local**: a verifier with the protocol specification, the published Bitcoin block, the Merkle proof, the Ed25519 signature, and the public key can verify a record offline. LedgerProof Foundation does not operate any centralized verification authority that participants depend on. Foundation-operated verification nodes exist as optional convenience services only.

The Foundation maintains an active draft contribution to the **IETF Supply Chain Integrity, Transparency and Trust (SCITT) Working Group** aligning LPR's transparency-log semantics with the SCITT receipt model (RFC drafts in progress as of filing date).

The Foundation publishes three reference SDK implementations:

1. **Python SDK** (`ledgerproof` on PyPI), with framework adapters for the most-used Python AI orchestration stacks.
2. **TypeScript SDK** (`@ledgerproof/sdk` on npm), with adapters for Node, edge runtimes (Vercel, Cloudflare Workers, Deno), and browser verification.
3. **Rust core library** (`ledgerproof` on crates.io) providing the canonical reference implementation for the protocol's cryptographic core.

A **cross-language conformance CI suite** verifies that all three implementations produce byte-identical canonical records for the same inputs and that records produced by any one SDK verify cleanly under any other. The conformance vectors are published openly.

Independent security review is under active commissioning: NCC Group and Trail of Bits have received scoping requests for protocol audit and cryptographic implementation review (sent at master-plan T+2). Audit reports will be published in full on completion.

### B.3 Standards-engagement interests

The Foundation seeks to contribute to standards work in the following areas, listed by priority:

**CEN-CENELEC technical committees of primary interest:**

- **CEN-CENELEC JTC 21 — Artificial Intelligence**, in particular the work streams addressing AI transparency, traceability, record-keeping, and post-market monitoring under standardisation request M/593, with attention to working groups developing harmonized standards for AI Act Article 12 (record-keeping), Article 13 (transparency and provision of information to deployers), Article 50 (transparency obligations for providers and deployers of certain AI systems), Article 60 (real-world testing), and Article 72 (post-market monitoring).
- **CEN-CENELEC JTC 13 — Cybersecurity and Data Protection**, on adjacent cryptographic-protocol work and on the intersection between AI transparency and cybersecurity supply-chain integrity.

**ISO/IEC mirror committees of secondary interest** (Foundation intends to participate through the DIN delegation and/or as a Category C liaison once eligible):

- **ISO/IEC JTC 1/SC 42 — Artificial Intelligence**, particularly WG 1 (Foundational standards), WG 2 (Data), WG 3 (Trustworthiness), and SG 1 (Computational approaches and characteristics).
- **ISO/IEC JTC 1/SC 27 — Information security, cybersecurity and privacy protection**, particularly WG 4 (Security controls and services) and WG 5 (Identity management and privacy technologies).

**ETSI groups of interest** (separate engagement track):

- **ETSI ISG-SAI — Securing Artificial Intelligence Industry Specification Group**, on AI-system integrity and supply-chain provenance.

**IETF working groups of existing engagement:**

- **SCITT WG** (Supply Chain Integrity, Transparency and Trust) — Foundation contributors are active on the WG mailing list and have submitted a draft contribution aligning LPR receipts with SCITT semantics.

### B.4 Financial qualification

The Foundation's funding picture at the filing date:

- **Initial capitalization**: A capital contribution from LedgerProof Inc. at Foundation formation, sized to fund the Foundation's first 24 months of operations at the budgeted run rate. Inc.'s seed financing round, on track to close at approximately **$10 million** at a **$45 million post-money valuation** on or before **June 25, 2026** (per the Founding Member program documents in `14-seed-close-pack/`), provides the source for this initial capital contribution.
- **Fiscal sponsorship**: New Venture Fund serves as the Foundation's fiscal sponsor through Q4 2026, providing 501(c)(3) tax-exempt cover for receipt of grants and member contributions during the IRS Form 1023 recognition period. New Venture Fund applies its standard 7% administrative fee on sponsored funds.
- **Y1 operating budget**: The Foundation's first-year budgeted expenses are in the low single-digit millions of US dollars, supporting protocol specification, standards engagement, audit publication, reference SDK maintenance, and a small core team.
- **Y1 standards-participation allocation**: approximately **$48,000** (~€44,000), allocated across DIN, AFNOR, and BSI memberships, JTC 21 participation costs, document fees, and translation services.
- **SME qualification**: At Y1 budgeted revenues, the Foundation comfortably qualifies under DIN's SME-tier criteria (the EU SME definition: fewer than 250 employees and either annual turnover not exceeding €50M or balance-sheet total not exceeding €43M). The Foundation expects to operate with fewer than 15 employees through Y1 and Y2.

Audited financial statements are not yet available given the Foundation's pre-formation status. The Foundation will submit Y1 Form 990 to the IRS on the standard timeline and will provide DIN with that filing as soon as it is publicly available. In the interim, the Foundation provides New Venture Fund's audited financial statements (sponsoring 501(c)(3)) as the substitute documentation customarily accepted by DIN for fiscally-sponsored applicants.

### B.5 Existing standards participation

**Active engagement** (at filing date):

- **IETF SCITT WG** — active mailing-list participation; draft contribution in progress for the Foundation-authored LPR-to-SCITT receipt alignment specification.

**Intended engagement** (within 12 months of filing):

- **ISO/IEC JTC 1/SC 42 WG 3 (Trustworthiness)** — participation via the German delegation through DIN, focused on traceability and transparency work items.
- **ETSI ISG-SAI** — separate observer-member application planned for Q4 2026, contingent on Foundation operational capacity.
- **CEN-CENELEC JTC 13** — mirror-committee observation through the DIN delegation on cryptographic-protocol adjacencies.

The Foundation does not currently hold liaison status with any of the above bodies.

### B.6 Named representatives

**Primary delegate to NA 043-01-42 AA (Künstliche Intelligenz) and JTC 21 matters:**

**Veronica S. Dawkins**, Founder and CEO of LedgerProof Inc. and Director (Foundation Board), LedgerProof Foundation. Conflict-of-interest disclosure: Dawkins serves as a director of both the Foundation and the affiliated commercial entity LedgerProof Inc. Dawkins will recuse on any specific work item where the Foundation's Standards Engagement Committee determines a material commercial conflict exists. All financial relationships, equity holdings, and material commercial relationships will be disclosed to the DIN secretariat on a standing basis and updated upon material change.

**Secondary delegate (to be confirmed by August 1, 2026 start date):**

**Foundation Executive Director (TBC)** — search in progress; final candidate to be confirmed by the Foundation's first independent board meeting (target: late July 2026). The Executive Director, once seated, becomes the Foundation's principal day-to-day delegate to DIN and JTC 21 mirror work; Dawkins steps back to alternate-delegate / oversight role.

**Foundation-side technical advisor on JTC 21 matters (subject to acceptance):**

**Sebastian Hallensleben**, Head of Digitalisation and AI at VDE / DKE, CEN-CENELEC JTC 21 rapporteur. Mr. Hallensleben is a candidate to serve as the Foundation's technical advisor on JTC 21 work, in an unpaid advisory capacity disclosed to all relevant committee secretariats. The Foundation will confirm Mr. Hallensleben's acceptance and the scope of his advisory role prior to any formal NWIP submission, and will recuse him from any conflict-of-interest situations including matters where VDE / DKE has independent commercial or technical positions.

### B.7 Statement of intent

The Foundation respectfully states its intent in joining DIN as follows:

The Foundation seeks to contribute, through DIN's national delegation to CEN-CENELEC JTC 21 and through DIN's mirror activities to ISO/IEC JTC 1/SC 42 and ETSI ISG-SAI, to the development of European and international standards for AI transparency, traceability, and post-market monitoring. The Foundation's contribution will focus on the specific technical area in which it has demonstrable expertise: **cryptographic record-keeping for AI-system inputs and outputs, with locally-verifiable tamper-evidence and decentralized timestamping**.

The Foundation intends, once admitted, to:

1. Attend NA 043-01-42 AA mirror-committee meetings on a regular basis through its delegated representatives.
2. Submit technical contributions to JTC 21 working drafts addressing record-keeping, traceability, and transparency, consistent with the obligations established by Article 12, Article 13, Article 50, Article 60, and Article 72 of Regulation (EU) 2024/1689.
3. Propose, in coordination with the German delegation and following standard NWIP procedure, one or more new work items addressing the standardization of cryptographic record-keeping protocols for AI systems, with target deliverable type of a European Standard (EN) or a Technical Specification (TS), as the committee determines.
4. Participate in mirror activities with ISO/IEC JTC 1/SC 42 and ETSI ISG-SAI on adjacent work, and serve as a coordinating presence for protocol-level interoperability across these venues.
5. Publish all Foundation contributions openly under permissive licenses, subject to CEN-CENELEC copyright and confidentiality rules governing in-progress working drafts.
6. Maintain a transparent register of all material commercial relationships, including the Foundation's structural relationship with LedgerProof Inc., available to the DIN secretariat on request.

### B.8 Commitment to the Article 40 standards process

The Foundation recognizes that the development of European harmonized standards under Regulation (EU) 2024/1689 is a multi-stakeholder process that operates over multi-year timelines, with deliberation, consensus-building, and revision as central features. The Foundation makes no claim that its protocol is, or will become, a harmonized standard cited in the *Official Journal of the European Union* under standardisation request M/593 or any successor mandate. Whether and how any work item the Foundation contributes to ultimately ripens into a harmonized standard, and whether such a harmonized standard is cited in the *OJEU* such that compliant systems benefit from the Article 40 presumption of conformity, is a matter exclusively for CEN, CENELEC, the European Commission, and the standardisation process — not for any individual contributor.

The Foundation commits to participating in that process in good faith, in compliance with CEN-CENELEC's internal regulations on intellectual property, competition, and conflict of interest, and with full transparency regarding its own commercial affiliations. The Foundation specifically acknowledges that it does not and will not represent to any third party — including AI system operators, regulators, or the public — that participation in the standards process confers any legal benefit prior to publication of a harmonized standard in the *OJEU*. The Foundation will conform its public communications and the public communications of its affiliated commercial entity to this principle.

### B.9 German-language equivalents for key paragraphs (Sprachdienst review required)

> **Translator note**: The following German-language drafts are provided for Sprachdienst review and revision. They are intended as appended summary materials accompanying the English-language application. They should be reviewed by a qualified legal translator (Lionbridge Legal or Acolad Legal, Frankfurt office, recommended) prior to filing. They are NOT to be filed without professional translation review.

**B.9.1 — German summary of B.1 (Anmeldende Organisation):**

Die LedgerProof Foundation (in Gründung) ist eine gemeinnützige Stiftung nach US-amerikanischem Recht (Delaware 501(c)(3)), die offene kryptographische Protokolle zur fälschungssicheren, lokal überprüfbaren Aufzeichnung von Ein- und Ausgaben künstlicher-Intelligenz-Systeme entwickelt und pflegt. Ziel ist die Unterstützung der Transparenzpflichten gemäß Verordnung (EU) 2024/1689 ("KI-Verordnung") sowie entsprechender Regelungen in den USA, dem Vereinigten Königreich und im asiatisch-pazifischen Raum. Die Stiftung wird treuhänderisch durch den New Venture Fund (US 501(c)(3)) verwaltet, bis die eigene Steuerbefreiung gemäß IRS Form 1023 anerkannt ist.

**B.9.2 — German summary of B.7 (Beitrittsabsicht):**

Die Stiftung beabsichtigt, über die deutsche Delegation bei CEN-CENELEC JTC 21 sowie über die Spiegelaktivitäten zu ISO/IEC JTC 1/SC 42 und ETSI ISG-SAI an der Entwicklung europäischer und internationaler Normen zu KI-Transparenz, Nachvollziehbarkeit und Marktüberwachung mitzuwirken. Der Beitrag der Stiftung konzentriert sich auf das fachlich nachweisbare Spezialgebiet kryptographischer Aufzeichnungsverfahren für KI-Systeme mit lokal überprüfbarer Manipulationsfestigkeit und dezentraler Zeitstempelung. Nach Aufnahme beabsichtigt die Stiftung, regelmäßig an Sitzungen des Spiegelausschusses NA 043-01-42 AA teilzunehmen, technische Beiträge zu JTC-21-Arbeitsentwürfen einzureichen sowie — in Abstimmung mit der deutschen Delegation und nach den üblichen Verfahren — einen oder mehrere Neue Arbeitspunkte (NWIP) zur Standardisierung kryptographischer Aufzeichnungsprotokolle für KI-Systeme vorzuschlagen.

**B.9.3 — German summary of B.8 (Verhältnis zum Verfahren harmonisierter Normen):**

Die Stiftung erkennt an, dass die Entwicklung harmonisierter europäischer Normen gemäß Verordnung (EU) 2024/1689 ein mehrjähriger, konsensbasierter Mehrparteien-Prozess ist. Die Stiftung erhebt keinerlei Anspruch darauf, dass ihr Protokoll eine harmonisierte Norm im Sinne von Artikel 40 der KI-Verordnung ist oder werden wird oder dass die Beteiligung am Normungsprozess vor Veröffentlichung einer entsprechenden harmonisierten Norm im Amtsblatt der Europäischen Union irgendeinen rechtlichen Vermutungsvorteil verleiht. Die Stiftung verpflichtet sich, sich im Verfahren in gutem Glauben, gemäß den internen Regelungen von CEN-CENELEC zu geistigem Eigentum, Wettbewerb und Interessenkonflikten sowie unter vollständiger Offenlegung ihrer kommerziellen Verbindungen zu beteiligen. Die Stiftung verpflichtet sich ferner, dass weder sie selbst noch das verbundene Unternehmen LedgerProof Inc. öffentlich anders kommunizieren werden.

### B.10 Signature block and supporting documents

**Signed for the applicant:**

Veronica S. Dawkins
Director, LedgerProof Foundation (in formation)
Date: [insertion at filing — target June 15, 2026]

**Supporting documents accompanying the application (list):**

1. Foundation Articles of Incorporation (Delaware) — to be filed; supplemental if not yet filed at application date.
2. New Venture Fund fiscal-sponsorship agreement.
3. New Venture Fund most recent audited financial statements (Form 990 and audit).
4. Foundation governance memorandum (board composition, committee structure, conflict-of-interest policy).
5. LedgerProof Inc. ↔ Foundation IP license agreement.
6. Standards Engagement Committee charter.
7. LedgerProof Protocol specification (current draft, hosted at `04-lpr-spec/`).
8. Cross-language SDK conformance suite documentation.
9. IETF SCITT WG draft contribution (in progress).
10. Sponsor endorsement letters (Hallensleben, Hauser, Toffaletti — to extent received by filing date; supplemental within 30 days otherwise).
11. SME qualification declaration (EU SME Recommendation 2003/361/EC criteria).
12. Conflict-of-interest disclosure (Dawkins dual-role declaration).

---

**End of application content. Filing target: Monday, June 15, 2026.**

**Owner**: Veronica
**Next document in sequence**: `14-seed-close-pack/07-jtc21-nwip-outline.md` (draft start: Wed Jun 24, 2026 per master-plan T+24)
