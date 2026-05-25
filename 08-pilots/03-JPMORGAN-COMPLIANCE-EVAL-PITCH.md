# Compliance Evaluation Pitch — JPMorgan Chase

**Delivered by:** Chris Morton (internal, JPMorgan)
**Targets:** JPMorgan internal compliance leadership; JPMorgan Risk; JPMorgan CIO of the relevant business unit
**Length:** One page

---

## The evaluation in one sentence

JPMorgan conducts a 90-day internal evaluation of LedgerProof Receipts (LPR) against a defined audit-evidence workflow (proposed: wire-transfer authorization receipts in a single mid-market business line), producing a written assessment for circulation to JPMorgan Compliance leadership and, with JPMorgan's approval, a published joint case study for the broader BFSI sector.

## Why JPMorgan, why now

JPMorgan is the world's largest bank by assets. Its compliance posture sets the de facto standard for the BFSI sector. The compliance pressures now converging on documentary integrity — wire-transfer fraud measured in billions per year, regulator demands for auditable AI-driven decisions, PCAOB consultation on blockchain-anchored audit evidence, the August 2026 EU AI Act enforcement, and the steady drumbeat of FFIEC and OCC commentary on documented control evidence — bear directly on the institutional risk JPMorgan carries.

LedgerProof Receipts provide a cryptographic audit-evidence layer that is:

- **Auditor-grade.** Receipts are independently verifiable by any external auditor (PwC, Deloitte, EY, KPMG) against the Bitcoin chain, without dependence on JPMorgan's infrastructure or LedgerProof's continued operation.
- **PCAOB-aligned.** The PCAOB's 2025 consultation on the sufficiency of blockchain-anchored records as audit evidence specifically contemplates the construction LPR uses.
- **GDPR-compliant by design.** The protocol anchors hashes, not document content. The European Data Protection Board's April 2025 draft guidance on personal data and the blockchain is satisfied by the LPR architectural pattern.
- **Vendor-neutral.** The specification is open. The reference implementations are MIT-licensed. The verifier is free. JPMorgan's evaluation creates no vendor lock-in.

## What the evaluation would entail

- **Scope:** A bounded workflow with high control significance and low integration risk. Proposed: wire-transfer authorization receipts in one mid-market business line where the audit-evidence value is acute. Chris to identify the right business unit.
- **Integration:** LedgerProof, Inc. provides the SDK and direct integration support. Anchoring proceeds against the Foundation-operated Bitcoin calendar at no charge to JPMorgan during the evaluation.
- **Cost during evaluation:** Zero, on both sides. LedgerProof waives all fees. JPMorgan's engineering investment is bounded to integration time only.
- **Duration:** 90 days from kickoff.
- **Outputs:**
  - Written internal assessment to JPMorgan Compliance leadership (assessment authors are JPMorgan; LedgerProof provides supporting technical documentation only)
  - A bilateral decision at Day 90: (a) extend to a paid production engagement, (b) extend the evaluation by another 90 days, (c) document findings and close

## What JPMorgan would receive

- A working, regulator-defensible, externally verifiable cryptographic audit trail for the in-scope workflow.
- First evaluator standing on a category that will become a procurement requirement at the Big 4 audit-firm level within 18-24 months.
- A direct seat in the open-standards conversation through invitations to participate in IETF and ISO TC 307 work where the LedgerProof Foundation engages.
- The internal evidence base to make a Bank-wide adoption decision in 2027 on a basis other than a vendor sales pitch.

## What LedgerProof would receive

- A named institutional evaluator. The launch press cycle includes the *evaluation* (not adoption — language must be precise) by a globally significant financial institution. JPMorgan reviews and approves any public language.
- Real institutional-grade load testing on the production protocol.
- The audit-firm and regulator conversations that flow naturally from JPMorgan's evaluation footprint.

## Decision being asked

A 30-minute conversation between Veronica and the JPMorgan internal compliance contact Chris identifies. If the contact finds the evaluation feasible and the scope appropriate, a one-page evaluation agreement (drafted by both legal teams) follows.

— end —

> **FOUNDER ACTION REQUIRED:**
> 1. Chris reviews and adjusts framing to match the specific JPMorgan-internal idiom he will be using.
> 2. Chris identifies the right internal contact. A VP-or-above in either Compliance or the relevant business unit's risk function is the appropriate level.
> 3. The "named evaluator" language is contingent on JPMorgan's written approval. If JPMorgan is not yet ready to be named in the launch press, the language degrades to "the Foundation is in evaluation conversations with a leading global financial institution."
> 4. Any evaluation agreement is a contract; the licensed attorney reviews before either side signs.
> 5. Honest-status: the launch press cycle must distinguish *evaluation* (a real status JPMorgan can comfortably grant) from *adoption* or *customer* (statuses requiring contracted production deployment). Do not blur these in any public language.
