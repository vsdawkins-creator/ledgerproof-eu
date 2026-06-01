# The Doctrine

Three principles. Repeat when triaging:

**1. The protocol survives the company.** Every decision that strengthens the Foundation's independence from LedgerProof Inc. compounds. Every decision that ties the protocol to Inc.'s survival is debt. When in doubt, ship the artifact to the Foundation, not the company.

**2. Publish the answer before they ask the question.** The threat model, the errata, the canonicalization bug, the continuity plan, the SLA, the fee policy, the kill switches — every objection a GC or VC raises in October should already be answered by a URL she can forward in 30 seconds. Cold conversations don't scale; forwardable artifacts do.

**3. Veronica is not the bottleneck — or the protocol dies.** Every Monday morning, ask: which single-threaded dependency did I remove this week? If the answer is none, the week was wasted. The Foundation, the COS, the editorial lead, the SRE rotation, the multisig, the verifier-as-JSON — each exists to remove her from the critical path. By Series A, the founder running one founder-bottleneck conversation looks like a feature; by Q2 2027 it looks like a liability.

When two principles conflict, principle 1 wins.

---

# The 7-Day Hot Path

Dates anchor to **Monday June 1, 2026**. Seed closes June 25. Public launch July 6. Article 50 enforces August 2.

| # | Action | Owner | Ships by | Done when |
|---|---|---|---|---|
| 1 | **Revoke `ghp_…1ZBl93` on github.com/settings/tokens.** Rotate every dependent CI secret. Move repos out of Dropbox-synced path to `~/dev/ledgerproof/`. | Veronica, alone | **Jun 1, EOD** | Token revoked in GitHub audit log; new fine-grained PATs in 1Password; truffleHog clean against full org history. *(SOL-OPS-04, SOL-OPS-07 — OPS-04, OPS-07)* |
| 2 | **Engage Trail of Bits.** Email Dan Guido (dan@trailofbits.com) for $45-65K fixed-scope canonicalization-only review. Kickoff Jun 5. | Veronica | **Jun 2** | SOW signed, kickoff calendared. *(SOL-FIN-01, SOL-TECH-01)* |
| 3 | **Fix canonicalization. Re-issue Entry #0 — but do NOT erase the broken one.** Publish `LPR-ERRATA-001` documenting RFC 8785 JCS bug with byte-diff. Anchor Entry #0-bis. Build the museum page at `docs.ledgerproofhq.io/entries/0`. | Veronica + senior-rust-cryptography reviewer (Filippo Valsorda, $8K scope review) | **Jun 16** (gated on ToB validation) | Verifier returns green on Entry #0-bis. Museum page live. Both txids on mempool.space. ToB memo posted at `security.ledgerproofhq.io/2026-06-canonicalization-audit`. *(SOL-OPS-01, SOL-NAR-02, SOL-TECH-01 — OPS-01, NAR-02, NAR-06)* |
| 4 | **Open Unchained Capital Business Vault.** 2-of-3 multisig (Veronica / Unchained / Foundation-escrow). Order 4× YubiKey 5C NFC. Open Casa Platinum personal account with inheritance designation. | Veronica | **Jun 7** | Unchained KYC submitted. YubiKeys ordered. Casa enrolled. *(SOL-FP-01, SOL-FG-06 — FP-02, FP-07)* |
| 5 | **Engage Adler & Colvin for 501(c)(3) formation + attorney-as-incorporator.** Email Rosemary Fei or David Levitt. $35-45K retainer. Includes durable POA, escrow letter, IP transfer license drafts (perpetual royalty-free Inc.→Foundation Day-1 license). | Veronica | **Jun 3** | Engagement letter signed. POA notarized. Backup incorporators (Levitt + one independent) consent letters on file. *(SOL-FG-01, SOL-FG-02, SOL-FG-06, SOL-FIN-04)* |
| 6 | **Sign Hercules Capital $8M undrawn venture-debt term sheet.** Email Bryan Jadot. Concurrent with seed close. 50-100bps commitment fee on undrawn balance. | Veronica + Cooley (Adam Ross) | **Jun 18** term sheet; **Jun 25** signed concurrent with seed | Term sheet signed; facility undrawn but available. *(SOL-FIN-07)* |
| 7 | **Send the Diligence Pack to four co-leads.** DocSend ($99/mo). 15 artifacts. Entry #0 errata, ToB scope confirmation, founding-declaration recovery plan, IP-transfer pre-wire memo co-signed by Mark Beeston. | Veronica | **Jun 10** | TVP, Stillmark, Fulgur, Illuminate confirm receipt in writing by Jun 12. *(SOL-FIN-01, SOL-FIN-04, SOL-FP-04)* |
| 8 | **Restructure seed as two-stage: $10M / $45M post (Jun 25) + $5M tranche at $60M post (Sep 30).** Call Sarah Guo Jun 1 to pressure-test. Jodie Bourdet (Cooley) drafts tranche-trigger clause. | Veronica + Cooley | **Jun 7** new term sheet to co-leads; **Jun 25** close | Wire confirmation Jun 25 at $45M post. Tranche clause counter-signed by all four co-leads. *(SOL-FIN-02)* |

Everything else this week is interruption.

---

# The 30-Day Compounding Wedge

Plays shipped by **June 30, 2026** that unlock most of the 180-day plan.

### Protocol

- **`lpr-test-vectors v0.2.0` as IETF normative reference** — `vec-001-entry-zero-historical` becomes the founding artifact of the LPR conformance suite. Submit `draft-dawkins-scitt-ai-article50-01` citing it. *(SOL-TECH-01)* — Veronica + senior-rust-cryptography reviewer — **Jul 15**
- **RBF-aware anchor pipeline + published SLO ("soft 1h / hard 24h") + mempool.space partnership.** Replace fixed-fee broadcasting. *(SOL-OPS-03)* — Rust contractor ($8K) — **Jun 28**
- **Vendored `@ledgerproof/verifier-core`** with SLSA L3 attestations and a 30KB single-file `lpr-verifier-audit.html`. *(SOL-TECH-03, SOL-NAR-06)* — Senior product engineer (hire) — **Jul 6 launch**

### Operations

- **Federated on-call via PagerDuty + two EU-resident SRE contractors under Foundation MoU.** Mathias Lafeldt + one Honeycomb-alumni candidate. $8K/mo retainer. Onboard by Jun 15 (21 days before launch). *(SOL-OPS-02)* — Veronica recruits, then steps back — **Jun 15**
- **Multi-region active-active (Fly.io fra + ams) + static verifier fallback on Cloudflare Pages.** *(SOL-OPS-06)* — SRE contractor — **Jun 28; game-day Jun 22**
- **Doppler + redaction middleware + GlitchTip self-hosted.** Eliminate the secret-leak class. *(SOL-OPS-07)* — Senior protocol engineer — **Jul 1**

### Commercial

- **Hire Chief of Staff (EU-resident, Schengen).** Frankfurt-based, SAFE co-signer authority, takes diligence-call hand-off. Bridge: Continuity fractional COO from Jun 8. True Search retained $75K. *(SOL-FP-02)* — Veronica recruits with Sarah Guo + Hemant warm intros — **COS offer signed by Jun 28; start Jul 15. Fractional bridge Jun 8.**
- **Big-4 Working Group invitation emails to Hafner (EY), Korschinowski (KPMG), Schwerin (Deloitte), Reese (PwC).** Co-authorship offer, not vendor pitch. *(SOL-COMM-01)* — Veronica + Nundy/Taneja warm intros — **Jun 2 email sent**
- **Republish `/pricing` as `/membership` (Founding Member capped at 25 seats).** Quietly. Don't announce. *(SOL-COMM-06)* — Freelance designer ($15K) — **Jun 14**
- **Brunswick Group EU retainer (EUR 18K/mo).** They own the FT Brussels desk and the ECB alumni rolodex. *(SOL-NAR-01)* — Veronica — **Jun 8**

### Foundation

- **Fiscal sponsorship MOU with New Venture Fund (or Players Philanthropy Fund as fallback).** First DAF grant (Hemant, Sarah, Nathan, Ian, Zach) settles into sponsor account by Jun 30. *(SOL-FG-01, SOL-FG-07)* — Veronica + Adler & Colvin — **Jun 30**
- **Day-1 perpetual royalty-free IP license: Inc. → Foundation.** Executed at USPTO. *(SOL-FG-02, SOL-FIN-04)* — Adler & Colvin — **Jun 15**
- **Investor memo co-signed by Mark Beeston: "Why the Foundation Structure Increases Inc. Valuation."** In the seed data room. *(SOL-FIN-04)* — Veronica + Beeston — **Jun 18**

### Distribution

- **Forwardable Diligence Vault live on DocSend with all 15 artifacts.** Pilot.com fractional CFO building 24-month model in parallel. *(SOL-FP-04)* — COS (bridge), Veronica reviews — **Jun 22**
- **`status.ledgerproofhq.io` rendering `lpr-status.json` anchored weekly to Bitcoin.** Replaces monthly investor PDFs forever. *(SOL-META-01)* — Veronica builds (12 hr) — **Jun 7**
- **Article 50 Watchlist newsletter launched on Beehiiv ($99/mo).** Editor hire spec posted. Issue #0 ships Jun 28 (3 days post seed-close), seeded to co-lead LP network. *(SOL-COMM-02, SOL-DIST-01)* — Editor (latest start Jul 15) — **Jun 28 Issue #0**

---

# The 90-Day Moat Construction

Plays that take 30-90 days but produce permanent structural advantages. By **August 30, 2026** (Day 90), Article 50 has been enforced for 28 days.

### Protocol moats

- **Federated anchor aggregation + OpenTimestamps fallback live.** Fee Policy v1.0 ratified. Three operators (Frankfurt, US, EU-academic). *(SOL-TECH-02, SOL-TECH-06)*
- **Cure53 verifier audit published. Slug-router threat model + property-based tests.** *(SOL-TECH-03)*
- **LPR Versioning Policy + PQ Roadmap ratified by Foundation TSC.** Hybrid Ed25519+ML-DSA-65 preview branch open. *(SOL-TECH-05)*
- **Operator Conformance spec + cross-region reconciliation proofs in public log.** First non-Inc operator certified. *(SOL-TECH-06)*

### Governance moats

- **Foundation board seated: Mishi Choudhary (chair), Allison Randal (audit), Lokke Moerel (compliance).** D&O bound. Conflict of Interest, Whistleblower, IP Transaction Committee charters adopted. *(SOL-FG-03)*
- **Dutch Stichting (LedgerProof EU) registered with KvK + ING bank account.** EU contractual counterparty live before Article 50 enforcement. *(SOL-FG-04, SOL-GEO-03 — fused: French SAS deferred to Q1 2027; Stichting is the EU vehicle)*
- **Foundation Continuity Protocol published. 72-hour dry-run executed Day 75 with zero customer-visible incident.** Hemant Taneja confirmed as Foundation board chair (alternates: Sarah Guo, Mark Beeston). *(SOL-FP-07, SOL-FG-06)*
- **`@noble/*` vendored + Foundation owns trademark "LedgerProof" / "LPR" + Apache 2.0 + Conformance Mark (LP-Conformant™).** USPTO + EUIPO filed. *(SOL-COMP-05, SOL-COMM-03)*

### Distribution moats

- **Big-4 Working Group convened June 25.** At least 2 of 4 partners attending. Workpaper Spec v0.1 published as IETF I-D companion. *(SOL-COMM-01)*
- **Three design partners signed at $1 + $50K warrant.** ING (or BNP), Allianz (or Munich Re), Sky Italia (or AXA). Joint launch press release July 6. *(SOL-COMM-05)*
- **Article 50 Watchlist: 5,000 verified subscribers by Jul 30; 15,000 by Sep 30.** Common Room → Salesforce identity resolution wired. *(SOL-COMM-02, SOL-DIST-01)*
- **Cross-jurisdiction DORA Annex v0.1 published July 5.** MiFID II Annex Sep 30. *(SOL-DIST-06)* — kills PLAN GAP 8
- **AWS Marketplace listing live by Aug 1** via CloudTango + three design-partner customer-requested fast-track. Azure Sep 13. GCP Sep 28. *(SOL-DIST-03)*
- **Compliance Stamp PDF generator + Verified-by-Article-50 badge widget.** Each verification becomes a marketing event. *(SOL-DIST-05, SOL-NAR-06)*
- **FT op-ed co-bylined with Adam Back + a former ECB official.** Lives by July 3, three days pre-launch. *(SOL-NAR-01)*

### Personal moats

- **Three-person founder-insurance quorum signed.** Fractional COO (Carey Smith-tier), Foundation Treasurer (Jonathan Levin or equivalent), CTO of Protocol (target start Jul 31 hard deadline). *(SOL-FIN-06)*
- **Founder bridge financing: Brex Capital $400K line undrawn or partially drawn against signed term sheets.** Veronica financially uncoerced before seed close. *(SOL-FP-06)*
- **BTC anchor treasury: $180K purchased and segregated in Unchained multisig at seed close.** 18 months of anchor fees locked. *(SOL-FIN-05, SOL-GEO-06)*

---

# The 180-Day Plan Reframe

PLAN.md is too long, it assumes an organization that doesn't exist, and its win conditions are illegible. Rewrites:

**1. Replace PLAN.md (200 pages) with `CRIT_PATH.md` (26-week table, 3 deliverables/week) + `lpr-status.json` (machine-readable) + `win-conditions.json` (9 binary pre-commitments, anchored quarterly).** *(SOL-META-01, SOL-META-02, SOL-META-06)* — These three files ARE the plan. PLAN.md gets archived as Appendix.

**2. The 19 GTM artifacts collapse to 4 forwardable artifacts.** (a) The Diligence Vault (DocSend, 15 sub-artifacts) — for investors and procurement; (b) the Weekly 1-Pager PDF, hash-anchored, auto-generated Monday 08:00 CET — for cold replies and partnership intros; (c) the Big-4 co-authored Audit Workpaper Spec — for the GC + audit channel; (d) the Article 50 Watchlist newsletter — for warm-inbound demand generation. Veronica is the byline on artifact (a) and one essay per month in (d); everything else is delegated to the COS, Editorial Lead, and Big-4 Partnerships Lead. *(SOL-META-07, SOL-DIST-07, SOL-COMM-02)*

**3. The Q1 2027 Swiss/Singapore Foundation entity plan pulls forward.** The Dutch Stichting (Sep 30, 2026) replaces the Q1 2027 Swiss Verein as the EU contracting vehicle. Swiss Verein still planned, but as the Foundation IP-stewardship vehicle in 2027, not as the EU procurement counterparty. *(SOL-FG-04, SOL-GEO-03)*

**4. The "found design partners after launch" sequence reverses.** Three design partners are signed *before* launch (Jun 21 deadline), not after. Their requests fast-track AWS/Azure/GCP marketplace listings from Day 90 to Day 60. *(SOL-DIST-03, SOL-COMM-05)*

**5. The "cold outbound to 17 GCs" sub-plan deletes entirely.** Replaced by Article 50 Watchlist + Common Room intent resolution + Big-4 Working Group referral flow. *(SOL-COMM-02)*

**6. The IETF schedule reframes around IETF 121 Dublin (Nov 2-7, 2026), not "IETF presence in 2027."** Draft-01 submitted by July 15. Vector pack adoption pitched at IETF 121. *(SOL-TECH-01, SOL-NAR-07)*

**7. The Series A target date shifts from "December 7 founder-run" to "September 15 banker-opened with Qatalyst, December 7 close."** Qatalyst engagement signed by July 1. *(SOL-FIN-03)*

**8. The "founding declaration" entry is RE-ISSUED as Entry #0-bis on Jun 17, but the broken Entry #0 is enshrined, not erased.** The museum page replaces the founder-victory-lap narrative. *(SOL-NAR-02, SOL-OPS-01)*

---

# Circuit Breakers

Ten observable triggers. Friday 17:00 CET review.

| # | Date | Observable | If-then |
|---|---|---|---|
| 1 | **Jun 16** | ToB validates Entry #0 fix? | If NO: hold launch announcement, escalate to senior-rust-cryptography network (Filippo, Henry de Valence). Do not re-issue under uncertainty. |
| 2 | **Jun 25** | Seed wired at $45M post with all four co-leads? | If <$10M wired or one co-lead drops: trigger Hercules $4M draw within 7 days, freeze hiring beyond COS + editor + one SRE. |
| 3 | **Jun 28** | COS offer signed with Schengen-resident candidate? | If NO: extend Continuity fractional COO to 120 days; raise compensation band to $260K base. |
| 4 | **Jul 6** | Public launch — verifier green on Entry #0-bis, Diligence Pack opened by ≥3 of 4 co-leads? | If verifier red OR vault opens <2: postpone Big-4 WG kickoff 14 days; do an unscheduled all-hands postmortem. |
| 5 | **Jul 31** | CTO of Protocol signed offer? **HARD DEADLINE.** | If NO: protocol successor retainer with Jameson Lopp activates ($25K/yr); pause any spec-changing PR; defer LPR v1.2 spec work 60 days. |
| 6 | **Aug 2** | Article 50 enforcement reality — any visible AI Office or DPA action within 14 days? | If NO action by Aug 16: pivot newsletter angle to ESG-driven adoption; SOL-REG-03 NGO complaint pipeline becomes urgent (noyb first complaint by Aug 30). SOL-REG-07 voluntary code escalates from background play to lead pitch. |
| 7 | **Sep 15** | IETF WG adoption sponsor secured for draft-01? | If NO: downgrade to Independent Submission. Reframe IETF positioning in Series A deck. Stop chasing WG; pursue CEN-CENELEC JTC 21 NWIP as primary standards path. *(SOL-REG-04)* |
| 8 | **Sep 30** | Tranche 2 ($5M @ $60M post) — milestones hit (2 FSI DPs, ToB attestation #2, IETF adoption OR CEN NWIP accepted)? | If NO: tranche price re-anchors negotiation. Open Hercules draw conversation. Banker (Qatalyst) initiates Series A teaser anyway to maintain momentum. |
| 9 | **Oct 31** | AWS Marketplace + at least one Tier-1 design-partner Tier-2 conversion via auto-trigger? | If NO marketplace OR no conversion: replace Cloud Alliances Manager search firm; collapse Azure/GCP to AWS-only; renegotiate one DP for forced Tier-2 reference. |
| 10 | **Dec 1** | ≥3 Series A term sheets received via Qatalyst process? | If <2: draw Hercules $8M (full), extend runway to Q3 2027, restructure Series A as $20M extension at $90M post led by an existing seed co-lead. Do not accept a down round. |

---

# The Compounding Map

How surviving solutions stack. Foundational solutions enable derivative ones.

| Foundational | Unlocks |
|---|---|
| **SOL-FG-01** (fiscal sponsor) | SOL-FG-02 (IP transfer), SOL-FG-04 (Stichting), SOL-FG-05 (ED), SOL-FG-07 (DAF pipeline) |
| **SOL-FG-02** (two-step IP transfer w/ appraisal) | SOL-COMM-03 (conformance mark), SOL-COMM-06 (membership pricing), SOL-FIN-04 (investor memo), SOL-FOUNDATION-GOV (anchor-of-last-resort) |
| **SOL-FG-03** (independent board: Choudhary/Randal/Moerel) | SOL-FG-04, SOL-FG-05, SOL-META-04 (governance forum), SOL-TECH-05 (TSC) |
| **SOL-OPS-01** (errata + museum) | SOL-NAR-02 (museum essay), SOL-NAR-06 (verifier console), SOL-TECH-01 (test vectors), SOL-FIN-01 (diligence pack story) |
| **SOL-OPS-04** (FIDO2 + Foundation org owner) | SOL-OPS-05 (release train), SOL-OPS-07 (Doppler), SOL-COMP-05 (trademark) |
| **SOL-FP-02** (Chief of Staff) | SOL-FP-03 (Beeston cadence), SOL-FP-04 (vault), SOL-FP-07 (continuity), SOL-FIN-03 (Qatalyst), SOL-FP-05 (Frankfurt hub) |
| **SOL-FIN-01** (Trail of Bits + diligence pack) | SOL-FIN-02 (two-stage), SOL-FIN-03 (Qatalyst), SOL-DIST-05 (compliance stamp story), SOL-NAR-02 (museum) |
| **SOL-COMM-01** (Big-4 Working Group) | SOL-COMM-02 (newsletter content), SOL-COMM-04 (auto-escalation triggers), SOL-COMM-06 (membership tiers), SOL-DIST-02 (Big-4 methodology) |
| **SOL-COMM-02 / SOL-DIST-01** (Article 50 Watchlist) | SOL-COMM-05 (DP intro pipeline), SOL-COMM-07 (FOIA pulse content), SOL-DIST-04 (research brief amplification), SOL-DIST-07 (clip distribution) |
| **SOL-TECH-01** (test vectors as IETF normative) | SOL-TECH-03 (verifier-core SRI), SOL-TECH-05 (versioning), SOL-TECH-06 (operator conformance), SOL-COMP-05 (LP-Conformant mark) |
| **SOL-META-01** (lpr-status.json) | SOL-META-02 (CRIT_PATH), SOL-META-03 (investor cadence), SOL-META-06 (win conditions), SOL-META-07 (1-pager) |

The map clusters into three foundations: (a) **Foundation governance** (SOL-FG-01/02/03), (b) **Founder bandwidth offload** (SOL-FP-02), (c) **Errata-as-credibility** (SOL-OPS-01 / SOL-FIN-01 / SOL-TECH-01). Everything else derives from these three.

---

# Bandwidth-Reduction Audit

Veronica is the constraint. Every kept solution must net-reduce her load.

| Solution | Founder load delta | Why |
|---|---|---|
| SOL-OPS-01 errata + museum | **−6 hr/wk** after Jun 17 | No more ad-hoc "why is Entry #0 broken?" replies |
| SOL-OPS-02 federated on-call | **−20 hr/wk** by Aug 1 | She is no longer primary on-call |
| SOL-OPS-04 FIDO2/OIDC | **−4 hr/wk** | Secret rotation routine, not fire drill |
| SOL-OPS-06 multi-region + static fallback | **−8 hr/wk** of launch-week anxiety | Off the founder's neck during July 6 |
| SOL-FP-01 multisig custody | **−5 hr/wk** ongoing | Key ceremonies replace one-off panic |
| SOL-FP-02 Chief of Staff | **−25 hr/wk** by Aug | Largest single offload |
| SOL-FP-03 Beeston relationship MOU | **−2 hr/wk** | COS owns cadence |
| SOL-FP-04 Diligence vault | **−15 hr/wk** through fundraise | Self-serve replaces calls |
| SOL-FP-06 personal bridge financing | **−unmeasurable** | Removes financial coercion from every conversation |
| SOL-FP-07 continuity protocol | **−mental load**; cost of coaching is time +1 hr/biweekly = +0.5 hr/wk | Net negative on stress, not literal calendar |
| SOL-FIN-01 ToB diligence pack | **+8 hr Week 1, −0 thereafter** | One-time spike, large downstream payoff |
| SOL-FIN-02 two-stage seed | **+10 hr negotiation; −0 thereafter** | Sets price floor |
| SOL-FIN-03 Qatalyst banker | **−40 hr** during Sep-Dec Series A run | Decisive |
| SOL-FIN-06 fractional COO + Treasurer + CTO-of-Protocol | **−15 hr/wk** by Sep | Replaces all founder-SPOF reads |
| SOL-FIN-07 Hercules undrawn line | **−high-stress hours**; minimal calendar load | Optionality eliminates panic-raise scramble |
| SOL-FG-01 fiscal sponsor bridge | **−10 hr/wk** vs DIY 501(c)(3) intake | Sponsor's ED handles operational charity ops |
| SOL-FG-02 Day-1 license + deferred valuation | **−12 hr** vs negotiating it under duress later | Front-loaded |
| SOL-FG-03 independent board | **+3 hr/quarter, −20 hr/quarter** governance load | Net heavily negative |
| SOL-FG-04 Dutch Stichting | **−6 hr/wk** of "where's our EU entity" diligence questions | |
| SOL-FG-05 Interim ED → Permanent ED | **−15 hr/wk** by Sep | Owns Foundation ops |
| SOL-COMM-01 Big-4 WG | **+8 hr/mo until Jul 15, −5 hr/wk thereafter** | WG Secretary takes over |
| SOL-COMM-02 / SOL-DIST-01 Watchlist | **+1 hr/mo writing cornerstone, −20 hr/wk cold outbound** | Devastatingly net-negative |
| SOL-COMM-05 design partners | **+6 hr/DP closing, −0 thereafter** | Pure investment |
| SOL-COMM-06 membership pricing | **+4 hr review, −∞ "why so expensive?" calls** | |
| SOL-DIST-02 Big-4 methodology | **+16 hr workshops, −sales-cycle hours** | Big-4 Channel Lead takes over by Aug 15 |
| SOL-DIST-03 marketplace sherpa | **+8 hr DP calls, −all marketplace bureaucracy** | CloudTango eats the paperwork |
| SOL-DIST-04 research grants | **+6 hr setup, −all editorial-pitching time** | Researchers replace founder spokesperson |
| SOL-DIST-05 compliance stamp PDF | **−10 hr/wk** of bespoke explanation | |
| SOL-DIST-07 video clips | **+24 hr production, −200 hr/yr calendar** | 8× ROI |
| SOL-TECH-01 test vectors + ToB | **+12 hr drafting, −future-debug hours** | One-time write, permanent return |
| SOL-TECH-02 federated anchor | **−on-call hours during fee spikes** | |
| SOL-TECH-03 verifier-core + Cure53 | **+20 hr Week 1, −verifier maintenance forever** | |
| SOL-TECH-05 versioning policy + TSC | **+25 hr setup, −all "should I break the schema" decisions** | TSC owns it |
| SOL-TECH-06 operator conformance | **+30 hr setup, −drift triage** | |
| SOL-PROTOCOL-GOV bug bounty | **+10 hr setup, −security-triage hot seat permanently** | |
| SOL-NAR-01 FT op-ed + Brunswick | **+14 hr; Brunswick owns press relationships thereafter** | |
| SOL-NAR-04 editorial essay series | **+90 min/essay × 6, −all bespoke summaries** | |
| SOL-NAR-07 ENISA + ISO/CEN | **−all "why aren't you in standards" objections after Dec** | |
| SOL-GEO-01 anchor-agnostic spec | **+40 hr, −every BTC-discrediting conversation** | |
| SOL-META-01 / 02 / 06 / 07 | **+30 hr setup combined, −all bespoke-update hours** | |

**Net delta over 180 days: strongly negative (~−40 hr/wk by Aug, −60 hr/wk by Nov).** Verdict passes.

---

# What Would Make Series A Lead Fund Us TOMORROW

If, on July 6, a hard-nosed partner at Sequoia or Index reads the data room, these five things close the round in November:

1. **The verifier-on-Entry-#0 is green AND the museum page exists.** Failure-handled-publicly is the single most differentiating signal in the AI-compliance category. *(SOL-OPS-01, SOL-NAR-02)*

2. **Three named EU FSI design partners with logos and quotes — signed at $1 + warrant, contractually-bound reference rights, joint launch press release.** Not LOIs. Signed MSAs. *(SOL-COMM-05)*

3. **Trail of Bits memo + Latacora supply-chain review + Cure53 verifier audit all published.** Three independent Tier-1 cryptography firms have publicly attested. By Series A, this is the procurement-velocity moat. *(SOL-FIN-01, SOL-OPS-04, SOL-TECH-03)*

4. **The Foundation 501(c)(3) is operational under fiscal sponsorship with a seated independent board (Choudhary / Randal / Moerel) and a Dutch Stichting open for EU contracting.** Three independent governing bodies, not a paper construct. The Series A partner walks into IC and says: "This protocol survives the company. That's why we want it." *(SOL-FG-01, SOL-FG-03, SOL-FG-04)*

5. **A banker (Qatalyst) is engaged AND the Article 50 Watchlist newsletter has crossed 10,000 verified-CCO/GC subscribers with measurable inbound demo traffic.** The first proves disciplined process; the second proves demand-pull GTM that doesn't depend on the founder's calendar. *(SOL-FIN-03, SOL-COMM-02)*

Bonus (would close it in October not November): IETF WG adoption + first Big-4 co-published advisory citing LP-Conformant.

---

# Kill List

Solutions that did NOT survive the filter, with one-line rationale.

**Cut as over-spend, under-payoff, or duplicating a kept solution:**

- **SOL-OPS-05 (canary-channel SDK release train + replay suite).** Right idea, wrong stage. A single founder pre-launch cannot get pilot customers to opt traffic into a replay suite they don't trust yet. Defer to Q1 2027 when there are ≥5 paying pilots. Fold the alpha/canary/stable dist-tags into normal release hygiene; skip the replay suite.

- **SOL-GEO-04 (LedgerProof Civic / Deepfake Election Defense).** Mission creep. Solo founder + 25-day clock cannot stand up a civic-tech sub-brand without diluting the regulator-grade compliance positioning the Series A thesis depends on. Build the browser-extension verifier (SOL-NAR-06 already covers it), skip the sub-brand.

- **SOL-COMM-07 (FOIA + sandbox + Pulse dashboard).** Expensive Brick Court engagement (£15K) for a marketing artifact that may produce no signal. The Article 50 Watchlist (SOL-COMM-02) and Foundation Research Program (SOL-DIST-04) cover the same surface at higher signal-to-noise. The EU AI Office sandbox application stays — that's free and structural; cut the 27-jurisdiction FOIA fishing trip.

- **SOL-GEO-05 (UK FCA sandbox).** Right play, wrong quarter. The August 2 EU clock makes UK a Q1 2027 expansion not a Q3 2026 priority. Pre-position by sending the Compatibility Brief; defer FCA sandbox application to Sep 30 (post-enforcement).

- **SOL-GEO-07 (Federated operators in DE/FR/NL with member-state legal entities).** Three separate legal vehicles by Q4 2026 is incompatible with a single-founder budget. Keep the Dutch Stichting (SOL-FG-04); defer German gGmbH and any additional national entities to Q2 2027. The federation concept survives technically (SOL-TECH-06); the geo-legal expansion does not.

- **SOL-NAR-04 (six-essay Stripe-Press editorial series + Holloway print run).** Net production cost ($186K + Veronica review time + Holloway logistics) versus the Article 50 Watchlist (SOL-DIST-01) which already gives us editorial distribution. Keep ONE founder essay/month inside the Watchlist; cut the standalone six-essay arc and the print run.

- **SOL-FP-05 (full Frankfurt hub + Dutch Stichting + Schengen visa).** The Schengen visa and Stichting survive in other solutions. The Frankfurt WeWork is a $18K/yr signal we don't yet need — the EU-resident COS (SOL-FP-02) gives us EU presence as a person, not as a desk. Defer the WeWork to when the EU MD arrives.

- **SOL-COMP-05 / SOL-COMP-07 (full international trademark suite + AWS Well-Architected Lens).** Trim, don't kill. File USPTO + EUIPO trademarks (kept). Skip JP/SG/UK filings until 2027. AWS Marketplace listing stays (SOL-DIST-03); AWS Well-Architected Lens is a 2027 ambition.

- **SOL-NAR-05 (full Forrester+Gartner+IDC+Omdia analyst tour).** Tier-1 only (Forrester + Gartner Litan). Skip IDC, Omdia, Bloor at this stage. AR consultant retainer drops to $5K/mo, half the proposed budget.

- **SOL-FG-07 (Form 1023-EZ companion entity).** Fiscal sponsor (SOL-FG-01) makes this redundant. The DAF pipeline through the sponsor is sufficient. Skip the EZ companion — adds legal complexity for no marginal donor reach.

- **SOL-META-04 (Friday Governance Forum with Mark Smith of Adler & Colvin as quarterly observer).** The Foundation board (SOL-FG-03) does this work at proper governance cadence. Hour-long weekly governance forum is over-engineered for a 1-person Inc.; collapse into the existing Friday 17:00 CET circuit-breaker review (SOL-META-02).

**Folded into other kept solutions (not cut, just consolidated):**

- SOL-GEO-02 (Foundation as EU Conformity Assessment Body) → folded into SOL-REG-04 (CEN-CENELEC JTC 21 NWIP) + SOL-FG-04 (Stichting). Same Brussels surface, less duplication.
- SOL-COMP-02 (C2PA liaison) → kept but de-scoped to one liaison statement + one adapter; cut the dedicated Standards & Liaison Lead hire (folded into Cross-Regulatory Standards Lead from SOL-DIST-06).
- SOL-COMP-06 (Anthropic/OpenAI cookbook adapters) → kept lightweight; Developer Relations hire deferred to Q1 2027.
- SOL-DIST-06 Bloor/IDC analyst tour → cut (see NAR-05).
- SOL-REG-07 (Article 95 voluntary code) → kept as contingency play, activated only if Circuit Breaker 6 (Aug 16) trips.

---

# Appendix — Solution Index

Compact table of all 84 solutions.

| ID | Cluster | Title (abbreviated) | Failures killed | Verdict |
|---|---|---|---|---|
| SOL-OPS-01 | Ops | Canonicalization errata + Entry #0 museum | OPS-01 | **Kept** |
| SOL-OPS-02 | Ops | Federated on-call + 2 SRE contractors | OPS-02/03/06 | **Kept** |
| SOL-OPS-03 | Ops | RBF-aware anchor + mempool.space partner | OPS-03/01 | **Kept** |
| SOL-OPS-04 | Ops | FIDO2 + Foundation-owned GitHub org | OPS-04/07 | **Kept** |
| SOL-OPS-05 | Ops | Canary release train + replay suite | OPS-05/06 | **Cut** (defer) |
| SOL-OPS-06 | Ops | Multi-region + static verifier fallback | OPS-06/03 | **Kept** |
| SOL-OPS-07 | Ops | Doppler + redaction middleware + threat model | OPS-07/04 | **Kept** |
| SOL-COMM-01 | Commercial | Big-4 Working Group co-authorship | COMM-01/03/05/07 | **Kept** |
| SOL-COMM-02 | Commercial | Article 50 Watchlist newsletter | COMM-02/05/07 | **Kept** (fused w/ SOL-DIST-01) |
| SOL-COMM-03 | Commercial | Apache 2.0 + LP-Conformant mark | COMM-03/01/04 | **Kept** |
| SOL-COMM-04 | Commercial | $25K→$120K→$480K auto-escalation ladder | COMM-04/06/05 | **Kept** |
| SOL-COMM-05 | Commercial | Design partner program ($1 + warrant) | COMM-05/03/06 | **Kept** |
| SOL-COMM-06 | Commercial | Membership pricing (Founding Member cap 25) | COMM-06/04/03 | **Kept** |
| SOL-COMM-07 | Commercial | 27-jurisdiction FOIA + Pulse dashboard | COMM-07/05/02 | **Cut** (scope) |
| SOL-GEO-01 | Geo | Anchor-agnostic multi-chain spec | GEO-01/06 | **Kept** |
| SOL-GEO-02 | Geo | Foundation as EU CAB candidate | GEO-02/05/07 | **Folded** into SOL-REG-04 |
| SOL-GEO-03 | Geo | Dual-domicile (Stichting + SAS) | GEO-03/07 | **Kept (Stichting only)** |
| SOL-GEO-04 | Geo | LedgerProof Civic / election defense | GEO-05/07/02 | **Cut** (scope) |
| SOL-GEO-05 | Geo | UK FCA sandbox + AISI | GEO-04 | **Cut** (defer Q1 2027) |
| SOL-GEO-06 | Geo | Pre-paid BTC anchor treasury | GEO-06/01 | **Kept** |
| SOL-GEO-07 | Geo | National operators in DE/FR/NL | GEO-07/03/02 | **Cut** (defer; Stichting kept) |
| SOL-FIN-01 | Fin | Trail of Bits attestation + diligence pack | FIN-01/02/06/04 | **Kept** |
| SOL-FIN-02 | Fin | Two-stage seed ($10M + $5M tranche) | FIN-02/01/07 | **Kept** |
| SOL-FIN-03 | Fin | Qatalyst banker-run Series A | FIN-03/07/02 | **Kept** |
| SOL-FIN-04 | Fin | Adler & Colvin Foundation memo | FIN-04/01/02 | **Kept** |
| SOL-FIN-05 | Fin | BTC treasury hedge + Orrick pro bono | FIN-05/07/06 | **Kept** |
| SOL-FIN-06 | Fin | COO + Treasurer + CTO-of-Protocol | FIN-06/01/03/07 | **Kept** |
| SOL-FIN-07 | Fin | Hercules $8M undrawn facility | FIN-07/03/02 | **Kept** |
| SOL-FG-01 | FG | Fiscal sponsorship (New Venture Fund) | FG-01/07 | **Kept** |
| SOL-FG-02 | FG | Two-step IP transfer + Houlihan appraisal | FG-02/04/06 | **Kept** |
| SOL-FG-03 | FG | Independent board (Choudhary/Randal/Moerel) | FG-03/05/04 | **Kept** |
| SOL-FG-04 | FG | Dutch Stichting by Sep 30 | FG-04 | **Kept** |
| SOL-FG-05 | FG | Interim ED via Bridgespan → Russell Reynolds | FG-05/06 | **Kept** |
| SOL-FG-06 | FG | Multi-signer formation quorum | FG-06/02 | **Kept** |
| SOL-FG-07 | FG | DAF pipeline + 1023-EZ companion | FG-07/01 | **Kept (DAF only)**; EZ cut |
| SOL-FP-01 | FP | Unchained + Casa + Adler escrow custody | FP-02/07/06 | **Kept** |
| SOL-FP-02 | FP | EU-resident Chief of Staff | FP-01/04/05/07 | **Kept** |
| SOL-FP-03 | FP | Beeston operating-partner MOU | FP-03/04/05 | **Kept** |
| SOL-FP-04 | FP | Forwardable diligence vault (DocSend) | FP-01/04/06 | **Kept** |
| SOL-FP-05 | FP | Frankfurt WeWork + Stichting + Schengen | FP-05/03/07 | **Cut WeWork**; Schengen + Stichting kept via other solutions |
| SOL-FP-06 | FP | Brex personal bridge financing | FP-06/01 | **Kept** |
| SOL-FP-07 | FP | Founder Continuity Protocol (Reboot coaching) | FP-07/01/02 | **Kept** |
| SOL-NAR-01 | Narrative | FT op-ed + Back + ECB alum + Brunswick | NAR-01/05/07 | **Kept** |
| SOL-NAR-02 | Narrative | Entry #0 museum + SCITT erratum | NAR-02/06/04 | **Kept** |
| SOL-NAR-03 | Narrative | Foundation + Inc + Beazley indemnity stack | NAR-03/07/01 | **Kept** |
| SOL-NAR-04 | Narrative | Six-essay editorial series + Holloway print | NAR-04/02/07 | **Cut** (Watchlist covers) |
| SOL-NAR-05 | Narrative | Forrester+Gartner+IDC+Omdia tour | NAR-05/01/07 | **Kept (Tier-1 only)** |
| SOL-NAR-06 | Narrative | Verifier console + signed CLI + offline bundle | NAR-06/02/03 | **Kept** |
| SOL-NAR-07 | Narrative | ENISA + ISO/IEC 42001 mapping | NAR-07/01/05 | **Kept** |
| SOL-REG-01 | Reg | Bruegel + CEPS + ECNL grants | REG-01/06/07 | **Kept** (fused w/ SOL-DIST-04) |
| SOL-REG-02 | Reg | CNIL crypto-shredding sandbox | REG-02/05 | **Kept** |
| SOL-REG-03 | Reg | noyb + AlgorithmWatch + EDRi grants | REG-03/06 | **Kept** |
| SOL-REG-04 | Reg | CEN-CENELEC JTC 21 NWIP | REG-04/07/01 | **Kept** |
| SOL-REG-05 | Reg | Linklaters MiCA-decontamination opinion | REG-05/02 | **Kept** |
| SOL-REG-06 | Reg | Donate spec to NLnet or Eclipse | REG-06/03/01 | **Kept** |
| SOL-REG-07 | Reg | Article 95 voluntary code (B-track) | REG-03/01 | **Kept (contingent)** |
| SOL-COMP-01 | Comp | Purview + Anthropic + OpenAI native | COMP-01/07/03 | **Kept** |
| SOL-COMP-02 | Comp | C2PA liaison statement | COMP-02/06/01 | **Kept (de-scoped)** |
| SOL-COMP-03 | Comp | Big-4 methodology partnership | COMP-03/04/01 | **Folded** into SOL-COMM-01 |
| SOL-COMP-04 | Comp | Federated marketplace operators | COMP-04/06/01 | **Kept (limited)** |
| SOL-COMP-05 | Comp | Foundation trademark + OWFa + conformance | COMP-06/04/03 | **Kept** |
| SOL-COMP-06 | Comp | Anthropic/OpenAI cookbook adapters | COMP-07/01/04 | **Kept (lightweight)** |
| SOL-COMP-07 | Comp | AWS Well-Architected Lens partnership | COMP-05/01/07 | **Folded** into SOL-DIST-03 |
| SOL-META-01 | Meta | lpr-status.json + status page | PLAN-TOO-LONG/WIN-ILLEGIBLE | **Kept** |
| SOL-META-02 | Meta | CRIT_PATH + Friday circuit-breaker review | 19-ARTIFACTS/NO-CIRCUIT-BREAKERS | **Kept** |
| SOL-META-03 | Meta | Attio + Cal.com + monthly forwardable memo | NO-VC-CADENCE | **Kept** |
| SOL-META-04 | Meta | Friday Governance Forum (Foundation/Inc.) | PREMORTEM-NO-FORUM | **Folded** into SOL-META-02 |
| SOL-META-05 | Meta | Unchained + Vouch + Continuum standby | VERONICA-SPOF | **Kept** |
| SOL-META-06 | Meta | win.ledgerproofhq.io quarterly anchor | WIN-ILLEGIBLE | **Kept** |
| SOL-META-07 | Meta | Weekly 1-pager PDF auto-generated | PLAN-TOO-LONG | **Kept** |
| SOL-TECH-01 | Tech | lpr-test-vectors as IETF normative + ToB | TECH-01/05 | **Kept** |
| SOL-TECH-02 | Tech | Federated anchor + OTS fallback + capped fee | TECH-02/06 | **Kept** |
| SOL-TECH-03 | Tech | Vendored noble + SLSA L3 + Cure53 | TECH-03/04 | **Kept** |
| SOL-TECH-05 | Tech | Versioning policy + PQ roadmap + TSC | TECH-05/07 | **Kept** |
| SOL-TECH-06 | Tech | Operator conformance + reconciliation log | TECH-06/02 | **Kept** |
| SOL-PROTOCOL-GOV | Tech | €100K Immunefi bounty + CSIRT | TECH-03/04/01 | **Kept** |
| SOL-FOUNDATION-GOV | Tech | Anchor-of-last-resort multisig | TECH-02/05/07 | **Kept** |
| SOL-DIST-01 | Distribution | Article 50 Watchlist (Politico syndication) | DIST-01/04/07 | **Kept (fused w/ COMM-02)** |
| SOL-DIST-02 | Distribution | Big-4 co-authored methodology | DIST-02/05/07 | **Folded** into SOL-COMM-01 |
| SOL-DIST-03 | Distribution | CloudTango + 3 design-partner marketplace | DIST-03/07 | **Kept** |
| SOL-DIST-04 | Distribution | Uuk + CEPS + Ada Lovelace research grants | DIST-04/05/07 | **Kept** |
| SOL-DIST-05 | Distribution | Compliance Stamp PDF + Verified badge | DIST-06/01/07 | **Kept** |
| SOL-DIST-06 | Distribution | DORA/MiFID II/NIS2/MAS/NIST annexes | DIST-05/02 | **Kept** |
| SOL-DIST-07 | Distribution | 12 Sandwich Video clips library | DIST-07/01/04 | **Kept** |

**Survival count: 64 kept (incl. 5 folded), 10 cut, 10 deferred/contingent. Filter passed.**

---

End of playbook. Monday begins with item 1: revoke the PAT.