# LedgerProof — Integrated Plan (Seed Close → Series A)

**Document version:** v1.0 (May 28, 2026)
**Owner:** Veronica S. Dawkins, Founder
**Horizon:** June 25, 2026 (seed close) → December 7, 2026 (Series A open)
**Fixed external constraint:** EU AI Act Article 50 enforces August 2, 2026

> **Master operating document as of Jun 1, 2026 — read this first**: [`14-seed-close-pack/04-atomic-explosion-master-plan.md`](14-seed-close-pack/04-atomic-explosion-master-plan.md). Five sequenced phases, seven workstreams, eight load-bearing corrections (C1-C8), eight kill switches (KS1-KS8). Synthesizes the reality-check ([`12-premortem/05-EXPLOSIVE-ADOPTION-REALITY-CHECK.md`](12-premortem/05-EXPLOSIVE-ADOPTION-REALITY-CHECK.md)), CFO model ([`14-seed-close-pack/01-cfo-24-month-model.md`](14-seed-close-pack/01-cfo-24-month-model.md)), and threat-model briefing ([`14-seed-close-pack/02-threat-model-briefing.md`](14-seed-close-pack/02-threat-model-briefing.md)) into a single execution spine. Corporate ops state in [`ops-state.json`](ops-state.json).

This is the single document that wires the **GTM plan** ([`08-gtm/`](08-gtm/00-MASTER-PLAN.md)) and the **code plan** ([`09-code-plan/`](09-code-plan/00-MASTER-CODE-PLAN-V2.md)) into one integrated view. Each milestone gate shows the commercial deliverables and the engineering deliverables side by side. Where one depends on the other, the dependency is named.

For commercial-only detail: [`08-gtm/00-MASTER-PLAN.md`](08-gtm/00-MASTER-PLAN.md)
For engineering-only detail: [`09-code-plan/00-MASTER-CODE-PLAN-V2.md`](09-code-plan/00-MASTER-CODE-PLAN-V2.md) (V2, converged with the [10X Playbook](12-premortem/04-10X-PLAYBOOK-MAY31.md); V1 archived)

---

## Operating thesis (one sentence)

Convert an EU regulatory deadline into a defensible open-protocol category in 180 days — without losing the operational discipline that lets the protocol survive a regulator examination.

---

## Track map (GTM ↔ engineering)

| GTM Track | Engineering Track | Coupling |
|---|---|---|
| **T1** Product & Protocol | **E1** Protocol & Spec | Same surface; spec changes drive customer comms |
| **T2** Enterprise Sales | **E2** SDKs / **E7** DevX | Sales asks fail if SDK quickstart fails; SDK regressions surface as sales blockers |
| **T3** Partnerships | **E7** DevX / **E2** SDKs | Big-4 + cloud marketplace = connector quality |
| **T4** Regulator & Standards | **E1** Spec / **E5** Security | Briefings depend on IETF status + cryptographic credibility |
| **T5** Foundation | **E1** Spec / **E4** Verifier+Registry | Foundation owns spec, registry, signing key |
| **T6** Marketing & Content | **E7** DevX / **E4** Verifier | Verifier portal IS the marketing artifact |
| **T7** Finance & Ops | **E5** Security / **E6** Observability | SOC 2 evidence flows from observability + supply chain |

---

## Gate 0 — Seed close (June 25, 2026)

**Status:** in progress

| Surface | Deliverable | Dependency |
|---|---|---|
| Commercial | $15M closed across TVP, Stillmark, Fulgur; signed SAFEs; wire received | — |
| Engineering | LPR v1.1 live; SDKs at 1.0; ~50K receipts anchored; PR #1 open | — |

**Cross-cut:** Founder retains all merge buttons until Day 30 hires land.

---

## Gate 1 — Day 30 (July 25, 2026) — Ready for August 2

**Single integrated goal:** the protocol, the SDKs, the operator, the verifier, and the sales motion all hold under 10x load on Day +8 (August 2 enforcement).

### Commercial ([GTM gate 1](08-gtm/00-MASTER-PLAN.md#gate-1--day-30-july-25-2026))

| Artifact | Depends on (engineering) |
|---|---|
| [FLI partnership outreach](08-gtm/day-30/01-fli-partnership-outreach.md) | Verifier portal stable URL (E4) |
| [Three persona cold emails](08-gtm/day-30/02-three-persona-cold-emails.md) | SDK quickstart works (E2/E7); pilot SOW pricing aligned with operator cost model (E3) |
| [Compliance Stamp PDF design spec](08-gtm/day-30/03-compliance-stamp-pdf-design-spec.md) | Stamp pipeline production design (E4) |
| [Regulator briefing](08-gtm/day-30/04-regulator-briefing.md) | IETF Datatracker status maintained (E1) |
| [Founder open letter](08-gtm/day-30/05-founder-open-letter.md) | Verifier portal anchor URL stable (E4) |
| [Shadow AI Inventory one-pager](08-gtm/day-30/06-shadow-ai-inventory-one-pager.md) | None — Foundation-side delivery |

### Engineering ([Code gate 1](09-code-plan/00-MASTER-CODE-PLAN.md#gate-1--day-30-july-25-2026--article-50-hardening))

| Artifact | Enables (commercial) |
|---|---|
| [Day 30 hardening checklist](09-code-plan/day-30/01-day-30-hardening-checklist.md) | All Day-30 commercial sends; go/no-go for August 2 |
| [SDK 1.1 spec](09-code-plan/day-30/02-sdk-1.1-spec.md) | Persona-email "≤50ms P99" claim; pilot SOW Schedule B SLOs |
| [Operator load test plan](09-code-plan/day-30/03-operator-load-test-plan.md) | "10M receipts/day" capacity statement in marketplace and sales decks |

### Cross-cut decisions for this gate

- **The Compliance Stamp PDF design spec is published commercially at Day 30 but the production pipeline is built at Day 90.** Reference stamp lives in the verifier portal from Day 30 as proof-of-design.
- **The persona cold emails reference the SDK quickstart; if F1/F2 in the hardening checklist slip, the MLOps email is pulled.**
- **PR #1 merge is the gating engineering decision for the Day 30 marketing launch — open PRs in CI affect the "live in production" narrative.**

---

## Gate 2 — Day 60 (August 24, 2026) — Post-enforcement stabilization

Article 50 enforcing for 22 days. First pilots running. Hiring begins.

### Commercial ([GTM gate 2](08-gtm/00-MASTER-PLAN.md#gate-2--day-60-august-24-2026))

| Artifact | Depends on (engineering) |
|---|---|
| [30-Day Pilot SOW](08-gtm/day-60/01-poc-sow-template.md) | SLO contracts in Schedule B match operator capacity (E3); P99 ≤50ms commitment depends on SDK 1.1 + operator load test results |
| [Reference customer playbook](08-gtm/day-60/02-reference-customer-playbook.md) | Foundation Canonical Registry public read API (E4); per-customer SLO dashboards (E6) |
| [Blind case study template](08-gtm/day-60/03-blind-case-study-template.md) | First pilot success metrics from operator dashboards (E3/E6) |

### Engineering ([Code gate 2](09-code-plan/00-MASTER-CODE-PLAN.md#gate-2--day-60-august-24-2026--post-enforcement-stabilization))

| Artifact | Enables (commercial) |
|---|---|
| [LPR v1.2 spec freeze](09-code-plan/day-60/01-lpr-v1.2-spec-freeze.md) | Code-of-Practice adaptation narrative for GC/CRO buyers; ISO 42001 mapping refresh |
| [Multi-region operator design](09-code-plan/day-60/02-multi-region-operator-design.md) | DORA Article 28 geographic-resilience procurement question; Series A multi-region claim |
| [Self-host quickstart](09-code-plan/day-60/03-self-host-quickstart.md) | DORA Article 28 "exit strategy" requirement; Big-4 partnership value-for-value framing; "what if LedgerProof fails?" answer |

### Cross-cut decisions for this gate

- **The self-host story is the single most important Day-60 engineering deliverable for commercial value.** It directly unlocks Big-4 LOIs (Day 90+) and FSI procurement closes (Day 120+). Treat it as Critical even though no customer has asked for it yet.
- **LPR v1.2 spec freeze is calendar-driven by the Code of Practice — the freeze must happen before Code finalization to land "we ship under any Code outcome" as a verifiable claim.**
- **First AE hire by Day 60 is gated on a working pilot SOW + SLO contracts the engineer can defend in front of a procurement team.**

---

## Gate 3 — Day 90 (September 23, 2026) — Scale & integrations

First production conversions. Big-4 outreach in market. Marketplace submissions.

### Commercial ([GTM gate 3](08-gtm/00-MASTER-PLAN.md#gate-3--day-90-september-23-2026))

| Artifact | Depends on (engineering) |
|---|---|
| [Big-4 partnership outreach](08-gtm/day-90/01-big-4-partnership-outreach.md) | Self-host reference operator GA (E3); LPR v1.2 deployed (E1) |
| [AWS Marketplace listing](08-gtm/day-90/02-aws-marketplace-listing.md) | Stamp PDF pipeline GA (E4); cloud connector spec (E2); SBOM + provenance (E5) |
| [Azure Marketplace listing](08-gtm/day-90/03-azure-marketplace-listing.md) | Azure OpenAI + Purview connectors (E2); EU data residency in operator (E3) |

### Engineering ([Code gate 3](09-code-plan/00-MASTER-CODE-PLAN.md#gate-3--day-90-september-23-2026--scale--integrations))

| Artifact | Enables (commercial) |
|---|---|
| [Multi-region active-active](09-code-plan/day-90/01-multi-region-active-active.md) | "Multi-region production" claim in marketplace + sales decks; resilience narrative for FSI |
| [Stamp PDF pipeline](09-code-plan/day-90/02-stamp-pdf-pipeline.md) | Pilot SOW Day-30 PDF deliverable; reference customer playbook artifact production; GC Board-pack story |
| [Cloud connector spec](09-code-plan/day-90/03-cloud-connector-spec.md) | "30 minutes to first receipt" claim in all three marketplaces; MLOps persona credibility |

### Cross-cut decisions for this gate

- **AWS Marketplace listing is submitted Day 90 but goes live Day ~120.** GTM and engineering coordinate the launch window so AWS goes live the same week the first case study lands.
- **Stamp PDF pipeline GA at Day 90 is the engineering trigger for the reference customer playbook to start producing artifacts.** Without GA pipeline, the playbook is theoretical.
- **Big-4 outreach sequence (Deloitte first) is gated on the self-host reference operator being publicly available — without it, the "no vendor lock-in" claim in the outreach email is unsupported.**

---

## Gate 4 — Day 120 (October 23, 2026) — Production at enterprise scale

15+ production customers; first regulator examinations. Big-4 LOIs landing.

### Commercial ([GTM gate 4](08-gtm/00-MASTER-PLAN.md#gate-4--day-120-october-23-2026))

| Artifact | Depends on (engineering) |
|---|---|
| [Webinar series outline](08-gtm/day-120/01-webinar-series-outline.md) | Customer-facing SLO dashboards (E6); cross-protocol bridges visible in verifier (E4) |
| [GCP Marketplace listing](08-gtm/day-120/02-gcp-marketplace-listing.md) | Vertex AI connector at 1.0 (E2); Sovereign Cloud deployment validated (E3) |
| [FSI sector whitepaper](08-gtm/day-120/03-fsi-sector-whitepaper.md) | DORA + ISO 42001 + MiFID II mappings up to date (E1); v1.2 profiles enabling sector adaptation (E1) |

### Engineering ([Code gate 4](09-code-plan/00-MASTER-CODE-PLAN.md#gate-4--day-120-october-23-2026--production-at-enterprise-scale))

| Artifact | Enables (commercial) |
|---|---|
| [PQ migration v0.1](09-code-plan/day-120/01-pq-migration-v0.1.md) | Series A "forward visibility" narrative; cryptographic seriousness signal for GCs |
| [Cross-protocol bridges](09-code-plan/day-120/02-cross-protocol-bridges.md) | Media customer C2PA compatibility; FSI SCITT compatibility; OpenTimestamps defense-in-depth |
| [SBOM & supply chain](09-code-plan/day-120/03-sbom-and-supply-chain.md) | SOC 2 Type 1 evidence (T7); marketplace listing security sections; procurement "verify the install" answer |

### Cross-cut decisions for this gate

- **SOC 2 Type 1 attestation lands at this gate.** Engineering provides the SBOM and provenance evidence; finance owns the audit relationship; founder signs the management assertion. All three must converge by Day 120.
- **PQ migration v0.1 is the only Day-120 artifact that is primarily for Series A audience, not customer audience.** Treat publication timing accordingly — late October to clear the SOC 2 milestone but before Series A diligence opens.
- **FSI sector whitepaper depends on at least one signed FSI reference customer (T2/T6 milestone).** If no FSI customer signs by Day 100, whitepaper publication slips by 30 days; do not publish anonymized as a substitute.

---

## Gate 5 — Day 180 (December 7, 2026) — Series A defensible posture

Article 50 enforcing for 128 days. Traction narrative replaces urgency narrative.

### Commercial ([GTM gate 5](08-gtm/00-MASTER-PLAN.md#gate-5--day-180-december-7-2026))

| Artifact | Depends on (engineering) |
|---|---|
| [Series A one-pager](08-gtm/day-180/01-series-a-one-pager.md) | All trailing-N metrics current; verifier portal anchor link verifiable (E4) |
| [Series A deck outline](08-gtm/day-180/02-series-a-deck-outline.md) | Receipts-anchored chart from operator data (E3/E6); structural moat evidence from E1+E5 |
| [Asia expansion brief](08-gtm/day-180/03-asia-expansion-brief.md) | Asia region provisioning plan complete (E3) |

### Engineering ([Code gate 5](09-code-plan/00-MASTER-CODE-PLAN.md#gate-5--day-180-december-7-2026--series-a-defensible-technical-posture))

| Artifact | Enables (commercial) |
|---|---|
| [LPR v2.0 PQ RFC](09-code-plan/day-180/01-lpr-v2.0-pq-rfc.md) | Series A "PQ on the roadmap" diligence answer; IETF WG citation in deck |
| [Series A technical diligence pack](09-code-plan/day-180/02-series-a-technical-diligence-pack.md) | Every Series A lead's technical advisor receives this pack; commercial deck is the cover, this is the substance |
| [Asia region provisioning plan](09-code-plan/day-180/03-asia-region-provisioning-plan.md) | Asia expansion brief's engineering credibility; Series A "$30M includes Asia" line item |

### Cross-cut decisions for this gate

- **The Series A one-pager + deck + diligence pack are reviewed together before any external send.** GTM-side handles narrative; engineering-side handles substance; founder owns the integration.
- **PQ RFC publication is timed to land before the first Series A diligence call.** Late Day-175 publication; nothing later — the artifact loses value if a Series A lead asks first.
- **Asia expansion is committed in the Series A one-pager AND in the technical provisioning plan. The two must agree on dates and dollar amounts to the line item.**

---

## Hiring sequence (integrated)

| # | Role | GTM trigger | Engineering trigger | Latest hire |
|---|---|---|---|---|
| 1 | Senior Product Engineer | — | Day 0 (SDK + DevX work) | Day 30 |
| 2 | Web Engineering Consultant | — | Day 0 (verifier + Stamp PDF UX) | Day 30 |
| 3 | Founding AE (Brussels/Frankfurt) | Day 30 — first pilot closed | Pilot SOW in market | Day 60 |
| 4 | Content lead (part-time, EU-based) | Day 30 — launch published | — | Day 60 |
| 5 | CFO advisor (fractional) | Day 30 — seed wire received | — | Day 60 |
| 6 | Spec Lead (full-time, IETF-engaged) | Day 30 — Big-4 outreach response | Day 30 — LPR v1.2 design begins | Day 60 |
| 7 | Security Advisor (fractional → full Day 120) | — | Day 30 — pentest kickoff | Day 60 |
| 8 | BD lead (Big-4 + cloud co-sell) | Day 60 — Big-4 response | — | Day 90 |
| 9 | SRE / Operator Lead | — | Day 60 — multi-region rollout | Day 90 |
| 10 | Foundation ED | Day 90 — 501(c)(3) approved | — | Day 120 |
| 11 | DevRel | — | Day 90 — marketplace launches imminent | Day 120 |
| 12 | EU sales team #2 + #3 | Day 120 — Big-4 LOI signed | — | Day 150 |
| 13 | Cryptography Researcher (PQ migration) | — | Day 120 — v2.0 RFC | Day 180 |
| 14 | Senior Backend Engineer #2 | — | Day 120 — registry GraphQL API | Day 180 |
| 15 | Asia GM (Singapore) | Day 180 — Series A closes | — | Day 210 |

---

## Budget envelope (integrated)

| Category | Day 0–180 spend | Source |
|---|---|---|
| Engineering headcount (founder + 8) | ~$1.4M annualized at Day 180 | seed |
| Commercial headcount (AE, BD, content, CFO advisor, Foundation ED) | ~$1.0M annualized | seed |
| Cloud + infra (Fly.io EU/US/UK + database + storage) | ~$240K | seed |
| Security (pentest, bug bounty, SOC 2, ISO 27001 in flight) | ~$180K | seed |
| Legal (Foundation, IP, contracts, multi-jurisdiction) | ~$220K | seed |
| Marketing (events, content, design) | ~$150K | seed |
| Tooling (CI, observability, secret management, design tools) | ~$60K | seed |
| Conferences + standards travel | ~$40K | seed |
| **Total Day 0–180 burn** | **~$3.3M** | leaves ~$11.7M of seed runway |

---

## Cadence (integrated)

### Daily
- 09:00 CET: operator + anchor health checks; SDK download metrics review
- Async: PR review on `main` for any public repo

### Weekly
| Day | Time (CET) | Cadence |
|---|---|---|
| Mon | 09:00 | Engineering sync (15 min) |
| Mon | 09:30 | Founder sync with eng + spec + ops leads |
| Tue | 09:00 | Outbound send window opens (commercial); no outbound Mon or Fri |
| Wed | 09:00 | Spec sync (15 min) |
| Thu | 16:00 | Pipeline review (sales + partnerships) |
| Fri | 12:00 | Regulator-and-standards review |

### Bi-weekly
- Investor update (2 paragraphs + dashboard link)
- Customer integration ticket review (engineering ↔ AE handoff)
- Foundation board prep (when operating)

### Monthly
- Audit-Ready Compliance Stamp PDFs issued to all paying customers
- Public Foundation transparency report (engineering metrics + commercial milestones)
- Production retrospective + capacity review
- Cost-per-receipt review

### Quarterly
- Roadmap publication on `spec.ledgerproofhq.io/roadmap`
- Pricing review
- Foundation board meeting

---

## Risk register (integrated)

| Risk | Likelihood | Impact | Owner | Mitigation |
|---|---|---|---|---|
| Article 50 enforcement delayed beyond Aug 2 | Low | High | Founder (GTM) | Narrative pivots to ISO 42001 + DORA; pilots already running on existing standards |
| Code of Practice mandates break LPR v1.1 schema | Medium | Medium | Spec Lead (E1) | Profile system absorbs; v1.2 hooks already scoped |
| Closed-protocol competitor with VC distribution outpaces seed cycle | Medium | Medium | Founder | Open protocol + Foundation + IETF positioning |
| Big-4 firms decline partnership terms | Medium | Medium | Founder → BD | All five firms approached simultaneously; symmetry is leverage |
| Operator outage during high-profile customer demo | Medium | High | SRE | Multi-region + SDK fallback queue; SLO refund triggers in pilot SOW |
| Bitcoin mainnet congestion stalls anchor commitment | Medium | High | SRE | CPFP/RBF bumping; multi-pool relay; documented degraded mode |
| LPR v1.2 schema breaks v1.1 reader assumptions | Low | High | Spec Lead | Profile system additive; CI enforces v1.1 receipts verify under v1.2 readers |
| SDK regression breaks a customer integration mid-pilot | Medium | High | Senior Product Engineer | Semantic versioning strict; canary release to staging customers; rollback automation |
| Pentest finds a cryptographic flaw in receipt issuance | Low | Critical | Security Advisor | Pre-pentest crypto review by external advisor; NIST-standardized primitives only |
| GDPR soft-delete posture rejected by a DPA | Medium | High | Spec Lead + Counsel | Documented in regulator briefing; design accommodates fully-deletable metadata if required |
| Founder bandwidth becomes single point of failure | High | High | Founder | Hiring sequence front-loads ops + sales relief; on-call removes founder by Day 120 |
| Series A market closes before Day 180 | Medium | Medium | Founder | Seed runway ~16 months at Day-180 burn; bridge available from existing investors |
| First reference customer refuses to be named after pilot success | Medium | High | Founding AE + Founder | Reference playbook tier system; multi-customer pipeline reduces single-customer dependency |

---

## What this plan does NOT include

- Series B planning (revisit at Day 150)
- US enterprise sales motion (deferred to $50M+ ARR run-rate)
- China expansion (deferred to 2028+)
- New product surfaces beyond the protocol + verifier + Stamp PDF
- M&A scenarios
- Open-source community grant program (Foundation may add at Day 180+)

If any of these surface as questions in a Series A diligence call, the answer is: "deliberately deferred; see master plan section 'What this plan does not include.'"

---

## Quick-find index

### By milestone
- Day 30: [GTM artifacts](08-gtm/day-30/) · [Engineering artifacts](09-code-plan/day-30/)
- Day 60: [GTM artifacts](08-gtm/day-60/) · [Engineering artifacts](09-code-plan/day-60/)
- Day 90: [GTM artifacts](08-gtm/day-90/) · [Engineering artifacts](09-code-plan/day-90/)
- Day 120: [GTM artifacts](08-gtm/day-120/) · [Engineering artifacts](09-code-plan/day-120/)
- Day 180: [GTM artifacts](08-gtm/day-180/) · [Engineering artifacts](09-code-plan/day-180/)

### By function
- Commercial master: [08-gtm/00-MASTER-PLAN.md](08-gtm/00-MASTER-PLAN.md)
- Engineering master (V2 — canonical): [09-code-plan/00-MASTER-CODE-PLAN-V2.md](09-code-plan/00-MASTER-CODE-PLAN-V2.md)
- Engineering master (V1 — archived): [09-code-plan/00-MASTER-CODE-PLAN.md](09-code-plan/00-MASTER-CODE-PLAN.md)
- 10X Playbook: [12-premortem/04-10X-PLAYBOOK-MAY31.md](12-premortem/04-10X-PLAYBOOK-MAY31.md)
- Premortem: [12-premortem/01-PREMORTEM-MAY31.md](12-premortem/01-PREMORTEM-MAY31.md)
- ISO/IEC 42001 mapping: [08-gtm/shared/iso-42001-ledgerproof-mapping.md](08-gtm/shared/iso-42001-ledgerproof-mapping.md)
- Repo conventions: [09-code-plan/shared/repo-conventions.md](09-code-plan/shared/repo-conventions.md)
- Release process: [09-code-plan/shared/release-process.md](09-code-plan/shared/release-process.md)
- Incident runbook: [09-code-plan/shared/incident-response-runbook.md](09-code-plan/shared/incident-response-runbook.md)

### By buyer persona (skills)
- Fortune-500 GC: `~/.claude/skills/fortune-500-general-counsel-buyer/SKILL.md`
- Fortune-500 CRO/CCO: `~/.claude/skills/fortune-500-cro-cco-buyer/SKILL.md`
- Fortune-500 MLOps Head: `~/.claude/skills/fortune-500-mlops-buyer/SKILL.md`

### By builder persona (skills)
- Senior product engineer: `~/.claude/skills/senior-product-engineer/SKILL.md`
- Senior web engineering consultant: `~/.claude/skills/senior-web-engineering-consultant/SKILL.md`
- Senior editorial content lead: `~/.claude/skills/senior-editorial-content-lead/SKILL.md`
