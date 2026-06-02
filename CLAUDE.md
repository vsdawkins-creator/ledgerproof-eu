# Memory — LedgerProof Launch

## Me
Veronica S. Dawkins, founder of LedgerProof Foundation. Building LPR — an open Bitcoin-anchored cryptographic receipt protocol for AI-generated content provenance. Based in Los Angeles. Public launch: **July 6, 2026**. EU AI Act Article 50 enforcement: **August 2, 2026** (68 days). Email: veronica@ledgerproofhq.io / spec@ledgerproofhq.io.

## Active fundraise — Seed round (close June 25, 2026) — UPDATED MAY 27
- **$15M total — three co-leads at $5M each / $45M post-money SAFE**
- Structure communicated to Aryan/TVP post-meeting May 27 (call went well)
- TVP, Stillmark, Fulgur each at $5M co-lead, each with board observer
- Illuminate (financial-services side) in inbound triage — potential 4th co-lead later
- Lead candidates (4 funds, all inbound same week May 25):
  - **TVP** (Trammell Venture Partners): Christopher Calicott + Aryan Malhotra — Wed May 27, 7:30am PDT
  - **Stillmark**: Alyse Killeen (LA-based) + Vikash Singh (London) — Wed May 27, **4:00pm PDT** via Teams
  - **Fulgur**: Michele Anastasio + Oleg Mikhalsky (Italy) — time TBD, replied this week
  - **Illuminate Financial**: Mark Beeston (founder, MP) — engaged personally May 26 "thanks, shared with team"
- Pitch posture: not running auction; parallel evaluation; honest when asked
- Decision point June 8; close June 25; launch July 6

## Key People (top 30)
| Who | Role | Verified email |
|-----|------|---|
| **Christopher Calicott** | MD, TVP. Bitcoin-native filter, Texas, low patience for blockchain pitches | — |
| **Aryan Malhotra** | Analyst, TVP. Routed the deal in; writes the memo | — |
| **Alyse Killeen** | Managing Partner, Stillmark. **LA-based** (not London). Bullish US Bitcoin | — |
| **Vikash Singh** | Principal, Stillmark. London-based, rigorous technical diligence | — |
| **Michele Anastasio** | Investment team, Fulgur Ventures. EU-focused | — |
| **Oleg Mikhalsky** | Fulgur Ventures. Deep technical background, Lightning ecosystem | — |
| **Mark Beeston** | Founder/MP, Illuminate Financial. UK-based, 1,400 institutional LPs · led Reality Defender Series A | `mb@illuminatefinancial.com` |
| **Hemant Taneja** | CEO, General Catalyst. Co-founded Responsible Innovation Labs; EU AI Champions; Mistral investor | **`htaneja@generalcatalyst.com`** ✅ |
| **Sarah Guo** | Founder, Conviction (AI-only fund). Backed Harvey, Mistral, Sierra, Baseten | **`sarah@conviction.com`** ✅ |
| **Zachary Bogue** | Co-Founder/MP, DCVC. Led Reality Defender's first Series A. Deep tech (defense, security, AI). | **`zbogue@dcvc.com`** ✅ |
| **Stephen Nundy** | Investment Partner & CTO, Lakestar. Technical diligence lead for the Swiss/EU fintech-infra fund. | **`stephen@lakestar.com`** ✅ |

→ Full people detail: memory/people/

## Active Projects
| Name | What |
|------|------|
| **LedgerProof v1.1** | LIVE in production Frankfurt; Art 50(1),(2),(4) coverage |
| **PR #1** | feat/lpr-v1.1-article-50-expansion — **ALL CI GREEN as of May 26**; ready to merge |
| **LPR 1.2 Canonicality Annex** | DRAFTED — lineage chains, similarity, attestation, Canonical Registry |
| **LPR 2.0 PQ Annex** | OUTLINED — hybrid Ed25519+Dilithium3, SPHINCS+ for high-assurance |
| **Unstoppable Master Plan** | 17 threats → 7 priority techs, 18 months post-close |
| **IETF draft** | `draft-dawkins-scitt-ai-article50-00` — posted + confirmed May 25 |
| **PyPI** | `ledgerproof` 1.0.0 + `langchain-ledgerproof` 1.0.0 live May 26 |
| **npm** | `@ledgerproof/sdk`, `@ledgerproof/vercel-ai`, `@ledgerproof/cloudflare-workers` live |

→ Full project detail: memory/projects/

## Critical numbers (know cold for tomorrow)
| What | Number |
|---|---|
| Raise | **$15M** ($5M × 3 co-leads — TVP/Stillmark/Fulgur) |
| Post-money | **$45M** SAFE |
| Close | **June 25, 2026** |
| Launch | **July 6, 2026** |
| **Article 50 enforcement (Peak 1)** | **Aug 2, 2026** |
| **Grandfather expiry + nudifier ban + Omnibus formal adoption (Peak 2)** | **Dec 2, 2026** |
| **HRAIS Annex III deadline (post-Omnibus)** | Dec 2, 2027 |
| **Annex I embedded systems deadline** | Aug 2, 2028 |
| Penalty (preferred framing) | **3% of global turnover, per article** (NOT €15M) |
| Margin at 1M receipts/day | **97%** |
| Per-receipt Bitcoin fee | **~$0.0003** at batched scale |
| LPR1 prefix + Merkle root | 4 + 32 = **36 bytes** OP_RETURN |
| Live anchor since | **May 18, 2026** |

## Canonical positioning (use everywhere)
**Tagline:** *"Evidence in runtime, not assertion."*
**Primary sales frame:** **Compliance Premium** — LedgerProof accelerates enterprise procurement velocity (revenue accelerator), with penalty avoidance as a side benefit. CEOs/CFOs approve revenue-accelerator spend; they cut risk-mitigation spend. Sell as a *deal-velocity tool*, not a compliance tool.
**Buyer language:** GCs say "governance framework," "audit trail," "risk management." NOT "AI tool" or "automation."

## Terms (hot cache — full set in memory/glossary.md)
| Term | Meaning |
|------|---------|
| LPR | LedgerProof Receipt |
| LPR1 | 4-byte OP_RETURN prefix |
| Article 50 | EU AI Act Art. 50, transparency obligations |
| FROST | Threshold Ed25519 signing (operator + Foundation arbitration) |
| RRL | Receipt Revocation List (Bitcoin-anchored) |
| NanoBanana | Google's image-editing AI; canonical AI vendor example |
| CRQC | Cryptographically Relevant Quantum Computer |
| canonicality | LPR 1.2 §6 — registry + arbitration for "which is the real one" |
| symposium | intouch\|Live SD, May 18 — first Bitcoin anchor broadcast |

## Open PRs across the org (as of Monday Jun 1, EOD)
| Repo | PR | Title | Status |
|---|---|---|---|
| `ledgerproof-platform` | **#1** | feat/lpr-v1.1 article-50 expansion (ALL GREEN CI) | Awaits Veronica merge |
| `ledgerproof-platform` | **#3** | ci/canonical-conformance-test (cross-lang hash CI, LPR-ERRATA-001 enforcement) | Opened Jun 1; awaits Veronica review |
| `quantum-edge-2` | **#2** | fix LPR1 magic-bytes conformance test | Opened May 28; restores green CI |
| `ledgerproof-verifier` | **#1** | feat/slug-routing-and-brand-alignment (3 layers: slug routing + brand + pre-v1 errata cards) | Opened May 28; updated Jun 1 |
| `ledgerproof-site` | **#1** | feat/article-50-landing-and-founder-letter (5 pages: /article-50, /letter, /spec/errata/001, /docs/entries/0, /r/founding-declaration) | Opened May 28; updated Jun 1 |

## Monday Jun 1 EOD state — operational substrate
- **PAT exposure** — scrubbed from disk, Keychain helper wired; **github.com revoke still pending Veronica**
- **Canonicalization bug** — ROOT-CAUSED in 5 minutes for $0; contained to Entry #0; LPR-ERRATA-001 issued
- **Trail of Bits scope** — shrunk from $45-65K/2-week to $15-25K/3-day; engagement email drafted at `13-monday-sprint/03`
- **Adler & Colvin** — 501(c)(3) + Day-1 IP license + multi-signer quorum email drafted at `13-monday-sprint/04`
- **Hercules Capital** — $8M undrawn facility email drafted at `13-monday-sprint/05`
- **Seed restructure** — two-stage proposal ($10M+$5M tranche) drafted to 4 co-leads at `13-monday-sprint/07`
- **Founding-declaration entry** — JSON payload ready at `13-monday-sprint/06`; issuance pending verifier PR merge
- **Operational substrate live**: `lpr-status.json` (weekly anchor) + `win-conditions.json` (quarterly anchor) + `CRIT_PATH.md` (26-week table)
- **Spec artifacts**: `LPR-ERRATA-001.md` + `LPR-FEE-001.md` + `LPR-VER-001.md` in `04-lpr-spec/`

## Open Founder Actions (priority order — Tuesday Jun 2 onward)
1. **NOW** — Revoke `ghp_…1ZBl93` on github.com/settings/tokens (E1, 90 sec)
2. **Today** — Send Trail of Bits + Adler & Colvin + Hercules engagement emails (drafts in `13-monday-sprint/`)
3. **Today** — Order Unchained Capital Business Vault + 4× YubiKey 5C NFC + Casa Platinum (E5)
4. **Tue Jun 2 09:00 PT** — Call Sarah Guo to pressure-test the two-stage seed restructure
5. **Tue Jun 2 morning PT** — Send seed-restructure note to TVP + Stillmark partners (one-on-one threads)
6. **Wed Jun 3 morning ET** — Send seed-restructure note to Fulgur + Mark Beeston
7. **By Jun 7** — Decision on the 5 open PRs (merge / iterate / close per repo)
8. **By Jun 18** — All four co-leads wire-confirm (one week before nominal close)
9. **Jun 25** — Seed close
10. **Jul 6** — Public launch
11. Aug 23, 2026 — npm token rotation due
12. Aug 24, 2026 — PyPI tokens rotation due

## Security/ops constraints (NON-NEGOTIABLE)
- **Never touch legacy iad deployment** — 3 anchors stay verifiable forever
- Secrets at `~/.ledgerproof-secrets/` mode 0600 — never commit
- GDPR safety net: emails forbidden at schema validation in `deployer_id`, `reviewer_role`, `review_rationale`
- Bitcoin OP_RETURN format: `"LPR1" || merkle_root_32` (36 bytes total) — DO NOT modify
- Never auto-merge PRs without explicit Veronica approval
- Recovery codes (PyPI, npm, GitHub) live in 1Password ONLY — never in chat

## Preferences
- Diligence-engineer rigor on every commit (use `senior-vc-diligence-engineer` skill)
- Senior-cryptography-contractor lens for protocol/audit work
- Spec-conformance before convenience
- Two-commit pattern for PRs: surgical fix + mechanical cleanup
- Lead with "3% of turnover" not "€15M" in marketing
- Defensive-only patent strategy (Apache/Eclipse model)
