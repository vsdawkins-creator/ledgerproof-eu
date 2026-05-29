# Unstoppable Master Plan

**Status:** Drafted May 26, 2026
**File:** `00-MASTER-PLAN/UNSTOPPABLE-MASTER-PLAN.md`
**Horizon:** 18 months post-seed-close (July 2026 → December 2027)

## What "unstoppable" means
Infrastructure where, for every plausible adversary, there's at least one structural defense that doesn't depend on a single party. Like SMTP, HTTP, TLS, BitTorrent, Bitcoin, Tor.

5 attributes shared by all unstoppable protocols:
1. Open specification
2. Multiple independent implementations
3. Economic incentives align with operation
4. Plural governance, not corporate
5. Censorship-resistant transport

LedgerProof has #1, #3, #4 in some form. This plan addresses #2 and #5, and hardens 1/3/4.

## 17 threats → 7 priority technologies

| # | Adversary | Tech that neutralizes |
|---|---|---|
| 1 | Cryptanalytic Ed25519 break | Priority 3 — Hybrid Ed25519+Dilithium3 |
| 2 | Quantum computer | Priority 3 |
| 3 | SHA-256 collision | Dual-hash Merkle in HighAssurance |
| 4 | Operator key compromise | Priority 2 — FROST-Ed25519 threshold |
| 5 | Operator insider attack | Priority 2 + Receipt Revocation List |
| 6 | Bitcoin failure (fees, sanctions, cartel) | Priority 1 — Multi-substrate |
| 7 | State censorship of operators | Priority 4 — Federated network + Tor |
| 8 | DNS censorship | Bitcoin-anchored operator discovery |
| 9 | Receipt loss when operator offline | libp2p gossip |
| 10 | Identity registry capture | DID plurality (did:web, did:key, did:btcr, did:ion, eIDAS) |
| 11 | Foundation acquisition | Multi-jurisdiction structure (US 501(c)(3) + Swiss Verein + Singapore) |
| 12 | Foundation regulatory pressure | Same as 11 |
| 13 | Proprietary fork | Defensive patent pool + Apache 2.0 + multiple impls |
| 14 | Supply-chain attack | Priority 6 — SLSA L3 + Sigstore + reproducible Wasm |
| 15 | AI-content polymorphism | Priority 5 — Multi-modal similarity |
| 16 | Real-time deepfake | Live-stream attestation (deferred but planned) |
| 17 | Standards fragmentation | Priority 7 — Cross-bridges to C2PA/SynthID/IPTC/ISCC |

## The 7 priority technologies (in order)

| Priority | Tech | Effort | Closes threats |
|---|---|---|---|
| **1** | Multi-substrate anchoring (Bitcoin + Ethereum + Celestia + CT-logs + Arweave) | 8-12 weeks | 6, partial 7 |
| **2** | FROST-Ed25519 threshold signing + Receipt Revocation List | 6-8 weeks | 4, 5 |
| **3** | Hybrid Ed25519 + Dilithium3 signatures (PQ readiness) | 6 weeks | 1, 2 |
| **4** | Federated operator network (≥3 jurisdictions, Tor-enabled) | 6-8 weeks + governance | 7, 8, 9 |
| **5** | Multi-modal similarity hashing (text/audio/video/code) | 12-16 weeks | 15 |
| **6** | SLSA L3 + reproducible WebAssembly verifier | 5 weeks | 14 |
| **7** | Cross-bridges to C2PA + SynthID + IPTC + ISCC | 8 weeks (2/bridge) | 17 — converts threats into distribution |

## 18-month timeline (post-close)

```
Month:         1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18
Hiring:        ████████
Audit (ToB):       █████████████
Priority 1:        ████████████████
Priority 2:        ████████████
Priority 3:                ████████████████████
Priority 4:                ████████████████
Priority 5:                        ████████████████████████
Priority 6:                                ████████
Priority 7:                                        ████████████
Governance:                  ████████████████████
Series A prep:                                              ████████████
```

Wall-clock with 3 engineers + 1 SRE + 1 governance lead: **18 months to all 7 in production**.

## Foundation governance hardening

### Multi-jurisdictional structure
- LedgerProof Foundation, Inc. (US Delaware 501(c)(3)) — Q3 2026
- LedgerProof Foundation Verein (Switzerland) — Q1 2027
- LedgerProof Foundation Asia (Singapore) — Q2 2027

### 5-seat board target (Q3 2026)
| Seat | Profile |
|---|---|
| 1 | Founder / Executive Director — Veronica |
| 2 | Bitcoin-native technologist (Calicott / Killeen orbit) |
| 3 | EU regulatory expert (former AI Office / EU Parliament rapporteur) |
| 4 | Academic cryptographer (Cas Cremers / Matt Green / Ian Goldberg) |
| 5 | Civil society / journalism (EFF / Mozilla alumnus / major media) |

### Charter restrictions
- No conversion to for-profit
- No acquisition by any single entity
- No single entity controls >1 seat
- Patent grant: perpetual irrevocable royalty-free to LPR-compatible implementations
- Asset disposition on dissolution: 100% to similar-mission 501(c)(3)

## Series A target (Q3 2027)
- All 7 priority techs in production
- 3+ operators, 3+ jurisdictions
- 2+ anchor substrates
- External security audit complete (Trail of Bits / NCC)
- SOC 2 Type 2 + ISO 27001 in flight
- 3+ Tier-1 enterprise customers
- Foundation board with named non-founder seats
- IETF SCITT working group active
- C2PA Coalition formal member
- **Target valuation: $200M–$400M post-money**

## One-line investor framing
*"There are seventeen specific ways someone or something could try to stop LedgerProof from being the open provenance layer for AI content. Seven priority technologies, executed over eighteen months on the seed capital we are raising, neutralize all seventeen. Each is mapped to a named adversary class, a dated milestone, and a contractor whose hiring brief already exists. By Q3 2027 the protocol is not 'hopefully' unstoppable — it is structurally unstoppable, and the artifacts to prove it are public."*
