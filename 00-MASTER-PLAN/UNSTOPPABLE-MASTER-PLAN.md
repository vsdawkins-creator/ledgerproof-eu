# LedgerProof — "Truly Unstoppable" Master Plan

**Document:** Engineering and governance roadmap to make LedgerProof structurally unstoppable
**Status:** Strategic master plan, May 26, 2026
**Author:** Veronica S. Dawkins, Founder, LedgerProof Foundation
**Horizon:** 18 months post-seed-close (July 2026 → December 2027)
**Use:** Internal engineering planning + investor diligence artifact (Series A foundation)

---

## 1 · What "unstoppable" means in this document

**Unstoppable infrastructure** is infrastructure that, for every plausible adversary or failure mode, has at least one structural defense that does not depend on a single party. The protocols that have earned this property — SMTP, HTTP, TLS, BitTorrent, Bitcoin, Tor — share five attributes:

1. The **specification is open** and implementable by anyone.
2. **Multiple independent implementations** exist.
3. **Economic incentives** align with continued operation.
4. **Governance is plural**, not corporate.
5. The **transport itself is censorship-resistant**.

LedgerProof has attributes 1, 3, and 4 in some form today. This plan addresses attributes 2 and 5, and hardens 1, 3, 4 against future capture attempts.

This is **not** a feature roadmap. It is a structural-defense roadmap. Each technology listed below neutralizes a specific class of adversary.

---

## 2 · Threat model and mitigation matrix

| # | Adversary / Failure | Existing protection | Gap | Closes by |
|---|---|---|---|---|
| 1 | **Cryptanalytic break of Ed25519** | None | Single-scheme exposure | Hybrid Ed25519 + Dilithium3 (LPR 2.0) |
| 2 | **Quantum computer breaks all classical crypto** | None | All v1.x receipts at risk | Post-quantum signatures + re-attestation flow |
| 3 | **SHA-256 collision attack** | None | Single-hash exposure | Dual-hash Merkle (SHA-256 + BLAKE3) in HighAssurance profile |
| 4 | **Operator signing key compromise** | HSM custody (Unchained) | Single signer | FROST-Ed25519 threshold signing (3-of-5) |
| 5 | **Operator insider attack** | Single-operator trust | No revocation mechanism | Receipt Revocation List (RRL) anchored to Bitcoin |
| 6 | **Bitcoin substrate failure (fee crisis, sanctions, cartel censorship)** | Hardcoded Bitcoin dependency | Single-substrate exposure | Multi-substrate anchoring (Ethereum, Celestia, federated CT logs) |
| 7 | **State-level operator censorship** | EU-only operator presence | Single-jurisdiction exposure | Federated operator network (≥3 jurisdictions) + Tor hidden-service endpoints |
| 8 | **DNS-level censorship of operators** | DNS-dependent endpoint discovery | DNS hijack defeats operators | Bitcoin-anchored operator discovery list (no DNS required) |
| 9 | **Receipt loss when operator goes offline** | Per-operator storage | Receipts tied to operator availability | libp2p / IPFS gossip between operators |
| 10 | **Identity-binding capture (centralized DID registry)** | did:web only | Single DID method | DID plurality: did:web, did:key, did:btcr, did:ion, eIDAS 2.0 EUDI |
| 11 | **Foundation acquisition / board takeover** | 501(c)(3) only | Single-jurisdiction Foundation | Multi-jurisdiction structure: US 501(c)(3) + Swiss Verein + Singapore non-profit |
| 12 | **Foundation regulatory pressure (single-state)** | Single regulator exposure | Same as #11 | Same |
| 13 | **Proprietary fork of the protocol** | Apache 2.0 license | License alone is not enough | Defensive patent pool + Foundation IP grant + multiple reference implementations |
| 14 | **Supply-chain attack on SDKs or operator binaries** | npm provenance + PyPI trusted publishers | No reproducible verifier | SLSA Level 3 build provenance + Sigstore signing + reproducible WebAssembly verifier |
| 15 | **AI-content polymorphism (re-encode, comma-change, watermark strip)** | Image pHash only | Text / audio / video / code uncovered | Multi-modal similarity hashing (TLSH, audio fingerprint, video keyframe, AST hash) |
| 16 | **Real-time deepfake (live video, voice cloning)** | None — receipts are after-the-fact | Live-stream attack surface | Continuous attestation via short-interval Merkle commitments |
| 17 | **Standards fragmentation (C2PA / SynthID / IPTC / ISCC diverge)** | C2PA bridge only | Three other standards uncovered | Bridges to SynthID, IPTC PhotoMetadata, ISCC |

---

## 3 · The seven priority technologies

Of the 17 threats above, seven technologies neutralize the majority of the risk surface and compound across multiple threats. These are the priority post-close engineering investments.

### Priority 1 — Multi-substrate anchoring

**Threats neutralized:** #6 (Bitcoin failure), partial #7 (jurisdictional substrate ban)
**Effort:** 8–12 engineer-weeks
**Why first:** Single-substrate dependency is the most named risk in investor diligence. Closing this risk first is the highest-confidence move.

**Substrates to support:**
- Bitcoin mainnet (current, primary)
- Ethereum mainnet (calldata anchoring)
- Celestia / EigenDA (data availability layers)
- Federated CT log network (operator-cosigned roots, no chain dependency)
- Arweave (economically-endowed permanent storage)

**Architecture:** The verifier API does not change. Receipts carry a substrate identifier; verifiers route to the appropriate proof-checker. New substrates are added via the existing Algorithm Identifier Registry pattern (per LPR 2.0 §5).

**Acceptance criteria:**
- At least 2 substrates in production (Bitcoin + Ethereum)
- Failover automation when primary fee market is uneconomic
- Substrate selection at receipt issuance is operator policy, not protocol mandate

### Priority 2 — FROST-Ed25519 threshold signing + Receipt Revocation List

**Threats neutralized:** #4 (operator key compromise), #5 (operator insider attack)
**Effort:** 6–8 engineer-weeks
**Why second:** The single most-cited operational risk for any cryptographic infrastructure. Solving it once enables Foundation arbitration (LPR 1.2 §6) AND operator hardening.

**Components:**
- `crates/ledgerproof-frost/` — FROST-Ed25519 DKG, partial signing, aggregation
- HSM integration: YubiHSM2, AWS CloudHSM, Intel SGX/AMD SEV-SNP attested enclaves
- Receipt Revocation List entries anchored alongside ordinary entries
- Per-anchor-cycle RRL refresh; verifiers consult RRL during verification

**Acceptance criteria:**
- 3-of-5 operator signing across geographically-separated HSMs
- Tested compromise simulation: revoke a key, verify all subsequent receipts gracefully reject
- Used by Foundation Arbitration Panel (LPR 1.2 §6.7)

### Priority 3 — Hybrid Ed25519 + Dilithium3 signatures (PQ readiness)

**Threats neutralized:** #1 (Ed25519 break), #2 (quantum break)
**Effort:** 6 engineer-weeks
**Why third:** "Harvest now, decrypt later" attacks mean receipts issued today are already at risk. The cost to add dual-signing now is trivial; the cost to retrofit it later is high.

**Implementation:**
- All v2.0 receipts dual-signed with Ed25519 + ML-DSA-65 (Dilithium3)
- DID documents include both classical and PQ public keys
- Verifier accepts either field name (`signature` or `sig_classical`) during transition
- Cryptographic agility registry (LPR 2.0 §5.1) supports future PQ scheme additions

**Acceptance criteria:**
- LPR 2.0 spec ratified (Q1 2027 per outline §6.3)
- All operators dual-signing by Q3 2027
- Receipts ~3.3 KB larger; throughput SLA preserved

### Priority 4 — Federated operator network (≥3 jurisdictions, Tor-enabled)

**Threats neutralized:** #7 (state censorship), #8 (DNS censorship), #9 (operator offline), partial #12 (Foundation pressure)
**Effort:** 6–8 engineer-weeks + Foundation governance work
**Why fourth:** "Federated" is currently a roadmap word; making it operational requires real second and third operators standing up.

**Components:**
- Foundation charter requires ≥3 active operators across ≥3 jurisdictions
- Each operator publishes `.onion` and Nym mixnet hidden-service endpoint in addition to standard HTTPS
- Bitcoin-anchored operator discovery list (no DNS dependency)
- libp2p gossip protocol so receipts are globally retrievable even if their issuing operator goes offline

**Operator candidates (commercial partnerships, not Foundation work):**
- **EU**: LedgerProof EU (existing, Frankfurt)
- **US**: TVP-introduced operator (Voltage, River, or Castle Island portfolio)
- **UK**: Stillmark-introduced operator
- **Asia-Pacific**: KDDI Web Communications (Japan) or NCS (Singapore)
- **LATAM**: A Foundation-supported nonprofit operator

**Acceptance criteria:**
- At least 3 operators in production across at least 3 jurisdictions
- Verifier UI cycles between operators automatically on failure
- Tor / Nym endpoints documented and tested

### Priority 5 — Multi-modal similarity hashing

**Threats neutralized:** #15 (AI polymorphism)
**Effort:** 12–16 engineer-weeks
**Why fifth:** This is the visible quality of the verifier UI. Without it, a $50 comma-change attack defeats the system at the end-user level. The protocol can be perfect; the user experience is what investors and customers see.

**Modalities:**
- Text: TLSH (LPR 1.2 §4)
- Image: pHash + CLIP embedding distance (already partial)
- Audio: Chromaprint spectral fingerprint
- Video: keyframe pHash + temporal fingerprint
- Code: tree-sitter AST canonical hash

**Acceptance criteria:**
- All five modalities in production
- Verifier UI flags near-duplicates with confidence scores
- Similarity Algorithm Registry maintained (LPR 1.2 §4.6)

### Priority 6 — SLSA L3 build provenance + reproducible WebAssembly verifier

**Threats neutralized:** #14 (supply-chain attack)
**Effort:** 5 engineer-weeks
**Why sixth:** A compromised verifier defeats every other defense. A reproducible verifier means "anyone can verify the verifier."

**Components:**
- SLSA Level 3 build provenance for every release artifact
- Sigstore + in-toto attestations
- Reproducible WebAssembly verifier (used in browser extensions, web tool, embedded badges)
- Build attestations themselves anchored to LedgerProof — recursive provenance

**Acceptance criteria:**
- All npm + PyPI + GitHub release artifacts SLSA L3
- WebAssembly verifier reproducible byte-for-byte across rebuilds
- Build attestations published to verify.ledgerproofhq.io

### Priority 7 — Cross-bridges to C2PA / SynthID / IPTC / ISCC

**Threats neutralized:** #17 (standards fragmentation) — and converts threat into distribution
**Effort:** 8 engineer-weeks (2 per bridge)
**Why seventh:** The lowest-effort, highest-marketing-leverage technology. Each bridge makes a competing standard a *distribution channel* for LedgerProof.

**Bridges:**
- **C2PA Coalition**: `org.ledgerproof.receipt.v1` assertion (already drafted; formal Coalition membership pending)
- **Google SynthID**: SynthID detector → LPR receipt bridge
- **IPTC PhotoMetadata**: IPTC standard → LPR receipt fields mapping
- **ISCC** (ISO/IEC 24138): ISCC content code → LPR similarity hash mapping

**Acceptance criteria:**
- All four bridges shipped as separate `@ledgerproof/bridge-*` npm packages and `ledgerproof-bridge-*` PyPI packages
- Reference implementations co-published with respective standards bodies
- "LedgerProof is interoperable with C2PA, SynthID, IPTC, ISCC" becomes a verifiable marketing claim

---

## 4 · 18-month timeline (post-close)

```
Month:         1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18
Hiring:        ████████
Audit (ToB):       █████████████
Priority 1:        ████████████████
Priority 2:        ████████████
Priority 3:                ████████████████████ (LPR 2.0 ratification Q1 2027 = M9)
Priority 4:                ████████████████ (federation operators)
Priority 5:                        ████████████████████████ (multi-modal)
Priority 6:                                ████████ (SLSA + Wasm)
Priority 7:                                        ████████████ (cross-bridges)

Governance:                  ████████████████████ (Foundation board, Swiss Verein, Singapore)
Series A prep:                                              ████████████ (Q3 2027)
```

Wall-clock: **18 months to all 7 technologies in production**.
With 3 senior engineers + 1 SRE + 1 governance lead, this is achievable on a seed-stage budget.

---

## 5 · Foundation governance hardening

The Foundation is the asset. Without governance hardening, the technical defenses are insufficient. The following governance steps proceed in parallel with the engineering work.

### 5.1 Multi-jurisdictional Foundation structure

| Entity | Jurisdiction | Status | Timeline |
|---|---|---|---|
| LedgerProof Foundation, Inc. | US (Delaware) 501(c)(3) | Filed | Q3 2026 |
| LedgerProof Foundation Verein | Switzerland | Not started | Q1 2027 |
| LedgerProof Foundation Asia | Singapore | Not started | Q2 2027 |

### 5.2 Founding board composition (target Q3 2026)

Five seats. No single entity controls more than one seat.

| Seat | Profile | Current candidate (illustrative) |
|---|---|---|
| 1 | Founder / Executive Director | Veronica S. Dawkins |
| 2 | Bitcoin-native technologist | TBD post-close (Christopher Calicott / Alyse Killeen orbit) |
| 3 | EU regulatory expert | TBD (former AI Office staff or EU Parliament rapporteur) |
| 4 | Academic cryptographer | TBD (Cas Cremers / Matt Green / Ian Goldberg orbit) |
| 5 | Civil society / journalism | TBD (EFF / Mozilla Foundation alumnus, or major media org) |

### 5.3 Charter restrictions (drafted, ratified at first board meeting)

- No conversion to for-profit
- No acquisition by any single entity
- Board composition: no single entity controls more than 1 seat
- Patent grant: perpetual, royalty-free, irrevocable license to any LPR-compatible operator
- Asset disposition on dissolution: 100% to another 501(c)(3) with substantially similar mission

### 5.4 Defensive patent pool

5 USPTO provisional patents already filed are assigned to LedgerProof Inc. with perpetual irrevocable license to the Foundation. Additional patents filed by Foundation members are joined to the same pool with the same terms.

The Foundation explicitly does not assert these patents against LPR-compatible implementations. Aggressors who assert patents against LPR-compatible implementations forfeit access to the pool (industry-standard Eclipse / Apache-style defensive patent clause).

---

## 6 · The Series A story this builds

By Q3 2027 (18 months post-seed-close), LedgerProof will have:

1. **All seven priority technologies in production**
2. **Multi-jurisdictional Foundation governance ratified**
3. **3+ operators across 3+ jurisdictions**
4. **2+ substrate anchoring in production**
5. **External security audit complete (Trail of Bits / NCC)**
6. **SOC 2 Type 2 + ISO 27001 in flight or complete**
7. **3+ Tier-1 enterprise customers (banks, media, regulators)**
8. **Foundation board with named non-founder seats**
9. **IETF SCITT working group active participation**
10. **C2PA Coalition formal member**

That is a Series A profile. The diligence question changes from "is this real?" to "what's the next 5-year horizon?"

**Target Series A valuation:** $200M–$400M post-money.
**Target Series A use of proceeds:** scale operator network globally; ship priority technologies that didn't make the seed-stage list (real-time stream attestation, ZK privacy receipts, threshold post-quantum signing).

---

## 7 · How this plan turns into reality

The plan itself does not matter. The execution matters. The execution requires:

1. **People:** 6 named senior contractors / FTEs whose hiring brief is already drafted (the `senior-*-contractor` skills in `~/.claude/skills/`).
2. **Capital:** $5M base, $7M upper bound. The 18-month plan above is fully fundable inside that envelope at the assumed team size and cost.
3. **Discipline:** monthly review of this plan against actuals. Slippage is documented in `00-MASTER-PLAN/UNSTOPPABLE-STATUS-{YYYY-MM}.md` files, not hidden.
4. **External signals:** quarterly publication of the Foundation Transparency Report, the operator PQ-posture report, and the cumulative threat-model coverage update. Investors and customers read these. They are the proof-of-execution that justifies the Series A markup.

---

## 8 · The one-line investor framing

> "There are seventeen specific ways someone or something could try to stop LedgerProof from being the open provenance layer for AI content. Seven priority technologies, executed over eighteen months on the seed capital we are raising, neutralize all seventeen. Each is mapped to a named adversary class, a dated milestone, and a contractor whose hiring brief already exists. The Foundation governance hardening proceeds in parallel. By Q3 2027 the protocol is not 'hopefully' unstoppable — it is structurally unstoppable, and the artifacts to prove it are public."

That sentence is what you say to a Series A partner two years from now.

---

*End of Unstoppable Master Plan, May 26, 2026.*
*Next review: monthly, beginning Q3 2026.*
