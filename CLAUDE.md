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

## PR #1 status (as of May 26, 4:30pm PDT)
- ALL GREEN. Rust build/test/clippy/fmt/audit pass. Web app pass.
- 4 commits ahead of origin/main: 98ce39ce (lint fixes), b9f9aa0d (fmt), 70c6b501 (CI workflow), e1e3410e (audit.toml)
- Issue #2 tracks sqlx 0.7→0.8 + reqwest 0.11→0.12 upgrade (before July 6 launch)
- Veronica retains the merge button

## Open Founder Actions (priority order)
1. **Wednesday May 27, 7:30am PDT** — TVP meeting (Calicott + Malhotra)
2. **Wednesday May 27, 4:00pm PDT** — Stillmark meeting (Killeen + Singh) via Teams
3. Reply to Fulgur when they confirm time
4. Reply to Illuminate ONLY when their team comes back with question/meeting
5. Merge PR #1 when ready
6. By June 8 — pick lead investor
7. By June 25 — close round
8. Aug 23, 2026 — npm token rotation due (90-day)
9. Aug 24, 2026 — PyPI tokens rotation due

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
