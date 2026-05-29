# Series A Technical Diligence Pack — Inventory and Storyline

**Purpose:** The exact list of artifacts a Series A lead's technical advisor receives during diligence. Each artifact has a one-line storyline, an owner, and a "what this proves" statement. The pack is assembled once at Day 180 and refreshed per Series A conversation.

**Delivery format:** Notion data room or Dropbox folder with read-only access. Each artifact is a forwardable file; no diligence-call dependency to make sense of any single artifact.

**Recipient:** Series A lead's technical advisor (typically a former CTO or VP Eng of an enterprise software company)

---

## Section 1 — Protocol & spec (E1)

| # | Artifact | What this proves |
|---|---|---|
| 1.1 | `spec.ledgerproofhq.io/lpr-1.2` — full spec text | The protocol is documented at production-grade quality |
| 1.2 | `datatracker.ietf.org/doc/draft-dawkins-scitt-ai-article50/` — IETF status | The protocol is in standards-track process |
| 1.3 | `datatracker.ietf.org/doc/draft-dawkins-scitt-ai-article50-v2/` — PQ draft | Cryptographic forward visibility |
| 1.4 | Test vectors (v1.1, v1.2) at `spec.ledgerproofhq.io/test-vectors/` | Implementation interoperability |
| 1.5 | Profile registry at `spec.ledgerproofhq.io/profiles/` | Regulatory evolution is absorbed without breaking changes |
| 1.6 | Conformance suite repo `github.com/ledgerproof/operator-ref/tests/conformance` | Two independent operator implementations produce identical receipts |

## Section 2 — SDKs (E2)

| # | Artifact | What this proves |
|---|---|---|
| 2.1 | `pypi.org/project/ledgerproof/` — Python SDK download stats | Real adoption (target: 100K+ downloads by Day 180) |
| 2.2 | `npmjs.com/package/@ledgerproof/sdk` — TS SDK download stats | Same |
| 2.3 | `pypi.org/project/langchain-ledgerproof/` — LangChain integration | Ecosystem reach |
| 2.4 | GitHub repos for Go + Java SDK at 1.x stable | Multi-language coverage |
| 2.5 | SBOM and SLSA provenance for last 6 SDK releases | Supply-chain hygiene at SOC 2 evidence quality |
| 2.6 | CI matrix coverage (Python 3.10/3.11/3.12, Node 18/20/22, Go 1.22/1.23, Java 17/21) | Production-grade release engineering |
| 2.7 | Connector packages (OpenAI, Anthropic, Azure OpenAI, Bedrock, Vertex AI) | Inference platform breadth |

## Section 3 — Operator (E3)

| # | Artifact | What this proves |
|---|---|---|
| 3.1 | Trailing 90-day SLO report — EU + US + UK | 99.9% sustained; multi-region active-active proven |
| 3.2 | Chaos test reports (W3 burst + W4 failure injection) | Resilience under documented adverse scenarios |
| 3.3 | Bitcoin anchor lag histogram (12 months) | Anchor SLO sustained even under Bitcoin congestion events |
| 3.4 | Reference operator at `github.com/ledgerproof/operator-ref` | Customers can self-host if commercial operator fails |
| 3.5 | Per-customer SLO dashboards (anonymized sample) | Customer-facing transparency |
| 3.6 | Operator capacity model + cost-per-receipt analysis | Unit economics defensible at scale |

## Section 4 — Verifier & registry (E4)

| # | Artifact | What this proves |
|---|---|---|
| 4.1 | `verify.ledgerproofhq.io` — live verifier | 10-second verification works |
| 4.2 | Verifier source at `github.com/ledgerproof/verifier-ref` | Verification is independent of the operator |
| 4.3 | Foundation Canonical Registry at `registry.ledgerproofhq.io` | Public read-only registry |
| 4.4 | Registry mirror policy (S3 + IPFS) | Trust-but-verify by third parties |
| 4.5 | Stamp PDF generation pipeline metrics | <8s end-to-end for 10M-receipt stamps |
| 4.6 | Cross-protocol bridge demos (C2PA, SCITT, OpenTimestamps) | Ecosystem coexistence |

## Section 5 — Security (E5)

| # | Artifact | What this proves |
|---|---|---|
| 5.1 | SOC 2 Type 1 attestation report (received Day 120) | Procurement-grade security posture |
| 5.2 | Pentest report (Trail of Bits or NCC Group, Day 90) — redacted public summary; full to lead under NDA | External validation |
| 5.3 | Vulnerability disclosure policy + bug bounty status | Active security program |
| 5.4 | Cryptographic primitive review by independent reviewer | Primitives are correctly implemented |
| 5.5 | Foundation signing key custody documentation | Operational key hygiene |
| 5.6 | GDPR data flow diagram + soft-delete attestation flow | GDPR posture defensible to a DPA |
| 5.7 | SLSA Level 3 provenance for production releases | Build-pipeline integrity |

## Section 6 — Observability & SRE (E6)

| # | Artifact | What this proves |
|---|---|---|
| 6.1 | `status.ledgerproofhq.io` — historical SLO data | Public transparency on availability |
| 6.2 | Incident response runbook (redacted version under NDA) | Operational maturity |
| 6.3 | Postmortems for any P0/P1 incidents in trailing 6 months | Learning culture documented |
| 6.4 | Receipt-lifecycle distributed tracing sample | Observability is end-to-end |
| 6.5 | On-call rotation schedule + escalation paths | Founder is no longer single point of failure |

## Section 7 — Developer experience (E7)

| # | Artifact | What this proves |
|---|---|---|
| 7.1 | `docs.ledgerproofhq.io` — full docs site | Documentation at par with leading developer tools |
| 7.2 | Quickstart paths for 6 stacks, each tested in CI | "30 minutes to first receipt" claim is real |
| 7.3 | Marketplace listings (AWS, Azure, GCP) with transaction volume | Distribution at scale |
| 7.4 | GitHub stars, forks, downstream usage signals | Open-source health |
| 7.5 | DevRel engagement metrics (community Slack, GitHub Discussions, conference talks) | Ecosystem traction |

## Section 8 — Foundation governance (cross-track)

| # | Artifact | What this proves |
|---|---|---|
| 8.1 | 501(c)(3) determination letter | Foundation is legally constituted |
| 8.2 | Swiss Verein registration documents | Multi-jurisdictional governance |
| 8.3 | Singapore non-profit application status | Asia governance prepared |
| 8.4 | Foundation board composition + independence ratio | Governance independence proven |
| 8.5 | Foundation public transparency reports (quarterly) | Operational transparency |
| 8.6 | Foundation Advisory Council membership | Industry coordination |

---

## What the diligence pack does NOT include

- Customer-specific data (anonymized where samples are needed)
- Founder financial documents
- Hiring pipeline names
- Big-4 partnership LOIs (those go in the separate commercial diligence pack)
- Investor terms or seed round documents (those go in the cap-table pack)

The technical pack is purely the engineering posture. It is reviewed by the lead's technical advisor; it does not include commercial or financial diligence material.

---

## How the pack tells the story

Reading the pack end-to-end, the technical advisor sees:

1. **A protocol with standards-track legitimacy** (Section 1)
2. **SDKs with real adoption and disciplined release engineering** (Section 2)
3. **An operator running at scale across three regions** (Section 3)
4. **Verification that does not depend on the operator** (Section 4)
5. **Security posture meeting enterprise procurement standards** (Section 5)
6. **Observability and SRE practices that survived first enforcement window** (Section 6)
7. **A developer experience that converts open-source interest to enterprise pipeline** (Section 7)
8. **Foundation governance that makes the protocol survive the company** (Section 8)

The story is: *the company built a protocol, the protocol survives the company, the company built a business on top of the protocol, the business is healthy, the moat is structural.*

---

## Refresh cadence

- Pack refreshed before each new Series A lead conversation (typically monthly)
- Each refresh updates the trailing-N-day metrics and any newly published artifacts
- Refresh is mechanical (a script regenerates the data room contents from canonical sources); no narrative changes between leads

---

## Owner of each artifact at Day 180

| Section | Owner | Backup |
|---|---|---|
| 1 (Spec) | Spec Lead | Founder |
| 2 (SDKs) | Senior Product Engineer | Spec Lead |
| 3 (Operator) | SRE | Founder |
| 4 (Verifier) | Web Engineering Consultant | SRE |
| 5 (Security) | Security Advisor (Day 120 onboard) | Founder |
| 6 (Observability) | SRE | DevRel |
| 7 (DevX) | DevRel | Senior Product Engineer |
| 8 (Governance) | Founder | Foundation ED (Day 120 onboard) |

The pack assembly itself is owned by Founder + Founding AE (commercial diligence pack owner) coordinating the data room.

---

## Pre-Day-180 checklist

- [ ] Every artifact above is current
- [ ] Every URL resolves
- [ ] Every "what this proves" statement matches the artifact's actual content
- [ ] At least two artifacts in each section
- [ ] Reading time end-to-end: ~6 hours (a technical advisor's typical diligence budget)
- [ ] Data room access controls tested (read-only for diligence advisors; never edit access)
- [ ] All NDAs in place before first diligence access
- [ ] Founder + Spec Lead briefed on common technical-advisor questions per section
