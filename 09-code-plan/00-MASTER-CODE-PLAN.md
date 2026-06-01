> **⚠ ARCHIVED — May 31, 2026.** This document is the originally-conceived 7-track gate-grid plan. It has been superseded by [`00-MASTER-CODE-PLAN-V2.md`](00-MASTER-CODE-PLAN-V2.md), which converges the engineering plan with the [10X Playbook](../12-premortem/04-10X-PLAYBOOK-MAY31.md) — doctrine-first, bandwidth-audited, with an explicit kill list and Foundation/Inc. boundary map. V1 survives only for historical reference. New engineering decisions read against V2.
>
> **What V2 changes:** the 7-track × 5-gate grid is dropped as a planning instrument (it implied a parallel-shipping team that doesn't exist); replaced by a 7-day hot path + 30-day compounding wedge + 90-day moat construction grouped by doctrine principle. The seven cross-track invariants and the inviolable constraints survive verbatim.

---

# LedgerProof Code Plan — Master (Seed Close → Series A)

**Document version:** v1.0 (May 28, 2026)
**Owner:** Veronica S. Dawkins, Founder + Spec Lead (founder until Day 60; spec lead hire from Day 60)
**Time horizon:** June 25, 2026 → December 7, 2026
**Fixed external constraint:** Article 50 enforcement August 2, 2026 — the operator must hold 99.9% from that date forward
**Inviolable constraints (carry forward verbatim):**
- Never touch legacy `iad` deployment — those 3 anchors stay verifiable forever
- Secrets at `~/.ledgerproof-secrets/` mode 0600 — never commit
- GDPR safety net: emails forbidden at schema validation in `deployer_id`, `reviewer_role`, `review_rationale`
- Bitcoin OP_RETURN format: `"LPR1" || merkle_root_32` (36 bytes total) — DO NOT modify
- Never auto-merge PRs without explicit Veronica approval
- Recovery codes (PyPI, npm, GitHub) in 1Password ONLY — never in chat

---

## Operating thesis

The protocol is shipped. The next six months are about **survival under load, evolution under uncertainty, and provability under examination.** Every engineering decision is evaluated against three questions:

1. Does this preserve the regulator's ability to verify without trusting us?
2. Does this preserve a customer's ability to leave us without re-issuing receipts?
3. Does this survive a 10x receipt volume increase?

Anything that fails any of the three does not ship.

---

## The seven engineering tracks

| Track | Owner | Definition of done at Series A |
|---|---|---|
| **E1 — Protocol & Spec** | Founder → spec lead Day 60 | LPR v1.2 shipped to production; PQ migration plan published; IETF WG adoption |
| **E2 — SDKs (Python, TS, future Go/Java)** | Founder → product engineer Day 30 | Python + TS at 1.x stable; Go + Java alpha; 99% test coverage on hot paths |
| **E3 — Operator (EU + US + UK)** | Founder → SRE hire Day 90 | 99.9% availability for 90 consecutive days; multi-region active-active |
| **E4 — Verifier & Canonical Registry** | Founder + web engineering consultant Day 30 | <2s verification at p95; public registry queryable by any third party |
| **E5 — Security & Cryptography** | Founder + security advisor Day 30 | SOC 2 Type 1 complete; pentest passed; bug bounty live; PQ primitives integrated as v2 candidates |
| **E6 — Observability & SRE** | Founder → SRE Day 90 | Full receipt-lifecycle tracing; customer-facing SLO dashboard; incident response runbook |
| **E7 — Developer Experience** | Founder → DevRel Day 120 | `pip install ledgerproof && python -m ledgerproof.demo` works in 90 seconds; published quickstarts for 6 stacks |

---

## Milestone gates

### Gate 0 — Seed close state (June 25, 2026)
- LPR v1.1 spec published; IETF draft confirmed
- Python SDK 1.0.0 on PyPI; TypeScript SDK 1.0.0 on npm; `langchain-ledgerproof` 1.0.0 on PyPI
- EU operator running Fly.io Frankfurt; ~50,000 receipts anchored
- Verifier portal live at verify.ledgerproofhq.io
- PR #1 on `ledgerproof-platform` open, awaiting merge decision
- 3 legacy `iad` anchors preserved; do not touch

### Gate 1 — Day 30 (July 25, 2026) — Article 50 hardening
**Single goal: be ready for August 2 enforcement at 10x current volume without breaking a sweat.**

| Track | Deliverable |
|---|---|
| E1 | LPR v1.1.1 patch released (Code-of-Practice compatibility hooks); v1.2 RFC draft circulated |
| E2 | Python SDK 1.1 (local queue fallback + retry); TS SDK 1.1 (same); LangChain integration smoothed |
| E3 | EU operator load-tested to 10M receipts/day; alerting wired; runbook published |
| E4 | Verifier hardened for 100x current traffic; canonical registry public read-only API live |
| E5 | Pentest scope finalized with Trail of Bits / NCC Group; PR #1 merged with audit-ready CI |
| E6 | Receipt-lifecycle distributed tracing live; per-customer SLO dashboards mocked |
| E7 | Quickstart published for Python, TypeScript, LangChain, OpenAI, Anthropic, Azure OpenAI |

Artifact: [01-day-30-hardening-checklist.md](day-30/01-day-30-hardening-checklist.md)
Artifact: [02-sdk-1.1-spec.md](day-30/02-sdk-1.1-spec.md)
Artifact: [03-operator-load-test-plan.md](day-30/03-operator-load-test-plan.md)

### Gate 2 — Day 60 (August 24, 2026) — Post-enforcement stabilization
Article 50 has been enforcing for 22 days. Pilots are running. The system is taking real customer load.

| Track | Deliverable |
|---|---|
| E1 | LPR v1.2 spec frozen; profile system implemented; backwards-compatible v1.1 readers must continue to verify |
| E2 | SDK 1.2 with v1.2 profile support; Go SDK alpha released; Java SDK design doc circulated |
| E3 | US operator (us-east-1) stood up in active-passive with EU; 99.9% target for the EU operator achieved |
| E4 | Verifier supports v1.2 profile resolution; registry exposes profile metadata |
| E5 | Spec lead hired; security advisor onboarded; SOC 2 Type 1 audit fieldwork |
| E6 | Status page (status.ledgerproofhq.io) live; PagerDuty escalation paths configured |
| E7 | Self-hosted operator quickstart published (Apache 2.0 reference impl) |

Artifact: [01-lpr-v1.2-spec-freeze.md](day-60/01-lpr-v1.2-spec-freeze.md)
Artifact: [02-multi-region-operator-design.md](day-60/02-multi-region-operator-design.md)
Artifact: [03-self-host-quickstart.md](day-60/03-self-host-quickstart.md)

### Gate 3 — Day 90 (September 23, 2026) — Scale & integrations
First production customers under load. Big-4 integrations begin. Cloud marketplace listings submitted.

| Track | Deliverable |
|---|---|
| E1 | LPR v1.2 deployed to production; first profile published for Code-of-Practice partial adaptation |
| E2 | Go SDK 1.0; Java SDK alpha; LangChain v2 with v1.2 support; Vertex AI + Azure OpenAI + Bedrock connectors |
| E3 | EU + US active-active; UK operator (London) provisioned; auto-failover validated under chaos test |
| E4 | Stamp PDF generation pipeline live in production; <8s end-to-end for 10M-receipt stamps |
| E5 | Pentest report delivered; remediations shipped; bug bounty live on HackerOne or equivalent |
| E6 | Customer-facing SLO dashboards GA; per-Customer status emails on incident |
| E7 | AWS Marketplace launch-ready (Day 120); Azure + GCP starter kits published |

Artifact: [01-multi-region-active-active.md](day-90/01-multi-region-active-active.md)
Artifact: [02-stamp-pdf-pipeline.md](day-90/02-stamp-pdf-pipeline.md)
Artifact: [03-cloud-connector-spec.md](day-90/03-cloud-connector-spec.md)

### Gate 4 — Day 120 (October 23, 2026) — Production at enterprise scale
15+ production customers; 100M+ receipts/month aggregate; first regulator examinations using stamps.

| Track | Deliverable |
|---|---|
| E1 | LPR v1.2.1 patch with Code-of-Practice adaptations as Code finalizes; PQ migration v0.1 design doc |
| E2 | Java SDK 1.0; .NET SDK alpha (for Azure FSI customers); SBOM published for every SDK release |
| E3 | Multi-region 99.95% sustained; per-region capacity at 3x peak observed load |
| E4 | Verifier supports cross-protocol attestations (C2PA, SCITT bridge); registry GraphQL API |
| E5 | SOC 2 Type 1 attestation received; Type 2 window opened; ISO 27001 audit kickoff |
| E6 | SLO reports auto-included in Stamp PDFs; capacity planning automated |
| E7 | DevRel hired; 6+ quickstart paths live; Cookiecutter / scaffold tooling published |

Artifact: [01-pq-migration-v0.1.md](day-120/01-pq-migration-v0.1.md)
Artifact: [02-cross-protocol-bridges.md](day-120/02-cross-protocol-bridges.md)
Artifact: [03-sbom-and-supply-chain.md](day-120/03-sbom-and-supply-chain.md)

### Gate 5 — Day 180 (December 7, 2026) — Series A defensible technical posture
The technical narrative must be: shipped, scaled, audited, evolving.

| Track | Deliverable |
|---|---|
| E1 | LPR v1.2 stable in production for 90+ days; v2.0 PQ design RFC circulated to IETF WG |
| E2 | All four SDKs (Python, TS, Go, Java) at 1.x stable; .NET in beta |
| E3 | Multi-region 99.9% sustained for 90 consecutive days; ready to add Asia (Singapore) in Q1 2027 |
| E4 | Verifier portal at 100K+ verifications/month; registry indexed by 3+ independent third parties |
| E5 | SOC 2 Type 1 in hand; Type 2 mid-fieldwork; pentest #2 scoped |
| E6 | Public status page with historical SLO; incident reports anchored as receipts (dogfooding) |
| E7 | Documentation site at docs.ledgerproofhq.io with full API ref, conceptual guides, and runbooks |

Artifact: [01-lpr-v2.0-pq-rfc.md](day-180/01-lpr-v2.0-pq-rfc.md)
Artifact: [02-series-a-technical-diligence-pack.md](day-180/02-series-a-technical-diligence-pack.md)
Artifact: [03-asia-region-provisioning-plan.md](day-180/03-asia-region-provisioning-plan.md)

---

## Repository topology

```
github.com/ledgerproof/
├── ledgerproof-platform/         ← monorepo: operator, verifier, registry, internal libs (private)
├── ledgerproof-spec/             ← LPR specification + IETF draft sources (public, Apache 2.0)
├── ledgerproof-py/               ← Python SDK (public, Apache 2.0)
├── ledgerproof-ts/               ← TypeScript SDK (public, Apache 2.0)
├── ledgerproof-go/               ← Go SDK (public, Apache 2.0) — Day 60
├── ledgerproof-java/             ← Java SDK (public, Apache 2.0) — Day 90
├── ledgerproof-dotnet/           ← .NET SDK (public, Apache 2.0) — Day 120
├── langchain-ledgerproof/        ← LangChain integration (public, Apache 2.0)
├── verifier-ref/                 ← Reference verifier implementation (public, Apache 2.0)
├── operator-ref/                 ← Reference self-hosted operator (public, Apache 2.0) — Day 60
├── mappings/                     ← ISO 42001, NIST RMF, DORA, MiFID II mapping docs (public, CC-BY-4.0)
└── governance/                   ← Foundation governance + Advisory Council records (public, CC-BY-4.0)
```

Visibility rule: anything a customer needs to verify a receipt without trusting us is **public**. Anything proprietary to the LedgerProof Inc. commercial service is private. The Foundation owns the spec, mapping documents, and reference implementations.

---

## Cadence

| Cadence | Activity |
|---|---|
| Daily | EU operator health checks; receipt anchor confirmation lag review (auto-paged at >24h) |
| Weekly | Eng sync 09:00 CET Monday (15 min); spec sync 09:00 CET Wednesday (15 min) |
| Weekly | Receipt volume + SLO digest published in #eng-internal |
| Bi-weekly | Customer integration ticket review |
| Monthly | Production retrospective; capacity review; cost-per-receipt review |
| Quarterly | Spec roadmap publication on spec.ledgerproofhq.io/roadmap |
| Quarterly | Public Foundation transparency report (receipts anchored, operators, governance changes) |
| Annual | Major version review (v2.0 process initiated at Day 180) |

---

## Engineering hiring sequence

| Order | Role | Trigger | Latest hire date |
|---|---|---|---|
| 1 | Senior Product Engineer (SDK + DevX) | Day 0 — seed close | Day 30 |
| 2 | Web Engineering Consultant (verifier portal + Stamp PDF UX) | Day 0 — seed close | Day 30 |
| 3 | Spec Lead (full-time, IETF-engaged) | Day 30 — Big-4 outreach response | Day 60 |
| 4 | Security Advisor (fractional → full Day 120) | Day 30 — pentest kickoff | Day 60 |
| 5 | SRE / Operator Lead | Day 60 — multi-region rollout | Day 90 |
| 6 | DevRel | Day 90 — marketplace launches imminent | Day 120 |
| 7 | Cryptography Researcher (PQ migration) | Day 120 — v2.0 RFC | Day 180 |
| 8 | Senior Backend Engineer #2 | Day 120 — registry GraphQL API | Day 180 |

Each role uses the relevant skill persona in `~/.claude/skills/` as interview filter.

---

## Budget envelope (engineering subset of seed)

| Category | Day 0–180 spend |
|---|---|
| Engineering headcount (founder + 8) | ~$1.4M annualized at Day 180 |
| Cloud + infra (Fly.io EU, US, UK) | ~$240K |
| Security (pentest, bug bounty, SOC 2/ISO audits) | ~$180K |
| Tooling (CI, observability, secret management) | ~$60K |
| Conferences + standards travel (IETF, EU events) | ~$40K |
| **Engineering total Day 0–180** | **~$1.9M** |

---

## Risk register (engineering-specific)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Bitcoin mainnet congestion stalls anchor commitment past SLO | Medium | High | Multi-pool relay; CPFP fee bumping; documented degraded-mode operation |
| Single-region operator outage during August 2 spike | Medium | Critical | US operator stood up Day 60 in active-passive; chaos-tested Day 90 |
| LPR v1.2 schema breaks v1.1 reader assumptions | Low | High | Profile system designed for additive evolution; v1.1 receipts must verify under v1.2 readers — enforced in CI |
| SDK regression breaks a customer integration mid-pilot | Medium | High | Semantic versioning strict; canary release to staging customers; rollback automation |
| Pentest finds a cryptographic flaw in receipt issuance | Low | Critical | Cryptography review by external advisor pre-pentest; primitives are NIST-standardized only |
| GDPR soft-delete posture rejected by a DPA examination | Medium | High | Posture documented in regulator briefing; design accommodates a fully-deletable metadata layer should it be required |
| PQ migration deadline (NIST 2030) creeps forward | Medium | Medium | v0.1 design doc by Day 120; primitives selected from NIST PQC standards only |
| Founder remains in critical path for production incidents past Day 90 | High | High | SRE hire by Day 90; runbooks before SRE start; PagerDuty escalation excludes founder by Day 120 |
| Open-source contributors fork without coordinating | Medium | Medium | CLA required; Foundation maintains canonical implementations; profile system contains divergence to operator-side, not spec-side |

---

## Cross-track invariants (must hold across every gate)

1. **Receipt format is append-only.** New fields are additive. Old receipts always verify under current readers.
2. **Profile system absorbs regulatory change.** No customer-side breaking changes from Code-of-Practice evolution.
3. **No PII at the anchor layer.** Schema rejection at parse time; pentest scope explicitly tests this.
4. **No content data leaves the customer's perimeter.** Only hashes and metadata. Pentest scope tests this.
5. **The verifier never depends on the operator.** A customer using our operator can verify with the public reference verifier and the public Bitcoin chain alone.
6. **Versioned everything.** Every published artifact (SDK, spec, mapping, runbook) has a version, a deprecation policy, and a migration path.
7. **Tamper-evidence dogfooding.** Foundation publishes its own incident reports, transparency reports, and Code-of-Practice consultation submissions as receipts.

---

## Documents in this plan

```
09-code-plan/
├── 00-MASTER-CODE-PLAN.md                ← you are here
├── day-30/
│   ├── 01-day-30-hardening-checklist.md
│   ├── 02-sdk-1.1-spec.md
│   └── 03-operator-load-test-plan.md
├── day-60/
│   ├── 01-lpr-v1.2-spec-freeze.md
│   ├── 02-multi-region-operator-design.md
│   └── 03-self-host-quickstart.md
├── day-90/
│   ├── 01-multi-region-active-active.md
│   ├── 02-stamp-pdf-pipeline.md
│   └── 03-cloud-connector-spec.md
├── day-120/
│   ├── 01-pq-migration-v0.1.md
│   ├── 02-cross-protocol-bridges.md
│   └── 03-sbom-and-supply-chain.md
├── day-180/
│   ├── 01-lpr-v2.0-pq-rfc.md
│   ├── 02-series-a-technical-diligence-pack.md
│   └── 03-asia-region-provisioning-plan.md
└── shared/
    ├── repo-conventions.md
    ├── release-process.md
    └── incident-response-runbook.md
```
