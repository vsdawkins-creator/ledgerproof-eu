# Forwardable Diligence Pack — DocSend Contents

**Hosted at:** DocSend ($99/mo). One DocSend "data room" per recipient class (co-leads / banker / counsel / Big-4 / Series A leads). View-tracking on for all.
**Access policy:** email-gated, NDA on cover page, screenshot prevention enabled, watermarked per viewer.
**Recipients (initial five):** TVP partner · Stillmark partner · Fulgur partner · Mark Beeston (Illuminate) · Cooley (Adam Ross + Jodie Bourdet, for the seed restructure work).

## The 15 artifacts

| # | Artifact | Source path | Status |
|---|---|---|---|
| 1 | **LedgerProof Master Plan** (integrator) | [`PLAN.md`](../PLAN.md) | ✅ shipped |
| 2 | **LedgerProof Code Plan V2** (engineering plan, converged with playbook) | [`09-code-plan/00-MASTER-CODE-PLAN-V2.md`](../09-code-plan/00-MASTER-CODE-PLAN-V2.md) | ✅ shipped |
| 3 | **GTM Master Plan + 19 artifacts** | [`08-gtm/00-MASTER-PLAN.md`](../08-gtm/00-MASTER-PLAN.md) + `08-gtm/day-*/` | ✅ shipped |
| 4 | **LPR Specification v1.1 + IETF Internet-Draft** | [`04-lpr-spec/`](../04-lpr-spec/) + Datatracker | ✅ shipped |
| 5 | **LPR-ERRATA-001** (first public errata — Entry #0 stored content_hash mismatch) | [`04-lpr-spec/LPR-ERRATA-001.md`](../04-lpr-spec/LPR-ERRATA-001.md) | ✅ shipped today |
| 6 | **Canonicalization Investigation Memo** (Monday root-cause; saves ToB $30–40K) | [`13-monday-sprint/01-canonicalization-investigation.md`](01-canonicalization-investigation.md) | ✅ shipped today |
| 7 | **Founding-declaration Receipt Content** (v1.1 issuance, supersedes Entry #0 for slug routing) | [`13-monday-sprint/06-founding-declaration-entry.md`](06-founding-declaration-entry.md) | ✅ drafted; **issuance pending verifier PR merge** |
| 8 | **Trail of Bits Engagement Letter** (3-day scoped canonicalization audit, $15–25K) | [`13-monday-sprint/03-trail-of-bits-email.md`](03-trail-of-bits-email.md) → ToB SOW response | drafted; **send today** |
| 9 | **Adler & Colvin Engagement Letter** (501(c)(3) formation + Day-1 IP license + multi-signer quorum) | [`13-monday-sprint/04-adler-colvin-email.md`](04-adler-colvin-email.md) → A&C engagement letter | drafted; **send today** |
| 10 | **Hercules Capital $8M Undrawn Term Sheet** | [`13-monday-sprint/05-hercules-capital-email.md`](05-hercules-capital-email.md) → term sheet response | drafted; **send today** |
| 11 | **Premortem Report** (11-lens, 75 surviving failure modes, adversarially verified) | [`12-premortem/01-PREMORTEM-MAY31.md`](../12-premortem/01-PREMORTEM-MAY31.md) | ✅ shipped Sat |
| 12 | **10X Playbook** (the Monday-morning operations document for 180 days) | [`12-premortem/04-10X-PLAYBOOK-MAY31.md`](../12-premortem/04-10X-PLAYBOOK-MAY31.md) | ✅ shipped Sat |
| 13 | **Production Operator Metrics** (live from `api.ledgerproofhq.io` + `status.ledgerproofhq.io`) | `status.ledgerproofhq.io` | live by Jun 7 (P3.4 from V2) |
| 14 | **24-Month Financial Model** (Pilot.com fractional CFO build) | TBD | engagement Jun 2; deliverable Jun 22 |
| 15 | **Foundation Independent Board Slate** (Choudhary chair, Randal audit, Moerel compliance — written outreach letters + initial responses) | TBD | A&C engagement letter triggers outreach Jun 5 |

## What's deliberately NOT in the diligence pack

- **Customer pipeline by name.** Big-4 working group + design-partner outreach is in flight; specific named accounts are surfaced under separate cover via NDA-gated 1:1 conversations, not in a viewer-tracked vault.
- **Cap table.** Sent separately by Cooley with the SAFE documents. Vault is for narrative + architecture; cap table is for execution.
- **Pricing decision rationale.** Membership pricing (Founding Member capped at 25 seats) ships Jun 14 — too late for this week's diligence pack window. Sent as a supplement after launch.
- **PAT incident write-up.** Mentioned in cover note (artifact 16 below); not a standalone artifact. The remediation is fully complete; the incident is non-load-bearing for the seed thesis.

## Cover note (one paragraph, top of the DocSend)

> This is the LedgerProof seed-close diligence pack as of Monday June 1, 2026. The artifacts are arranged to be read in order: PLAN.md (1) → Code Plan V2 (2) → GTM Plan (3) → Spec + IETF (4). The first errata (5) and its investigation memo (6) are the most important governance artifacts in the pack — they demonstrate how the Foundation handles bugs in public. The four engagement letters (7–10) are this week's execution. The premortem (11) and 10X playbook (12) are the strategic substrate. The status page (13), financial model (14), and board slate (15) are in flight and will populate before close. The 8-item 7-day hot path lives at the top of artifact 12; the proposed two-stage seed restructure note is in your individual inbox. Questions to veronica@ledgerproofhq.io; response SLA 4 business hours during the close window.

## DocSend operational settings

- **Watermark every page** with viewer email + IP + viewing-time.
- **Disable downloading** initially. Re-enable per-viewer after first call.
- **Track per-page time-on-page.** A viewer who skips the errata is a viewer who hasn't done the diligence; flag for a phone call.
- **Per-recipient links.** Never share the same link across viewers. Easier to revoke; better signal.
- **Email reply alert** when a viewer opens within 30 minutes of receiving the link. Use the open as the trigger to schedule the 20-minute call same-day.

## Send sequence

| When | Action |
|---|---|
| **Tue Jun 2, 09:00 PT** | Send DocSend links + seed-restructure note to TVP, Stillmark |
| **Wed Jun 3, 08:00 ET** | Send DocSend links + seed-restructure note to Fulgur, Mark Beeston |
| **Wed Jun 3, EOD** | If any have not opened, follow up via the prior thread |
| **Fri Jun 5, EOD** | Status check: who has booked the 20-minute call? |
| **Wed Jun 10** | Hard deadline for verbal confirmation on the two-stage restructure |
| **Wed Jun 18** | Hard deadline for signed subscription agreements |
| **Thu Jun 25** | Wire date |

## What the diligence pack is NOT a substitute for

- 1:1 calls with each partner. Pack opens the conversation; the conversation closes the wire.
- The verifier URL `verify.ledgerproofhq.io/r/founding-declaration` — every partner clicks it within 10 seconds of receiving the pack. By Wednesday this MUST resolve to green-on-all-checks. The verifier PR must merge by EOD Tuesday for that to be true.
