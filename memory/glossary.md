# Glossary

LedgerProof internal language, spec terms, and infra names.

## Acronyms
| Term | Meaning | Context |
|------|---------|---------|
| LPR | LedgerProof Receipt | The v1.0 spec; format published under CC BY 4.0 |
| LPR1 | 4-byte ASCII OP_RETURN prefix | LPR v1.0 §5.4 — `"LPR1" ‖ <32-byte Merkle root>` = 36 bytes total |
| AI Act | Regulation (EU) 2024/1689 | EU Artificial Intelligence Act |
| Art. 50 | EU AI Act Article 50 | Transparency obligations for AI-generated content; enforceable Aug 2, 2026 |
| GDPR | Regulation (EU) 2016/679 | Art. 17 = right to erasure |
| SCITT | Supply Chain Integrity, Transparency, Trust | IETF working group |
| VCP | Verifiable Content Protocol | draft-kamimura-scitt-vcp |
| AGT | Agent Governance Toolkit | Microsoft, April 2026, MIT license |
| C2PA | Coalition for Content Provenance and Authenticity | Complementary metadata format |
| CRQC | Cryptographically Relevant Quantum Computer | Threat horizon 2030–35 |
| PQC | Post-Quantum Cryptography | ML-DSA-65, SLH-DSA, etc. |
| HSM | Hardware Security Module | Required for HighAssurance-v1 profile |
| TEE | Trusted Execution Environment | Acceptable alternative to HSM |
| eIDAS | EU electronic ID/trust services regulation | Art. 42 = qualified timestamps |
| CEN/CENELEC | EU standards bodies | Will publish AI Act technical standards under Art. 40 |
| BaFin | German federal financial supervisory authority | Example EU supervisory authority |
| CNIL | French data protection authority | Example EU supervisory authority |
| ICO | UK Information Commissioner's Office | Example supervisory authority |
| LEI | Legal Entity Identifier | Valid `deployer_id` format |
| EUID | European Unique Identifier | Valid `deployer_id` format |
| TVP | Wednesday May 27 video call narrative | Founder shorthand |
| SEP-1763 | LedgerProof interceptor implementation | In `05-sep-1763-impl/` |

## LPR Profiles
| Profile tag | Purpose |
|---|---|
| Core (v1.0) | Baseline — SHA-256, Ed25519, CBOR, RFC 6962, Bitcoin OP_RETURN |
| LongHorizon-v1 | Adds ML-DSA-65 composite signatures for post-CRQC verifiability |
| HighAssurance-v1 | HSM-backed key + sub-hourly anchoring + multi-calendar |
| EU-AI-ACT-50-v1 | EU AI Act Article 50 compliance — adds `eu_ai_act_50` object to `authorship` |

## Internal Terms
| Term | Meaning |
|------|---------|
| the symposium | intouch\|Live San Diego, May 18 — real Bitcoin anchor broadcast |
| the spec | `04-lpr-spec/LPR-1.0-SPECIFICATION.md` |
| the EU operator | `ledgerproof-api-eu` Fly app in Frankfurt (fra) |
| the legacy / legacy iad | The original Rust API in iad — serves 3 historical anchors, MUST NOT be touched |
| the three anchors | Bitcoin mainnet anchors from May 6, May 13, May 18 |
| the EU twin | Spec-conformant EU deployment that mirrors legacy but adds Art. 50 + GDPR |
| TVP | Wednesday May 27 video call where Veronica demonstrates EU deployment live |
| the contractor lens | Senior Rust + cryptography contractor review style (audit-grade) |
| Phase 2 | EU anchor worker — funded EU hot wallet, EU OP_RETURN broadcasts |

## Infrastructure / Services
| Name | What it is |
|---|---|
| `ledgerproof-api` | Legacy Rust/Axum API in iad — historical anchors |
| `ledgerproof-anchor` | Legacy Rust anchor worker in iad — daily Esplora broadcasts |
| `ledgerproof-api-eu` | New Rust/Axum API in fra — LPR v1.0 production, EU |
| `ledgerproof-db-eu` | Postgres in fra, 10 GB |
| api.ledgerproofhq.io | Legacy public hostname (iad) |
| api-eu.ledgerproofhq.io | EU public hostname (pending DNS + cert) |
| Esplora | Blockstream block-explorer API used by anchor worker |

## Tools / Vendors
| Tool | Used for |
|---|---|
| Fly.io | Production hosting (iad, fra regions) |
| Bitcoin mainnet | Anchor substrate (OP_RETURN) |
| Let's Encrypt | TLS certs (via Fly) |
| 1Password | Where founder secrets should live |
| Postgres | App database |

## Project Codenames
| Codename | Project |
|---|---|
| EU Sprint | The May 24 sprint that took EU operator live |
| Phase 2 | EU anchor worker rollout |

## Nicknames
| Nickname | Person |
|---|---|
| Frank | Frank — has a Riot senior-engineering network for cryptographer review |
| Peter Todd | OpenTimestamps author; warm-intro target for cryptographer sign-off |
