---
title: LedgerProof Foundation — status, governance, transparency
description: The LedgerProof Foundation stewards the open Bitcoin-anchored Article 50 transparency protocol. This page documents Foundation formation status, governance structure, key personnel, financial disclosures, and Bitcoin-anchored governance events. Updated in real time as formation milestones land.
---

> **Status as of 3 June 2026:** Foundation is in formation. United States 501(c)(3) public charity under Delaware law (Adler & Colvin counsel) with Dutch Stichting EU subsidiary in formation (Amsterdam, NautaDutilh counsel). Interim signing key in use; multisig root-key ceremony scheduled for 15 August 2026. Founding Executive Director: Veronica S. Dawkins. Board ratification target: 31 August 2026.
>
> This page is the canonical public record of Foundation status. Every claim below is either independently verifiable (court filings, IETF Datatracker, Bitcoin chain) or is flagged with the date and method by which it will become verifiable.

## What the Foundation does

The LedgerProof Foundation stewards three things:

1. **The LedgerProof Protocol** (`LPR v1.1` and successors) — the open specification for Bitcoin-anchored Article 50 transparency receipts, published as IETF Internet-Draft `draft-dawkins-scitt-ai-article50-00` (SCITT working group track).
2. **The reference implementations** — Python, TypeScript, and Rust libraries plus 29 framework adapters, all under Apache License 2.0, source at `github.com/vsdawkins-creator/ledgerproof-eu` (migrating to `github.com/vsdawkins-creator/ledgerproof-eu` post-launch).
3. **Foundation governance evidence** — every ratified Foundation decision (board minutes, key rotations, charter ratifications, security policy revisions) is Bitcoin-anchored as a `foundation_governance_event/v1` record, so that the Foundation's governance is itself verifiable using the same protocol the Foundation stewards.

The Foundation does NOT:
- Sell software or services (the reference implementations are free; commercial offerings come from LedgerProof Inc., a separate Delaware C-corp)
- Endorse particular deployers or vendors
- Collect personal data from receipt issuers, verifiers, or natural persons referenced in receipts
- Operate as a certification body (deployers self-certify against the protocol; the Foundation publishes test vectors and verifier tooling)

## Legal structure

| Entity | Form | Jurisdiction | Status | Counsel |
|--------|------|--------------|--------|---------|
| LedgerProof Foundation | 501(c)(3) public charity | Delaware, USA | **In formation** — Articles of Incorporation drafting, target filing on or before 15 June 2026 | [Adler & Colvin](https://adlercolvin.com/) |
| LedgerProof Stichting | Stichting (Dutch foundation) | Amsterdam, Netherlands | **In formation** — KvK registration drafting | [NautaDutilh](https://www.nautadutilh.com/) |
| LedgerProof Inc. | Delaware C-corporation | Delaware, USA | Active | [Cooley](https://www.cooley.com/) |

The Foundation (US) and Stichting (EU) are governance siblings. The Stichting handles EU regulatory engagement, EU enforcement-authority correspondence, and EU-resident receipt-anchoring contracts. The Foundation handles IETF specification stewardship, US regulatory engagement, and the global open-source release.

LedgerProof Inc. is a separate Delaware C-corporation that builds and sells managed services (cloud-hosted receipt anchoring, enterprise support contracts, premium SLAs). The Inc. funds the Foundation via a published grant agreement ($50K/mo starting August 2026, structured to avoid private inurement per IRS guidance). The Inc. and Foundation share no overlapping board members other than the founding Executive Director through 31 August 2026; thereafter they diverge fully per the charter.

**Why this structure**: The protocol must outlive the company. A US 501(c)(3) with a Dutch Stichting subsidiary is the cleanest legal structure we identified for an open protocol with global regulatory salience and EU institutional engagement requirements. The structure traces to a 2024 conversation with Lokke Moerel on Dutch foundation law combined with Adler & Colvin's read on US public-charity governance.

## People

### Founding Executive Director (interim, through Board ratification)

**Veronica S. Dawkins** — Founder, LedgerProof Foundation (in formation). Author of the LedgerProof Protocol specification and the IETF Internet-Draft. Prior background published in the [Author identity disclosure](/foundation/identity-disclosure/) (forthcoming — filing on or before 15 June 2026).

### Counsel of record

- **501(c)(3) formation & governance**: Adler & Colvin (San Francisco) — engagement letter signed Jun 2026
- **Dutch Stichting formation**: NautaDutilh (Amsterdam) — engagement letter in negotiation
- **Inc. corporate & seed financing**: Cooley (San Francisco)
- **EU regulatory & supervisory authority engagement**: Stibbe (Brussels) — scoping memo in progress

### Board (target composition, ratification 31 August 2026)

Per the draft charter, the Foundation Board will comprise:

- 1 seat: Founding Executive Director (Veronica S. Dawkins) — non-voting on matters of executive compensation per IRS conflict-of-interest policy
- 2 seats: Independent technical (cryptography, distributed systems, or applied formal methods background)
- 2 seats: Independent legal/regulatory (EU AI Act, GDPR, or US administrative law background)
- 1 seat: Independent civil society / public interest (data subject rights or AI accountability advocacy background)
- 1 seat: Rotating, 24-month term, public application process — first holder selected by initial 6 members from open application pool

**Currently confirmed**: 0 seats. Board composition is being assembled through a documented outreach process; candidate names will be disclosed at the point of acceptance, not at the point of approach.

### Advisors

The Foundation engages technical and policy advisors on a project basis. Current named advisors will be disclosed on this page on the date their first advisory output (memo, public comment, code review) lands. We do not name advisors who have only had introductory conversations.

## Foundation governance events (Bitcoin-anchored)

Every ratified Foundation governance decision is recorded as a `foundation_governance_event/v1` record, signed by the current Foundation signing key, Merkle-batched with other Foundation events, and anchored to Bitcoin mainnet via OP_RETURN. The format is `LPR1 || merkle_root_32` (36 bytes total).

| Event ID | Date | Event type | Anchor txid | Status |
|----------|------|------------|-------------|--------|
| `gov-2026-06-02-eu-ai-office-consultation` | 2 June 2026 | EU AI Office Article 50 Guidelines consultation submission | (pending Bitcoin confirmation; OpenTimestamps receipt at `17-futurium/anchored-receipts/2026-06-02-article-50-consultation/`) | Submitted; anchor confirming |

Future scheduled events (will populate this table as they land):

- **15 August 2026**: Multisig root-key ceremony (signing key rotation from interim Ed25519 single-key to 3-of-5 multisig)
- **31 August 2026**: Initial Board ratification + charter adoption
- **15 September 2026**: Annual Foundation transparency report (first issuance)

## Cryptographic posture

### Signing keys

- **Interim Foundation signing key (Ed25519)**: public key `qtG5TDcBlGR/25zsC/Cik3+rnUupR5XB2dSB+/IKUzA=` (Base64 encoding of 32-byte Ed25519 public key per RFC 8032)
- **Storage**: private key stored offline; signing operations performed on an air-gapped machine for governance events; receipt-signing key is a separate per-Foundation-deployment subordinate
- **Rotation**: scheduled 15 August 2026 to a 3-of-5 multisig held by Foundation officers + independent custody partner
- **Compromise response**: documented in the [Security disclosure policy](/security/disclosure/), § Bitcoin anchoring failure modes

### Receipt anchoring

- **Anchor cadence**: ~144 Merkle batches per day at scale (every ~10 minutes, aligned with Bitcoin block cadence)
- **Anchor cost**: approximately USD $17K/month at current Bitcoin fee levels; modeled flat in the [operating model](https://github.com/vsdawkins-creator/ledgerproof-eu) per assumption A10
- **OpenTimestamps integration**: receipts use OpenTimestamps for asynchronous proof construction; the Foundation operates its own calendar mirror for resilience against single-calendar-server compromise

## Financial transparency

Per US 501(c)(3) governance norms, the Foundation will publish annually:

- Form 990 (US IRS public charity return)
- Audited financial statements
- Board-approved budget and variance against prior year
- Grant agreements with related parties (specifically the Inc.→Foundation grant agreement and any Stichting↔Foundation transfers)

**First scheduled disclosure**: April 2027 (covering partial fiscal year August 2026 – July 2027 — the Foundation operates on an August-to-July fiscal year aligned with the Inc.)

**Current financial position (June 2026)**: The Foundation has not yet received its first grant disbursement (scheduled August 2026). Pre-formation expenses (legal counsel for formation, IETF Datatracker fees, OpenTimestamps calendar mirror infrastructure) are bridged by the Founding Executive Director personally and will be reimbursed by the Inc. via documented receipts post-formation per IRS guidance on founder reimbursement.

## What the Foundation will never do

These commitments are governance commitments, not marketing — they will be encoded in the charter and any modification requires Bitcoin-anchored governance event with supermajority Board approval:

1. **Endorse a specific deployer, vendor, or commercial product.** The Foundation publishes specifications, reference implementations, and verifier tooling. It does not publish "approved vendor" lists.
2. **Claim that a deployer using the protocol is "Article 40 conformant."** Article 40 presumption of conformity is a regulator function, not a Foundation function. We are explicit about this in every public communication.
3. **Allow the protocol to require a Foundation-operated SaaS endpoint to verify.** Verifier independence is a non-negotiable architectural commitment. Any protocol change that would weaken this is rejected on charter grounds, not on technical grounds.
4. **Collect personal data from receipt issuers or verifiers as a condition of using the protocol.** The protocol is GDPR-friendly by structure; the Foundation's own operations are GDPR-compliant by policy.
5. **Accept funding from sources that would compromise the Foundation's regulatory independence.** No funding from EU member-state governments other than research grants under arm's-length competitive processes; no funding from companies under active EU AI Act enforcement action; no funding conditional on protocol changes.
6. **Operate the Foundation in a jurisdiction that does not provide independent judicial review of charitable governance.** US and Netherlands chosen specifically for this reason; expansion to additional jurisdictions requires Board supermajority and independent legal review.

## Conflict-of-interest disclosures

- **Founding Executive Director**: Holds equity in LedgerProof Inc. (founder common stock). Recuses from any Foundation decision involving Inc. grant terms, Inc. partnership terms, or any other matter where Foundation interest and Inc. interest could diverge. Through 31 August 2026 (pre-Board), conflicted matters are referred to outside counsel (Adler & Colvin) for independent review.
- **Counsel of record**: Adler & Colvin, NautaDutilh, Cooley, and Stibbe have no equity or compensation arrangements with the Foundation other than standard hourly billing for legal services. Engagement letters available on request.

## How to contact the Foundation

- **General**: `info@ledgerproofhq.io`
- **Security disclosure**: `security@ledgerproofhq.io` (see [Security disclosure policy](/security/disclosure/))
- **Regulatory authorities (EU)**: `regulatory-eu@ledgerproofhq.io` (forwarded to Stibbe Brussels for triage)
- **Regulatory authorities (US)**: `regulatory-us@ledgerproofhq.io`
- **Press**: `press@ledgerproofhq.io`
- **Funding inquiries (grants, donations)**: `grants@ledgerproofhq.io` (note: the Foundation has not yet established its grant acceptance pipeline; inquiries received before August 2026 will be acknowledged and answered post-formation)

Postal addresses for both the US Foundation and EU Stichting will be published on this page on the date of formal incorporation in each jurisdiction.

## Changes to this page

Material changes to this page (changes to governance structure, board composition, financial commitments, "never do" list) are themselves Bitcoin-anchored as `foundation_governance_event/v1` records of type `foundation_status_page_revision`. Minor edits (typo corrections, link updates, formatting) are made without anchoring and noted in the page revision history.

**Revision history:**
- 3 June 2026: Initial publication (anchored as governance event; txid pending)

---

*This page is the public-facing status disclosure of LedgerProof Foundation (in formation). It is maintained by the Founding Executive Director under personal accountability through 31 August 2026, and by the Foundation Board thereafter. Inaccuracies are bugs and should be reported via `info@ledgerproofhq.io` or as a vulnerability under the [Security disclosure policy](/security/disclosure/) if they involve cryptographic or governance integrity claims.*
