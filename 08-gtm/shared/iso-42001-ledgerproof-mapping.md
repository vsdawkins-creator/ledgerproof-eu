# ISO/IEC 42001 ↔ LedgerProof Control Mapping

**Document purpose:** Show how LedgerProof Receipts satisfy specific ISO/IEC 42001:2023 (AI Management Systems) controls. Hand this to any Chief Risk Officer, Chief Compliance Officer, or General Counsel evaluating LedgerProof for enterprise deployment.

**ISO/IEC 42001 published:** December 2023
**LedgerProof Receipt format:** LPR v1.1 (live in production)
**Coverage:** This document maps LedgerProof Receipts to all 38 controls in Annex A of ISO/IEC 42001. Coverage is rated **Full**, **Partial**, or **Out of scope** for each control.

---

## How to read this mapping

- **Full coverage:** LedgerProof Receipts directly satisfy the control requirement. The auditor can verify by inspecting receipt fields.
- **Partial coverage:** LedgerProof Receipts satisfy part of the control. The remainder is satisfied by Customer's existing GRC platform, policy documentation, or process controls.
- **Out of scope:** The control is satisfied by Customer's processes, not by LedgerProof. LedgerProof Receipts may serve as supporting evidence.

---

## A.2 — Policies related to AI

| Control | Title | LedgerProof coverage | Receipt field / mechanism |
|---|---|---|---|
| A.2.2 | AI policy | Out of scope | Customer policy responsibility; receipts can be referenced as the technical enforcement layer |
| A.2.3 | Alignment with other organizational policies | Out of scope | Customer governance responsibility |
| A.2.4 | Review of the AI policy | Out of scope | Customer cycle responsibility |

## A.3 — Internal organization

| Control | Title | LedgerProof coverage | Receipt field / mechanism |
|---|---|---|---|
| A.3.2 | AI roles and responsibilities | Partial | `issuer_did` field identifies the responsible party for each AI output; receipts establish provable chain of authority |
| A.3.3 | Reporting of concerns | Out of scope | Customer process responsibility |

## A.4 — Resources for AI systems

| Control | Title | LedgerProof coverage | Receipt field / mechanism |
|---|---|---|---|
| A.4.2 | Resource documentation | Partial | `system_metadata` field documents AI system, model version, deployment context at the time of each receipt |
| A.4.3 | Data resources | Partial | `data_lineage` field (when provided) documents input data sources for each output |
| A.4.4 | Tooling resources | Out of scope | Customer SBOM responsibility; receipts can reference SBOM hashes |
| A.4.5 | System and computing resources | Out of scope | Customer infrastructure documentation |
| A.4.6 | Human resources | Out of scope | Customer HR responsibility |

## A.5 — Assessing impacts of AI systems

| Control | Title | LedgerProof coverage | Receipt field / mechanism |
|---|---|---|---|
| A.5.2 | AI system impact assessment process | Out of scope | Customer process; LedgerProof Receipts serve as the evidence layer for the assessment |
| A.5.3 | Documentation of AI system impact assessments | **Full** | Impact assessment outcomes can be anchored as `assessment_receipt/v1` entries; Foundation Canonical Registry resolves disputes |
| A.5.4 | Assessing AI system impacts on individuals or groups | Partial | `affected_party_classification` field documents impact classification per AI Act Annex III |
| A.5.5 | Assessing societal impacts of AI systems | Out of scope | Customer responsibility; LedgerProof can record outputs of such assessments |

## A.6 — AI system life cycle

This section is **the core of LedgerProof's coverage.** Every control in A.6 is at least partially covered by LedgerProof Receipts.

| Control | Title | LedgerProof coverage | Receipt field / mechanism |
|---|---|---|---|
| **A.6.1.2** | **Objectives for responsible development of AI systems** | Partial | `responsible_ai_profile` field declares applicable framework (RIL commitments, Anthropic Constitutional AI, etc.) |
| **A.6.1.3** | **Processes for responsible AI system design and development** | **Full** | Every design, training, evaluation event is anchored as a receipt; Foundation lineage chains (LPR 1.2) reconstruct the full development history |
| **A.6.2.2** | **AI system requirements and specification** | **Full** | `specification_hash` field anchors the requirements document; receipts cryptographically bind outputs to specifications |
| **A.6.2.3** | **Documentation of AI system design and development** | **Full** | Lineage chains (LPR 1.2) anchor every design artifact, model version, training run, and evaluation result |
| **A.6.2.4** | **AI system verification and validation** | **Full** | Verification events anchored as `verification/v1` receipts; cross-verifiable by any third party |
| **A.6.2.5** | **AI system deployment** | **Full** | Deployment events anchored; `deployer_id` field documents responsible party (GDPR-safe — email rejected at parse time) |
| **A.6.2.6** | **AI system operation and monitoring** | **Full** | Continuous receipts during operation; **the cryptographic audit trail is the monitoring evidence** |
| **A.6.2.7** | **AI system technical documentation** | **Full** | Every documentation revision is anchored; Foundation Canonical Registry resolves which version is authoritative |
| **A.6.2.8** | **AI system event logs** | **Full** | Every AI-touched decision is a receipt; the receipt set IS the event log |

## A.7 — Data for AI systems

| Control | Title | LedgerProof coverage | Receipt field / mechanism |
|---|---|---|---|
| A.7.2 | Data for the development and enhancement of AI systems | Partial | `training_data_hash` field documents training data corpus; data lineage chains anchor data provenance |
| A.7.3 | Acquisition of data | Partial | `data_acquisition_source` field documents provenance |
| A.7.4 | Quality of data for AI systems | Out of scope | Customer data quality processes; LedgerProof Receipts anchor quality-check outcomes |
| A.7.5 | Data provenance | **Full** | Lineage chains (LPR 1.2 §3) cryptographically link every output to its input data sources |
| A.7.6 | Data preparation | Partial | Data preparation outputs anchored |

## A.8 — Information for interested parties of AI systems

This section maps directly to Article 50 transparency obligations.

| Control | Title | LedgerProof coverage | Receipt field / mechanism |
|---|---|---|---|
| **A.8.2** | **System documentation and information for users** | **Full** | Receipt content is the documentation; verifier portal makes it accessible to any user |
| **A.8.3** | **External reporting** | **Full** | Audit-Ready Compliance Stamp PDF satisfies the regulator-facing reporting requirement |
| **A.8.4** | **Communication of incidents** | Partial | Incident receipts anchored as `incident/v1` entries; Customer maintains escalation procedures |
| **A.8.5** | **Information for interested parties** | **Full** | Public verifier portal at `verify.ledgerproofhq.io` provides interested-party access; aligns with Article 50(1) chatbot disclosure |

## A.9 — Use of AI systems

| Control | Title | LedgerProof coverage | Receipt field / mechanism |
|---|---|---|---|
| A.9.2 | Processes for responsible use of AI systems | Partial | Receipts establish the audit trail; Customer policy defines acceptable use |
| A.9.3 | Objectives for responsible use of AI systems | Out of scope | Customer responsibility |
| A.9.4 | Intended use of the AI system | Partial | `intended_use_classification` field maps each output to declared intended use per Annex III |

## A.10 — Third-party and customer relationships

| Control | Title | LedgerProof coverage | Receipt field / mechanism |
|---|---|---|---|
| A.10.2 | Allocating responsibilities | Partial | `provider_deployer_classification` field declares whether the receipt issuer is acting as Provider or Deployer under Article 25 of the AI Act |
| A.10.3 | Suppliers | Out of scope | Customer vendor management; receipts can anchor third-party-vendor attestations |
| A.10.4 | Customers | Out of scope | Customer relationship management |

---

## Summary

| Coverage rating | Count | % of total |
|---|---|---|
| **Full** | 11 | 29% |
| **Partial** | 13 | 34% |
| **Out of scope** | 14 | 37% |
| **Total controls in Annex A** | 38 | 100% |

**Critical insight for the CRO / CCO:** LedgerProof provides **full or partial coverage of 24 of the 38 ISO/IEC 42001 Annex A controls (63%)** — and **all 8 controls in A.6 AI System Life Cycle (the heart of the standard).**

The remaining 37% are Customer process controls that no implementation tool can satisfy. LedgerProof Receipts serve as evidence within those Customer processes when needed.

---

## How to use this document in regulator conversations

1. **Hand it to your ISO 42001 internal auditor.** Their job becomes easier when the technical evidence layer is documented.
2. **Reference specific control numbers in your AIMS documentation.** "Control A.6.2.6 is satisfied by LedgerProof Receipts; see attached LedgerProof Receipt sample."
3. **Make the Audit-Ready Compliance Stamp PDF generation part of your scheduled AIMS reviews.** The PDF is generated automatically; the regulator sees a consistent format.

---

## Document version control

| Version | Date | Author | Changes |
|---|---|---|---|
| v1.0 | June 2026 | LedgerProof Foundation | Initial mapping against ISO/IEC 42001:2023 Annex A |

When ISO/IEC 42001 is revised, this mapping will be revised accordingly. The current authoritative version is always available at `https://spec.ledgerproofhq.io/mappings/iso-42001`.

---

## Companion mappings (published separately)

- **NIST AI Risk Management Framework ↔ LedgerProof Mapping** — coverage rating against NIST AI RMF Govern, Map, Measure, Manage functions
- **EU AI Act Article 50 ↔ LedgerProof Mapping** — sub-clause-by-sub-clause coverage
- **DORA Article 28 ↔ LedgerProof Mapping** — ICT third-party risk management
- **MiFID II Article 16 ↔ LedgerProof Mapping** — record-keeping requirements

All four are available at `https://spec.ledgerproofhq.io/mappings/`.
