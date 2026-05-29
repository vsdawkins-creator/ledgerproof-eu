# Release Process

**Purpose:** Single, consistent release process for SDKs, connectors, reference operator, reference verifier, and (with extensions) the commercial operator. Optimized for high frequency of safe, small releases — not low frequency of large ones.

---

## Release cadence

| Artifact | Cadence target |
|---|---|
| Python SDK | Every 2 weeks (patch); every 6 weeks (minor) |
| TypeScript SDK | Same |
| Go / Java / .NET SDKs | Every 4 weeks |
| Connector packages | Tracks upstream provider releases with ≤ 2-week lag |
| LangChain integration | Tracks LangChain minor releases |
| Reference operator | Every 4 weeks |
| Reference verifier | Every 4 weeks |
| Commercial operator | Continuous (multiple per day at steady state) |
| LPR spec | Quarterly minor; ad-hoc patches for errata |

Releases happen on Tuesdays or Wednesdays at 14:00 CET. Never Friday. Never the day before a public holiday.

---

## Release types

### Patch release (X.Y.Z → X.Y.Z+1)
- Bug fixes only
- No new features
- No behavior changes
- No new public APIs
- Released after: 1 maintainer review on the changes + green CI
- Can be released hot in response to a customer-reported regression

### Minor release (X.Y.0 → X.Y+1.0)
- New features, additive only
- No breaking changes
- New public APIs allowed
- Released after: 1 maintainer review + green CI + 48h beta window with at least 3 customers
- Announced in release notes

### Major release (X.0.0 → X+1.0.0)
- Breaking changes allowed
- New required APIs allowed
- Migration guide required
- Released after: 2 maintainer reviews + Founder sign-off + green CI + 14-day beta window + customer migration guide published
- Announced 30 days in advance via email to customers

### Pre-release (rc, beta, alpha)
- Released to PyPI/npm with pre-release tags
- Beta testers opt in explicitly
- Not announced to all customers
- May break compatibility within pre-release line

---

## Release checklist (per SDK release)

- [ ] All open Critical/High issues for this release resolved
- [ ] CHANGELOG.md updated with sections: Added, Changed, Deprecated, Removed, Fixed, Security
- [ ] Version bumped in: `pyproject.toml` / `package.json` / `go.mod` / `pom.xml` (whichever applies)
- [ ] Migration guide updated (for minor/major)
- [ ] Docs site preview validated
- [ ] CI green on `main` and on the release tag
- [ ] SBOM generated and verified
- [ ] SLSA provenance generated and verified
- [ ] Signed Git tag created (`git tag -s vX.Y.Z`)
- [ ] GitHub release published with release notes, SBOM, checksums
- [ ] Package published to PyPI/npm via OIDC trusted publisher (no long-lived tokens)
- [ ] Customer announcement email sent (minor/major) or Slack ping (patch)
- [ ] Status page updated if release affects operator behavior
- [ ] First-customer canary deploy confirmed healthy (for operator releases)

---

## OIDC trusted publishing

**No long-lived publishing tokens in CI.** PyPI and npm publishing uses OIDC trusted publishers:

- PyPI: trusted publisher configured per project to GitHub Actions workflow
- npm: GitHub Actions OIDC with `--provenance` flag

This eliminates token theft risk and produces verifiable provenance per release.

Local publishing is forbidden. Only the release workflow in GitHub Actions may publish.

---

## Versioning before 1.0

For pre-1.0 SDKs (Go, Java alpha, .NET alpha at Day 180):
- Use `0.X.Y` versioning
- Minor bumps (0.X.0 → 0.X+1.0) may include breaking changes
- Patch bumps (0.X.Y → 0.X.Y+1) cannot include breaking changes
- Move to 1.0 only when API has been stable for 30 days under at least 2 paying customers

---

## Beta cohort

For minor/major SDK releases, a pre-release `rc.1` ships to a beta cohort:
- 5+ paying customers (pilot or production tier)
- 48–72 hour window before GA
- Beta cohort uses dedicated Slack channel for fast feedback
- A critical issue from the cohort blocks GA

Beta cohort signs an addendum to their pilot SOW or production agreement covering pre-release software terms.

---

## Hotfix process

For Critical issues in production:

1. **Triage:** Founder + Senior Product Engineer assess severity within 30 minutes
2. **Branch:** Create `hotfix/X.Y.Z` from the release tag
3. **Fix:** Minimum viable fix; no scope creep
4. **Review:** 1 maintainer review (Founder for protocol-affecting changes)
5. **Release:** Patch bump (X.Y.Z+1); skip beta cohort
6. **Notify:** Affected customers informed by email within 4 hours of release
7. **Postmortem:** Within 5 business days

Hotfix bypasses the 48h beta window. The cost of speed must be justified by customer impact.

---

## Operator release process (`ledgerproof-platform`)

Commercial operator releases happen continuously but follow the same gates:

- Every commit to `main` triggers staging deployment
- Staging gets 4 hours of synthetic-load soak
- Promotion to production requires:
  - Green CI on all checks
  - Green staging metrics
  - No incidents in production for the prior 1 hour
  - Manual promote button (no auto-promote)
- Promotion is canary: 5% → 25% → 100% with 30-minute observation between steps
- Rollback to prior version is one button click; auto-rollback if error rate spikes

**Founder approval required for:**
- Changes to Bitcoin anchor commit logic
- Changes to receipt schema validation
- Changes to Foundation signing key handling
- Changes to legacy `iad` deployment — **NEVER. DO NOT.**

---

## Release announcement template

```
# LedgerProof <SDK/Operator/etc> vX.Y.Z released

Date: YYYY-MM-DD
Type: Patch / Minor / Major

## Summary
[1-2 sentences]

## Changes
[From CHANGELOG]

## Upgrade
[For minor: "pip install --upgrade ledgerproof"; for major: link to migration guide]

## Verifying this release
- Tag: vX.Y.Z
- SHA: <commit>
- Signed tag: yes
- SBOM: <link>
- Provenance: <link>
- Checksums: <link>

## Support
- Patch / minor: existing support channel
- Major: dedicated migration support via your customer success channel
```

---

## Customer notifications

| Release type | Customer notification |
|---|---|
| Patch | In-app notification or Slack ping to integration owners |
| Minor | Email to customer success contacts + release notes on dashboard |
| Major | Email 30 days in advance + email at release + dashboard banner for 14 days + customer success outreach |
| Hotfix (Critical) | Email + Slack within 4 hours of release |
| Operator-only patch | Status page entry; no customer notification unless SLO-affecting |

---

## Release retros

Monthly: review the prior month's releases. Look at:
- Time from PR merge to release
- Number of hotfixes (target: <2/month)
- Number of post-release issues (target: <3/month)
- Customer adoption of latest version (target: 80%+ within 60 days)

Adjust the cadence and beta window targets quarterly based on retro data.

---

## Spec releases

LPR spec releases (LPR v1.1.1, v1.2.0, etc.) follow a different process:

- Spec releases are RFC-style: there is a draft window, a public comment period, and a freeze
- v1.2 spec freeze process documented in [LPR v1.2 spec freeze](../day-60/01-lpr-v1.2-spec-freeze.md)
- Spec releases trigger SDK releases (every SDK must support the new spec within 30 days)
- Spec releases are announced via IETF Datatracker + spec.ledgerproofhq.io + Foundation transparency report

---

## What never ships

- Code that has not run in CI
- Code without tests
- Code with a Critical security advisory unaddressed
- Code that breaks v1.x receipt verification
- Code that touches the legacy `iad` deployment
- Code that introduces a long-lived publishing token
- Code that auto-merges itself (no auto-merge bots anywhere)
