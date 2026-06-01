# LedgerProof Code Plan — V2 (Converged with 10X Playbook)

**Document version:** v2.0 (May 31, 2026)
**Supersedes:** [00-MASTER-CODE-PLAN.md](00-MASTER-CODE-PLAN.md) (v1.0, May 28, 2026)
**Owner:** Veronica S. Dawkins, Founder + Spec Lead (until Day 60); spec lead hire thereafter
**Operational substrate:**
- `CRIT_PATH.md` — 26-week table, 3 engineering deliverables per week
- `lpr-status.json` — machine-readable status fed from operator + CI, anchored weekly
- `win-conditions.json` — 9 binary pre-commitments, anchored quarterly

**This document is the architectural and doctrinal layer.** The week-by-week execution lives in `CRIT_PATH.md`. The runtime truth lives in `lpr-status.json`. If you find yourself reading this document for "what ships next Tuesday," you are in the wrong file.

---

## Inviolable constraints (verbatim — carried from v1, never to be removed)

- Never touch legacy `iad` deployment — those 3 anchors stay verifiable forever
- Secrets at `~/.ledgerproof-secrets/` mode 0600 — never commit
- GDPR safety net: emails forbidden at schema validation in `deployer_id`, `reviewer_role`, `review_rationale`
- Bitcoin OP_RETURN format: `"LPR1" || merkle_root_32` (36 bytes total) — DO NOT modify
- Never auto-merge PRs without explicit Veronica approval
- Recovery codes (PyPI, npm, GitHub) in 1Password ONLY — never in chat

---

## The Doctrine

Three principles. Every PR description references one in its body. If a change references none, it does not ship.

### P1 · The protocol survives the company

Every engineering decision that strengthens Foundation independence from Inc. compounds. Every line of code that requires LedgerProof Inc.'s service to be running for a customer to verify a receipt is debt — slated for refactor before Series A. The verifier, the test vectors, the canonical registry's read API, and the OpenTimestamps fallback all migrate to Foundation ownership before December 7.

*Operational implication:* every artifact gets a `@foundation`, `@inc`, or `@bridge` tag (see Foundation/Inc. Boundary Map below). The `@bridge` count must trend monotonically toward zero.

*Solutions traced:* SOL-FG-02 (Day-1 IP license), SOL-TECH-01 (test vectors at IETF), SOL-TECH-03 (vendored verifier-core), SOL-TECH-06 (operator conformance spec), SOL-FOUNDATION-GOV (anchor-of-last-resort).

### P2 · Publish the answer before they ask the question

Every objection a regulator, GC, or Series A partner raises in October exists by July 6 as a URL that loads in under 2 seconds. Cold conversations don't scale; forwardable engineering artifacts do. The cost of writing an artifact once is permanent; the cost of explaining it on a call is per-prospect-per-week.

*Operational implication:* every architectural decision generates a public document at `spec.ledgerproofhq.io/*` or `docs.ledgerproofhq.io/*` before it generates a code change. ADRs are the contract; commits implement the contract.

*Solutions traced:* SOL-OPS-01 (errata + museum), SOL-TECH-01 (test vectors), SOL-TECH-05 (versioning + PQ), SOL-PROTOCOL-GOV (bug bounty CSIRT).

### P3 · Veronica is not the bottleneck — or the protocol dies

Every Monday: which single-threaded engineering dependency did I remove this week? The federated on-call rotation, the multisig anchor key, the Foundation-owned GitHub org, the Doppler secret vault, the static verifier fallback, the per-customer SLO automation — each exists to remove the founder from the critical path of a 3am incident or a Tuesday merge.

*Operational implication:* every deliverable has a mandatory `founder_load_delta` column. Net delta across all in-flight work must be negative — if it isn't, no new work starts until existing work is offloaded.

*Solutions traced:* SOL-OPS-02 (federated on-call), SOL-OPS-04 (FIDO2 + Foundation org), SOL-OPS-06 (multi-region + static fallback), SOL-FP-01 (multisig custody), SOL-TECH-05 (TSC).

**Conflict resolution rule:** when P2 and P3 conflict (publishing artifacts costs founder bandwidth), P3 wins for the week and the artifact ships the following week. When P1 conflicts with anything, **P1 wins absolutely.**

---

## What dies from v1

**The 7-track × 5-gate deliverable grid.** It implied parallel-shipping by a team that does not exist. With one founder + 2–3 contractors through Day 60, the grid became a guilt-generation device. The tracks survive only as PR-description labels (E1–E7) — they do not survive as a planning instrument.

**The Risk Register as a list.** Replaced by the Engineering Circuit Breakers table — risk-as-an-observable-trigger, not risk-as-a-narrative. Every risk that mattered in the v1 register either has a circuit breaker observable in v2, or it was not actually a load-bearing risk.

**"Day N hardening checklist" as the planning unit.** Replaced by the doctrine principles + the bandwidth audit. The hardening checklists survive as **implementation specs** referenced by the wedge/moat sections — they are documentation, not the plan.

## What survives from v1

**The seven cross-track invariants** (still load-bearing — these are protocol-level commitments, not planning instruments):

1. **Receipt format is append-only.** New fields are additive. Old receipts always verify under current readers. Enforced in CI via the `lpr-test-vectors` corpus.
2. **Profile system absorbs regulatory change.** No customer-side breaking changes from Code-of-Practice evolution.
3. **No PII at the anchor layer.** Schema rejection at parse time; pentest scope explicitly tests this.
4. **No content data leaves the customer's perimeter.** Only hashes and metadata. Pentest scope tests this.
5. **The verifier never depends on the operator.** A customer using our operator can verify with the public reference verifier and the public Bitcoin chain alone. Day-180 enforcement: the verifier ships as a 30 KB single-file HTML bundle (`lpr-verifier-audit.html`) that loads with zero network egress.
6. **Versioned everything.** Every published artifact has a version, a deprecation policy, and a migration path.
7. **Tamper-evidence dogfooding.** Foundation publishes its own incident reports, transparency reports, and Code-of-Practice consultation submissions as receipts.

**The seven track labels** (E1 Protocol & Spec, E2 SDKs, E3 Operator, E4 Verifier & Registry, E5 Security & Cryptography, E6 Observability & SRE, E7 Developer Experience). These continue to label PR scopes and CODEOWNERS routing. They are no longer a planning grid.

---

## The 7-Day Engineering Hot Path (Jun 1–7, 2026)

Engineering work only. Commercial/Foundation/Financial items live in the master playbook's hot path.

| # | Engineering action | Owner | Done when | Founder-load delta |
|---|---|---|---|---|
| **E1** | **Revoke `ghp_…1ZBl93` on github.com/settings/tokens.** Rotate every CI secret. Move repos out of Dropbox-synced path to `~/dev/ledgerproof/`. Verify `find ~/dev -name config -path "*/.git/*" \| xargs grep -E 'ghp_'` returns empty. | Veronica | Jun 1 EOD; GitHub audit log shows revoke; new fine-grained PATs in 1Password | +3 hr now, **−4 hr/wk** ongoing *(SOL-OPS-04)* |
| **E2** | **Hold broken `verify.ledgerproofhq.io/r/founding-declaration` and `/r/0` behind a "Coming July 6" holding page.** Single-line edit to `ledgerproof-verifier/index.html` + Vercel redeploy. | Veronica | Jun 1 EOD; `curl -s https://verify.ledgerproofhq.io/r/founding-declaration` returns holding markup | **−12 hr/wk** of incoming "why does this fail?" replies *(SOL-OPS-01, SOL-NAR-02)* |
| **E3** | **Bisect the canonicalization bug.** Compare Rust `serde_json` output for Entry #0 against `@noble/hashes` SHA-256 over the same input bytes. Identify exact byte-diff (likely JCS RFC 8785 key ordering vs. ad-hoc). | Veronica + Filippo Valsorda ($8K scope review) | Jun 3; root cause documented in draft `LPR-ERRATA-001.md` | +8 hr now, **−∞ hr** of future debug *(SOL-TECH-01)* |
| **E4** | **Engage Trail of Bits for canonicalization-only fixed-scope review.** Email Dan Guido (dan@trailofbits.com). $45–65K, two-week engagement. | Veronica | Jun 2; SOW signed; Jun 5 kickoff | One-time *(SOL-FIN-01, SOL-TECH-01)* |
| **E5** | **Order 4× YubiKey 5C NFC; open Unchained Capital Business Vault.** 2-of-3 multisig (Veronica / Unchained / Foundation-escrow). | Veronica | Jun 7; KYC submitted; keys in mail | **−5 hr/wk** ongoing *(SOL-FP-01, SOL-FG-06)* |
| **E6** | **Move launch repo and locker repo out of Dropbox path.** `~/dev/ledgerproof/launch/`, `~/dev/ledgerproof/locker/`, symlinks back if needed. | Veronica | Jun 1 alongside E1; no PATs remain on disk | **−ambient risk surface** *(SOL-OPS-04)* |
| **E7** | **CI test: hash a 100-entry corpus identically in Rust and TypeScript; fail the build on drift.** Add to ledgerproof-platform CI matrix. | Veronica | Jun 6; PR opened against current `feat/lpr-v1.1-article-50-expansion` | +6 hr now, **−all future canonicalization drift** *(SOL-TECH-01, SOL-TECH-06)* |
| **E8** | **Cut a `v1.1.1-pre` SDK release on Python + TS that pins `@noble/*` to known-good SHA-pinned versions** and adds SLSA L1 provenance. Stage only — not published. | Veronica | Jun 7; staging registry holds the release; `npm view @ledgerproof/sdk@1.1.1-pre.0` returns the metadata | One-time *(SOL-TECH-03, SOL-OPS-07)* |

**Cumulative this week:** +25 hr one-time effort, then **−21 hr/wk steady-state from Jun 8 onward**. Net: pays itself back by Jun 19. Pre-launch margin: 9 days.

Everything not on this list is interruption.

---

## The 30-Day Compounding Wedge (by Jun 30)

Grouped by which doctrine principle each play serves. Every item has owner, deadline, founder-load delta.

### P1 plays — the protocol survives the company

**P1.1 · `lpr-test-vectors v0.2.0` as IETF normative reference.** A Foundation-owned conformance corpus that any third-party implementation must pass. `vec-001-entry-zero-historical` becomes the founding artifact (the broken Entry #0 plus the corrected one, both with full byte-level diff). Submit `draft-dawkins-scitt-ai-article50-01` referencing the corpus as normative.
- Owner: Veronica + senior-rust-cryptography contractor
- Deadline: Jul 15 (post-launch by 9 days; pre-IETF 121 Dublin by 4 months)
- Load: +12 hr drafting, **−all future drift triage**
- *(SOL-TECH-01)*

**P1.2 · Day-1 perpetual royalty-free IP license: Inc. → Foundation, executed at USPTO.** Engineering touchpoint: `LICENSE` and `NOTICE` files across all 11 public repos update to cite Foundation copyright with Inc. as one of multiple operators. The license is perpetual, royalty-free, irrevocable, sublicensable.
- Owner: Adler & Colvin + Veronica
- Deadline: Jun 15
- Load: **−12 hr** vs. negotiating under duress later
- *(SOL-FG-02, SOL-FIN-04)*

**P1.3 · `@ledgerproof/verifier-core` vendored.** SLSA L3 attestations on every release. A 30 KB single-file `lpr-verifier-audit.html` that loads with zero network egress and verifies any LPR receipt against a local Bitcoin block-header dump. Ships in `ledgerproof-spec` repo, signed by Foundation key.
- Owner: Senior product engineer hire
- Deadline: Jul 6 (launch day artifact)
- Load: +20 hr week one, **−verifier maintenance forever**
- *(SOL-TECH-03, SOL-NAR-06)*

**P1.4 · Foundation owns the `ledgerproof` GitHub org.** Migrate from `vsdawkins-creator/*` namespace. Two-factor mandatory; signed commits required on `main`; org owner = Veronica + one independent (Mishi Choudhary candidate). All public repos move; private operator repo stays under Inc. namespace.
- Owner: Veronica
- Deadline: Jun 22
- Load: +8 hr migration, **−ambient supply-chain risk**
- *(SOL-OPS-04)*

### P2 plays — publish the answer before they ask

**P2.1 · `LPR-ERRATA-001` published at `spec.ledgerproofhq.io/errata/001`** with byte-diff, root cause, repro instructions, Trail of Bits validation letter. The museum page at `docs.ledgerproofhq.io/entries/0` explains why the broken Entry #0 is enshrined, not erased.
- Owner: Veronica + ToB validation
- Deadline: Jun 17
- Load: +8 hr writing, **−6 hr/wk ongoing**
- *(SOL-OPS-01, SOL-NAR-02)*

**P2.2 · Fee policy v1.0** at `spec.ledgerproofhq.io/fee-policy-v1`. Soft-1h / hard-24h anchor SLO; RBF fee-bump behavior; fee-ceiling-then-batch fallback; OpenTimestamps escalation path if Bitcoin mempool stays congested >24h.
- Owner: Veronica + Rust contractor ($8K)
- Deadline: Jun 28
- Load: +6 hr writing, **−on-call hours during fee spikes**
- *(SOL-OPS-03, SOL-TECH-02)*

**P2.3 · Versioning policy** at `spec.ledgerproofhq.io/versioning-v1`. OP_RETURN tag-bump rule for breaking changes (current: `LPR1`; future: `LPR2` is breaking, `LPR1.A` is additive). 10-year backward-compat commitment. Dual-tag interregnum semantics. Profile system documented as the additive evolution path.
- Owner: Veronica
- Deadline: Jul 1
- Load: +25 hr setup, **−all "should I break the schema" decisions** (TSC owns it from Day 90)
- *(SOL-TECH-05)*

**P2.4 · Slug-router threat model** at `spec.ledgerproofhq.io/threat-models/slug-router`. STRIDE; append-only constraint; signed slug-map anchor. Renders the underlying receipt ID prominently so the slug is decorative.
- Owner: Veronica + senior-vc-diligence-engineer review pass
- Deadline: Jun 24
- Load: +4 hr writing, **−every "is the slug a security hole" diligence question**
- *(SOL-TECH-03)*

**P2.5 · Operator conformance spec v0.1** at `spec.ledgerproofhq.io/operator-conformance-v0.1`. Defines the minimum behavior any LedgerProof operator must implement to claim conformance. Cross-region reconciliation proofs published in a public append-only log. Inc.'s EU operator must pass its own conformance suite — dogfooded by design.
- Owner: Veronica + SRE contractor
- Deadline: Jul 7 (one day post-launch — first non-Inc operator certification target = Day 90)
- Load: +30 hr setup, **−drift triage forever**
- *(SOL-TECH-06)*

### P3 plays — Veronica is not the bottleneck

**P3.1 · Federated on-call via PagerDuty + two EU-resident SRE contractors** under Foundation MoU. Mathias Lafeldt + one Honeycomb-alumni candidate. $8K/mo retainer each. Onboard 21 days before launch.
- Owner: Veronica recruits, then steps back
- Deadline: Jun 15 (contractors signed; rotation live)
- Load: **−20 hr/wk by Aug 1**
- *(SOL-OPS-02)*

**P3.2 · Multi-region active-active (Fly.io `fra` + `ams`) + static verifier fallback on Cloudflare Pages.** Game-day rehearsal Jun 22; production cutover Jun 28. The static fallback bundle is signed by Foundation key and serves as the disaster-recovery verifier.
- Owner: SRE contractor
- Deadline: Jun 28
- Load: **−8 hr/wk** of launch-week anxiety
- *(SOL-OPS-06)*

**P3.3 · Doppler secret vault + redaction middleware + GlitchTip self-hosted.** Eliminates the entire secret-leak class. Per-job ephemeral tokens in CI. Redaction middleware in the API layer strips known credential patterns from any outbound response or error log.
- Owner: Senior product engineer hire
- Deadline: Jul 1
- Load: **−4 hr/wk** routine + **−one whole risk category**
- *(SOL-OPS-07)*

**P3.4 · `status.ledgerproofhq.io`** rendering `lpr-status.json` anchored weekly to Bitcoin. Replaces monthly investor PDFs forever. Anyone — investor, customer, regulator — gets the same machine-readable truth.
- Owner: Veronica builds (12 hr investment)
- Deadline: Jun 7
- Load: +12 hr setup, **−all bespoke status updates**
- *(SOL-META-01)*

---

## The 90-Day Engineering Moat Construction (by Aug 30)

By Day 90, Article 50 has been enforced for 28 days. The technical posture must be: shipped, scaled, audited, evolving — and structurally hard to replicate.

### Protocol moats

- **Federated anchor aggregation + OpenTimestamps fallback live.** Three operators (Frankfurt, US, EU-academic) running. Aggregation reduces per-receipt OP_RETURN cost by ~95% via Merkle batching. *(SOL-TECH-02, SOL-TECH-06)*
- **Cure53 verifier audit published.** Slug-router property-based tests in CI. Bundle signed with SLSA L3 provenance. *(SOL-TECH-03)*
- **LPR Versioning Policy + PQ Roadmap ratified by Foundation Technical Steering Committee (TSC).** Hybrid Ed25519+ML-DSA-65 preview branch open in `ledgerproof-spec`. The TSC is the structural answer to "founder bottleneck on spec decisions." Three TSC seats: Foundation chair, Inc. CTO, independent (target: Henry de Valence or Jameson Lopp). *(SOL-TECH-05)*
- **Operator Conformance spec v1.0** ratified. First non-Inc operator certified — target candidate: an EU-academic operator (Eindhoven or KU Leuven). Public reconciliation log live. *(SOL-TECH-06)*
- **€100K Immunefi bug bounty live**, funded by Foundation, scope = receipt format + verifier + canonicalization + slug router + supply-chain. *(SOL-PROTOCOL-GOV)*
- **Anchor-agnostic multi-chain spec drafted** (kills "crypto-bro project" objection without committing to multi-chain — the spec exists, the operator stays Bitcoin-only). *(SOL-GEO-01)*

### Operational moats

- **99.9% sustained for 30+ days** across EU + US active-active. UK provisioned but cold (warm switchover documented; activation deferred to Day 120). *(SOL-OPS-02, SOL-OPS-06)*
- **RBF-aware anchor with mempool.space partnership for fee oracle.** Published worst-case SLO. Degraded-mode operation documented and tested. *(SOL-OPS-03)*
- **Foundation-Held Anchor-of-Last-Resort:** cold-storage Foundation key that can issue a recovery anchor receipt if Inc. service dies for >30 days. Spec-as-survivable-asset. Key ceremony attended by Foundation board + independent crypto witness. *(SOL-FOUNDATION-GOV)*
- **Chaos game-days monthly** starting Jul 22. Each tests one specific failure: anchor-stall, region-loss, signing-key-rotation, canary-bad-release, DNS-poisoning. Each produces a runbook delta. *(SOL-OPS-02, SOL-OPS-06)*

### Distribution moats (engineering surface)

- **AWS Marketplace listing live by Aug 1** via CloudTango fast-track + three design-partner customer-requested escalations. *(SOL-DIST-03)*
- **Compliance Stamp PDF generator + `Verified-by-Article-50` badge widget.** Each verification renders an HTML widget the customer can embed; each embed becomes a marketing event because every visitor sees Foundation branding + verifier link. *(SOL-DIST-05)*
- **DORA Annex v0.1 published Jul 5.** MiFID II annex by Sep 30. NIS2 and MAS FEAT outlines. Each annex is a profile + a public mapping document. *(SOL-DIST-06)*
- **`lpr-verifier` CLI signed with Sigstore + offline bundle.** Verifier console at `verify.ledgerproofhq.io/cli` documents the CLI alongside the web verifier. *(SOL-NAR-06)*

### Security moats

- **Trail of Bits canonicalization-only audit memo published** (from the Day 1–17 engagement). *(SOL-FIN-01, SOL-TECH-01)*
- **Latacora supply-chain review published.** Scope: SDK dependency tree, CI provenance, release-signing posture, secret management. *(SOL-OPS-04, SOL-OPS-07)*
- **Pentest #1 by NCC Group or Bishop Fox** completed and report published at `security.ledgerproofhq.io/pentest/2026-08-ncc`. Findings remediated within the engagement window. *(SOL-FIN-01)*

---

## The 180-Day Engineering Posture (Dec 7 — Series A open)

The narrative the Series A diligence engineer reads in 20 minutes (the "fund-us-tomorrow" Series A list, engineering subset):

| Track | Status by Dec 7 |
|---|---|
| **Spec** | LPR v1.2 stable in production for 90+ days. v2.0 PQ design RFC circulated at IETF 121 Dublin (Nov 2–7). TSC operating. |
| **SDKs** | Python + TS at 1.x stable. Go alpha (deferred GA). Java alpha (deferred GA). .NET deferred to Q1 2027 (in kill list). |
| **Operator** | EU + US + UK at 99.9% for 90 consecutive days. Three independent operators in the federation (Inc. + 2 non-Inc.). Asia provisioning plan signed off; activation Q1 2027. |
| **Verifier + Registry** | 100K+ verifications/month. Cure53 audit published. Static fallback bundle downloadable. Slug router formally threat-modeled. Foundation-owned read API. |
| **Security** | SOC 2 Type 1 attestation in hand. Type 2 mid-fieldwork. ToB + Latacora + Cure53 audits all published. Bug bounty has paid at least one valid report. |
| **Observability** | Public status page with historical SLO. Incident reports anchored as receipts. Per-customer SLO dashboards GA. |
| **DX** | Docs at `docs.ledgerproofhq.io` with API ref, conceptual guides, runbooks. Quickstarts for Python, TS, LangChain, OpenAI, Anthropic, Azure OpenAI, Vertex AI, Bedrock. |

---

## Engineering Circuit Breakers (Friday 17:00 CET review)

The engineering-only subset of the playbook's circuit breakers. Tripping one is not a failure; ignoring one is.

| Date | Observable | If-then |
|---|---|---|
| **Jun 16** | ToB validates Entry #0 fix? | If NO: hold launch announcement; escalate to senior-rust-cryptography network (Filippo Valsorda, Henry de Valence). Do not re-issue under uncertainty. |
| **Jun 22** | Multi-region game-day passed? | If NO: postpone US operator cutover one week; do not stand up UK before EU+US chaos clean. |
| **Jun 28** | Federated on-call rotation has owned ≥1 simulated incident? | If NO: extend onboarding 14 days; founder stays primary pager through Jul 12. |
| **Jul 6** | Verifier green on Entry #0-bis AND SLSA L3 attestations on every release artifact AND `lpr-verifier-audit.html` ≤32 KB? | If verifier red OR attestations missing OR bundle >40 KB: postpone Big-4 Working Group kickoff 14 days. |
| **Jul 31** | CTO of Protocol signed offer? **HARD DEADLINE.** | If NO: protocol successor retainer with Jameson Lopp activates ($25K/yr); pause any spec-changing PR; defer LPR v1.2 spec work 60 days. |
| **Aug 16** | EU operator at 99.9% for the first 14 days of Article 50 enforcement? | If NO: trigger SOL-OPS-02 expansion (third SRE contractor); declare a 30-day code freeze on E1/E4. |
| **Sep 15** | IETF WG adoption sponsor secured for draft-01? | If NO: downgrade to Independent Submission. Pursue CEN-CENELEC JTC 21 NWIP as primary standards path. |
| **Oct 15** | SOC 2 Type 1 attestation received? | If NO: pause new pilot signings; redirect 30% of engineering capacity to audit remediation. |
| **Nov 15** | Bug bounty has paid ≥1 valid report by this date? | If NO and 0 reports: scope is wrong (bounty insufficient or scope too narrow); revise scope, double bounty pool. |

---

## Foundation/Inc. Boundary Map

Every engineering artifact gets one of three tags. The tags drive CODEOWNERS, repo ownership, copyright headers, release-signing keys, and CI/CD secrets.

### `@foundation` artifacts

Foundation owns IP, signs releases, publishes spec, governs change.

| Artifact | Repo | License | Day owned-by-Foundation |
|---|---|---|---|
| LPR Specification + IETF drafts | `ledgerproof-spec` | Apache-2.0 + CC-BY-4.0 (drafts) | Jun 15 |
| Conformance test vectors | `lpr-test-vectors` | Apache-2.0 | Jul 15 |
| Reference verifier core | `verifier-core` | Apache-2.0 | Jul 6 |
| Reference verifier UI | `verifier-ref` | Apache-2.0 | Day 60 |
| Reference self-hosted operator | `operator-ref` | Apache-2.0 | Day 60 |
| Regulation mappings (ISO 42001, NIST RMF, DORA, MiFID II) | `mappings` | CC-BY-4.0 | Jun 30 |
| Foundation governance records | `governance` | CC-BY-4.0 | Day 30 |
| Bug bounty scope + CSIRT runbook | `security-policy` | CC-BY-4.0 | Day 60 |

### `@inc` artifacts

LedgerProof Inc. owns; commercial service code; never required for receipt verification by any third party.

| Artifact | Repo | Notes |
|---|---|---|
| EU operator deployment configs + runbooks | `ledgerproof-platform/operator-eu` | Private |
| US operator | `ledgerproof-platform/operator-us` | Private, lazy-init |
| UK operator | `ledgerproof-platform/operator-uk` | Private, Day 90+ |
| Billing + customer dashboard | `ledgerproof-platform/billing` | Private |
| Commercial Stamp PDF tier features | `ledgerproof-platform/stamp-pro` | Private |
| Sales tooling (`10-gtm-code/`) | `LedgerProof-Launch-July6/10-gtm-code` | Private, OSS at Foundation discretion |

### `@bridge` artifacts (must migrate by Series A)

Lives at Inc. now, migrates to Foundation by Day 180. Any remaining `@bridge` on Dec 7 is a Series A diligence finding.

| Artifact | Current owner | Target migration date |
|---|---|---|
| Canonical Registry read API | Inc. | Day 90 → Foundation |
| Stamp PDF generation pipeline (free-tier) | Inc. | Day 120 → Foundation |
| Incident response runbook | Inc. | Day 90 → Foundation |
| Fee policy implementation | Inc. | Day 90 → Foundation |
| `lpr-status.json` schema + signing | Inc. | Day 60 → Foundation |
| Public docs site (`docs.ledgerproofhq.io`) | Inc. | Day 120 → Foundation |

**Enforcement:** CI fails any PR that increases the `@bridge` count without an explicit `bridge-justification:` trailer in the commit message. The `@bridge` count is published weekly in `lpr-status.json` and reviewed at the Friday circuit-breaker meeting.

---

## Engineering Bandwidth Audit

Mandatory column on every deliverable. Net engineering bandwidth delta over 180 days must be **strongly negative** — net buys founder bandwidth back.

| Solution | Founder load delta | Why |
|---|---|---|
| SOL-OPS-01 errata + museum | **−6 hr/wk** after Jun 17 | No more ad-hoc "why is Entry #0 broken?" replies |
| SOL-OPS-02 federated on-call | **−20 hr/wk** by Aug 1 | Founder no longer primary pager |
| SOL-OPS-04 FIDO2 + Foundation org | **−4 hr/wk** ongoing | Secret rotation is routine, not fire drill |
| SOL-OPS-06 multi-region + static fallback | **−8 hr/wk** of launch-week anxiety | Off the founder's neck during July 6 |
| SOL-OPS-07 Doppler + redaction middleware | **−4 hr/wk** | Eliminates the secret-leak triage class |
| SOL-TECH-01 test vectors + ToB | +12 hr drafting, **−all future-debug** | One-time write, permanent return |
| SOL-TECH-02 federated anchor + OTS fallback | **−on-call hours during fee spikes** | Capped fee → no pager during congestion |
| SOL-TECH-03 vendored noble + SLSA L3 + Cure53 | +20 hr Week 1, **−verifier maintenance forever** | Audited dependency surface |
| SOL-TECH-05 versioning + PQ + TSC | +25 hr setup, **−all schema-break decisions** | TSC owns it from Day 90 |
| SOL-TECH-06 operator conformance | +30 hr setup, **−drift triage forever** | First non-Inc operator certified at Day 90 |
| SOL-PROTOCOL-GOV €100K bounty + CSIRT | +10 hr setup, **−security-triage hot seat permanently** | External researchers do the work |
| SOL-FOUNDATION-GOV anchor-of-last-resort | +6 hr key ceremony, **−existential risk** | Foundation can survive Inc. failure |
| SOL-FG-02 Day-1 IP license | **−12 hr** vs. negotiating under duress | Front-loaded |
| SOL-META-01 `lpr-status.json` | +12 hr build, **−all bespoke status updates** | Self-service truth |

**Net engineering bandwidth delta:** ~**−40 hr/wk by Aug**, ~**−55 hr/wk by Nov**. Plan passes its own test.

If a new deliverable proposal does not have a net-negative `founder_load_delta`, it does not enter the plan. Period.

---

## Engineering Kill List

Engineering work cut per the 10X filter. Tracked here so future-Veronica doesn't reach for it again without checking why it was cut.

- **SOL-OPS-05 — canary-channel SDK release train + replay suite.** Right idea, wrong stage. A single founder pre-launch cannot get pilot customers to opt traffic into a replay suite they don't trust yet. **Defer to Q1 2027** when ≥5 paying pilots exist. Fold the alpha/canary/stable dist-tags into normal release hygiene; skip the replay infrastructure for now.
- **Go SDK 1.0 by Day 90.** Cut to alpha only. **Defer GA to Q1 2027.** The Day-180 narrative does not require Go GA. Frees 4 engineering weeks for E3/E4 moats.
- **.NET SDK alpha by Day 120.** Cut entirely. **Defer to Q2 2027.** Azure FSI customers can integrate via the TS SDK + edge adapter through Series A.
- **Java SDK 1.0 by Day 180.** Cut to alpha only. A serious Java SDK demands 6+ weeks of engineering; Day 180 narrative does not require GA Java.
- **Registry GraphQL API by Day 120.** Cut. REST + JSON is sufficient through Series A. GraphQL is a 2027 ergonomics improvement, not a structural moat.
- **Cookiecutter / scaffold tooling published.** Cut from Day 120. The 6 quickstarts cover this need; scaffolding adds maintenance debt for marginal acquisition lift.
- **Per-customer SLO dashboards GA at Day 90.** De-scoped — the customer-facing SLO surface ships as a per-customer JSON endpoint at Day 90 (no UI), with a dashboard UI deferred to Day 150. UI is decorative; the JSON is load-bearing.
- **AWS Well-Architected Lens partnership.** Cut. Folded into the AWS Marketplace listing via CloudTango. Lens partnership is a 2027 ambition.

Each cut frees engineering capacity for the P1/P2/P3 plays that move the structural needle.

---

## Forwardable Engineering Artifacts (the P2 deliverable set)

Every artifact in this list is a URL a Series A diligence engineer can load in under 2 seconds. None requires the founder to be on a call.

| URL | What it is | Owner | Ships by |
|---|---|---|---|
| `spec.ledgerproofhq.io/errata/001` | Canonicalization bug write-up + ToB validation | Foundation | Jun 17 |
| `docs.ledgerproofhq.io/entries/0` | Entry #0 museum page | Foundation | Jun 17 |
| `spec.ledgerproofhq.io/fee-policy-v1` | Anchor SLO + RBF behavior + OTS fallback | Foundation | Jun 28 |
| `spec.ledgerproofhq.io/versioning-v1` | OP_RETURN tag rules + 10-year backward-compat commitment | Foundation | Jul 1 |
| `spec.ledgerproofhq.io/threat-models/slug-router` | STRIDE threat model | Foundation | Jun 24 |
| `spec.ledgerproofhq.io/operator-conformance-v0.1` | Operator conformance spec | Foundation | Jul 7 |
| `spec.ledgerproofhq.io/pq-roadmap` | Post-quantum migration plan | Foundation | Day 90 |
| `security.ledgerproofhq.io/pentest/2026-08-ncc` | Pentest #1 report | Inc. → Foundation | Day 90 |
| `security.ledgerproofhq.io/tob/2026-06-canonicalization` | Trail of Bits audit memo | Inc. → Foundation | Day 30 |
| `security.ledgerproofhq.io/latacora/2026-07-supply-chain` | Latacora supply-chain review | Inc. → Foundation | Day 45 |
| `security.ledgerproofhq.io/cure53/2026-08-verifier` | Cure53 verifier audit | Foundation | Day 90 |
| `verify.ledgerproofhq.io/cli` | Signed CLI verifier docs + offline bundle | Foundation | Day 90 |
| `status.ledgerproofhq.io` | Live status page, anchored weekly | Inc. → Foundation Day 60 | Jun 7 |
| `bounty.ledgerproofhq.io` | Immunefi bug bounty scope | Foundation | Day 90 |

The forwardable-artifact list IS the marketing surface. The Article 50 Watchlist newsletter links to these URLs; the Big-4 working group references these URLs; the Series A diligence pack is a DocSend containing these URLs as PDF prints.

---

## Repository Topology V2

The 11 public repos under `github.com/ledgerproof/` get re-tagged. Migration from `vsdawkins-creator/*` namespace is a P1.4 task.

```
github.com/ledgerproof/   (@foundation org)
├── ledgerproof-spec/             ← LPR specification + IETF draft sources
├── lpr-test-vectors/             ← Conformance corpus, NEW at Day 30
├── verifier-core/                ← Vendored verification library, NEW at Day 30
├── verifier-ref/                 ← Reference verifier UI (SPA + 30 KB single-file)
├── operator-ref/                 ← Reference self-hosted operator
├── ledgerproof-py/               ← Python SDK
├── ledgerproof-ts/               ← TypeScript SDK
├── ledgerproof-go/               ← Go SDK (alpha through Series A)
├── ledgerproof-java/             ← Java SDK (alpha through Series A)
├── langchain-ledgerproof/        ← LangChain integration
├── mappings/                     ← ISO 42001, NIST RMF, DORA, MiFID II
├── governance/                   ← Foundation governance + Advisory Council records
└── security-policy/              ← Bug bounty scope, CSIRT runbook, threat models

github.com/ledgerproof-inc/   (@inc org)
└── ledgerproof-platform/         ← Operator monorepo (private)
```

**Visibility rule:** anything a customer needs to verify a receipt without trusting LedgerProof Inc. is **public**. Anything proprietary to the commercial service is private. The Foundation owns the spec, mappings, reference implementations, and the verifier.

---

## CI / Release / Signing Posture

The P1 + P2 implications for the build pipeline:

- **All release artifacts get SLSA L3 provenance** by Day 60. GitHub Actions workflow templates published in `governance/`.
- **All releases signed with Sigstore + Foundation key.** No raw `npm publish` or `cargo publish` from a developer machine. Day 30.
- **Cross-language hash conformance tests in CI** on every PR. Day 7 (E7 of the hot path).
- **Branch protection on `main`** for all `@foundation` repos: required reviews from 2 owners, signed commits, status checks, no force-push. Day 30.
- **PyPI Trusted Publishers (OIDC).** No PyPI tokens on disk. Day 30.
- **npm 2FA-on-publish + provenance attestations.** Day 30.
- **Gitleaks + Trufflehog as pre-commit hooks + CI step.** Day 30.

---

## Technical Steering Committee (TSC) Charter Sketch

The TSC is the structural answer to "founder bottleneck on spec decisions" — and the P1 enforcement layer for the spec.

- **Three seats:** Foundation chair (Veronica through Day 180; rotates to Foundation ED after), Inc. CTO (the CTO-of-Protocol hire, deadline Jul 31), one independent (target: Henry de Valence or Jameson Lopp).
- **Quorum:** 2 of 3.
- **Veto:** the independent seat has explicit veto on any breaking spec change.
- **Cadence:** monthly synchronous review; async PR review otherwise.
- **Scope:** versioning decisions, profile additions, PQ migration timing, conformance test additions.
- **Out of scope:** operator implementation details, commercial pricing, marketing.
- **Records:** all decisions published as receipts in `governance/` and anchored to Bitcoin.

Charter v0.1 drafted Jul 15; ratified by Foundation board at Day 90 meeting.

---

## Engineering Hiring Sequence (trimmed from v1)

| # | Role | Trigger | Latest hire |
|---|---|---|---|
| 1 | Senior Product Engineer (SDK + DevX) | Day 0 — seed close | Day 30 |
| 2 | Web Engineering Consultant (verifier UX + Stamp PDF) | Day 0 — seed close | Day 30 |
| 3 | Senior Rust Cryptography Contractor (canonicalization + test vectors) | Day 1 — Trail of Bits engagement | Day 14 |
| 4 | SRE Contractor #1 (Mathias Lafeldt) | Day 0 — federated on-call | Day 15 |
| 5 | SRE Contractor #2 (Honeycomb alumni) | Day 0 — federated on-call | Day 15 |
| 6 | Spec Lead / CTO of Protocol | Day 30 | **Day 60 hard deadline (circuit breaker Jul 31)** |
| 7 | Security Advisor (fractional → full Day 120) | Day 30 — pentest kickoff | Day 60 |
| 8 | Foundation ED (interim → permanent) | Day 60 | Day 120 |
| 9 | DevRel | Day 90 — marketplace launches imminent | Day 120 |
| 10 | Cryptography Researcher (PQ migration) | Day 120 — v2.0 RFC | Day 180 |

The Day-180 engineering org: founder + 8 (2 contractors, 6 FTE + 2 fractional). The Series A funds the next wave; this plan does not.

---

## Engineering Budget Envelope (engineering subset of seed)

| Category | Day 0–180 spend |
|---|---|
| Engineering headcount (founder + 6 FTE + 2 fractional) | ~$1.4M annualized at Day 180 |
| Cloud + infra (Fly.io EU + US + UK; Cloudflare; mempool.space partnership) | ~$240K |
| Security audits (Trail of Bits + Latacora + Cure53 + NCC pentest) | ~$180K |
| Bug bounty pool (Foundation-funded, Immunefi-hosted) | ~$100K |
| Tooling (CI, observability, Doppler, GlitchTip, PagerDuty) | ~$60K |
| Conferences + standards travel (IETF 121 Dublin, CEN-CENELEC JTC 21) | ~$40K |
| **Engineering total Day 0–180** | **~$2.0M** |

Up from v1's ~$1.9M (added bug-bounty pool). Still ~60% of the engineering envelope reserved for capability creation vs. ~40% for security/audit/cloud — appropriate ratio for a pre-Series-A protocol company.

---

## What this V2 document replaces

- [`09-code-plan/00-MASTER-CODE-PLAN.md`](00-MASTER-CODE-PLAN.md) — archived. Reads V2 in tandem with the Doctrine + Kill List as the planning instrument. V1 survives only for historical reference of the originally-conceived 7-track gate grid.
- [`09-code-plan/day-{30,60,90,120,180}/*.md`](.) — kept as **implementation specs** referenced by the wedge/moat sections. They are documentation, not the plan.
- The Engineering Risk Register from v1 — folded into the Engineering Circuit Breakers table. Risk-as-an-observable-trigger replaces risk-as-a-narrative.

## What this V2 document adds

- The **doctrine** as the first filter for every engineering decision (P1, P2, P3).
- The **Foundation/Inc. boundary map** as a top-level engineering constraint, not a Q1 2027 deliverable.
- The **bandwidth audit** as a mandatory column on every deliverable.
- The **kill list** as a structural part of the plan, with rationale for each cut.
- The **forwardable engineering artifacts** table as the engineering surface of the P2 doctrine.
- The **TSC charter sketch** as the structural answer to founder-as-spec-bottleneck.
- `lpr-status.json` + `win-conditions.json` + `CRIT_PATH.md` as the **operational substrate** the plan is read against.

---

## Migration plan (how to actually swap V1 for V2)

1. **Today:** commit this file (`00-MASTER-CODE-PLAN-V2.md`) alongside V1.
2. **Today + 1:** update [`PLAN.md`](../PLAN.md) integrator to reference V2 as the canonical engineering plan; V1 becomes "historical reference."
3. **Today + 7:** prepend a header to [`00-MASTER-CODE-PLAN.md`](00-MASTER-CODE-PLAN.md) v1 marking it archived as of May 31, 2026, with a redirect to V2.
4. **Day 30:** build `CRIT_PATH.md` (26-week table) by extracting all deliverables from V2 + the playbook into a single week-indexed grid. The day-{30,60,90,120,180}/ files become implementation specs referenced from `CRIT_PATH.md`.
5. **Day 30:** stand up `lpr-status.json` schema + endpoint. First weekly anchor by Jun 7.
6. **Day 60:** the V2 plan is the only document used in weekly engineering review. V1 is archived; new engineers onboarded against V2.

---

## End of plan. Monday begins with hot-path item E1: revoke the PAT.
