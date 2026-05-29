# Day 30 Hardening Checklist — Ready for August 2

**Purpose:** Single checklist of every technical gate that must close before Article 50 enforcement on August 2, 2026. Every item has an owner, a verification method, and a rollback plan. If any item is red on July 30, August 2 is at risk.

**Owner:** Founder
**Review cadence:** Daily 09:00 CET review starting July 15

---

## A — Operator readiness

| # | Item | Verification | Status | Rollback |
|---|---|---|---|---|
| A1 | EU operator (Fly.io Frankfurt) at 99.5% for trailing 30 days | status.ledgerproofhq.io historical | open | N/A (sustaining) |
| A2 | Load tested to 10M receipts/day sustained | k6 test report archived | open | Reduce customer scaling commitments |
| A3 | Bitcoin anchor commits at p95 < 30 minutes | Operator metrics dashboard | open | Manual fee-bump procedure |
| A4 | Bitcoin anchor never delayed > 24h | Daily alert + manual page | open | Multi-pool failover |
| A5 | Operator state recoverable from cold start in < 15 min | Disaster recovery drill report | open | Run drill weekly |
| A6 | All operator secrets in 1Password + Fly secrets store; mode 0600 on disk | Pre-flight audit | open | Rotate-and-pause |
| A7 | Legacy `iad` deployment untouched; 3 anchors still verify | Run verifier against canonical hashes | open | Do not modify |
| A8 | Per-customer rate limits enforced (default 100 req/s; configurable upward) | Synthetic test in CI | open | Reject upward |

## B — SDK readiness

| # | Item | Verification | Rollback |
|---|---|---|---|
| B1 | Python SDK 1.0.x stable for 14 days with no critical issues | GitHub issue tracker | Pin previous version |
| B2 | TypeScript SDK 1.0.x stable for 14 days | GitHub issue tracker | Pin previous version |
| B3 | LangChain integration tested against LangChain 0.3.x latest | CI matrix | Document last-known-good |
| B4 | SDK local queue + retry implemented (no inference blocking on operator unavailability) | Integration test | Revert to direct mode |
| B5 | SDK telemetry opt-out documented and respected | Privacy review | N/A |
| B6 | SDK SBOM published per release | GitHub release artifact | N/A |
| B7 | SDK 1.0 → 1.1 upgrade path tested with three downstream apps | Beta customer signoff | Revert |

## C — Verifier & registry readiness

| # | Item | Verification | Rollback |
|---|---|---|---|
| C1 | verify.ledgerproofhq.io load tested to 100x current traffic | k6 report | CDN tier upgrade |
| C2 | Verifier cold start < 2s p95 | RUM monitoring | Warm pool |
| C3 | Verifier verifies all v1.0 + v1.1 receipts (regression set: 1000 receipts) | CI gate | Block deploy |
| C4 | Canonical registry read-only API live at registry.ledgerproofhq.io | Smoke tests | N/A |
| C5 | Registry mirror published (S3 + IPFS) for trust-but-verify by third parties | Hash check | N/A |
| C6 | All published mapping documents reachable from verifier portal | Link check | N/A |

## D — Security readiness

| # | Item | Verification | Rollback |
|---|---|---|---|
| D1 | PR #1 merged or explicitly held with documented reason | Veronica approval | Hold open |
| D2 | Pentest scope signed; engagement starts before Aug 2 | Statement of Work countersigned | N/A |
| D3 | security@ledgerproofhq.io PGP key published; monitored 7d/wk | Test email + response | N/A |
| D4 | Dependency vulnerability scan in CI; no critical advisories unsuppressed | audit.toml + cargo-audit / pip-audit | Block deploy |
| D5 | Ed25519 signing key custody documented (1Password + hardware HSM by Day 60) | Custody doc reviewed by security advisor | N/A |
| D6 | DID document published at did.ledgerproofhq.io; public-key resolution tested | Browser test | Republish |
| D7 | All GitHub repos have branch protection on main; reviews required | Repo settings audit | N/A |

## E — Observability & SRE readiness

| # | Item | Verification | Rollback |
|---|---|---|---|
| E1 | PagerDuty (or Grafana OnCall) escalation paths configured | Test page | Manual escalation |
| E2 | Receipt-lifecycle distributed tracing covers issuance → anchor → confirmation | Sample trace inspected | Logs-only fallback |
| E3 | Status page (status.ledgerproofhq.io) live with auto-update from health checks | Manual incident test | Manual updates |
| E4 | Incident response runbook published internally; reviewed by founder | Runbook signoff | N/A |
| E5 | Customer notification email templates approved | Comms review | Manual drafts |
| E6 | Bitcoin anchor lag dashboard public | URL test | N/A |

## F — Developer experience readiness

| # | Item | Verification | Rollback |
|---|---|---|---|
| F1 | Quickstart: `pip install ledgerproof && python -m ledgerproof.demo` works in 90s on a clean machine | Macro test on macOS + Ubuntu | Document workaround |
| F2 | Quickstart: TypeScript equivalent works in 90s | Macro test | Same |
| F3 | LangChain quickstart published with 50-line example | Run example | N/A |
| F4 | OpenAI integration quickstart | Run example | N/A |
| F5 | Anthropic integration quickstart | Run example | N/A |
| F6 | Azure OpenAI integration quickstart | Run example | N/A |
| F7 | docs.ledgerproofhq.io has API reference auto-generated from SDK source | Build artifact | N/A |

## G — Spec readiness

| # | Item | Verification | Rollback |
|---|---|---|---|
| G1 | LPR v1.1 spec frozen at spec.ledgerproofhq.io/lpr-1.1 (immutable URL) | URL stability check | N/A |
| G2 | LPR v1.1.1 errata published if any spec ambiguities surfaced | Erratum log | N/A |
| G3 | LPR v1.2 working draft circulated to spec mailing list + Foundation Advisory | Mailing list archive | N/A |
| G4 | IETF Datatracker entry remains current; revision -01 submitted if needed | Datatracker | N/A |
| G5 | Mapping documents (ISO 42001, NIST RMF) published and linked from spec | URL test | N/A |

---

## Daily go/no-go decision matrix (July 15 → August 2)

**Green / Yellow / Red status per area each day.**

| Date | A — Operator | B — SDK | C — Verifier | D — Security | E — Observability | F — DevX | G — Spec | Decision |
|---|---|---|---|---|---|---|---|---|
| Jul 15 | | | | | | | | |
| Jul 16 | | | | | | | | |
| ... | | | | | | | | |
| Aug 1 | | | | | | | | **Final go/no-go** |

**Decision rule:** Any Red in A, B, C, D, or E = no-go without explicit founder override + documented mitigation. Yellow in F or G = acceptable; ship plan moves forward.

---

## Out of scope for Day 30 (explicit)

These are tracked but explicitly NOT August-2 gates:

- v1.2 spec frozen — Gate 2 (Day 60)
- US operator — Gate 2 (Day 60)
- Self-host operator reference impl — Gate 2 (Day 60)
- Go SDK alpha — Gate 2 (Day 60)
- SOC 2 Type 1 attestation — Gate 4 (Day 120)
- PQ migration design — Gate 4 (Day 120)
- Cross-protocol bridges (C2PA) — Gate 4 (Day 120)

Treat anyone proposing to pull them forward as a scope-expansion request requiring founder approval.

---

## Communication plan if a Red surfaces between July 25 and August 2

1. Founder posts in #eng-internal within 30 minutes of surfacing
2. Mitigation plan drafted within 4 hours
3. If mitigation cannot land before Aug 2, customers with pilots in flight are notified by Veronica personally within 24 hours
4. Public status page updates only after customer notification
5. No regulator notification unless the issue affects a stamp PDF that has been delivered to a regulator
