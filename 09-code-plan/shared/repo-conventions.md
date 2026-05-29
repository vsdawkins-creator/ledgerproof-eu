# Repository Conventions

**Purpose:** Single source of truth for how every LedgerProof repository is structured, named, branched, reviewed, released, and decommissioned. Reference for every new hire.

---

## Repo naming

| Pattern | Use |
|---|---|
| `ledgerproof-<lang>` | Language SDK (e.g., `ledgerproof-py`, `ledgerproof-ts`, `ledgerproof-go`, `ledgerproof-java`, `ledgerproof-dotnet`) |
| `ledgerproof-<platform>` | Platform connector (`ledgerproof-openai-py`, `ledgerproof-bedrock-ts`, etc.) |
| `langchain-ledgerproof` | Ecosystem integration (legacy naming preserved for PyPI registration) |
| `ledgerproof-platform` | Private monorepo: commercial operator, verifier, registry (private) |
| `ledgerproof-spec` | Protocol specification + IETF draft sources (public) |
| `verifier-ref` | Reference verifier implementation (public) |
| `operator-ref` | Reference operator implementation (public) |
| `mappings` | Regulatory mapping documents (public, CC-BY-4.0) |
| `governance` | Foundation governance documents (public) |

All repos live under `github.com/ledgerproof/`.

---

## Visibility

| Repo class | Default visibility | Rationale |
|---|---|---|
| SDKs | Public, Apache 2.0 | Customers verify integration code; ecosystem participation |
| Connectors | Public, Apache 2.0 | Same |
| Reference operator / verifier | Public, Apache 2.0 | Customers self-host or audit |
| Spec | Public, Apache 2.0 (text); test vectors CC-0 | Open standard |
| Mappings | Public, CC-BY-4.0 | Industry reference materials |
| Commercial operator (`ledgerproof-platform`) | Private | Operational competitive surface |
| Governance | Public, CC-BY-4.0 | Foundation transparency |
| Internal tooling | Private | Operational |

Any private→public transition requires Founder + Security Advisor sign-off and a security review of historical commits.

---

## Branching

- **`main`** is always green and deployable
- **`release/X.Y`** branches are created for SDK and operator releases; supported per [release-process.md](release-process.md)
- **Feature branches:** `feature/<short-slug>` for short-lived work; squash-merge to main
- **Bug fix branches:** `fix/<short-slug>`
- **Hotfix branches:** `hotfix/<X.Y.Z>` against release branches

No long-lived feature branches. If a feature takes longer than 2 weeks, it ships behind a feature flag.

---

## Branch protection on `main` (all public repos)

- Require pull request before merging
- Require at least 1 review from a Maintainer
- Require all CI checks to pass
- Require linear history (no merge commits)
- Require signed commits (Foundation policy by Day 90)
- Restrict force pushes
- Restrict deletions
- **No auto-merge.** Every merge is a deliberate human action.

For `ledgerproof-platform` (private), additional rule: require Founder approval for changes to `internal/anchor/` (Bitcoin anchoring logic).

---

## Commit messages

Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`.

Scope (optional): a single word identifying the area (e.g., `sdk`, `operator`, `verifier`, `merkle`, `anchor`).

Subject: imperative, present tense, lowercase first letter, no trailing period.

Body: explain *why*, not what. Reference issues by number.

Footer: `BREAKING CHANGE: <description>` for breaking changes (in SDK 2.0 territory).

Example:
```
feat(sdk): add local queue fallback for offline operator

When the operator is unreachable, enqueue receipts to a local
SQLite-backed queue with exponential backoff retry. Resolves the
issue where customer inference latency was bounded by operator
availability.

Refs: #142
```

---

## File layout (per-language SDK)

```
ledgerproof-<lang>/
├── README.md
├── LICENSE                  ← Apache 2.0
├── CHANGELOG.md             ← Keep-a-Changelog format
├── CONTRIBUTING.md
├── SECURITY.md              ← Vulnerability disclosure policy
├── .github/
│   ├── workflows/           ← CI: test, lint, release, sbom, slsa
│   └── ISSUE_TEMPLATE/
├── src/                     ← Source code (Python: `src/ledgerproof/`, TS: `src/`, Go: cmd/+internal/)
├── tests/                   ← Test suite
├── docs/                    ← Per-language docs source (auto-published to docs.ledgerproofhq.io)
├── examples/                ← Runnable examples for each major usage pattern
└── bench/                   ← Performance benchmarks
```

---

## Code review

- Every PR requires at least 1 maintainer review
- Maintainer reviews focus on: correctness, security, test coverage, documentation, API stability
- Style nits use `nit:` prefix and are non-blocking
- Maintainer may request changes; PR author addresses, re-requests review
- Founder-only review required for any change to: receipt schema, Bitcoin anchor format, cryptographic primitives, GDPR PII rejection logic

---

## Testing standards

| Test category | Where it runs | Pass threshold |
|---|---|---|
| Unit | Per-commit CI | 95% line coverage on hot paths |
| Integration (against staging) | Per-PR CI (gated marker) | All scenarios green |
| Conformance | Per-release CI (operators only) | All vectors pass |
| End-to-end | Nightly | Allowed flakiness <2% |
| Load | Pre-release | Per the [load test plan](../day-30/03-operator-load-test-plan.md) |
| Security (SAST + dependency scan) | Per-commit CI | No new highs without documented suppression |

CI gating: a PR cannot merge if any unit, integration, or security check is red. Nightly E2E and load tests do not gate per-PR but block releases.

---

## Documentation

Docs live in the repo (Markdown), are auto-published to `docs.ledgerproofhq.io/<repo>/`. Docs PR is required for any:
- New public API
- Behavior change visible to consumers
- New configuration option
- New error class

CI lints docs for broken links and unrenderable code blocks.

---

## Maintainer roles

| Role | Responsibilities | Number at Day 180 |
|---|---|---|
| Founder | All repos; approver on protocol-affecting changes | 1 |
| Spec Lead | `ledgerproof-spec`, all conformance suites | 1 |
| Senior Product Engineer | All SDK repos | 1 |
| SRE | `ledgerproof-platform`, infrastructure | 1 |
| DevRel | Examples, docs, community engagement | 1 (from Day 120) |
| External contributors | Per-repo, after CLA signed | growing |

Maintainer additions require Founder approval. Maintainer removal is documented in the governance repo.

---

## CLA (Contributor License Agreement)

External contributors sign a Foundation CLA before merging code. Modeled on the Apache ICLA. CLA repository at `github.com/ledgerproof/cla-records` (private). CLA validation runs in CI; PRs blocked until CLA is on file.

Minor doc fixes (typos, link fixes) under a 30-line threshold do not require CLA.

---

## Issue and discussion management

- GitHub Issues for bug reports, feature requests, and tasks
- GitHub Discussions for design conversations and Q&A
- Public issue tracker for all public repos
- Private security issues go to `security@ledgerproofhq.io`, never to public trackers

Issue triage: weekly cadence; SLA on first response 5 business days for public reports, 2 business days for paying customers.

---

## Versioning

- SemVer strictly: `MAJOR.MINOR.PATCH`
- `MAJOR` bumps for breaking API/protocol changes
- `MINOR` bumps for additive changes
- `PATCH` bumps for bug fixes
- Pre-release tags: `-alpha.N`, `-beta.N`, `-rc.N`
- Build metadata: `+build.<sha>` for internal builds

Cross-repo coordination: SDK 1.x and reference operator 1.x speak LPR v1.x. SDK 2.x and reference operator 2.x speak LPR v2.x. Mixed pairing (SDK 1.x + operator 2.x or vice versa) is supported as documented in compatibility matrices.

---

## Deprecation policy

A public API marked deprecated must:
- Be documented as deprecated in the CHANGELOG and release notes
- Continue to function for at least 6 months
- Emit a deprecation warning at runtime (where reasonable)
- Have a clear migration path in docs

Removal of a deprecated API is a MAJOR version bump. We do not remove APIs in MINOR releases.

LPR receipt format itself follows a stricter rule: receipts are verifiable forever. We never remove receipt-format support in the verifier.

---

## Decommissioning a repo

Rare but documented:
1. Mark archived in README and via GitHub's archive feature
2. Document the reason and the alternative
3. Foundation transparency report includes the archival decision
4. Repository remains accessible read-only indefinitely

Never delete a repo. Never rewrite history on `main` of a public repo.
