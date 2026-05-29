# Azure Marketplace Listing Copy — LedgerProof for EU AI Act

**Purpose:** Drop-in copy for Azure Marketplace. Distinct from AWS Marketplace listing in three respects: (1) Microsoft procurement language conventions; (2) Microsoft Cloud for Sovereignty alignment; (3) explicit Microsoft Purview integration callout.

**Submission target:** Day 105. Live ~Day 135.

**Strategic insight:** Microsoft has the largest installed base in EU regulated industries among the three hyperscalers. The Azure listing is the highest-volume marketplace channel for our ICP (FSI + media + public sector). Treat it as primary, not secondary.

---

## Product title
**LedgerProof — EU AI Act Article 50 Receipts (Bitcoin-Anchored Audit Trail)**

## Search summary (200 chars)
Open-protocol cryptographic receipts that prove EU AI Act Article 50 compliance. Bitcoin-anchored. Microsoft Purview and Azure OpenAI compatible. Live in production at Frankfurt since May 2026.

## Long description

LedgerProof generates regulator-verifiable receipts for every AI-generated output your organization produces, satisfying EU AI Act Article 50 transparency obligations in a form that holds up under regulator examination.

The protocol is published as an IETF Internet-Draft and governed by the LedgerProof Foundation (US 501(c)(3) in formation; Swiss Verein and Singapore non-profit twins Q1 2027). Every receipt is signed Ed25519, anchored to Bitcoin mainnet via OP_RETURN, and independently verifiable by any third party — including your regulator — without trusting LedgerProof.

**Native Azure integrations:**
- **Azure OpenAI Service:** LedgerProof SDK wraps any Azure OpenAI completion or chat call; receipts capture model deployment, prompt hash, and output hash with zero content transmission to LedgerProof.
- **Microsoft Purview:** Receipt metadata flows into Purview Data Map; compliance team views AI lineage alongside data lineage in one pane of glass.
- **Microsoft Sentinel:** Receipt anomalies (failed anchors, schema-rejected outputs) emit Sentinel alerts via Azure Monitor.
- **Azure Logic Apps + Power Automate:** Pre-built connector triggers receipt issuance from any flow.
- **Microsoft Defender for Cloud:** LedgerProof posture surfaces as a compliance control finding under the EU AI Act regulatory compliance dashboard.
- **Microsoft Cloud for Sovereignty:** Receipt storage and operator hosted in EU-only Azure regions; no third-country data transfer.

**Coverage:**
- EU AI Act Article 50(1), 50(2), 50(4) — full
- ISO/IEC 42001:2023 — 24 of 38 Annex A controls (all 8 in A.6 AI System Life Cycle)
- NIST AI RMF — Govern, Map, Measure, Manage
- DORA Article 28 — ICT third-party risk evidence
- MiFID II Article 16 — record-keeping
- GDPR Article 17 — soft-delete semantics with schema-level PII rejection

## Pricing dimensions

| Plan | Annual fee | Monthly receipts included | Overage |
|---|---|---|---|
| **Pilot** | $25,000 | 1,000,000 | Not applicable — 30 days |
| **Production — Tier 1** | $120,000 | 10,000,000 | $0.001 per receipt |
| **Production — Tier 2** | $360,000 | 50,000,000 | $0.0008 per receipt |
| **Enterprise** | Contact | Unlimited + dedicated EU sub-operator | Custom |

All plans include Audit-Ready Compliance Stamp PDFs, verifier portal access, and Microsoft Purview integration.

## Categories
- AI + Machine Learning → AI Governance
- Security → Compliance
- Analytics → Data Governance

## Industries
- Financial Services
- Media & Entertainment
- Healthcare
- Government

## Microsoft Cloud for Sovereignty alignment

LedgerProof operates exclusively from Azure EU regions (West Europe, North Europe, France Central, Germany West Central) for customers requesting Sovereignty alignment. Receipt anchor operations target Bitcoin mainnet via EU-routed mining pool relay; no anchor operation requires data egress from EU jurisdictions.

The protocol's cryptographic primitives (SHA-256, Ed25519, RFC 6962 Merkle, canonical CBOR per RFC 8949) are all NIST-standardized and approved under EU Cybersecurity Act conformity assessments.

## Solution accelerator

LedgerProof publishes a Microsoft-co-branded solution accelerator template at [Microsoft AI gallery URL] (pending approval). The template provisions:
- Azure OpenAI Service instance pre-wired to LedgerProof SDK
- Azure Function for receipt issuance
- Logic App for Stamp PDF generation
- Purview integration
- Sentinel alert rules

Deployment time from accelerator: ~45 minutes to first receipt.

## Procurement-ready

- **SOC 2 Type 1 attestation:** attached to listing
- **SOC 2 Type 2:** in progress; expected by Day 270
- **ISO 27001:** in progress; expected by Day 360
- **Penetration test:** Trail of Bits or NCC Group, completing by Day 90
- **DPA:** standard DPA available; Customer-specific amendments accepted
- **MSA-light SOW for pilot:** $25K, four pages, fully creditable to annual contract within 60 days

## Microsoft AI Cloud Partner Program

LedgerProof is enrolled in the Microsoft AI Cloud Partner Program at the Solutions Partner level for AI Platform (designation expected by Day 120). Co-sell readiness submitted [date]; transactable on Marketplace from launch.

## Support tiers

| Tier | Response time | Channel |
|---|---|---|
| Pilot | 24 business hours | Email |
| Production | 4 business hours | Slack Connect + email |
| Enterprise | 1 business hour | Dedicated TAM + founder access for compliance escalations |

## Required URLs
- Product page: `https://ledgerproofhq.io/azure`
- Documentation: `https://docs.ledgerproofhq.io/azure`
- Verifier portal: `https://verify.ledgerproofhq.io`
- IETF draft: `https://datatracker.ietf.org/doc/draft-dawkins-scitt-ai-article50/`
- Purview integration guide: `https://docs.ledgerproofhq.io/purview`

## Search keywords
EU AI Act, Article 50, AI compliance, AI governance, ISO 42001, NIST AI RMF, DORA, MiFID II, audit trail, AI transparency, synthetic media disclosure, deepfake disclosure, AI watermarking, cryptographic receipts, Bitcoin anchoring, SCITT, AI provenance, AI lineage, Microsoft Purview, Azure OpenAI, Microsoft Cloud for Sovereignty
