# Memory — LedgerProof Launch

## Me
Veronica S. Dawkins, founder/editor of the LedgerProof Foundation. Building LPR v1.0 — an open Bitcoin-anchored cryptographic receipt format for AI-generated content provenance. Public launch target: **July 6, 2026**.

## Active Status (as of 2026-05-24)
- **EU operator is LIVE** in Frankfurt: `https://ledgerproof-api-eu.fly.dev/v1/health` returns 200.
- Spec-conformant LPR v1.0 — RFC 6962 Merkle w/ domain separation, EU AI Act Article 50 content schema, GDPR Article 17 erasure.
- Deployed **70 days ahead** of the August 2, 2026 EU AI Act Article 50 enforcement date.
- Three real Bitcoin mainnet anchors live from May 6 / 13 / 18 (intouch|Live San Diego symposium demo was real).

## Key Terms
| Term | Meaning |
|------|---------|
| **LPR** | LedgerProof Receipt — the v1.0 cryptographic receipt spec |
| **LPR1** | 4-byte OP_RETURN prefix |
| **Article 50** | EU AI Act 2024/1689 Art. 50 — AI transparency obligations, enforceable Aug 2, 2026 |
| **EU-AI-ACT-50-v1** | LPR profile tag for Article 50-compliant receipts |
| **LongHorizon-v1** | LPR profile w/ ML-DSA-65 PQC composite signatures |
| **HighAssurance-v1** | LPR profile w/ HSM + sub-hourly anchoring + multi-calendar |
| **SCITT** | IETF Supply Chain Integrity, Transparency, Trust working group |
| **SEP-1763** | Interceptor implementation in `05-sep-1763-impl/` |
| **TVP** | Wednesday May 27 video call narrative |
| **CRQC** | Cryptographically Relevant Quantum Computer (threat horizon 2030–35) |
| **symposium** | intouch\|Live San Diego, May 18 — real Bitcoin anchor broadcast |

## Infrastructure
| Resource | Region | Status |
|---|---|---|
| `ledgerproof-api-eu` (Fly app) | fra | **Live** — LPR v1.0 production — `https://api-eu.ledgerproofhq.io` |
| `ledgerproof-db-eu` (Postgres) | fra, 10 GB | Healthy, 5 migrations applied |
| Legacy `ledgerproof-api` | iad | Untouched — serves 3 historical anchors |
| Legacy `ledgerproof-anchor` | iad | Daily Esplora broadcast worker |
| EU anchor worker | — | **Not deployed** — Phase 2, post-pilot |
| EU monthly cost | — | ~$25–35/mo |

## Active Branch / Code
- Branch: `feat/lpr-1.0-eu-spec-conformant` — **pushed to origin** (`vsdawkins-creator/ledgerproof-platform`)
- PR open at: `https://github.com/vsdawkins-creator/ledgerproof-platform/pull/new/feat/lpr-1.0-eu-spec-conformant`
- 4 commits: RFC 6962 Merkle, AiArticle50Content schema, GDPR soft-delete, fly.api-eu.toml
- Tests: 8/8 Merkle, 11/11 EU AI Act 50 schema — all pass
- Production code matches LPR 1.0 spec (RFC 6962 Merkle, 36-byte OP_RETURN)

## Key Docs (this dir)
| File | Purpose |
|---|---|
| `04-lpr-spec/LPR-1.0-SPECIFICATION.md` | v1.0 base spec |
| `04-lpr-spec/LPR-1.1-SPECIFICATION.md` | **v1.1 — full Article 50 coverage (50(1),(2),(4))** |
| `04-lpr-spec/IETF-DRAFT-DAWKINS-SCITT-AI-ARTICLE50-00.txt` | **IETF draft — submit to SCITT WG** |
| `04-lpr-spec/C2PA-ASSERTION-SPEC.md` | **C2PA assertion mapping — `org.ledgerproof.receipt.v1`** |
| `12-eu-compliance/01-EU-AI-ACT-50-PROFILE.md` | Article 50 profile (v1.0) |
| `12-eu-compliance/02-C2PA-COMPATIBILITY.md` | C2PA compatibility (existing) |
| `12-eu-compliance/07-EIDAS-COMPATIBILITY.md` | **eIDAS compatibility statement** |
| `12-eu-compliance/08-EU-COP-SIGNATORY-APPLICATION.md` | **EU AI Act Code of Practice signatory application** |
| `07-coalition/03-LPR-V1.1-ADOPTION-LETTER.md` | **Founding-adopter coalition letter template** |
| `09-capital/outreach/01-LANGCHAIN-PARTNERSHIP-PROPOSAL.md` | **LangChain partnership proposal** |
| `EU-SPRINT-STATUS.md` | Sprint status |
| `WHAT-LEDGERPROOF-EU-DOES.md` | Institution/investor explainer |
| `HOW-LEDGERPROOF-HANDLES-DEEPFAKES.md` | Regulator/journalist explainer (Art. 50(2)) |
| `13-api-backend/CONTRACTOR-AUDIT-MAY24.md` | Senior Rust audit |
| `13-api-backend/EU-SMOKE-TEST-PLAN.md` | 7-test EU validation plan |
| `13-api-backend/EU-DNS-PLAN.md` | DNS wire-up for api-eu.ledgerproofhq.io |
| `13-api-backend/eu-ai-act-50-test-receipt.py` | E2E receipt issuance (v1.1 fields) |
| `13-api-backend/run-eu-smoke-tests.sh` | 7-test smoke runner |
| `13-api-backend/POSTGRES-PASSWORD-ROTATION.md` | Password rotation runbook |

→ Full project detail: `memory/projects/ledgerproof-eu.md`
→ Glossary: `memory/glossary.md`

## LPR v1.1 Sprint Status (2026-05-25)
- ✅ **v1.1 spec written** — `04-lpr-spec/LPR-1.1-SPECIFICATION.md` (Article 50(1),(2),(4))
- ✅ **Rust schema updated** — `vendor/quantum-edge-2/src/schemas.rs` — 29 tests pass (18 new)
- ✅ **Backwards compat verified** — v1.0 receipts parse under v1.1 with serde defaults
- ✅ **GDPR-safe new types** — `AiHumanReviewContent`, `AiChatbotSessionContent` (no PII, role identifiers, email rejection)
- ✅ **Public API endpoints added** — `GET /v1/verify/:seq` and `GET /v1/receipts/by-content-hash/:sha256` (unauthenticated, for regulators)
- ✅ **Production smoke** — 7/7 pass with v1.1 fields against v1.0 production (backwards compat live)
- ✅ **IETF draft** — `draft-dawkins-scitt-ai-article50-00` ready for submission
- ✅ **C2PA assertion spec** — `org.ledgerproof.receipt.v1` mapping ready for CAWG submission
- ✅ **eIDAS compatibility statement** — published
- ✅ **EU Code of Practice signatory application** — package complete
- ✅ **Coalition adoption letter** — template ready for TVP portfolio (target: 5 signatories by July 6)
- ✅ **LangChain partnership proposal** — email ready to send
- ⏳ **Deploy v1.1 to production** — Veronica must `cargo build` + `fly deploy --app ledgerproof-api-eu` to enable new API endpoints
- ⏳ **Push quantum-edge-2 v1.1 upstream** — vendor edits need to land in `vsdawkins-creator/quantum-edge-2` then bump the `rev =` pin in workspace Cargo.toml

## Open Founder Actions (priority order)
1. ✅ ~~Rotate EU Postgres password~~ — Rotated 2026-05-23 22:31 PDT. Original password (`lVsM03xlM99aS0w`) dead. New password in `eu-postgres.txt`, never appeared in chat. `db: ok` confirmed.
2. ✅ ~~Back up `~/.ledgerproof-secrets/` to 1Password~~ — Done: AES-256 encrypted DMG, 2 secure locations.
3. ✅ ~~Install fly CLI~~ — v0.4.54, authenticated.
4. ✅ ~~DNS: `api-eu CNAME ledgerproof-api-eu.fly.dev` + TLS cert~~ — Done 2026-05-25. `https://api-eu.ledgerproofhq.io` live, Let's Encrypt cert issued.
5. ✅ ~~Push `feat/lpr-1.0-eu-spec-conformant` + open PR to main~~ — Pushed. Open PR at GitHub.
6. ✅ ~~**Run full smoke suite**~~ — **PASS 7 / FAIL 0 / SKIP 2** (T3 WireGuard/network). DEMO-READY. Fixes: counter bug, ADMIN_SECRET head-1, unique KEY_ID per run, artifact_hash/content_type/bytes fields. Committed 2026-05-25.
7. Decide EU anchor worker timing (fund EU hot wallet) — Phase 2.
8. Rate limiting (tower-governor) — pre-scale hardening.
9. §8.5 spec-code field divergence — resolve before IETF draft (flagged, deferred).

## Wednesday May 27 — TVP narrative
> "LedgerProof's EU operator is live in Frankfurt as of May 24. Spec-conformant LPR v1.0 — RFC 6962 Merkle with domain separation, EU AI Act Article 50 content schema validated server-side, GDPR Article 17 erasure endpoint. `https://ledgerproof-api-eu.fly.dev/v1/health` is up right now. Three pre-launch demo anchors on Bitcoin mainnet from May, including the symposium broadcast. LPR v1.0 production anchoring begins with the first EU pilot. Seventy days ahead of the August 2 enforcement date."

Every word demonstrable live on the call.

## Secrets Location
`~/.ledgerproof-secrets/` (mode 0600): `operator_key.pem` (Ed25519, pub `d56a74ae...d87`), `api_key_salt.txt`, `eu-postgres.txt`, `eu-app-secrets.txt`.

## Preferences
- Senior-cryptography-contractor lens for any Rust/protocol/audit work (use `anthropic-skills:senior-rust-cryptography-contractor`)
- Spec-conformance before convenience
- Never touch legacy iad deployment — those 3 anchors stay verifiable forever
