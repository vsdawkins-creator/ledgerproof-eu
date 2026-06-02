# CRIT_PATH — LedgerProof critical path, Jun 1 → Dec 7, 2026

**Generated:** Monday June 1, 2026
**Cadence:** 3 deliverables per week, week-indexed. **One row = one Tuesday.** Friday 17:00 CET = circuit-breaker review.
**Reads against:** [`PLAN.md`](PLAN.md) (integrator), [`09-code-plan/00-MASTER-CODE-PLAN-V2.md`](09-code-plan/00-MASTER-CODE-PLAN-V2.md) (engineering), [`12-premortem/04-10X-PLAYBOOK-MAY31.md`](12-premortem/04-10X-PLAYBOOK-MAY31.md) (operations).
**Operational substrate:** [`lpr-status.json`](lpr-status.json) (protocol state, weekly anchor), [`win-conditions.json`](win-conditions.json) (quarterly boolean win conditions), [`ops-state.json`](ops-state.json) (corporate ops state: phase, corrections C1-C8, kill switches KS1-KS8, workstreams W1-W7).
**Master operating document:** [`14-seed-close-pack/04-atomic-explosion-master-plan.md`](14-seed-close-pack/04-atomic-explosion-master-plan.md).

**Reading key:** ⚡ = single-founder action (cannot be delegated). 🤝 = depends on a contractor or counsel. 🌐 = depends on a counterparty (regulator, customer, investor). ⭕ = circuit-breaker observable.

---

| Week | Tuesday | Deliverable 1 | Deliverable 2 | Deliverable 3 |
|---:|---|---|---|---|
| **W1** | Jun 02 | ⚡ Revoke PAT; secrets rotated; Keychain helper wired (SOL-OPS-04) | ⚡ Holding page live on `/r/founding-declaration` and `/r/0` (SOL-OPS-01) | ⚡ Trail of Bits + Adler & Colvin + Hercules engagement emails sent (SOL-FIN-01, SOL-FG-01, SOL-FIN-07) |
| **W2** | Jun 09 | 🤝 ToB canonicalization audit kickoff Jun 5; in-flight | 🌐 Seed restructure: all 4 co-leads confirm two-stage in writing (SOL-FIN-02) | 🤝 Adler & Colvin engagement letter signed; durable POA notarized; fiscal sponsor MOU drafted (SOL-FG-01, SOL-FG-06) |
| **W3** | Jun 16 | ⭕ ToB validates v1.1+ canonicalization (circuit breaker — if NO, hold launch) | 🤝 Day-1 Inc→Foundation IP license filed at USPTO (SOL-FG-02) | ⚡ Founding-declaration entry issued via publisher portal; aliases.json updated; verifier green on `/r/founding-declaration` (SOL-OPS-01) |
| **W4** | Jun 23 | 🤝 Federated on-call rotation live (Mathias Lafeldt + Honeycomb-alumni); founder no longer primary pager (SOL-OPS-02) | ⭕ Multi-region game-day passed (Fly fra+ams; static fallback live on Cloudflare Pages) (SOL-OPS-06) | ⚡ Diligence pack sent to 4 co-leads via DocSend; per-recipient watermarked links |
| **W5** | Jun 30 | 🌐 **SEED CLOSE: $10M @ $45M post wired** Jun 25; Hercules $8M undrawn signed concurrent (SOL-FIN-02, SOL-FIN-07) | 🤝 Federated anchor pipeline live (RBF + OTS fallback); fee policy v1.0 published (SOL-OPS-03, SOL-TECH-02) | 🤝 Doppler vault + redaction middleware + GlitchTip self-hosted (SOL-OPS-07) |
| **W6** | Jul 07 | ⚡ **PUBLIC LAUNCH Jul 6**: founder open letter published; Article 50 landing page live; verifier green on Entry #0-bis (SOL-NAR-02, SOL-OPS-01) | 🤝 verifier-core vendored with SLSA L3 attestations; `lpr-verifier-audit.html` ≤32KB single-file shipped (SOL-TECH-03) | 🌐 First press: FT op-ed with Adam Back + ECB alum byline; Politico EU desk pickup (SOL-NAR-01) |
| **W7** | Jul 14 | 🤝 IETF `draft-dawkins-scitt-ai-article50-01` submitted with `lpr-test-vectors v0.2.0` as normative reference (SOL-TECH-01) | 🤝 Form 1023 long-form filed with expedited handling citing EU deadline (SOL-FG-01) | ⚡ Chief of Staff offer signed (Schengen-resident, SAFE co-signer authority); start date Jul 15 (SOL-FP-02) |
| **W8** | Jul 21 | 🤝 Big-4 Working Group invitation emails to Hafner (EY), Korschinowski (KPMG), Schwerin (Deloitte), Reese (PwC); co-authorship offer (SOL-COMM-01) | 🤝 Versioning policy + PQ roadmap doc + slug-router threat model all published at spec.ledgerproofhq.io (SOL-TECH-05) | 🌐 Article 50 Watchlist newsletter Issue #1 published on Beehiiv; seeded to co-lead LP network |
| **W9** | Jul 28 | ⭕ **CTO of Protocol signed offer (HARD DEADLINE Jul 31)** — if not, Lopp $25K/yr retainer activates and v1.2 spec work pauses (SOL-FIN-06) | 🤝 First chaos game-day: anchor-stall scenario; runbook delta committed | 🤝 NCC Group or Bishop Fox pentest #1 scope finalized |
| **W10** | Aug 04 | 🌐 **Article 50 enforcement begins Aug 2**; EU operator at 99.9% target for first 14d (SOL-OPS-02) | 🌐 Three design partners signed at $1 + warrant + reference rights; joint launch press release (SOL-COMM-05) | 🤝 AWS Marketplace listing live (CloudTango fast-track) (SOL-DIST-03) |
| **W11** | Aug 11 | ⭕ EU operator 99.9% for first 14d of enforcement (Aug 16 circuit-breaker — if NO, third SRE contractor + code freeze) | 🤝 Operator Conformance Spec v0.1 ratified; first non-Inc operator (EU-academic) certification in progress (SOL-TECH-06) | 🤝 ToB memo published at security.ledgerproofhq.io/tob/2026-06-canonicalization-audit |
| **W12** | Aug 18 | 🤝 €100K Immunefi bug bounty live, Foundation-funded (SOL-PROTOCOL-GOV) | 🤝 Latacora supply-chain review delivered + published | 🌐 Article 50 Watchlist passes 5K verified subscribers; tracked in `lpr-status.json` |
| **W13** | Aug 25 | 🌐 Three independent Foundation board members signed (Choudhary chair, Randal audit, Moerel compliance); D&O policy bound (SOL-FG-03) | 🤝 Foundation Continuity Protocol 72-hour dry-run executed with zero customer-visible incident (SOL-FP-07) | 🤝 NCC pentest delivered; remediations shipped within engagement window |
| **W14** | Sep 01 | **Q1 QUARTERLY ANCHOR**: `win-conditions.json` boolean state declared and anchored as receipt | 🤝 Technical Steering Committee charter ratified; independent veto seat seated | 🤝 Cure53 verifier audit published |
| **W15** | Sep 08 | 🤝 Azure Marketplace listing live | 🌐 Qatalyst engagement signed; Series A teaser drafted; banker-led process begins (SOL-FIN-03) | 🤝 Pilot retrospectives published as receipts; first design-partner Tier-2 conversion conversation opens (SOL-COMM-04) |
| **W16** | Sep 15 | ⭕ IETF WG adoption sponsor secured for `draft-01` — if NO, downgrade to Independent Submission; pursue CEN-CENELEC JTC 21 NWIP as primary path (SOL-REG-04) | 🌐 Big-4 Working Group convened; at least 2 of 4 partners attending; workpaper spec v0.1 published as IETF I-D companion (SOL-COMM-01) | 🤝 GCP Marketplace listing submitted; Vertex AI connector at 1.0 |
| **W17** | Sep 22 | 🤝 LPR v1.2 spec frozen; profile system implemented; v1.1 readers must continue to verify (CI enforced) (SOL-TECH-05) | 🤝 US operator (us-east-1) at 99.9% for 30 consecutive days; UK provisioned but cold | 🤝 Compliance Stamp PDF generator + Verified-by-Article-50 badge widget GA (SOL-DIST-05) |
| **W18** | Sep 29 | ⭕ **TRANCHE 2 MILESTONE CHECK Sep 30**: 2 FSI DPs signed + ToB memo published + IETF adoption OR CEN NWIP accepted; if NO, tranche price re-anchors (SOL-FIN-02) | 🌐 Dutch Stichting registered with KvK; ING bank account open; EU contractual counterparty LIVE (SOL-FG-04) | 🤝 DORA Annex v0.1 published; MiFID II annex outline (SOL-DIST-06) |
| **W19** | Oct 06 | 🤝 LPR v1.2 deployed to production; first profile published for Code-of-Practice partial adaptation | 🤝 Multi-region active-active EU + US + UK at 99.9% target | 🌐 Big-4 first co-authored advisory cites LP-Conformant (SOL-COMM-01) |
| **W20** | Oct 13 | ⭕ SOC 2 Type 1 attestation received (Oct 15 circuit-breaker — if NO, pause new pilot signings; redirect 30% eng capacity to remediation) | 🤝 LPR v1.2.1 patch shipped with first Code-of-Practice adaptations as Code finalizes | 🤝 PQ migration v0.1 design doc published at spec.ledgerproofhq.io/pq-roadmap |
| **W21** | Oct 20 | 🌐 First Tier-1 design-partner Tier-2 conversion ($120K ACV); revenue line item appears in `lpr-status.json` | 🤝 SBOM published for every SDK release; SLSA L3 enforced in CI | 🤝 Cross-protocol bridges live (C2PA + SCITT); registry GraphQL API DEFERRED per kill list |
| **W22** | Oct 27 | ⭕ AWS Marketplace live + at least one Tier-2 design-partner conversion via auto-trigger — if NO, replace Cloud Alliances Manager search firm; collapse to AWS-only | 🤝 Two regulator/standards engagements on record (CEN-CENELEC JTC 21 contribution; AI Office briefing) (SOL-REG-04) | 🌐 Watchlist passes 15K verified subscribers; Common Room → Salesforce identity resolution wired |
| **W23** | Nov 03 | 🌐 **IETF 121 Dublin Nov 2-7**: Veronica + spec lead present; LPR draft-02 prep | 🤝 IETF WG adoption confirmed OR CEN-CENELEC NWIP accepted | 🤝 Type 2 SOC 2 audit window opens; ISO 27001 audit kickoff |
| **W24** | Nov 10 | 🤝 Qatalyst Series A teaser distributed; investor diligence calls opening (SOL-FIN-03) | 🤝 Pentest #2 scope finalized | 🌐 Founder essay #4 in Watchlist newsletter; FT op-ed #2 |
| **W25** | Nov 17 | ⭕ **Signed Series A LOI from Tier-1 fund OR runway >9 months as of Jan 1** (Nov 15 circuit-breaker — if NO, begin bridge round conversations now, not December) | 🤝 EU + US + UK operators sustained 99.9% for 90 consecutive days | 🤝 Cure53 audit + Latacora + ToB attestations all live at security.ledgerproofhq.io |
| **W26** | Nov 24 | 🌐 Three+ Series A term sheets received; selection process underway | 🤝 LPR v2.0 PQ design RFC circulated to IETF WG | 🌐 Big-4 LP-Conformant program announcement |
| **W27** | Dec 01 | **Q2 QUARTERLY ANCHOR**: `win-conditions.json` boolean state declared and anchored | ⭕ ≥3 Series A term sheets received via Qatalyst process (Dec 1 circuit-breaker — if <2, draw Hercules $8M, extend runway to Q3 2027) | 🌐 Foundation transparency report Q4 2026 published and anchored |
| **W28** | Dec 08 | **SERIES A OPEN Dec 7**: Selected lead; term sheet signed; closing process begins | 🌐 Asia expansion brief signed off; Singapore non-profit registration Q1 2027 confirmed | 🌐 Plan reads from `lpr-status.json` + `win-conditions.json`; PLAN.md V1 fully retired |

---

## Inter-week milestones (off-Tuesday-grid)

### Foundation Root-Key Ceremony — Friday Aug 15, 2026

Falls between W11 (Aug 11) and W12 (Aug 18) — does not fit the Tuesday-grid above. Tracked here as a discrete milestone.

- **Objective**: Establish un-compromised genesis state for the Foundation key hierarchy (2-of-3 multisig anchor key + Foundation root signing key).
- **Allocation**: $15K G&A (HSMs, independent legal witnesses, physical secure facility, ceremony video documentation, post-ceremony hash anchored to Bitcoin as a Foundation receipt).
- **Dependency (UPSTREAM)**: Threat-model briefing §11 ceremony recommendations incorporated into the design by Aug 1 (target). Senior Security Advisor sign-off Aug 8.
- **Dependency (DOWNSTREAM)**: Combined NCC + Trail of Bits + Cure53 audit memo Aug 31 references the ceremony and includes the ceremony hash as a verifiable receipt. Sequencing: Aug 15 ceremony → Aug 31 memo. Not reversed.
- **Owner**: Veronica + Foundation Executive Director (post Aug 1 start) + Senior Security Advisor + independent observers (target: 2 of 3 from {Mishi Choudhary, Allison Randal, Lokke Moerel}).
- **Circuit breaker**: If ceremony slips past Aug 22, the Aug 31 combined memo also slips; Big-4 + Series A diligence compounds the delay. Replan within 48 hours of any slip.
- **Reference**: See [`14-seed-close-pack/04-atomic-explosion-master-plan.md`](14-seed-close-pack/04-atomic-explosion-master-plan.md) §5 Phase D.

---

## How to use this file

1. **Every Tuesday morning,** read the row for that week. If three deliverables are listed, those are the three commitments.
2. **Every Friday at 17:00 CET,** review the row's ⭕ items. Trip a circuit breaker = follow the if-then in [Code Plan V2 § Engineering Circuit Breakers](09-code-plan/00-MASTER-CODE-PLAN-V2.md#engineering-circuit-breakers).
3. **Every deliverable cites a SOL-* solution ID** from the [10X playbook](12-premortem/04-10X-PLAYBOOK-MAY31.md). When you need to know why something is on the list, read its solution.
4. **Status updates land in [`lpr-status.json`](lpr-status.json) weekly.** That file is the runtime truth. This file is the plan.
5. **Boolean win conditions update quarterly** in [`win-conditions.json`](win-conditions.json). The boolean state is anchored as a Bitcoin receipt at each anchor cadence.

## What's NOT on this list

- Cold outbound to 17 EU GCs — replaced by Article 50 Watchlist + Big-4 Working Group referral flow (per playbook kill list).
- Go SDK 1.0, Java SDK 1.0, .NET SDK, Registry GraphQL — all deferred to Q1+ 2027 per Code Plan V2 kill list.
- LedgerProof Civic / election-defense / Sandwich Video clip library / Frankfurt WeWork — all cut per 10X playbook kill list.

## Hardness key

- **⚡ single-founder action** — Veronica must do this herself; cannot delegate.
- **🤝 contractor/counsel dependent** — requires a paid third party already engaged.
- **🌐 counterparty dependent** — requires a regulator, customer, or investor to take action we cannot force.
- **⭕ circuit-breaker observable** — Friday 17:00 CET review item; tripping triggers a documented if-then.

## Editing this file

Direct edits welcome — but every change to a deliverable must:
1. Cite the SOL-* that justifies it
2. Update `lpr-status.json` if the deliverable is in flight
3. Update `win-conditions.json` if it changes a quarterly anchor commitment
4. Get cross-referenced in the next Friday circuit-breaker review

If a row falls behind by more than one week, it surfaces at the Friday review with an honest "why" — not a re-slide.
