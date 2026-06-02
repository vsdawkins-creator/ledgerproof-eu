# THE ATOMIC EXPLOSION — Master Execution Plan

**Author**: Veronica S. Dawkins, Founder — LedgerProof
**Drafted**: Monday June 1, 2026 — 19:40 PDT (T-0)
**Scope**: T-0 (now) through T+182 (Sunday Nov 29, 2026)
**Status**: Operating document. Every other artifact in the repo cross-references this.

> **One-line thesis**: The Foundation publishes a credibly-audited open protocol; Inc. monetizes hosted services around it; one anchor enterprise deal funds the protocol-distribution sprint that delivers regulatory standing in time for Article 50 enforcement.

---

## 0. State of Play (T-0)

**What we have (assets):**
- LPR v1.1 spec public on IETF Datatracker (`draft-dawkins-scitt-ai-article50-00`)
- Python SDK 1.1.1rc0 + TypeScript SDK 1.1.1-pre.0 + Rust quantum-edge-2
- Cross-language conformance CI (PR #3 path)
- Verifier portal live (slug routing + brand alignment + LPR-ERRATA-001 surfaced)
- Commercial site (5 pages) live, vercel.json redirect in place
- 24-month operating model (`01-cfo-24-month-model.md`) — Y1 BASE $9.4M booked / $6.7M run-rate ARR
- NCC Group / Trail of Bits / Cure53 threat-model briefing (`02-threat-model-briefing.md`)
- 14-day handoff integration plan (`03-handoff-integration.md`)
- 11 hiring-persona skills in `~/.claude/skills/`
- Real-10 contact map (post reality-check): Toffaletti, Bezombes, Hallensleben, Gross, Gómez, Hauser, O, Domínguez Álvarez, Ammanath, Birkholz
- Repo hygiene clean (PAT scrubbed, gitignore extended, gh installed)
- Foundation/Inc. dual-entity structure designed; Adler & Colvin retainer pending sign

**What we lack:**
- Foundation 1023 not filed; fiscal-sponsor MOU unsigned
- Cooley engagement letter signed but Founding Member / Strategic Beta Partner templates not drafted
- Zero signed customer contracts (Founding Member pipeline = 0)
- Zero signed seed papers (lead co-leads conversations active but unpapered)
- Zero hires (Veronica is sole operator; CoS, senior protocol engineer, Foundation ED, DevRel all open)
- No DIN membership; no JTC 21 standing
- No audit engagement letter signed
- Kong plugin, LangChain integration, Envoy filter: not built
- US/EU counterweight anchor (to balance Tencent/Riot press exposure): not identified
- Cash position: pre-seed — every external commitment is conditional on Jun 25 close

**The eight load-bearing corrections (from the adversarial pass, must hold everywhere):**

| # | Correction | Where it bites |
|---|------------|----------------|
| C1 | Article 95 confers reputational signal, NOT presumption of conformity. Only Article 40 hENs do. | Regulatory briefs, press kit, investor pitch |
| C2 | Kong sits on outbound enterprise APIs (publish-side), NOT inbound third-party data inspection. Inbound surface = Snowflake UDFs / Databricks / Airflow / Prefect. | Spec pack, plugin roadmap, customer demos |
| C3 | LangChain Inc. and LlamaIndex Inc. are companies. We approach them as integration partners; we do NOT recruit committers via fractional equity advisor agreements (employer conflict + off-market equity). | Distribution plan, advisor cap-table |
| C4 | Verification must be local (Merkle proof + Ed25519 sig + Bitcoin anchor — offline). LP verification nodes are convenience, not requirement. | Plugin specs, SDK docs, press kit |
| C5 | Enterprise compliance dashboard = their SIEM (Splunk/Datadog/ServiceNow/Vanta/Drata). `/v/{slug}` is OUR public portal. Two surfaces, two integrations. | Distribution plan, demo flow |
| C6 | Kong `body_filter` kills streaming AI latency. Stream-aware signing required. HSM signing latency requires Merkle-batch design (N requests → 1 signature). | Engineering spec |
| C7 | LangChain has migrated to LangGraph for production agents. Target BOTH callback handlers (legacy) AND LangGraph node middleware (current). | LangChain integration spec |
| C8 | Tencent parent ownership of Riot Games creates EU-press vulnerability. Need US or EU counterweight anchor in the SAME window. | Commercial plan, PR plan |

---

## 1. The Critical Path

```
Today (Jun 1)
    │
    ├─ Jun 2  ─ NCC/ToB audit emails sent + DIN application briefing
    ├─ Jun 3  ─ Operating model out to TVP/Stillmark + threat-model out to Cure53
    ├─ Jun 4  ─ Fulgur/Beeston brief + summary memo
    ├─ Jun 5  ─ Adler & Colvin engagement letter signed + Veronica POA notarized
    ├─ Jun 8  ─ Hercules Capital walkthrough + senior protocol engineer JD live
    ├─ Jun 11 ─ Hallensleben + Toffaletti warm-intro requests + threat-model exec summary to co-leads
    ├─ Jun 15 ─ Inc.→Foundation IP license executed at USPTO + DIN application filed
    ├─ Jun 18 ─ Riot Games Strategic Beta Partner SOW redline closed (target)
    ├─ Jun 25 ─ SEED CLOSE: $10M @ $45M post-money + $5M tranche conditional + Hercules $8M facility signed
    │
    ├─ Jul 3  ─ FT op-ed lands (3 days pre-launch)
    ├─ Jul 6  ─ PUBLIC LAUNCH: 5-pub embargoed coverage breaks 06:00 CET; Foundation 1023 filed
    │
    ├─ Aug 2  ─ EU AI ACT ARTICLE 50 ENFORCEMENT BEGINS
    ├─ Aug 15 ─ Foundation root-key ceremony complete
    ├─ Aug 16 ─ Circuit Breaker 6: if zero visible enforcement, second-narrative track activates
    ├─ Aug 30 ─ Foundation board seated (Choudhary chair, Randal audit, Moerel compliance)
    ├─ Aug 31 ─ NCC Group / Trail of Bits audit memo publication (full v1.1 sign-off)
    │
    ├─ Sep 30 ─ Tranche-trigger evaluation: 2 FSI design partners + audit memo + IETF or CEN advance → $5M tranche releases
    ├─ Oct ?   ─ IRS determination letter target (expedited handling)
    ├─ Nov 29 ─ Series A teaser deck ready; Qatalyst engagement letter; H1 2027 Series A window opens
    └─ Dec ?   ─ Y1 ARR booked target: $9.4M (BASE) / $14M (STRETCH)
```

**The four kill-switches on this path** — if any trips, we replan within 48 hours:

1. **No audit engagement letter by Jun 8** → Aug 31 audit memo slips → Big-4 + standards + Series A all push right one quarter.
2. **Tencent/Riot press leaks before US/EU counterweight anchor confirms** → Brussels narrative collapses → 500K awareness path needs full reframe.
3. **<$8M raised at Jun 25 close** → cannot fund senior protocol engineer + Brussels counsel + audit simultaneously → choose two of three.
4. **No DIN application filed by Jun 21** → DIN membership confirmation slips past Aug 2 → "DIN member, JTC 21 active" line drops from press kit.

---

## 2. Phase A — Seed Close Sprint (T+0 → T+25 days, Jun 1 → Jun 25)

**One-line objective**: Close $10M @ $45M post + $5M tranche-conditional + Hercules $8M facility, all by EOD Jun 25.

### A.1 — Commercial Track

| Day | Action | Owner | Artifact |
|-----|--------|-------|----------|
| Jun 2 | Founding Member Agreement v0.1 draft request to Cooley (4-page constraint) | Veronica → Cooley | `13-monday-sprint/founding-member-agreement-v01.md` |
| Jun 2 | Strategic Beta Partner Agreement v0.1 draft request to Cooley (5-6 page) | Veronica → Cooley | `13-monday-sprint/strategic-beta-partner-v01.md` |
| Jun 4 | Riot Games introduction via Frank — Strategic Beta Partner deal sized at $1M with $1M discount (effective $2M list) | Veronica + Frank | Email thread + Zoom recording |
| Jun 5 | **US/EU counterweight anchor identification sprint** (C8 mitigation): target list of 5 — candidates include Stripe, Adyen, Klarna, DZ Bank, Allianz, BBVA, ING, Wise | Veronica + Brunswick (or eq.) prospect | `14-seed-close-pack/counterweight-anchor-targets.md` |
| Jun 8 | 3 of 5 anchor targets contacted via warm intro | Veronica | Outbound log in `lpr-status.json` |
| Jun 10 | Founding Member outbound wave 1: 30 targets (FSI + AI vendors) | Veronica + outbound contractor (fractional) | Attio + send log |
| Jun 15 | First Founding Member LOI signed (target — not blocking seed) | Veronica | Signed PDF |
| Jun 18 | Riot Strategic Beta Partner SOW redline closed | Veronica + Cooley + Riot Legal | Signed SOW |
| Jun 22 | Counterweight anchor LOI signed (target) | Veronica | Signed PDF |
| Jun 25 | Seed close confirmation; all wire instructions executed | Veronica + Cooley | Cap table v1.0 |

### A.2 — Regulatory / Standards Track

| Day | Action | Owner | Artifact |
|-----|--------|-------|----------|
| Jun 2 | NCC Group + Trail of Bits engagement emails (threat-model briefing attached) | Veronica | `13-monday-sprint/ncc-engagement-email.md` |
| Jun 2 | **DIN SME Membership Application Briefing** drafted | Veronica + EU regulatory strategist persona | `14-seed-close-pack/05-din-membership-application.md` |
| Jun 3 | Cure53 engagement email (verifier-specific scope) | Veronica | `14-seed-close-pack/cure53-engagement-email.md` |
| Jun 5 | Audit engagement letters returned (target — kill-switch 1) | NCC + ToB → Veronica | Signed engagement letters |
| Jun 11 | Hallensleben warm-intro request via Birkholz (IETF SCITT WG co-chair) | Veronica | Email + log entry |
| Jun 11 | Toffaletti warm-intro request via DIGITAL SME Alliance contact | Veronica | Email + log entry |
| Jun 15 | **DIN SME membership application filed** (kill-switch 4) | Veronica | DIN application receipt |
| Jun 18 | Foundation submission to EU AI Office Code of Practice GPAI transparency chapter consultation drafted | Veronica + EU regulatory strategist persona | `14-seed-close-pack/06-coc-gpai-submission-v01.md` |
| Jun 22 | CoC GPAI submission filed on Foundation letterhead | Veronica | Foundation receipt anchored |
| Jun 24 | JTC 21 NWIP outline draft started | Veronica + EU regulatory strategist persona | `14-seed-close-pack/07-jtc21-nwip-outline.md` |

### A.3 — Engineering Track

| Day | Action | Owner | Artifact |
|-----|--------|-------|----------|
| Jun 2 | Open PRs (verifier #1, site #1, platform #3, quantum-edge-2 #2) merge decisions + roll-forward | Veronica | Merge log |
| Jun 4 | **`15-protocol-distribution/` directory created with adversarially-corrected specs**: | Veronica | New directory |
|       | • `kong-plugin-spec.md` — OUTBOUND API publication, stream-aware signing, Merkle-batch HSM (C2, C6) | | |
|       | • `snowflake-udf-spec.md` — INBOUND third-party data verification surface (C2) | | |
|       | • `databricks-notebook-spec.md` — INBOUND batch-data verification surface (C2) | | |
|       | • `langchain-langgraph-middleware-spec.md` — LangGraph + callbacks dual target (C7) | | |
|       | • `envoy-wasm-filter-spec.md` — service-mesh attestation | | |
|       | • `siem-connector-spec.md` — Splunk/Datadog/Vanta/Drata receipt push (C5) | | |
| Jun 8 | Senior protocol engineer JD live (Greenhouse / public posting) | Veronica | JD + posting URL |
| Jun 10 | LangChain Inc. + LlamaIndex Inc. partnership outreach (C3 — Harrison Chase / Jerry Liu) | Veronica | Outreach log |
| Jun 12 | Verifier portal v1.1 (per-receipt SIEM webhook export endpoint) | Solo or contractor | PR + deploy |
| Jun 18 | Senior protocol engineer first-round interviews (3 candidates) | Veronica + technical advisor | Interview notes |
| Jun 22 | Top candidate offer extended | Veronica | Offer letter |

### A.4 — Legal / Finance Track

| Day | Action | Owner | Artifact |
|-----|--------|-------|----------|
| Jun 3 | Adler & Colvin engagement letter signed | Veronica | Signed engagement letter |
| Jun 5 | Veronica durable POA notarized | Veronica + notary | POA |
| Jun 5 | Founder-SPOF mitigation: attorney-as-incorporator + 2 backup incorporator consent letters | Adler & Colvin | Consent letters |
| Jun 8 | Hercules Capital walkthrough (operating model Y1 P&L + cohort waterfall + cash trajectory only) | Veronica + CFO advisor | Zoom recording |
| Jun 9 | Cooley cap-table excerpt review for Series A diligence prep | Cooley | Cap table v0.9 |
| Jun 10 | G&A allocation tab → Adler & Colvin | Veronica | Updated `01-cfo-24-month-model.md` |
| Jun 14 | Day-1 perpetual royalty-free IP license Inc.→Foundation drafted | Adler & Colvin + Cooley | Draft license |
| Jun 15 | IP license executed at USPTO | Veronica + USPTO filing | Filed assignment |
| Jun 20 | Fiscal sponsorship MOU with New Venture Fund drafted | Adler & Colvin | Draft MOU |
| Jun 25 | Hercules $8M facility documentation signed (undrawn) | Cooley + Hercules legal | Signed facility docs |
| Jun 25 | Two-stage SAFE executed: $10M @ $45M post + $5M tranche-conditional clause | Cooley + co-leads | Signed SAFEs |
| Jun 25 | Cap table v1.0 published to co-leads | Cooley | Cap table v1.0 |

### A.5 — PR / Comms Track

| Day | Action | Owner | Artifact |
|-----|--------|-------|----------|
| Jun 3 | Brunswick Group EU (or Edelman / FleishmanHillard / Hill+Knowlton / APCO EU) pitch meeting requests | Veronica + PR strategist persona | Meeting requests |
| Jun 10 | PR firm selected; 4-month retainer signed (€18-25K/mo) | Veronica | Signed retainer |
| Jun 12 | Press calendar through Q4 2026 drafted | PR firm | `14-seed-close-pack/press-calendar-q4-2026.md` |
| Jun 17 | Founder media training session 1 (FT Brussels prep) | PR firm + Veronica | Training notes |
| Jun 22 | FT op-ed draft v1 (Veronica byline, possibly Adam Back co-byline if Bitcoin-credibility angle) | PR firm + Veronica | `14-seed-close-pack/ft-oped-draft-v1.md` |
| Jun 24 | Embargoed launch briefings scheduled: FT Brussels, Politico EU, Handelsblatt, Le Monde, Euractiv | PR firm | Calendar entries |

### A.6 — Hiring Track

Hiring sequence is sequenced to cash availability. Pre-seed close (T+0 → T+25): only outreach + interview pipeline. Post-close (T+25 onwards): offers extended.

| Role | T+0→T+25 status | Target start |
|------|-----------------|--------------|
| Chief of Staff | JD posted Jun 8; first-round interviews Jun 15-22 | Jul 6 |
| Senior Protocol Engineer | JD posted Jun 8; interviews Jun 18-22; offer Jun 22 | Jul 13 |
| Foundation Executive Director | Outreach Jun 10-22 (advisor-network only) | Aug 1 |
| EU Enterprise AE | JD draft only | Sep 1 |
| Big-4 Partnerships Lead | JD draft only | Sep 15 |
| DevRel / Developer Advocate | JD draft only | Aug 15 |

### A.7 — Security / Audit Track

| Day | Action | Owner |
|-----|--------|-------|
| Jun 2 | NCC Group + Trail of Bits engagement emails sent (threat-model briefing attached) | Veronica |
| Jun 3 | Cure53 engagement email sent (verifier-specific scope $60-90K) | Veronica |
| Jun 5 | Audit engagement letters returned (kill-switch 1 trigger if not) | NCC + ToB → Veronica |
| Jun 8 | Audit kickoff calls held | Veronica + auditors |
| Jun 8 → Jul 29 | Audit fieldwork (canonicalization, slug-router, pre-v1.0 entry handling, replay, Merkle, Ed25519 strict mode, @noble supply chain, GDPR Article 17 soft delete, Bitcoin reorg, OP_RETURN payload size) | Auditors |
| Jun 12 | LPR-ERRATA-001 root-cause briefing call with auditors | Veronica + auditors |

---

## 3. Phase B — Launch Window (T+25 → T+35, Jun 25 → Jul 6)

**One-line objective**: 5-publication embargoed coverage breaks 06:00 CET Jul 6; Foundation 1023 filed same day.

| Day | Action | Owner |
|-----|--------|-------|
| Jun 26 | Cash wires landed; Hercules facility executed undrawn | Veronica + ops |
| Jun 27 | Adler & Colvin Form 1023 long-form 90% complete | Adler & Colvin |
| Jun 29 | Hire offers extended: CoS + Senior Protocol Engineer | Veronica |
| Jun 30 | Press kit finalized; embargoed releases distributed (T-6) | PR firm |
| Jul 1 | FT op-ed copy-edit final; submission to FT Brussels | PR firm |
| Jul 3 | **FT op-ed lands** (T-3 pre-launch) | FT Brussels |
| Jul 6 — 06:00 CET | **PUBLIC LAUNCH**: 5-publication coverage breaks | PR firm |
| Jul 6 | Form 1023 long-form filed with expedited handling request | Adler & Colvin |
| Jul 6 | Foundation declaration entry issued via publisher portal | Veronica (only she has credentials) |
| Jul 6 | Founding Member program publicly opens | Veronica + AE pipeline |

---

## 4. Phase C — Pre-Enforcement Sprint (T+35 → T+62, Jul 6 → Aug 2)

**One-line objective**: Reach 15 signed Founding Members + Kong plugin v0.1 shipped + LangChain integration v0.1 shipped + Foundation board chair confirmed, before Article 50 enforcement begins Aug 2.

| Workstream | Target by Aug 2 |
|------------|-----------------|
| Commercial | 15 signed Founding Members ($600K-1.5M Y1 booked); Riot Strategic Beta Partner deployed in production at one Riot subsidiary; counterweight anchor LOI converted to signed contract |
| Standards | DIN membership confirmed; JTC 21 NWIP outline submitted via DIN delegation; Hallensleben + Toffaletti one-on-ones held |
| Engineering | Kong plugin v0.1 open-sourced (Apache 2.0); LangChain integration v0.1 PR'd to LangChain Inc. partnership; Snowflake UDF spec implemented as reference |
| Regulatory | 3 of 5 national competent authority informational briefings held (BaFin, CNIL, AGCOM as primary; BfDI + AP as secondary) |
| Legal | Foundation board chair confirmed (Mishi Choudhary target); Foundation board minutes published as receipts; Foundation Council Charter ratified |
| PR | Politico EU AI policy desk weekly mention cadence established; Handelsblatt + Le Monde one tier-2 piece each |
| Hiring | CoS + Senior Protocol Engineer onboarded; Foundation ED offer extended |
| Security | Audit fieldwork complete; draft audit memo distributed to auditors for finalization |

---

## 5. Phase D — Enforcement + Audit Memo (T+62 → T+91, Aug 2 → Aug 31)

**One-line objective**: Survive enforcement-week press cycle; publish audit memo Aug 31; Foundation board seated Aug 30.

| Day | Action |
|-----|--------|
| Aug 2 | Article 50 enforcement begins. Politico EU AI Daily watchlist activated. |
| Aug 2-9 | Enforcement-week press cycle: founder-on-call to Brunswick; reactive comments only with PR firm prep. |
| Aug 15 | Foundation root-key ceremony (San Francisco or Zurich); independent observers; published as receipt. |
| Aug 16 | **Circuit Breaker 6 evaluation**: if zero visible enforcement action by Aug 16, second-narrative track activates. Pre-drafted op-ed published. |
| Aug 22 | Article 95 voluntary code of conduct outline filed with EU AI Office (reputational signal — NOT presumption of conformity per C1). |
| Aug 30 | Foundation board seated: Choudhary (chair), Randal (audit), Moerel (compliance). |
| Aug 31 | **Audit memo publication**: NCC Group + Trail of Bits combined audit memo published on Foundation site; SHA-256 anchored. |

---

## 6. Phase E — Series A Setup (T+91 → T+182, Sep → Nov)

**One-line objective**: Tranche-trigger releases Sep 30; Y1 ARR trajectory on track for $9.4M booked / $6.7M recognized; Series A teaser deck + Qatalyst engagement letter ready by Nov 29.

| Phase | Action |
|-------|--------|
| Sep | Tranche-trigger evaluation Sep 30: (a) 2 FSI design partners signed, (b) audit memo published Aug 31, (c) IETF SCITT WG adoption OR CEN NWIP advance — if all three, $5M tranche releases. |
| Sep | IRS Form 1023 examination dialog opens (expedited handling). |
| Sep | EU Enterprise AE + DevRel onboarded. |
| Oct | IRS determination letter target. |
| Oct | Series A diligence pack legal documents 100% prepped (Aug 15 baseline already met). |
| Oct | Foundation Q3 990 prep (Adler & Colvin). |
| Nov | Series A teaser deck v1.0 (15-18 slides, reality-checked numbers — NOT $86M Y1 nor $65B Y5). |
| Nov 29 | Qatalyst (or alternate banker) engagement letter signed. |
| Dec | Y1 ARR review: BASE $9.4M booked / STRETCH $14M booked. Series A window decision. |

---

## 7. Seven Workstreams (perpendicular cuts through all phases)

Phases are time-axis. Workstreams are domain-axis. Every artifact in the repo belongs to one workstream.

| # | Workstream | Lead | Cadence |
|---|-----------|------|---------|
| W1 | Commercial (customers + revenue) | Veronica → EU AE (Sep) | Daily standup post-CoS-hire |
| W2 | Regulatory / Standards | Veronica + fractional EU regulatory affairs strategist | Weekly tracker update |
| W3 | Engineering / Protocol | Veronica + Senior Protocol Engineer (Jul 13) | Daily; weekly demo Friday |
| W4 | Legal / Finance | Cooley + Adler & Colvin + fractional CFO | Weekly Tuesday sync |
| W5 | PR / Comms | Brunswick (or eq.) + Veronica | Weekly Wednesday sync |
| W6 | Hiring | Veronica + CoS (Jul 6) | Weekly Monday pipeline review |
| W7 | Security / Audit | Veronica + NCC + ToB + Cure53 + Senior Security Advisor | Weekly Thursday sync |

---

## 8. Circuit Breakers — Kill Conditions and Branches

| CB | Trigger | Window | Branch |
|----|---------|--------|--------|
| CB1 | No NCC + ToB engagement letter by Jun 8 | T+0 → T+8 | Switch to Cure53-only + extend timeline +30 days; tranche-trigger Sep 30 becomes conditional on Cure53 memo only. |
| CB2 | <$8M raised at Jun 25 close | T+25 | Drop senior protocol engineer hire OR Brussels counsel OR audit (must drop one). Default drop: Brussels counsel — keep audit + eng. |
| CB3 | Riot/Tencent press leak before counterweight anchor confirms | Any | Brunswick crisis response within 4 hours; Foundation independence FAQ deployed; founder media silence until counterweight confirms. |
| CB4 | DIN application not filed by Jun 21 | T+21 | Switch primary standards path to AFNOR (France) or NEN (Netherlands) — both have member-org NWIP authority. Lose 4 weeks. |
| CB5 | Kong plugin v0.1 not shipped by Aug 2 | T+62 | Ship Snowflake UDF + LangChain integration only; defer Kong to Q4; reframe enterprise narrative around data-plane (not API-plane). |
| CB6 | Zero visible Article 50 enforcement by Aug 16 | T+76 | Activate second-narrative track: pre-drafted op-ed published; commercial narrative shifts to "voluntary adoption now reduces future enforcement exposure". |
| CB7 | LangChain Inc. partnership refused | Any | Ship as community integration outside main; pursue LlamaIndex Inc. partnership as primary; reset adoption-curve assumption -6 months. |
| CB8 | IRS Form 1023 returned with substantive deficiency | Sep-Oct | Adler & Colvin response within 14 days; fiscal sponsorship via New Venture Fund continues as bridge; charitable contributions flow uninterrupted. |

---

## 9. The Money Flow

### Cash IN

| Source | Amount | Timing | Conditions |
|--------|--------|--------|------------|
| Seed SAFE Tranche 1 | $10M | Jun 25 | Co-leads commit at $45M post-money |
| Hercules facility | $8M undrawn (optionality) | Jun 25 | Commitment fee 50-100 bps on undrawn; no covenants that force draw |
| Riot Strategic Beta Partner | $1M | Jul 1 (target) | Discount $1M off $2M list — accounted as $1M cash + $1M deferred discount per ASC 606 |
| Counterweight anchor | $300-500K | Aug 1-15 (target) | Founding Member tier or Anchor tier |
| Founding Member program | $1-3M booked Y1 | Rolling Jul 6 onwards | $50-150K standard tier, $250-500K anchor tier |
| Seed SAFE Tranche 2 | $5M | Sep 30 | 2 FSI design partners + audit memo + IETF/CEN advance |

### Cash OUT (illustrative monthly, after seed close)

| Category | Monthly burn (Jul-Sep) | Annual basis |
|----------|------------------------|--------------|
| Founder + CoS + Sr Protocol Engineer | $80K | $960K |
| Foundation ED + EU AE + DevRel (Aug-Sep starts) | $50K | $600K |
| Cooley + Adler & Colvin + Brussels counsel | $40K | $480K |
| Brunswick (or eq.) PR retainer | $22K | $264K |
| NCC + ToB + Cure53 audit | $150-200K total Jun-Aug | one-time |
| Audit memo finalization Q4 | $25K | one-time |
| DIN + AFNOR + BSI fees + JTC 21 participation | $4K | $48K |
| Cloud / infra / SaaS | $8K | $96K |
| Foundation root key ceremony Aug 15 | $15K | one-time |
| Insurance (D&O, E&O, key person) | $10K | $120K |
| Travel + Brussels + audit + standards bodies | $15K | $180K |
| Contingency 15% | $30K | $360K |
| **Total monthly** | **~$259K + one-times** | **~$3.1M annual** |

### Runway sanity check

$10M Tranche 1 - ~$200K closing costs - ~$150K Q3 one-times = ~$9.65M deployable.
At ~$259K/mo, runway = ~37 months *before revenue*.
With Riot $1M Jul + counterweight $400K Aug + Founding Member $80K/mo from Aug onwards, runway extends to ~42 months and trends to EBITDA breakeven Q1 2028 per the operating model BASE case.

---

## 10. Hire Sequence

Sequenced strictly to (a) cash availability and (b) which gate they unlock.

| # | Role | Posting | Offer | Start | Loaded comp | Unlocks |
|---|------|---------|-------|-------|-------------|---------|
| 1 | Chief of Staff | Jun 8 | Jun 29 | Jul 6 | $250K | Founder bandwidth — every other hire flows through CoS pipeline |
| 2 | Senior Protocol Engineer | Jun 8 | Jun 22 | Jul 13 | $300K | Kong/LangChain/Snowflake plugins ship Q3 |
| 3 | DevRel / Developer Advocate | Jul 1 | Jul 25 | Aug 15 | $220K | OSS adoption curve; LangChain Inc. partnership management |
| 4 | Foundation Executive Director | Jul 1 (advisor network) | Jul 20 | Aug 1 | $280K (Foundation entity) | Regulator cadence; Foundation board recruitment; 1023 examination response |
| 5 | EU Enterprise AE | Aug 15 | Aug 30 | Sep 1 | $300K (50% commission) | EU enterprise pipeline; Founding Member conversion |
| 6 | Big-4 Partnerships Lead | Sep 1 | Sep 22 | Sep 15 | $320K | KPMG/PwC/EY/Deloitte working group seat conversion |
| 7 | Senior Security Advisor | Fractional Jun 5 | Jun 12 | Jun 15 | $20K/mo fractional | Audit oversight; LPR-ERRATA-NNN process |
| 8 | Fractional CFO | Jun 5 | Jun 8 | Jun 10 | $15-20K/mo | Operating model maintenance; Hercules walkthrough; Series A diligence prep |
| 9 | Senior 501(c)(3) Foundation Counsel | Already in pipeline (Adler & Colvin) | Jun 3 | Jun 3 | $35-45K retainer + hourly | Form 1023 + fiscal sponsor + IP license |
| 10 | Senior Commercial Counsel | Already in pipeline (Cooley — Adam Ross / Jodie Bourdet) | Jun 3 | Active | Hourly | SAFE + Hercules + Founding Member + Strategic Beta Partner |
| 11 | EU Regulatory Affairs Strategist | Fractional Jul 1 | Jul 8 | Jul 15 | €18-25K/mo | DG-CNECT cadence; CoC submissions; CNIL Compatibility Memo |
| 12 | EU Regulatory PR Strategist (Brunswick or eq.) | Jun 3 outreach | Jun 10 | Active Jun 15 | €18-25K/mo | FT op-ed; embargoed launch coordination; crisis response |

By Sep 1: 6 full-time, 4 fractional, 2 retained. Total loaded ~$2.0M/year salary + ~$80K/mo fractional + project fees.

---

## 11. The Tonight Action List (now → 23:59 PDT)

1. **Commit this plan** (`14-seed-close-pack/04-atomic-explosion-master-plan.md`) + push to `origin/main`.
2. **Open 3 draft email files** for tomorrow 08:00 PDT send:
   - `13-monday-sprint/email-ncc-engagement-jun02.md`
   - `13-monday-sprint/email-tob-engagement-jun02.md`
   - `13-monday-sprint/email-cure53-engagement-jun03.md`
3. **Update `lpr-status.json` + `win-conditions.json`** with the eight load-bearing corrections, the four kill-switches, and the seven workstreams.
4. **Update `CRIT_PATH.md`** to add the W11 (Aug 15) Foundation root-key ceremony as a tracked milestone with $15K G&A line.
5. **Update `PLAN.md`** to mark Phase A → E sequence and reference this master plan as the operating document.
6. **Sleep by 22:00.** Tuesday morning matters more than tonight's last hour.

## 12. The Tomorrow Morning Action List (Tue Jun 2, 08:00 → 12:00 PDT)

| Time | Action |
|------|--------|
| 08:00 | Coffee. Open `04-atomic-explosion-master-plan.md`. Confirm nothing changed overnight. |
| 08:15 | Send NCC Group engagement email + threat-model briefing attached |
| 08:25 | Send Trail of Bits engagement email + threat-model briefing attached |
| 08:35 | Send Cure53 engagement email (verifier-specific scope) |
| 09:00 | Open `05-din-membership-application.md` draft (target: complete by 12:00 for Wed Jun 3 filing) |
| 10:30 | 30-min break — walk |
| 11:00 | Resume DIN application draft |
| 12:00 | DIN application ready for review |
| 12:00-13:00 | Lunch + walk |
| 13:00-17:00 | Outreach wave: 5 PR firm pitch requests + 3 Adler & Colvin engagement-letter follow-up + Cooley Founding Member template request + Sarah Guo / co-lead pressure-test conversations |
| 17:00-19:00 | Dinner + family |
| 19:00-21:00 | Spec pack: open `15-protocol-distribution/` directory + draft `kong-plugin-spec.md` v0.1 (adversarially-corrected) |
| 21:00 | Stop. Commit. Sleep. |

## 13. Tracking + Cadence

| Artifact | Updated by | Cadence |
|----------|-----------|---------|
| This master plan | Veronica | Weekly Sunday evening (or when a circuit breaker trips) |
| `PLAN.md` | Veronica + CoS | Daily |
| `CRIT_PATH.md` | Veronica + CoS | When a milestone moves |
| `lpr-status.json` | Auto + Veronica | After every customer / regulator / standards / audit touch |
| `win-conditions.json` | Veronica | When a kill condition activates |
| `01-cfo-24-month-model.md` | Fractional CFO | Monthly close |
| `02-threat-model-briefing.md` | Senior Security Advisor + Veronica | When audit fieldwork surfaces new threat |
| `03-handoff-integration.md` | Veronica | After every external send |
| `04-atomic-explosion-master-plan.md` | Veronica | Weekly + after every circuit breaker |

---

## 14. What This Plan Is NOT

This plan is reality-checked. It is NOT:

- $86M Y1 ARR
- $65B Y5 valuation
- 50 super-spreader contact map (13 of those 50 were eliminated by the reality-check)
- "Article 95 confers presumption of conformity" (it does NOT — C1)
- "Kong intercepts inbound third-party AI data" (it does NOT — C2)
- "We recruit a LangChain committer via fractional equity" (we do NOT — C3)
- "Verification requires LP nodes" (it does NOT — C4)
- "`/v/{slug}` is the enterprise compliance dashboard" (it is NOT — C5)
- "Body-filter all the things" (no — C6)
- "Callback handlers only" (no — C7)
- "Riot anchor alone is sufficient" (it is NOT — C8 requires counterweight)

What this plan IS: a sequenced, cash-funded, circuit-broken, multi-track execution sequence that takes us from solo-founder pre-seed (today, Jun 1 19:40 PDT) to Series A teaser ready (Nov 29) without any of the eight load-bearing errors that would have discredited us with a regulator, an auditor, an enterprise buyer, or a category-creator investor.

**One-line motto for the next 25 days**: *Close the round. Sign the audit. File the DIN. Send the briefs. Ship the spec pack. Hire the CoS. Hire the engineer. Land the anchor. Land the counterweight. Then launch.*

—— Veronica S. Dawkins, Founder, LedgerProof
Monday June 1, 2026 — 19:40 PDT
