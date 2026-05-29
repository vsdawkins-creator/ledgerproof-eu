# LedgerProof — Financial Services Regulatory Addendum

**Prepared for:** Illuminate Financial Management investment committee
**Author:** Veronica S. Dawkins, Founder, LedgerProof Foundation
**Date:** May 26, 2026
**Purpose:** Map LedgerProof's protocol to the specific EU and UK financial-services regulatory regimes that Illuminate's LP institutions are already navigating. Demonstrate that LedgerProof is not a generic "AI compliance" tool — it is purpose-fit infrastructure for the financial-services compliance stack you and your LPs already operate.

---

## 1 · Why financial services is the wedge

AI deployment inside banks, insurers, and asset managers is exploding — model risk teams estimate $200B–$1T in financial-services AI spend over 2025–2027. Three regulatory regimes converge on the same operational requirement:

> **For every AI-assisted decision or AI-generated document, the institution must be able to produce, on demand, a cryptographic record of what model was used, on what inputs, by which authorized user, at what time — and a regulator-verifiable proof that the record has not been altered after the fact.**

That record is exactly what an LPR receipt is. LedgerProof is not selling "AI provenance" to financial services — it is selling **the missing audit-trail layer** that DORA, MiFID II, and EBA outsourcing guidelines have collectively been pointing toward for three years.

---

## 2 · DORA (Digital Operational Resilience Act) — in force Jan 17, 2025

DORA applies to ~22,000 EU financial entities including banks, payment institutions, insurers, investment firms, central counterparties, and crypto-asset service providers.

### Article 28 — ICT third-party risk management

**Requirement:** Financial entities must maintain comprehensive records of all ICT services provided by third parties (including AI-as-a-service: OpenAI, Anthropic, Google, Microsoft), with the ability to demonstrate to the European Supervisory Authorities that:

- The services have been provided as contracted
- Any AI-generated content used in regulated processes is identifiable
- The full lifecycle of third-party services is auditable
- The institution can produce evidence of the chain of custody for any decision

**LedgerProof's role:**

| DORA Article 28 requirement | LedgerProof receipt field |
|---|---|
| "Identification of the function performed by the ICT service" | `content_type` + profile classification |
| "Date and time the service was provided" | Bitcoin-anchored timestamp (block height + tx index) |
| "The provider's identity" | `issuer_did` of the AI vendor's operator |
| "The institution's user who authorized the service" | `deployer_id` (with GDPR-safe non-PII identifier) |
| "Audit trail unmodifiable after the fact" | Cryptographic receipt + Bitcoin OP_RETURN anchor |

**Operational benefit:** A bank's DORA Article 28 register transitions from "we have a contract and we trust the vendor's logs" to "every AI interaction is independently verifiable; the proof is anchored to a public chain we don't control."

### Article 13 — ICT-related incident reporting

DORA requires reporting of "major ICT-related incidents" within strict timeframes. An AI hallucination or deepfake fraud event that affects a regulated process is reportable.

**LedgerProof's role:** When an institution discovers a problematic AI-generated artifact, the LPR receipt provides:
- Exact timestamp of generation
- The model + version (via Mechanism 4 model fingerprinting in v1.2)
- Whether the artifact has been modified since (cryptographic integrity)
- The chain of subsequent receipts (lineage chains in v1.2)

This converts incident response from forensic reconstruction to log-pull.

### Article 30 — Sub-contracting

When AI vendors sub-contract (e.g., OpenAI using Azure infrastructure), DORA requires the institution to maintain visibility. LedgerProof's federated operator network is structurally aligned: each operator in the federation is independently auditable.

---

## 3 · MiFID II — record-keeping and best execution

### Article 16(6) and (7) — Record-keeping

**Requirement:** Investment firms must keep "records of all services, activities and transactions undertaken by it sufficient to enable the competent authority to fulfil its supervisory tasks" for at least 5 years (10 years for certain records). Records must be "tamper-proof" and "easily accessible to the competent authority."

**The unsolved problem in 2026:** Banks increasingly use AI-generated research, AI-assisted trade rationales, and AI-drafted client communications. Existing MiFID II record-keeping systems (Verint, NICE, Symphony) capture *that* something happened, but cannot prove *what was generated* without trusting the AI vendor's own logs — which the regulator cannot independently verify.

**LedgerProof's role:** Every AI-generated record is anchored to Bitcoin at issuance. Five years later, the regulator (FCA, BaFin, AMF, CONSOB) can independently verify the record without relying on the bank's storage, the AI vendor's storage, or any single intermediary. The Bitcoin chain is the integrity witness.

**Concrete artifact:** A LedgerProof-anchored MiFID II Article 16 record-keeping module can be drop-in alongside existing call-recording infrastructure. The institution gains regulator-grade tamper evidence; the regulator gains cryptographic independence from the institution's own systems.

### RTS 6 (Regulatory Technical Standard on algorithmic trading)

Trading firms must maintain "complete and accurate records" of every algorithmic trade's rationale, including any AI-generated input. LPR receipts can anchor:
- The prompt or query sent to the AI
- The AI-generated rationale
- The trader's authorization to act on the rationale
- The eventual trade decision

This makes RTS 6 compliance machine-verifiable rather than a manual reconciliation exercise.

---

## 4 · EBA Guidelines on Outsourcing Arrangements (EBA/GL/2019/02)

The European Banking Authority's outsourcing guidelines apply to all credit institutions, payment institutions, and electronic money institutions. They require:

- Pre-outsourcing risk assessment
- Written contracts with specific clauses
- Continuous monitoring of outsourced services
- Exit and substitutability planning
- **Documented audit rights, including the right to access records of the service provider**

### How LedgerProof solves the audit-rights problem

The hardest unsolved problem in AI outsourcing is the audit-rights gap. A French bank contracts OpenAI; the EBA expects the bank to be able to audit OpenAI's records related to the bank's usage. In practice, this access is limited.

LedgerProof restructures the problem: **the audit record is not held by the AI vendor — it is anchored to Bitcoin at issuance**. The bank's audit rights are satisfied by the existence of the LPR receipt, which the bank holds independently. The regulator can verify the receipt without any cooperation from the AI vendor.

This is the same model that **SWIFT** uses to make interbank message integrity auditable without any single bank or central institution being able to forge or hide messages.

---

## 5 · FCA Supervisory Statement SS1/23 — Model Risk Management for Banks

The UK Prudential Regulation Authority's SS1/23 (effective May 2024) requires UK banks to maintain a model inventory, document model lifecycle events, and **maintain evidence of independent validation**.

For AI models specifically:
- Model version control
- Input/output logging
- Lineage of model-generated artifacts
- Independent validation records

**LedgerProof's role:** Each AI model's outputs are anchored receipts. The model inventory references receipt IDs. Independent validators counter-sign receipts via Mechanism 5 (witness attestation, v1.2). The bank produces an immutable audit trail without depending on the AI vendor's cooperation.

---

## 6 · Solvency II — Insurance industry parallel

For insurers operating in the EU, **Solvency II Articles 41 and 44** require model documentation and governance. AI-assisted underwriting is now standard at Allianz, AXA, Generali, Munich Re. The same audit-trail requirements apply.

EIOPA's 2024 supervisory statement on AI explicitly references the need for "verifiable provenance of AI-generated underwriting rationale." LedgerProof provides exactly that.

---

## 7 · Reference architecture: Bank-side deployment

A typical EU bank deployment of LedgerProof for financial-services regulatory coverage:

```
┌────────────────────────────────────────────────────────────────────┐
│  Bank's AI-using systems                                           │
│  Research desk · Underwriting · Trading floor · Client comms       │
└────────────────────────────────────────────────────────────────────┘
                          │
                          │  LedgerProof SDK
                          │  (Python, TypeScript, Rust)
                          ▼
┌────────────────────────────────────────────────────────────────────┐
│  Bank's existing record-keeping infrastructure                     │
│  Verint, NICE, Symphony, internal data lake                        │
│  + LedgerProof anchor layer                                        │
└────────────────────────────────────────────────────────────────────┘
                          │
                          │  Daily batch anchoring
                          ▼
┌────────────────────────────────────────────────────────────────────┐
│  LedgerProof Operator (LedgerProof Foundation or bank-operated)    │
│  Frankfurt-EU / London-UK depending on data residency              │
└────────────────────────────────────────────────────────────────────┘
                          │
                          │  Bitcoin OP_RETURN anchor
                          ▼
┌────────────────────────────────────────────────────────────────────┐
│  Bitcoin mainnet — permanent, public, audit-independent            │
└────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────────┐
│  Regulator (EBA, FCA, BaFin, AMF, EIOPA, PRA, etc.)                │
│  Verifies any receipt independently via verify.ledgerproofhq.io    │
│  or self-hosted verifier                                           │
└────────────────────────────────────────────────────────────────────┘
```

**Critical property:** The regulator's verification does not require cooperation from the bank or the AI vendor. The proof is held by the chain itself.

---

## 8 · Pricing model for financial-services customers

| Tier | Annual receipts | ACV | Includes |
|---|---|---|---|
| **Pilot** | up to 10,000 | $25K | Single environment, email support |
| **Production — Regional Bank** | up to 1M | $100–150K | Multi-environment, 99.5% SLA, dedicated CSM |
| **Production — Tier-1 Bank** | up to 50M | $400–600K | Dedicated operator option, 99.9% SLA, regulator liaison |
| **Enterprise — Global Bank** | unlimited + own operator | $1.2M+ | White-label operator deployment, audit support, custom profile |

These ACVs are reasonable next to existing MiFID II record-keeping spend (typically $500K–5M/year per Tier-1 bank for vendors like Verint, NICE Actimize).

---

## 9 · The Illuminate-specific value proposition

Illuminate's portfolio thesis is: invest in B2B infrastructure that sells *into* the 1,400 financial institutions in the LP base. The pattern that has worked: Cobalt (post-trade processing), Droit (regulatory rules), Genesis Global (low-code financial apps), Saphyre (account onboarding), Capitolis (capital optimization).

**LedgerProof fits this pattern exactly.** It is:
- B2B infrastructure
- Sold into the same buyer (Chief Compliance Officer + Chief Data Officer)
- Solves a regulatory pain that Illuminate's LPs feel acutely (DORA + MiFID II + AI Act overlap)
- Has a 5-year-plus stickiness profile (record-keeping requirements are 5–10 years)
- Has expansion economics (every new AI use case = new receipts billed)

Illuminate's introduction-driven sales motion would compress LedgerProof's enterprise sales cycle from typical 12–18 months down to 3–6 months by giving direct CCO/CDO-level access at named institutions.

---

## 10 · Specific concerns Illuminate's diligence will surface

We anticipate, and have answers for:

| Concern | Answer |
|---|---|
| "Is Bitcoin acceptable to your bank LPs?" | Yes — Bitcoin OP_RETURN anchoring is technically and operationally separate from holding or trading BTC. The bank never touches a wallet. Multiple Tier-1 banks already use Bitcoin-anchored CT logs and timestamping services without any treasury involvement. |
| "What about jurisdictional concerns (US sanctions, China policy)?" | The protocol supports multi-substrate anchoring per LPR 1.0 §8. Banks operating in jurisdictions where Bitcoin is restricted can use federated CT-log anchors with the same verification API. No code change for the bank. |
| "GDPR compatibility?" | LPR is GDPR-by-construction. No personal data is ever anchored. Schema validation forbids email and other PII at parse time. Article 17 erasure preserves chain integrity. Reviewed by EU counsel. |
| "Why not just use SWIFT-style closed networks?" | Closed networks require every party to be a member. LedgerProof works for AI vendors who will never join a closed network (OpenAI, Anthropic, etc.). The protocol bridges open AI ecosystems and closed financial-services audit requirements. |
| "Operational risk — what if the operator fails?" | Federated network: ≥3 operators across ≥3 jurisdictions. No single point of failure. Banks may also operate their own operator for highest-tier deployments (and we provide the deployment package). |
| "Pricing scalability?" | Per-receipt economics improve with scale (Merkle batching). Tier-1 bank ACVs of $400K–600K are well within budget for what this displaces. ROI calculator available on request. |

---

## 11 · Proposed pilot structure for Illuminate-introduced banks

A standard 90-day pilot:

| Phase | Duration | Activity |
|---|---|---|
| Discovery | 2 weeks | LedgerProof solution architect maps bank's AI use cases to LPR receipt structure |
| Sandbox integration | 4 weeks | Pilot deployment against bank's non-production AI workflow |
| Production preview | 4 weeks | Limited production scope (1–2 desks or processes) with full LPR receipts |
| Audit demonstration | 2 weeks | Mock regulatory audit demonstrating end-to-end verifiability |
| Decision point | — | Bank decides on Tier-2 or Tier-3 production engagement |

Pilot cost: $25K, fully creditable toward Year-1 production contract.

---

## 12 · Closing

LedgerProof is positioned at the precise intersection of:
- A regulatory mandate with €15M / 3% turnover penalties (EU AI Act Article 50)
- A €200B+ technology category (AI in financial services)
- An open protocol with no platform-capture risk
- A live production deployment with shipped SDKs and an IETF draft
- A buyer (financial-services CCO/CDO) that Illuminate has a direct hotline to

The match between Illuminate's portfolio thesis and LedgerProof's seed-stage opportunity is among the cleanest I have seen described. We would welcome the opportunity to discuss specific pilot pairings with Illuminate's LP institutions once your team has completed initial evaluation.

---

*Prepared for Illuminate Financial Management investment team. Confidential.*
*LedgerProof Foundation — May 26, 2026.*
