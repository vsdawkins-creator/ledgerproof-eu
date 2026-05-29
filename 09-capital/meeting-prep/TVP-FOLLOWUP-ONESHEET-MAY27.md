# LedgerProof — Article 50 Recap, Technical Status, Roadmap

**To:** Aryan Malhotra, Trammell Venture Partners
**From:** Veronica S. Dawkins, Founder, LedgerProof Foundation
**Date:** May 27, 2026
**Re:** Follow-up to our call — Article 50 deep-dive, current technical state, where it's going

Aryan — thank you for the conversation today. As discussed, here is the consolidated brief on the EU AI Act Article 50 landscape, LedgerProof's current technical position, and the eighteen-month roadmap. Anything cited here is supported by a longer document in our data room; happy to send any of them.

---

## 1 · EU AI Act Article 50 — what it actually mandates

Enforceable **August 2, 2026** (67 days from this letter).

| Sub-article | Obligation | Who is on the hook |
|---|---|---|
| **50(1)** | Inform users they're interacting with AI (chatbots) | Providers of AI systems |
| **50(2)** | Mark synthetic audio / image / video / text in a **machine-readable format** detectable as artificially generated | Providers of AI generators (foundation models + applications) |
| **50(4)** | Disclose that deepfake content has been artificially manipulated | Deployers of deepfakes |

**Penalty: €15M or 3% of worldwide annual turnover, whichever is HIGHER, per infringement.** For a Tier-1 bank or major AI vendor, that is materially a 9- or 10-figure exposure event, not a fine.

**The implementation gap the law leaves open:** Article 50 specifies *what* must happen, not *how*. There is no agreed European technical standard for machine-readable AI content marking. That is the space LedgerProof fills.

---

## 2 · LedgerProof's technical answer

**An open cryptographic protocol** (LPR — LedgerProof Receipt) that binds AI-generated content to a permanent, machine-verifiable receipt anchored to the Bitcoin blockchain.

### How a receipt is constructed (every AI output, in <100ms)

```
AI output (image, text, audio, video, code, document)
        │
        ├──▶ SHA-256 hash of canonical content
        │
        ├──▶ CBOR-encoded receipt with:
        │       • content_hash (32 bytes)
        │       • issuer_did (the AI vendor's verifiable identity)
        │       • content_type + Article 50 profile classification
        │       • timestamp (RFC 3339)
        │       • EU-AI-ACT-50-v1.1 disclosure fields
        │
        ├──▶ Ed25519 signature over canonical entry hash
        │
        └──▶ Batched into RFC 6962 Merkle tree
                │
                └──▶ Bitcoin OP_RETURN broadcast:
                        "LPR1" (4 bytes) || merkle_root (32 bytes) = 36 bytes
```

### The cryptographic stack

| Layer | Algorithm | Rationale |
|---|---|---|
| Content hash | SHA-256 | NIST-standardized, universally supported |
| Signature | Ed25519 | Fast, small, well-audited, RFC 8032 |
| Merkle tree | RFC 6962 with domain separation | Same construction used in Certificate Transparency |
| Anchor | Bitcoin OP_RETURN | Most expensive timestamping medium on Earth to attack |
| Encoding | Canonical CBOR (RFC 8949) | Deterministic, byte-identical across implementations |
| Identity | W3C DIDs + Verifiable Credentials | eIDAS-compatible for EU qualified electronic seals |

### Cost economics

| Volume | Per-receipt Bitcoin fee | Per-receipt LedgerProof fee | Operating margin |
|---|---|---|---|
| 10K/day | ~$0.003 | $0.01 | 70% |
| 100K/day | ~$0.0003 | $0.005 | 94% |
| **1M/day** | **~$0.00003** | **$0.001** | **97%** |

Margins compound with scale via Merkle batching.

### GDPR compatibility (by construction — not retrofitted)

No personal data is ever anchored. Only the SHA-256 hash + non-PII metadata reaches Bitcoin. Schema validation **rejects email addresses at parse time** in three fields (`deployer_id`, `reviewer_role`, `review_rationale`) — the regulator-safe rail is enforced in code, not policy. Article 17 erasure preserves chain identity while nulling content fields.

---

## 3 · Production status — what is live today

| Asset | Status |
|---|---|
| **EU operator** | Live in production at `api-eu.ledgerproofhq.io` (Fly.io Frankfurt) since May 18; 100% uptime |
| **Real Bitcoin mainnet anchors** | Three live anchors (May 6 / 13 / 18) with full Merkle inclusion proofs |
| **LPR v1.1 specification** | Published, covers all three Article 50 sub-articles |
| **Python SDK** (`ledgerproof`) | Live on PyPI, v1.0.0 (`pip install ledgerproof`) |
| **LangChain integration** (`langchain-ledgerproof`) | Live on PyPI, v1.0.0 |
| **TypeScript SDK** (`@ledgerproof/sdk`) | Live on npm |
| **Vercel AI SDK adapter** | Live on npm |
| **Cloudflare Workers binding** | Live on npm |
| **Browser extensions** | Chrome / Firefox / Safari — published, store reviews in progress |
| **WordPress plugin** | Alpha published |
| **Public verifier** | `verify.ledgerproofhq.io` |
| **Provenance Search** | `search.ledgerproofhq.io` (paste image → find receipt) |
| **IETF Internet-Draft** | `draft-dawkins-scitt-ai-article50-00` posted and confirmed on Datatracker May 25 |
| **C2PA assertion specification** | `org.ledgerproof.receipt.v1` drafted for CAWG submission |
| **eIDAS compatibility statement** | Published |
| **EU AI Act Code of Practice signatory application** | Package complete; submission pending |

### Code repository state (as of this email)

- Active branch: `feat/lpr-v1.1-article-50-expansion` on `vsdawkins-creator/ledgerproof-platform`
- **CI: all green** (Rust build, test, clippy, fmt, cargo-audit; web app build + type-check)
- Pull request open and merge-ready
- Vendored dependencies including `quantum-edge-2` (the cryptographic core); Merkle and canonicalization byte-identical across Rust, Python, and TypeScript

### Patent posture

Five USPTO provisional applications filed covering: receipt format and verifier API, OP_RETURN anchor format, Merkle batching for high-throughput AI provenance, C2PA assertion bridge, and GDPR-by-construction schema validation. Strategy is defensive-only — patents assigned to LedgerProof Inc. with perpetual royalty-free license to the Foundation, and from the Foundation to any LPR-compatible implementation, on the Apache / Eclipse model.

---

## 4 · Roadmap — where this goes

### LPR 1.2 — Canonicality Layer (Q3 2026, post-close)

Four new mechanisms answering "which receipt is the canonical one when multiple exist?"

1. **Lineage chains** — receipts reference prior versions, forming a Merkle DAG of authorized edits with same-DID-or-delegation succession rules
2. **Multi-modal similarity hashing** — TLSH for text, perceptual hash for images (shipped), audio fingerprinting (Chromaprint), video keyframe hashing, code AST canonicalization
3. **Witness attestation** — counter-signatures by notaries, regulators, publishers, witnesses; itself anchored
4. **Foundation Canonical Registry** — FROST-Ed25519 threshold-signed dispute resolution; resolutions are themselves anchored receipts

Full normative spec annex drafted: 33 implementation tickets across 5 phases; 22-week elapsed implementation with a 3-engineer team. Backward-compatibility contract: every v1.0/1.1 receipt verifies byte-identically under v1.2.

### LPR 2.0 — Post-Quantum Annex (Q1 2027 ratification)

- Hybrid Ed25519 + ML-DSA-65 (Dilithium3) for ordinary receipts
- SPHINCS+ (SLH-DSA-SHA2-256s) for high-assurance long-horizon receipts (legal, government, IP)
- Cryptographic agility framework for future scheme transitions
- Migration path that preserves every v1.x receipt's verifiability indefinitely

Drafted as an outline; public review Q4 2026, ratification Q1 2027.

### The 18-month "structurally unstoppable" plan

Seven priority technologies, each neutralizing a named adversary class:

| Priority | Tech | Adversary neutralized |
|---|---|---|
| 1 | Multi-substrate anchoring (Bitcoin + Ethereum + Celestia + CT-log federation) | Single-chain failure or jurisdictional ban |
| 2 | FROST-Ed25519 threshold signing + Receipt Revocation List | Operator key compromise / insider attack |
| 3 | Hybrid Ed25519 + Dilithium3 signatures | Quantum / cryptanalytic break |
| 4 | Federated operator network (≥3 jurisdictions, Tor-enabled) | State censorship |
| 5 | Multi-modal similarity hashing | AI-content polymorphism (re-encode, comma-change, watermark strip) |
| 6 | SLSA L3 + reproducible WebAssembly verifier | Supply-chain attack on the verifier itself |
| 7 | Cross-bridges to C2PA + SynthID + IPTC + ISCC | Standards fragmentation — converts threat into distribution |

Master plan document fully written. Foundation governance hardening (US 501(c)(3) + Swiss Verein + Singapore non-profit) proceeds in parallel with the engineering work.

### Series A target (Q3 2027)

All seven priority technologies in production, three operators across three jurisdictions, two substrates in production, external security audit complete (Trail of Bits / NCC), SOC 2 Type 2 in flight, 3+ Tier-1 enterprise customers. Target Series A valuation: $200–400M post-money.

---

## 5 · The round — updated structure

As discussed on the call, the seed round is sized at **$15M, structured as three co-leads at $5M each.**

- **Three co-leads at $5M each** — TVP, Stillmark, Fulgur (with whom we are also in active conversation)
- **Post-money: $45M SAFE** (preserves the pre-money math from the original $5M-at-$30M-post structure while accommodating the larger raise)
- **Close: June 25, 2026**
- **Public launch: July 6, 2026**
- **Pro-rata to all $500K+ participants**
- **One board observer per co-lead** (three observers); independent advisor seat reserved for an EU regulatory expert
- **Foundation governance separate** from LedgerProof Inc. cap table

This structure gives each Bitcoin-native fund a meaningful position, gives the company eighteen months of runway through Series A, and preserves the founder's ability to recruit a fourth co-lead from the financial-services side (Illuminate Financial is in active inbound triage) without diluting the existing three.

### Use of $15M

| Allocation | Amount | Purpose |
|---|---|---|
| Engineering team (6 senior contractors → FTEs) | $5.4M | Rust + cryptography, Python SDK, TypeScript/edge, DevOps/SRE, browser extensions, technical writing |
| Independent security audit (Trail of Bits / NCC) | $400K | Protocol + reference implementation |
| Foundation governance (US + Swiss + Singapore) | $300K | Multi-jurisdiction structure, board recruitment, charter |
| Operator infrastructure (3 jurisdictions) | $1.8M | Fly / hyperscaler infra, HSM custody, federation deployment |
| Patents + IP counsel (Fenwick + Bird & Bird) | $200K | Defensive patent strategy execution |
| GTM (Tier-1 enterprise sales + Foundation engagement) | $4.5M | First 10 enterprise customers, EU regulator engagement, EU CoP signatory work |
| Reserve / runway buffer | $2.4M | 6-month operational cushion through Series A |
| **Total** | **$15M** | **18 months runway through Series A in Q3 2027** |

---

## 6 · Next steps

1. **Data room access** — I will send a Box link separately with the LPR 1.0 + 1.1 specifications, the LPR 1.2 Canonicality Annex, the LPR 2.0 Post-Quantum Annex outline, the Unstoppable Master Plan, the EU regulatory dossier, and the production deployment runbooks.
2. **Technical diligence call** — happy to schedule a follow-up with your technical advisor at any time. The cryptographic stack will withstand any Trail-of-Bits-grade review.
3. **SAFE document** — ready to share on TVP's preferred template.
4. **Timeline reminder** — close target is June 25. The Article 50 enforcement clock (Aug 2) is the structural reason this is not a roll-the-round-for-six-weeks situation.

Aryan, please let me know what else would help you assemble the internal memo, and what your timeline is to surface this to Christopher and the IC. Anything I can produce that makes that conversation cleaner is yours on request.

Best,
Veronica S. Dawkins
Founder, LedgerProof Foundation
veronica@ledgerproofhq.io
spec@ledgerproofhq.io

---

*Appendix on request: full LPR 1.2 spec annex, LPR 2.0 PQ outline, Unstoppable Master Plan, financial-services regulatory mapping (DORA / MiFID II / EBA / SS1/23 / Solvency II), 33-ticket v1.2 implementation plan, full meeting prep document.*
