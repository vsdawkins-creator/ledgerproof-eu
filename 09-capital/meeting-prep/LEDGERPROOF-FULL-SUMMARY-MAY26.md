# LedgerProof — Full Situation Summary & Technical Specs

**Date:** May 26, 2026
**Prepared for:** Veronica S. Dawkins, Founder
**Use:** Investor diligence, regulator briefings, technical hand-off

---

## 1 · The one-paragraph version

LedgerProof is an **open cryptographic protocol** that binds AI-generated content (text, images, video, audio, documents) to a permanent, machine-verifiable receipt anchored to the Bitcoin blockchain. The protocol covers all three obligations of **EU AI Act Article 50** — chatbot transparency, synthetic media labeling, and deepfake disclosure — which become enforceable on **August 2, 2026**. The infrastructure is **production-live** as of May 18, 2026, with SDKs published worldwide, an IETF Internet-Draft accepted by Datatracker (May 25), and three top Bitcoin-native venture funds reaching out the same week. The company structure is a **501(c)(3) Foundation** (which owns the protocol) plus **LedgerProof Inc.** (which operates the commercial calendar). A $5M / $30M post-money seed round closes June 25, 2026; public launch July 6, 2026.

---

## 2 · The market window

| Date | Event |
|---|---|
| Aug 1, 2024 | EU AI Act in force (overall) |
| Feb 2, 2025 | Article 5 (prohibited practices) enforced |
| **May 18, 2026** | LedgerProof LPR v1.0 live anchor on Bitcoin mainnet |
| **May 25, 2026** | IETF draft `draft-dawkins-scitt-ai-article50-00` accepted |
| **May 26, 2026** | Python SDK live on PyPI |
| **June 25, 2026** | Seed round close target |
| **July 6, 2026** | LedgerProof v1.1 public launch |
| **August 2, 2026** | EU AI Act Article 50 transparency obligations enforceable |
| **August 2, 2027** | Full general-purpose AI obligations |

**Penalty for Article 50 non-compliance:** up to €15M or 3% of global annual turnover, whichever is higher.

---

## 3 · What Article 50 actually requires

### 50(1) — Chatbot transparency
Anyone interacting with a chatbot or AI system must be informed they are interacting with AI, unless it is obvious.

### 50(2) — Synthetic media marking
Providers of AI systems generating synthetic audio, image, video, or text **must ensure the output is marked in a machine-readable format and detectable as artificially generated.**

### 50(4) — Deepfake disclosure
Deployers of deepfakes must disclose that content has been artificially generated or manipulated.

**Implementation gap:** No existing standard combines (a) machine-readable, (b) tamper-evident, (c) jurisdiction-agnostic, (d) regulator-queryable for all three. LedgerProof v1.1 is the first protocol to cover all three under a single receipt format.

---

## 4 · How LedgerProof works (plain-English flow)

```
1. AI generates content
     ↓
2. SDK computes SHA-256 of the canonical content
     ↓
3. SDK builds an LPR entry (typed CBOR object with issuer, jurisdiction, profile)
     ↓
4. SDK signs the entry with the operator's Ed25519 key
     ↓
5. Entry is submitted to a calendar operator (federated network)
     ↓
6. Operator batches entries via RFC 6962 Merkle tree
     ↓
7. Operator publishes the Merkle root as a Bitcoin OP_RETURN transaction
        (4-byte "LPR1" prefix + 32-byte Merkle root = 36 bytes total)
     ↓
8. Receipt is returned to the customer with an entry_hash + verify_url
     ↓
9. Any third party can verify the receipt by:
        — Fetching the entry from the verifier API
        — Recomputing the SHA-256 over the content
        — Walking the Merkle proof to the Bitcoin transaction
        — Confirming the Bitcoin transaction is mined and >6 confirmations
```

The full cycle from content generation to confirmed Bitcoin anchor: typically **10–60 minutes**. The receipt itself is returned in **under 200ms** with status `PENDING`; anchor status promotes to `ANCHORED` (in mempool) and then `CONFIRMED` (≥6 blocks).

---

## 5 · Architecture diagram (text form)

```
┌──────────────────────────────────────────────────────────────────────┐
│  Customer Application (any AI vendor, any language)                  │
│    OpenAI · Anthropic · Google · Mistral · LangChain · custom        │
└──────────────────────────────────────────────────────────────────────┘
                          │
                          │  ledgerproof SDK
                          │  (Python, TypeScript, Rust, Go-planned)
                          ▼
┌──────────────────────────────────────────────────────────────────────┐
│  LedgerProof Calendar Operator (LedgerProof Inc., commercial)        │
│    REST API: api-eu.ledgerproofhq.io                                 │
│    — POST /v1/entries        (submit content + metadata)             │
│    — GET  /v1/verify/{id}    (verify a receipt)                      │
│    — GET  /v1/anchor/{root}  (lookup an anchor by root)              │
│    Operator key: Ed25519, hardware-custodied via Unchained multisig  │
└──────────────────────────────────────────────────────────────────────┘
                          │
                          │  Merkle batching (RFC 6962-compatible)
                          ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Bitcoin Mainnet — OP_RETURN anchor transaction                      │
│  Payload: "LPR1" || merkle_root_32                                   │
│  Permanent. Public. Verifiable forever.                              │
└──────────────────────────────────────────────────────────────────────┘
                          │
                          │  Verifier libraries
                          ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Browser extensions (Chrome / Firefox / Safari)                      │
│  WordPress plugin · Provenance Search · C2PA viewer integration      │
│  Anyone, anywhere, can verify any LPR receipt.                       │
└──────────────────────────────────────────────────────────────────────┘
```

The Foundation governs the **protocol specification** (LPR 1.0). LedgerProof Inc. operates the **first calendar operator**. The architecture explicitly supports a federation — any party can run a calendar operator and issue receipts under the same protocol.

---

## 6 · Technical specifications — the cryptography

### 6.1 Hash function
- **SHA-256** for all content hashing and Merkle tree construction
- Domain separation: `0x00` prefix for leaves, `0x01` prefix for internal nodes (RFC 6962)

### 6.2 Signature scheme
- **Ed25519** over the raw 32-byte SHA-256 entry hash
- Operator key generation: hardware-backed (HSM via Unchained Capital integration for production)
- Operator key rotation policy: annual, with overlap window

### 6.3 Canonical encoding
- Entries are canonical JSON: **sorted keys, compact separators, ASCII-safe escaping**
- Rust serde_json and Python's `json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)` produce byte-identical output
- TypeScript implementation matches via a custom canonicalizer (tested against Rust output)

### 6.4 Merkle tree
- **RFC 6962** Certificate Transparency-style binary Merkle tree
- Domain-separated leaf and internal node hashing
- Trees up to 2²⁰ entries per batch (≈1M receipts in a single Bitcoin anchor)

### 6.5 Bitcoin anchoring
- **OP_RETURN** output in a standard Bitcoin transaction
- Payload: `4Y4C 4C 50 52 31` (ASCII "LPR1") followed by the 32-byte Merkle root
- Total OP_RETURN payload: **36 bytes**
- Anchor frequency: every ≤10 minutes, or when batch size reaches 100,000 entries (whichever first)
- Confirmation threshold for `CONFIRMED` status: **6 blocks**

### 6.6 Per-receipt economics at scale
| Volume | Per-receipt Bitcoin fee | Per-receipt LedgerProof fee | Operating margin |
|---|---|---|---|
| 10K/day | ~$0.003 | $0.01 | 70% |
| 100K/day | ~$0.0003 | $0.005 | 94% |
| 1M/day | ~$0.00003 | $0.001 | 97% |

The economics improve with scale because Bitcoin fees are amortized across the Merkle batch.

---

## 7 · GDPR compatibility — by construction

This is the single most important compliance design decision. **No personal data is ever anchored on Bitcoin.**

| Field | Stored where | Why |
|---|---|---|
| Content (the actual AI output) | **Off-chain only** | Customers retain it |
| SHA-256 hash of content | Off-chain + Merkle tree + Bitcoin | Not personal data |
| Operator identity | Off-chain | Public commercial entity |
| Issuer DID | Off-chain | Operator's public identifier |
| End-user identity | **Never collected** | Schema validation forbids it |

### Article 17 (Right to be Forgotten) compliance
When a customer requests deletion:
- The off-chain entry is **null-ified** in the operator's database (content fields wiped)
- The chain identity (entry_hash, anchor) is preserved
- The Bitcoin OP_RETURN is unaffected (it only contains a Merkle root — never personal data)
- The receipt becomes verifiable-but-empty: a third party can confirm "this anchor existed" but cannot recover the deleted content

### Schema-level enforcement
The Pydantic v2 model in the Python SDK and the corresponding Rust struct **forbid** email addresses in three fields at parse time:
- `deployer_id`
- `reviewer_role`
- `review_rationale`

Submissions containing email addresses in these fields are rejected before they reach the network. This is the GDPR safety net — a programmer cannot accidentally leak PII into the receipt.

---

## 8 · Software inventory — what is published and where

### Python (PyPI — live as of May 26, 2026)
| Package | Version | Function |
|---|---|---|
| `ledgerproof` | 1.0.0 | Core SDK + OpenAI / Anthropic / Google / Mistral adapters |
| `langchain-ledgerproof` | 1.0.0 | LangChain callback handler |

Install: `pip install ledgerproof langchain-ledgerproof`

### TypeScript / JavaScript (npm — live as of May 25, 2026)
| Package | Version | Function |
|---|---|---|
| `@ledgerproof/sdk` | 1.0.0 | Core SDK + Node + browser |
| `@ledgerproof/vercel-ai` | 1.0.1 | Vercel AI SDK plugin |
| `@ledgerproof/cloudflare-workers` | 1.0.0 | Cloudflare Workers AI binding |

Install: `npm install @ledgerproof/sdk`

### Browser extensions
- Chrome — published, awaiting Web Store review
- Firefox — published, awaiting AMO review
- Safari — built, TestFlight ready
- Edge — inherits from Chrome MV3

### WordPress plugin
- Alpha — github.com/ledgerproof/wordpress-plugin
- Adds an LPR receipt + verifier badge to AI-generated post content

### Web tools
- **Verifier UI**: https://verify.ledgerproofhq.io
- **Provenance Search**: https://search.ledgerproofhq.io (paste an image, get the LPR if it exists)
- **Enterprise Admin Console**: https://console.ledgerproofhq.io (operator dashboard)

### Specification documents
- **LPR 1.0 Spec**: `04-lpr-spec/LPR-1.0-SPECIFICATION.md` (Creative Commons BY 4.0)
- **EU AI Act Article 50 Profile**: `04-lpr-spec/LPR-EU-AI-ACT-50-PROFILE-v1.1.md`
- **C2PA Assertion Spec**: `04-lpr-spec/C2PA-ASSERTION-SPEC.md`
- **IETF Internet-Draft**: `draft-dawkins-scitt-ai-article50-00` (live on Datatracker)

---

## 9 · Infrastructure — production reality

| Component | Provider | Region | Notes |
|---|---|---|---|
| EU operator API | Fly.io | Frankfurt | Primary EU data-residency operator |
| US operator API | Fly.io | Iad / Sjc | Secondary, for US-domiciled customers |
| Anchor worker | Fly.io | Frankfurt | Runs the Merkle batcher + Bitcoin tx broadcaster |
| Bitcoin node | Voltage | EU | Anchor broadcast and confirmation polling |
| Operator key custody | Unchained Capital | US | 2-of-3 multisig, hardware-backed |
| DNS / TLS | Cloudflare | Global | DDoS protection, EU data-flow controls |
| Observability | Grafana Cloud | EU | Prometheus metrics, OpenTelemetry traces |
| Secrets management | 1Password + Fly.io secrets | — | No secrets in repo, mode 0600 local |
| CI/CD | GitHub Actions | — | Required green checks: tests, sbom, audit |
| Supply-chain security | Cargo vendor + SLSA Level 3 build | — | Reproducible builds for the Rust core |

**Uptime since May 18:** 100%. No incidents.

---

## 10 · The team — present and planned

### Present
- **Veronica S. Dawkins** — Founder, Foundation Director, Technical Lead. Designed the protocol, wrote the spec, built the reference implementation, ran the launch.

### Planned hires post-close (July 6 launch sprint)
1. **Senior Rust + Cryptography Engineer** — full-time, EU-based preferred
2. **Senior Python SDK Engineer** — contractor → FTE
3. **Senior TypeScript / Edge Engineer** — contractor
4. **Senior DevOps / SRE Engineer** — contractor → FTE
5. **Senior Technical Writer** — contractor (docs.ledgerproofhq.io)
6. **Senior Browser Extension Engineer** — contractor

Skill specs for all six roles exist in `~/.claude/skills/` — contractor selection criteria, day-one task assignments, and code review templates are pre-written.

---

## 11 · Patents and IP

**Five USPTO provisional patent applications filed:**
1. LPR receipt format and verifier API
2. Bitcoin OP_RETURN anchor format with LPR1 prefix
3. Merkle batching protocol for high-throughput AI provenance
4. C2PA assertion bridge (`org.ledgerproof.receipt.v1`)
5. GDPR-by-construction schema validation

**IP assignment:**
- Patents assigned to LedgerProof Inc.
- Perpetual, royalty-free, irrevocable license granted to LedgerProof Foundation
- Foundation can sub-license to any LPR-compatible operator at zero cost
- This structure ensures the protocol cannot be captured by the commercial entity

---

## 12 · The capital situation

### The round
- **$5M base** raise, expandable to **$7M** if all three Bitcoin-native funds participate
- **$30M post-money SAFE** valuation (anchored, may move up only if a fund leads aggressively)
- **June 25, 2026** close
- Pro-rata for participants ≥$500K
- One board observer for the lead investor
- Independent advisor seat to be filled in Q3 (regulatory expert)

### The three funds
| Fund | Lead contact | Status | Meeting |
|---|---|---|---|
| **Trammell Venture Partners** | Christopher Calicott + Aryan Malhotra | Scheduled | Wed May 27, 9:30 AM CT |
| **Stillmark** | Alyse Killeen + Vikash Singh | Confirmed | Wed May 27, 4:00 PM PDT |
| **Fulgur Ventures** | Michele Anastasio + Oleg Mikhalsky | Reply sent | This week or next |

### Decision timeline
- **June 8** — first term sheet expected
- **June 15** — lead investor selected
- **June 25** — round closes
- **July 6** — public launch

### Runway without external capital
Current burn supports operations through Q4 2026 conservatively. The protocol is shipped and live; capital accelerates GTM, it does not enable existence.

---

## 13 · Strategic posture — the honest assessment

In the space of one week, the position has gone from:
- One scheduled investor call (TVP)

…to:
- **Three Bitcoin-native VCs in active evaluation**
- **LPR v1.1 deployed in production with 100% uptime**
- **Three npm packages and two PyPI packages live globally**
- **IETF Internet-Draft accepted to Datatracker**
- **Regulator engagement records in two EU institutions**
- **EU AI Act Code of Practice signatory application prepared**

This is the strongest pre-close position a Bitcoin-native protocol-layer founder can occupy.

**Posture for the meetings:**
- Run each conversation cleanly on its own merit.
- Do not weaponize the multi-fund situation. State it honestly when asked.
- Do not lower the valuation. Do not extend the timeline beyond June 25 unless all three pass.
- Pick the lead based on strategic fit first, dollar amount second, speed third.

---

## 14 · What can go wrong — and the mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| All three funds want longer diligence than June 25 permits | Medium | Have a "speed-to-yes" lead identified by June 8. Extend to July 15 only if necessary. |
| All three pass | Low | Hybrid round: smaller checks from Ten31, Castle Island, Bitcoin Frontier Fund + angels. Self-fund through pilot revenue if necessary. |
| EU Commission delays Article 50 enforcement | Low | Enforcement is a treaty obligation under in-force EU law since Aug 2024. Member states are already publishing guidance. |
| Competitor ships a similar protocol | Medium-low | IETF process + Foundation governance + first-mover infrastructure deployment make this difficult. C2PA itself is positioning to incorporate LPR-style anchors. |
| Bitcoin fee market spike makes anchoring expensive | Medium | Merkle batching already amortizes fees. Multi-substrate fallback profiles (Ethereum, federated CT logs) defined in LPR 1.0 §8. |
| Operator key compromise | Very low | 2-of-3 multisig via Unchained, hardware-custodied, annual rotation, no single point of failure. |
| GDPR challenge | Very low | No personal data is ever anchored. Schema validation forbids PII at parse time. Article 17 soft-delete preserves chain identity while wiping content. |

---

## 15 · The closing line

This is not a hype cycle. It is a regulatory mandate from a jurisdiction with €15M-and-3%-of-turnover enforcement teeth, arriving in **68 days**, with a working protocol, a Foundation, an IETF draft, published SDKs, and three of the most respected Bitcoin-native funds in the world reaching out the same week.

The protocol is live. The capital decision is the only remaining variable.

---

*Prepared May 26, 2026 · LedgerProof Foundation · Veronica S. Dawkins · veronica@ledgerproofhq.io*
