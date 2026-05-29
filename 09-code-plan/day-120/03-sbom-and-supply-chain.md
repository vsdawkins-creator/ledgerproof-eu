# SBOM & Supply Chain Security — Day 120

**Purpose:** Every artifact LedgerProof ships (SDK, operator binary, reference implementation, marketplace listings) is accompanied by a verifiable Software Bill of Materials. Customers running our code in regulated environments need this; Series A diligence audiences expect this; the protocol's open-source posture mandates this.

**Owner:** Security Advisor (Day 30 onboard; full hire Day 120) + Spec Lead
**Target GA:** Day 120, ahead of marketplace cloud launches

---

## What we publish per release

For every released artifact:

1. **SPDX SBOM** — package inventory in SPDX 2.3 JSON
2. **CycloneDX SBOM** — alternate format for CycloneDX-consuming tools
3. **Provenance attestation** — SLSA Level 3 build attestation (in-toto format)
4. **Signed checksums** — SHA-256 of all release artifacts, signed by Foundation release key
5. **Vulnerability advisory log** — `audit.toml` (Rust) / `audit.json` (others) documenting suppressed advisories with rationale

All five artifacts are linked from the GitHub release page and from a per-version page at `releases.ledgerproofhq.io/<artifact>/<version>`.

---

## Tooling

| Language | SBOM tool | Provenance tool |
|---|---|---|
| Rust (commercial operator) | `cargo-cyclonedx`, `cargo-spdx` | `slsa-framework/slsa-github-generator` |
| Go (reference operator, Go SDK) | `syft`, `cyclonedx-gomod` | Same |
| Python (Python SDK + LangChain) | `cyclonedx-python-lib`, `pip-licenses` | Same |
| TypeScript / Node (TS SDK) | `@cyclonedx/cyclonedx-npm` | Same |
| Java (Java SDK) | `cyclonedx-maven-plugin` | Same |
| .NET (planned Day 120 alpha) | `cyclonedx-dotnet` | Same |
| Container images (operator, verifier) | `syft`, `grype`, `trivy` | `cosign` for signing |

All tooling runs in CI on every release. CI fails if any SBOM cannot be produced or any high/critical vulnerability is detected without a documented suppression.

---

## Vulnerability management policy

| Severity | Default policy | Override mechanism |
|---|---|---|
| Critical | Block release until patched or actively mitigated | Founder + Security Advisor sign-off on `audit.toml` entry with mitigation |
| High | Block release until patched, mitigated, or documented | Spec Lead approval on `audit.toml` entry |
| Medium | Tracked; address within 60 days | None needed; track in issue |
| Low | Tracked; address opportunistically | None needed; track in issue |
| Informational | Logged; no action required | None |

`audit.toml` (or equivalent per-language) entries require:
- CVE ID or advisory link
- Severity
- Reachable in our code paths (yes/no/unknown)
- Mitigation in place
- Re-evaluation date
- Approver

These files are committed; the suppression log is part of the public release narrative.

---

## Build provenance — SLSA Level 3

Target Level 3 for production releases:
- **Source:** Builds run from a tagged commit; no local builds; no developer-direct uploads
- **Build:** GitHub Actions hosted runners; no self-hosted (to avoid supply-chain risk on runner compromise)
- **Provenance:** SLSA provenance attestation generated per release; signed via Fulcio + Rekor (sigstore) or Foundation Ed25519 key
- **Hermetic build:** Bazel-based or container-isolated; dependencies pinned by hash

For the commercial operator (private repo), the same Level 3 process runs internally. The provenance attestation is included in SOC 2 audit evidence.

---

## Container images

| Image | Registry | Tag policy | Signing |
|---|---|---|---|
| `ghcr.io/ledgerproof/operator-ref` | GitHub Container Registry (public) | Semantic version + git SHA | `cosign sign --keyless` |
| `ghcr.io/ledgerproof/verifier-ref` | GHCR (public) | Same | Same |
| Commercial operator | Fly.io image registry (private) | Same + environment label | Foundation key |

All images:
- Multi-arch (linux/amd64, linux/arm64)
- Built from distroless base
- Run as non-root
- No package manager in runtime image
- Vulnerability scan in CI gating release

---

## Dependency hygiene

**Pinning:** Every dependency pinned by version + content hash (Cargo.lock, package-lock.json, go.sum, Pipfile.lock, etc.). No "latest" or "*" version specifications anywhere.

**Updates:** Renovate Bot runs weekly. Updates are reviewed and merged in dedicated dependency-update PRs (separate from feature PRs). Major version updates require explicit reasoning in PR description.

**License compliance:** SBOM tools surface license per dependency. Permitted licenses: Apache-2.0, MIT, BSD-{2,3}, ISC, MPL-2.0 with review, CC0. Copyleft (GPL family) is forbidden in shipped binaries — discovered presence requires either replacement or an explicit license-compatibility memo (rare).

---

## What customers can verify

Given a published binary, a customer or auditor can:

1. Pull the SBOM and confirm the dependency tree
2. Pull the SLSA provenance and confirm the build was reproduced from a tagged source commit
3. Pull the signed checksum and confirm the binary matches
4. Pull the audit log and review documented vulnerability suppressions
5. Compare two consecutive releases' SBOMs to see exactly what changed
6. Re-build from source and confirm bit-equivalence (where the language toolchain supports reproducible builds — Go yes, Rust partially, others varies)

This is the answer to "how do we know we're running what you say we're running" from procurement.

---

## Marketplace and customer-facing artifacts

| Artifact | SBOM included | Provenance included |
|---|---|---|
| GitHub release | ✓ | ✓ |
| PyPI package | SBOM linked from package metadata | Provenance via PEP 740 (when supported) |
| npm package | SBOM linked from package.json | Provenance via npm provenance feature |
| AWS Marketplace listing | SBOM bundled with listing artifacts | Linked from listing |
| Azure Marketplace listing | Same | Same |
| GCP Marketplace listing | Same | Same |
| Container images | SBOM via OCI annotation | Cosign attestation |
| Customer-delivered binaries (rare) | Bundled | Bundled |

Marketplace listings reference the SBOM and provenance prominently in the security section of the listing — procurement teams scan for these.

---

## SOC 2 implications

SBOM and provenance are direct evidence for SOC 2 controls in:
- CC3.4 (Change management)
- CC7.1 (System monitoring)
- CC7.4 (Incident response)
- CC8.1 (Change management)

The Day 120 SBOM & supply chain posture is timed deliberately: SOC 2 Type 1 attestation lands at Day 120, and the SBOM + provenance evidence is what the auditor uses to confirm change management controls.

---

## Pre-GA checklist

- [ ] SBOM generation runs in CI for every shipping artifact
- [ ] SLSA provenance generation integrated for every shipping artifact
- [ ] `audit.toml` (or equivalent) lives in every repo with a documented review cadence
- [ ] Renovate Bot configured for every repo
- [ ] `releases.ledgerproofhq.io` lists all artifacts with their SBOMs and provenance
- [ ] Customer-facing "verify your install" documentation published at docs.ledgerproofhq.io/security/verify-install
- [ ] Cosign keyless signing tested for container images
- [ ] First external auditor (SOC 2 Type 1) confirms SBOM/provenance evidence is sufficient
- [ ] Vulnerability disclosure policy linked from every repo and docs site

---

## What's deferred to v2.0 / future

- Reproducible builds across all languages (Rust toolchain limits)
- Software supply chain attestation for build environment (the GHA runners themselves)
- Per-customer SBOM diffs for compliance reporting
- Native integration with customer GRC SBOM consumption (ServiceNow, Snyk, etc.)

---

## Open questions

1. **Foundation release key vs. Sigstore keyless.** Sigstore is friendlier; Foundation key is more controlled. **Recommend both: Sigstore keyless for community trust, Foundation key for enterprise customers requiring named-key signing.**
2. **SBOM for the Bitcoin anchor pool relays we use.** They are external services, not our code. **Recommend documentation reference only; not actionable as SBOM.**
3. **SBOM updates for unmodified dependencies during minor releases.** Republish SBOM each release or skip when unchanged? **Recommend always republish — diff-checkers expect a per-version SBOM.**
4. **Vulnerability disclosure embargo.** When a vulnerability is reported privately, how long before public disclosure? **Recommend 90 days standard, with extension to 120 for complex fixes; immediate disclosure if active exploitation detected.**
