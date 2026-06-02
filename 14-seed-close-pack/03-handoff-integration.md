# LedgerProof Seed-Close → Series-A Integration Layer
**Owner:** Veronica S. Dawkins | **Date:** 2026-06-01 (Monday) | **Seed close target:** 2026-06-25 (T-24 days) | **Audit kickoff target:** 2026-06-08 (T-7 days) | **Article 50 enforcement:** 2026-08-02 (T-62 days)

---

## 1. THE DOCUMENT MAP

| Artifact | Recipient | Send window | Delivery format | Gating condition |
|---|---|---|---|---|
| **Operating Model — full (Artifacts 1-4)** | TVP (lead), Stillmark (Bitcoin-anchor lead) | Jun 3 (Wed) | DocSend, watermarked, 14-day expiry, no download | NDA already in place from term-sheet round |
| **Operating Model — Base + Stretch only, no Downside** | Fulgur Ventures | Jun 4 (Thu) | DocSend, watermarked | Fulgur is following, not leading; Downside introduces optionality they'd negotiate against |
| **Operating Model — 4-page summary memo only** | Illuminate / Mark Beeston | Jun 4 (Thu) | Signed PDF over Proton | Mark is a strategic angel, not institutional; full model is overkill and creates leak risk |
| **Operating Model — Y1 P&L + cohort waterfall + cash trajectory** | Hercules Capital (Bryan Jadot) | Jun 8 (Mon) | DocSend + 30-min Zoom walkthrough | Hercules needs cash floor + ARR ramp for covenant package; Foundation expense detail is private |
| **Operating Model — G&A expense allocation tab only (A17 detail)** | Adler & Colvin (Eve Borenstein) | Jun 10 (Wed) | Signed PDF + 1023 supplement | Needed for §509(a)(2) public-support fraction projection |
| **Operating Model — cap table + warrant schedule excerpt** | Cooley (Adam Ross) | Jun 9 (Tue) | Carta export + redlined SAFE | Drives the seed-restructure SAFE drafting |
| **Threat-Model Briefing — full** | NCC Group (primary) + Trail of Bits (alternate) | Jun 2 (Tue) | Mutual NDA + signed PDF + repo read access on SoW execution | Already drafted; ship tomorrow |
| **Threat-Model Briefing — full + LPR-ERRATA-001 RCA** | Cure53 (verifier-scope alternate) | Jun 3 (Wed) | Same as above | Verifier scope is their specialty |
| **Threat-Model Briefing — exec summary (§1, §5, §7)** | Four seed co-leads | Jun 11 (Thu) | DocSend addendum to operating model | Buyer-facing proof that security audit is locked, not aspirational |
| **Foundation Quarterly Governance Pack** (model G&A + audit memo + Foundation board minutes) | Foundation board (when seated, target Q4 2026) | Quarterly, first pack Oct 15 2026 | Board portal (Diligent / Boardable) + signed PDF | Cannot ship until 3 independent directors seated |
| **Series A Diligence Pack (Artifact 4 + completed audit memo + 6-mo cohort dashboard)** | Qatalyst → Series A leads | Sep 15 → Nov 15, 2026 | Full virtual data room (Datasite or Intralinks) + Loom walkthrough of the cohort dashboard | Audit memo (Aug 31) + Q3 cohort actuals (Oct 5) must be in hand |

---

## 2. THE CROSS-REFERENCE INDEX

| Connection point | Operating Model location | Threat-Model Briefing location | Resolution |
|---|---|---|---|
| **Audit engagement fee** | R&D (audits) line: $125K Jul-26 + $50K Sep-26 + $80K Nov-26 = $255K (A14) | §8 budget ceiling $200K (combined v1.1 + verifier) | Reconcile: model's $125K Jul is NCC/ToB primary; $80K Nov is Cure53 verifier-scope; $50K Sep is Latacora pen-test (separate scope, not in briefing). **Action:** update A14 footnote to reference LPR-AUDIT-SOW-REQ-2026-06 line-item. |
| **Audit completion date** | Diligence Pack item #5 due Sep 1, 2026 | §9 final memo published Aug 31, 2026 | Tight but aligned. 24-hour buffer between memo signing and Qatalyst-readable diligence room. **Single point of failure — see Risk #1.** |
| **LPR-ERRATA-001** | Diligence-killer call-out (Artifact 4 footer) | §5 full RCA + §4.5 insider-risk threat | Both reference the same `pre-v1-entries.json` allowlist mechanism. **Action:** ensure the GitHub commit hash for the publisher-side fix is identical in both documents and in the data room. |
| **Big-4 partnership timing** | Implied in S&M ramp Q4 2026 (A19, 30% → 65% of new ARR) | Not directly addressed | Big-4 working group convening Q4 2026 depends on a signed audit memo as the "is this a real protocol" gate. **Add to PLAN.md.** |
| **Article 50 enforcement (Aug 2, 2026)** | A7 enterprise ramp assumption; Artifact 2 footnote ("78% of May-28 rev from cohorts signed post-enforcement") | §9 timeline rationale ("regulator hands before then") | Both documents pivot on the same calendar date. If enforcement slips, both ramps slip. |
| **Foundation root key ceremony (Day 90, ~Aug 15, 2026)** | Not in model | §2.1 Foundation root key + §4.5 m-of-n threshold | **Gap.** Add ceremony as a milestone to CRIT_PATH.md; allocate $15K to G&A Aug-26 for ceremony logistics + travel. |
| **Headcount: Standards & Reg head (Sep 2026, Brussels)** | A12 + A13 ($280K fully loaded) | §7 deliverable handoff to regulators (BaFin, AFM, EU AI Office) | The Std&Reg hire is the human channel for the audit memo. Without that hire, the memo sits on a shelf. |
| **VP Eng start date (Jul 15, 2026)** | A12 headcount; Diligence-killer call-out | §1.4 audit deliverable accountability | VPE owns audit remediation SLA (§10). Slip in VPE start = slip in remediation = slip in Sep 1 diligence readiness. |

---

## 3. THE 14-DAY HANDOFF SEQUENCE

| Day | Date | Action | Recipient | Format |
|---|---|---|---|---|
| 1 | Mon Jun 1 | Lock the integration layer; finalize this document; brief CoS-elect | Internal | Repo commit |
| 2 | Tue Jun 2 | Send threat-model briefing + NDA to NCC Group (Jen Fernick) and Trail of Bits (Dan Guido) | NCC, ToB | PDF + mutual NDA |
| 3 | Wed Jun 3 | Send full operating model to TVP + Stillmark; send threat-model briefing to Cure53 (Mario Heiderich) | TVP, Stillmark, Cure53 | DocSend + PDF |
| 4 | Thu Jun 4 | Send tailored model to Fulgur; send 4-page memo to Mark Beeston | Fulgur, Beeston | DocSend, signed PDF |
| 5 | Fri Jun 5 | Diligence Q&A calls: TVP (10am), Stillmark (2pm) | TVP, Stillmark | Zoom |
| 6 | Sat Jun 6 | Audit firm responses begin to arrive; founder reviews bids over weekend | NCC/ToB/Cure53 | Async |
| 8 | Mon Jun 8 | **Audit kickoff target** with selected firm (decision tree §4); send Hercules the model + walkthrough | Audit firm, Hercules | Kickoff call + Zoom |
| 9 | Tue Jun 9 | Send Cooley the cap table + warrant excerpt; review SAFE redlines | Cooley | Carta export + redlines |
| 10 | Wed Jun 10 | Send Adler & Colvin the G&A allocation tab; 1023 follow-through call | A&C | Signed PDF |
| 11 | Thu Jun 11 | Send threat-model exec summary to the four seed co-leads as addendum | All four co-leads | DocSend addendum |
| 12 | Fri Jun 12 | Diligence Q&A calls: Fulgur (11am), Beeston (3pm) | Fulgur, Beeston | Zoom |
| 15 | Mon Jun 15 | Architecture walkthrough with audit firm (per §9 of briefing) | Audit firm | In-person if NCC-NYC, else Zoom |
| 17 | Wed Jun 17 | Co-lead syndicate alignment call: TVP + Stillmark + Fulgur + Beeston + Cooley | All | Zoom |
| 19 | Fri Jun 19 | SAFE documents distributed for signature | All four co-leads | DocuSign |
| 22 | Mon Jun 22 | Hercules debt facility signature | Hercules | DocuSign |
| 24 | Wed Jun 24 | Signature window closes; final compliance check | All | Cooley confirms |
| **25** | **Thu Jun 25** | **Seed wire ($12M) + Hercules facility signed; press embargo lifts 8am ET Jun 26** | All | Wire + press release |

**Calendar discipline:** Veronica blocks 9-11am ET every weekday for diligence Q&A; CoS-elect (starting Jun 8) protects that block. No founder meetings before 9am or after 6pm Jun 1-25 except the four co-lead Q&A windows above.

---

## 4. THE MONDAY-MORNING DECISION TREE

| Decision | Options | Default recommendation | Decision deadline | Cost of waiting |
|---|---|---|---|---|
| **Which audit firm?** | (a) NCC Group full v1.1 + verifier ($150-200K) (b) ToB full + verifier ($150-200K) (c) NCC for core + Cure53 for verifier (split, ~$180K) | **(c) Split scope** — Cure53's verifier expertise is differentiated; NCC's Rust/canonicalization depth is unmatched. Combined memo carries more weight than single-firm. | Fri Jun 5 EOD | Each day past Jun 5 compresses the 12-week timeline; Aug 31 publication slips 1:1 |
| **Audit scope tier** | $80K canonicalization-only / $150K full / $200K full + PoC + re-test | **$200K ceiling** — model already absorbs $255K across three Q3-Q4 audit lines; re-test budget non-negotiable for Series A credibility | Fri Jun 5 EOD | Lower tier = weaker memo = lower Series A multiple |
| **Which model scenario goes to co-leads?** | Base only / Base + Stretch / Base + Stretch + Downside | **Base + Stretch to TVP and Stillmark; Base + Stretch to Fulgur (no Downside); 4-page memo to Beeston** | Already locked above | Showing Downside to a follower invites re-pricing |
| **Which model goes to Hercules?** | Full or Y1-only | **Y1 P&L + cohort waterfall + cash trajectory** | Mon Jun 8 | Hercules only underwrites against 12-mo visibility; Y2 detail invites covenants we don't want |
| **Foundation root-key ceremony date** | Jul 15 / Aug 15 / Sep 1 | **Aug 15** — needs VPE on board (Jul 15 start) + Brussels counsel review (Jul retainer active) + 30-day key-share courier window | Thu Jun 11 (book ceremony logistics) | Slip past Aug 15 = `aliases.json` insider-risk threat (§4.5) unmitigated at enforcement date |
| **Standards & Reg head: Brussels or remote?** | Brussels resident ($280K loaded, A13) / Remote EU ($230K loaded) | **Brussels** — per Artifact 4 #6, AISBL vs Stichting question requires in-person counsel coordination; remote candidate cannot drive JTC 21 liaison status | Open req by Jun 15; offer by Aug 1 | Slip to Q4 hire = miss JTC 21 Sep meeting → 25× → 20× multiple |
| **Pilot.com vs Burkland** for FY26 reviewed financials | Pilot ($24K/yr) / Burkland ($36K/yr but stronger venture-stage reps) | **Pilot.com** — adequate for seed, swap to Burkland at Series A close | Jun 30 | Either works; default to lower cost now |

---

## 5. RISK CALL-OUTS

**Risk 1 — Audit Memo Slip (single-point-of-failure compound risk).**
If the Aug 31 memo publication slips by even two weeks:
- Diligence Pack item #5 (operating model Artifact 4) misses Sep 1 deadline → Qatalyst Q3 launch delays → Series A close slips from Feb-27 to Apr-27
- Big-4 partnership convening Q4 2026 loses its "real protocol" gate → cascades to ~600K EU compliance officer reach assumption
- Article 50 enforcement Aug 2 starts without our memo in regulator hands → competitors (Vanta native crypto path, Downside scenario A6) get the first-mover regulator slot
- The 14-day handoff sequence above absorbs zero slack. Mitigation: contractually require **draft memo by Aug 10** (§9 milestone) as the slip-detection date, not Aug 31.

**Risk 2 — Seed Closes Below $10M.**
If the round comes in at $8-9M instead of $12M (one co-lead drops; market repricing):
- $200K audit budget + $264K annual Brussels counsel (A15) + $250K COS (A13) + $400K VPE (A13) consume 11% of the smaller raise in the first 6 months alone
- Foundation grant (A17, $50K/mo = $600K/yr) becomes politically impossible to defend to a $8M-cap board
- Forced choice: defer Std&Reg hire to Q1 2027 (kills JTC 21 liaison) OR cut audit scope to $80K canonicalization-only (kills regulator-facing memo weight) OR defer Foundation grant (breaks Foundation independence narrative)
- **Mitigation:** before Jun 5 decision deadline, model a $9M-net contingency in the operating model as a 4th scenario column; preserve audit + Std&Reg, cut Foundation grant to $25K/mo + defer Mktg #1 hire to Q2 2027.

**Risk 3 — Cross-Document LPR-ERRATA-001 Inconsistency.**
The threat-model briefing (§5) tells the auditor the publisher-side fix is contained to Entry #0. The operating model (Artifact 4 footer) tells the Series A engineer to look for the fix commit hash. If those two documents reference different commit hashes — or if the `pre-v1-entries.json` Foundation-root signature is not in place by Aug 15 ceremony — a Series A diligence engineer with a free afternoon finds the discrepancy and converts a Medium finding into a Critical perception event. **Mitigation:** assign VPE on day 1 (Jul 15) to own a single integrity check across PLAN.md, the audit briefing, the diligence pack, and the public errata page. One person, one source of truth.

---

## 6. RELATIONSHIP TO EXISTING REPOSITORY DOCS

| Existing doc | What gets embedded | New section / amendment |
|---|---|---|
| `PLAN.md` | Pointer to both new artifacts; Big-4 Q4 working-group convening as a milestone; Foundation root-key ceremony Aug 15 | Add §"Seed-to-Series-A Bridge" linking to both new files |
| `04-lpr-spec/` | **Threat-model briefing lives here** as `04-lpr-spec/AUDIT-SOW-REQ-2026-06.md` (canonical filename per briefing header) | New file; cross-link from `00-MASTER-CODE-PLAN-V2.md` Phase 6 |
| `09-code-plan/00-MASTER-CODE-PLAN-V2.md` | Audit kickoff Jun 8, mid-readout Jul 13, final Aug 31 as gating milestones for v1.2 release | New "Audit Gate" subsection between Phase 6 and Phase 7 |
| `12-premortem/04-10X-PLAYBOOK-MAY31.md` | Cohort waterfall (Operating Model Artifact 2) — the 78%-post-enforcement insight is the playbook's empirical spine | Replace any pre-existing rev projection table with Artifact 2 verbatim |
| `12-premortem/05-EXPLOSIVE-ADOPTION-REALITY-CHECK.md` | Downside scenario column (Vanta-ships-native risk) | Add cross-reference; the reality-check arc (A4, A5, A7) flows directly from this document |
| `lpr-status.json` | Weekly cash position (Operating Model Y1 closing cash row); audit milestone status; headcount actuals vs A12 | Three new fields: `cash_position_usd`, `audit_status` (pre/kickoff/draft/published), `fte_count` |
| `CRIT_PATH.md` | **Operating model lives here** as the canonical financial truth; embed the Assumption Registry verbatim; add Foundation root-key ceremony + Std&Reg hire + audit milestones | New §"Financial Critical Path" with full Assumption Registry |
| `win-conditions.json` | Two new conditions: `audit_memo_published_by_2026_08_31`, `series_a_lead_signed_by_2027_03_15` | Schema addition |
| `13-monday-sprint/*.md` | This integration document itself, as `13-monday-sprint/2026-06-01-integration-layer.md`; the 14-day sequence as the sprint backlog | New file plus updated `sprint-backlog.md` |

**Single source of truth principle:** the operating model spec is `CRIT_PATH.md`; the live spreadsheet `financial-model-v1.xlsx` is the working instance; `lpr-status.json` is the weekly snapshot. Three files, one truth.

---

## 7. WHAT'S STILL MISSING

| # | Deliverable | Owner | Target date |
|---|---|---|---|
| 1 | **Foundation root-key ceremony runbook** — m-of-n threshold scheme selection (Shamir vs FROST), share-holder identities (3 of 5 default), HSM model selection, ceremony location (likely Brussels), travel + courier logistics, witness protocol, video-recording policy | VPE + Senior Cryptography Contractor | Aug 1, 2026 (ceremony Aug 15) |
| 2 | **$9M-contingency scenario column** in the operating model | Fractional CFO | Jun 4, 2026 (before Fulgur Q&A) |
| 3 | **Foundation/Inc. shared-services agreement** — the legal instrument that lets Inc. pay the audit fee ($200K) for a Foundation-published memo at `security.ledgerproofhq.io` without breaking the §509(a)(2) public-support fraction or creating an unrelated-business-income event | Adler & Colvin + Cooley | Aug 1, 2026 (before audit memo publishes) |
| 4 | **JTC 21 liaison application package** — written by the Standards & Reg hire, requires Brussels counsel sign-off, requires Foundation board consent | Std&Reg Head + Stibbe + Foundation board chair | Oct 1, 2026 (for Nov JTC 21 plenary) |
| 5 | **Series A narrative deck (16 slides)** — Qatalyst-grade, distinct from the operating model, distinct from the diligence pack; embeds the cohort waterfall as slide 7, the audit memo as slide 11, the Big-4 logos as slide 13 | Veronica + CoS + external designer (Standard Industries or similar) | Sep 15, 2026 (for Qatalyst kickoff) |

---

## 8. THE MONDAY-MORNING ACTION LIST

1. **By 11am ET today (Jun 1):** Email NCC Group (Jen Fernick), Trail of Bits (Dan Guido), and Cure53 (Mario Heiderich) with the threat-model briefing attached and a request for proposal by Friday Jun 5 EOD. Mutual NDA attached. Subject line: "LedgerProof v1.1 audit RFP — response due Jun 5 — Aug 31 publication."

2. **By 3pm ET today:** Call Adam Ross at Cooley to confirm the seed-restructure SAFE drafting timeline supports Jun 19 signature distribution. Confirm the cap table excerpt format Cooley needs from Carta. Book the Jun 9 review call.

3. **By EOD today:** Send a calendar invite to CoS-elect for Mon Jun 8, 9am ET, "calendar discipline handoff." Forward the 14-day sequence above. The CoS owns protecting the 9-11am ET diligence-Q&A block from Jun 8 onward.

4. **By 10am ET Tue Jun 2:** Send the full operating model to TVP (Toby Coppel) with a Loom walkthrough (8-10 min, founder-narrated, cohort waterfall focus). Book Fri Jun 5 10am Q&A. Same package to Stillmark (Alyse Killeen) by 12pm ET, with Fri Jun 5 2pm Q&A.

5. **By EOD Wed Jun 3:** Make the audit-firm decision (decision tree §4). Default: split scope (NCC core + Cure53 verifier, $180K combined). Send signature-ready SoWs Thursday for Monday Jun 8 kickoff. Confirm $125K Jul-26 R&D line in the operating model (A14) reconciles to the actual SoW total; if it doesn't, update the model before it goes to Hercules on Jun 8.