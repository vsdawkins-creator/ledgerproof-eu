# LedgerProof Platform — 2036 Architecture Brief

**Version:** Draft 1.0
**Date:** May 20, 2026 (45 days before public launch)
**Author:** LedgerProof Foundation (in formation), with research synthesis across eight macro domains
**Status:** Internal architecture document for founder + cryptographer reviewer + IETF working-group engagement
**Reads-with:** `research/wave1-macro/01-quantum-pqc-trajectory.md`, `research/wave1-macro/02-domains-2-through-8-synthesis.md`, `../04-lpr-spec/LPR-1.0-SPECIFICATION.md`, `../02-whitepaper/FOUNDING-WHITEPAPER-DRAFT.md`

---

## Executive summary

This document specifies the LedgerProof platform's architecture across a ten-year horizon — from the July 6, 2026 launch through 2036 — and traces back from the 2036 end-state to the Day-1 architectural commitments that must be embedded in the LPR v1.0 specification published at launch. The brief is the empirical product of eight verified macro-domain research findings (post-quantum cryptography, IETF standards landscape, AI agent economy, real-world-asset tokenization, deepfake threat trajectory, AI regulation evolution, Bitcoin substrate evolution, and competitive landscape) saved in `research/wave1-macro/`.

The central architectural conclusion: **LedgerProof can credibly become the cryptographic-provenance transaction-network layer for the documentary economy of the AI era — comparable in structural shape to Visa, DTCC, SWIFT, and VeriSign — if six Day-1 commitments are embedded in the v1.0 specification before public launch on July 6, 2026.** Those commitments are detailed in Section 5.

This document is not a marketing artifact. It is the foundation a Trail-of-Bits-grade cryptographer auditor, an IETF working-group chair, a sovereign-state procurement officer, and a Big 4 audit firm methodology owner can all read and find airtight.

---

## 1 · The 2036 end-state, restated against verified research

By 2036, LedgerProof is structurally on the same tier as the trust-infrastructure utilities that emerged in the 19th and 20th centuries. The end-state conditions, with each anchored to verified research:

### Technical conditions

| Condition | Anchored to research |
|---|---|
| 100M–1B+ receipts anchored per day at mature throughput | Agent-economy forecasts: Gartner 20% of monetary transactions programmable by 2030; 50% of supply-chain solutions using agentic AI; multi-trillion-dollar agent commerce by mid-decade (Domain 3) |
| Multi-substrate anchoring (Bitcoin primary; opt-in alternates) | Bitcoin Core v30 expanded OP_RETURN to 100KB (Oct 10 2025); Bitcoin sovereign + institutional adoption confirmed; substrate diversification remains a credible Year-3+ extension (Domain 7) |
| Post-quantum hybrid signatures fully deployed for high-assurance profiles | NIST FIPS 204 ML-DSA finalized Aug 2024; CNSA 2.0 mandates 2027/2030/2031/2035 deadlines; Composite ML-DSA+Ed25519 standardization nearing RFC (Domain 1) |
| Federated calendar-operator network (no single calendar required for verification) | OpenTimestamps' decade-of-production model proves the operator-network pattern; multi-operator architecture is the consensus design for sustained public infrastructure (Domain 1 + Domain 2 SCITT) |
| DID-compatible identity for institutions, humans, and AI agents | DID standards mature; ERC-8004 confirms on-chain agent-identity demand; Composite-ML-DSA signer-pubkey schema is DID-compatible (Domain 3 + Domain 1) |

### Standards conditions

| Condition | Anchored to research |
|---|---|
| Multiple IETF RFCs published as SCITT profiles | `draft-ietf-scitt-architecture-22` is the working-group draft; `draft-kamimura-scitt-vcp-01` confirms VeritasChain has filed a SCITT profile; our `draft-dawkins-scitt-lpr-00` is the natural sibling (Domain 2) |
| ISO standard ratified citing LPR as reference Bitcoin-anchor profile | ISO TC 307 (Blockchain and DLT) is the natural home; multi-year cycle; achievable by Year 5 (Domain 2) |
| Named in EU AI Act successor and NIST guidance | EU AI Omnibus adopted Nov 2025; high-risk obligations Dec 2027; NIST 800-series in active revision (Domain 6) |
| Court precedents in 4+ jurisdictions | US federal court precedent achievable Year 2–4 via the legal vertical (D1) and Myle Phan-Gale's informal counsel (separate document) |

### Network conditions

| Condition | Anchored to research |
|---|---|
| 1,000+ named member institutions | Visa's network economics (~3.9B cardholders + 100M merchants); SWIFT (~11,000 institutions). 1,000-institution scale is conservative for a 10-year horizon (Domain 3 + Domain 4) |
| Foundation transitions to member-owned cooperative utility | DTCC, SWIFT, pre-IPO NYSE established the cooperative-utility pattern; the structural decision must be made in Phase 3 (Year 3–5) |
| Endowment > $500M; perpetuity guaranteed | ISRG/Let's Encrypt operates at $5M/year donations + sponsorships; scaling endowment to $500M+ by Year 10 follows the standard nonprofit endowment-building arc |

### Cultural/regulatory conditions

| Condition | Anchored to research |
|---|---|
| LedgerProof Seal consumer-recognized at SSL-padlock level | UL Listed mark recognition is the comparable; multi-decade arc but achievable |
| Cited in OECD digital-trust framework; UNCITRAL/ITU instruments | International standards bodies move on 5–10 year cycles; achievable by Year 8–10 (Domain 6) |
| "LedgerProof'd" enters language as verb | Cultural adoption follows technical adoption; achievable on the Stripe / Google language-adoption arc |

---

## 2 · The ten-layer architecture (top-to-bottom specification)

The platform decomposes into ten architectural layers, each with a defined contract to the layers above and below. The decomposition follows the standard pattern used by trust-infrastructure utilities (the OSI model, the W3C stack, the IETF layering).

### Layer 10 — Governance & Internationalization

**Function**: Establishes who decides, in what jurisdictions, with what governance instruments, and in what languages the platform operates.

**Day-1 components**:
- LedgerProof Foundation (Delaware 501(c)(3) in-formation) and LedgerProof, Inc. (Delaware C-Corp) — dual structure announced July 6, 2026.
- Founding Board with five named members + three outside signatories on the Provenance Manifesto.
- Governance documents on disk (Articles, Bylaws, Charter, Conflict of Interest Policy).
- Standards-engagement commitment: IETF SCITT, ISO TC 307, NIST, W3C, ETSI, ENISA.

**Year 3–5 evolution**: Foundation transitions to member-owned cooperative utility (DTCC/SWIFT pattern). Multi-jurisdictional presence: US (Delaware), EU (Brussels), Asia-Pacific (Singapore).

**Year 5+ evolution**: Endowment-funded perpetuity (target $500M by Year 10). Multi-language verifier (target 30+ languages). Cited in OECD, UNCITRAL, ITU instruments.

### Layer 9 — Economic / Transaction Network Fee Layer

**Function**: Captures the economic value of network operations and distributes it across operators, the cooperative, and the Foundation endowment.

**Day-1 components**:
- API subscription tiers (Free / Builder / Team / Business / Enterprise) — already specified in earlier session work.
- Per-receipt usage pricing on top of subscription caps.
- Article 50 Compliance Pack bundled subscription.
- Legal-vertical (D1) per-firm and per-matter pricing.

**Year 3–5 evolution**: Basis-points-on-value pricing for RWA-anchoring and high-value contracts; per-anchor network transaction fees flowing to the cooperative; member-institution annual dues; OEM licensing royalties.

**Year 5–10 evolution**: Stripe Treasury-comparable financial-services layer; cyber-insurance commission revenue; certification-body services; sovereign per-citizen micro-fees; DID-registry annual fees.

**Architectural commitment Day 1**: every receipt has accounting metadata sufficient to support all future fee models — receipt records carry information about the paying party, the network-fee tier, and the routing of any per-transaction fees once that model is introduced.

### Layer 8 — SDK & Application Layer

**Function**: Provides the language-specific libraries, framework integrations, and operating-system surfaces through which the platform is consumed.

**Day-1 components**:
- LPR Python reference SDK (MIT, published to GitHub).
- LPR TypeScript reference SDK (MIT, published to GitHub).
- SEP-1763 MCP interceptor reference implementation (already drafted, in `05-sep-1763-impl/`).
- Public API surface at `api.ledgerproofhq.io`.

**Year 2–3 evolution**: SDKs in Rust, Go, Java, C++, Swift, Kotlin. Framework integrations: LangChain, LangGraph, OpenAI Assistants, Haystack, PydanticAI, AutoGen, CrewAI.

**Year 3–5 evolution**: OS-level integration patterns — Finder/Explorer right-click verify, macOS/iOS Secure Enclave integration, Android TEE integration, browser extensions for Chrome/Firefox/Safari/Edge.

**Year 5–10 evolution**: White-label deployments; certified-implementer program; app marketplace for LP-integrated tools; embedded in document-management software (Adobe, Microsoft 365, Google Workspace, Salesforce, Notion).

### Layer 7 — Verification Infrastructure

**Function**: Provides the verifier service that allows any party to verify any LPR receipt independently.

**Day-1 components**:
- Foundation-operated public verifier at `verify.ledgerproofhq.io`.
- Browser-based verification interface (no installation required).
- Open-source reference verifier in Python and TypeScript (anyone can run their own).
- Verification API endpoints for programmatic integration.
- The verifier's source code must be published at launch — non-negotiable.

**Year 2–3 evolution**: Multi-region deployment (Americas, EU, APAC). Sub-200ms verification latency from any browser worldwide. Browser-extension verifiers for major browsers.

**Year 3–5 evolution**: Mobile-native verification (iOS, Android). Verifier accessible offline for legacy-system contexts. Multi-language UX (target 10 languages by Year 5, 30 by Year 10).

**Year 5–10 evolution**: Verifier-as-search-engine — the canonical source of "is this document real" answers at scale. Federated verifier-redundancy across hundreds of operators.

### Layer 6 — Composability / Bridges Layer

**Function**: Provides bidirectional interoperability with adjacent provenance standards.

**Day-1 components**:
- Strict-superset relationship with OpenTimestamps (OPR sub-profile defined in spec).
- Embeddability inside C2PA manifests (binding spec drafted; reference implementation v1.1).
- VeritasChain VAP composability (LPR as candidate Bitcoin-anchor profile).
- Microsoft AGT receipt wrapping (LPR can carry AGT receipts as wrapped payload).
- IETF SCITT profile — LPR repositioned as `draft-dawkins-scitt-lpr-00` (verified in research: VeritasChain has already filed `draft-kamimura-scitt-vcp-01`, confirming this is the right home).

**Year 2–3 evolution**: ERC-8004 bridge for Ethereum-aware customers; W3C Verifiable Credentials interop; ISO 32000 (PDF) provenance embedding.

**Year 3–5 evolution**: CBDC and stablecoin reserve-attestation integration; tokenized-RWA issuance-and-custody profiles.

**Architectural commitment Day 1**: the `profile` field in every LPR receipt allows future bridge profiles to be added without breaking v1.0 receipt verification.

### Layer 5 — Privacy / Selective Disclosure Layer

**Function**: Provides cryptographic guarantees that the protocol does not compromise the privacy of anchored content.

**Day-1 components**:
- Hash-only anchoring (content never on-chain).
- GDPR Article 17 compliance architecture: deletion of off-chain content renders the on-chain hash a disconnected reference.
- Off-chain storage abstraction (customer-controlled).
- Salted-hash profile for receipts where the hash itself could be claimed as personal data.

**Year 2–3 evolution**: Zero-knowledge proof profiles for selective disclosure (proving a document property without revealing the document).

**Year 3–5 evolution**: Privacy-preserving membership proofs (institutional members can prove participation without revealing transaction details).

**Year 5–10 evolution**: Fully homomorphic operations on encrypted receipts where applicable.

### Layer 4 — Identity Layer

**Function**: Establishes who or what signs a receipt, and how that identity is verified.

**Day-1 components**:
- Ed25519 public key as `signer_pubkey` (default).
- DID-compatible `signer_id` field (per LPR v1.0 spec, already designed).
- Receipt schema explicitly supports HUMAN, AI_MODEL, HYBRID, INSTITUTION actor types.

**Year 2–3 evolution**: DID registry operated by the Foundation (target launch Year 2). Hardware-attested signing key custody (HSM-as-a-service for enterprise).

**Year 3–5 evolution**: AI-agent identity registry — every named AI agent of consequence registered with cryptographic provenance. Multi-sig and threshold-signature institutional identities.

**Year 5–10 evolution**: Cross-jurisdictional identity recognition (per the EU eIDAS 2.0 and successor frameworks). Identity-revocation registry compatible with all major identity ecosystems.

### Layer 3 — Calendar / Operator Network Layer

**Function**: Aggregates receipts into Merkle trees for batch anchoring. At maturity, federates across multiple operators with no single point of failure.

**Day-1 components**:
- Foundation-operated calendar at `calendar.ledgerproofhq.io`.
- 24-hour aggregation window (Standard tier).
- Calendar-operator protocol specified in the LPR v1.0 spec (third parties can run compatible calendars from Day 1).
- Multi-calendar verification model (verification does not require contact with any specific calendar).

**Year 2–3 evolution**: Five-to-ten named third-party calendar operators (academic institutions, regional sovereign-government calendars, industry-specific operators).

**Year 3–5 evolution**: Hierarchical Merkle aggregation (Merkle of Merkles for multi-region calendars). Sub-block commitment via federated co-signing for sub-second latency at the premium tier. Operator staking and accountability protocol.

**Year 5–10 evolution**: 100+ federated calendar operators globally. Operator-incentive mechanism (anchoring-fee distribution) and accountability framework. Permanent operator-availability guarantees via the Foundation cooperative.

### Layer 2 — Protocol Core (LPR receipt format)

**Function**: The canonical cryptographic format that binds a document to its authorship, timestamp, and chain.

**Day-1 components**: LPR v1.0 specification, already drafted in `04-lpr-spec/LPR-1.0-SPECIFICATION.md`. Receipt schema includes:
- `lpr_version`, `receipt_id`, `trace_id`, `timestamp_ns`, `timestamp_iso`
- `artifact` (content_hash, hash_algo, content_type, content_bytes)
- `authorship` (actor_type, actor_id, actor_assertion, tool_chain)
- `chain` (prev_receipt_hash)
- `signature` (sig_algo, sig_bytes, signer_pubkey)
- **NEW per Day-1 commitment (this brief)**: `additional_signatures` (array, optional)
- `anchor` (merkle_leaf_hash, anchor_status, btc_txid, btc_block_height, merkle_path)
- **NEW per Day-1 commitment (this brief)**: `substrate` field on anchor (defaults to "bitcoin-mainnet")

**Year 2–3 evolution**: LPR v1.1 introduces formal SCITT-profile binding; LPR v1.2 introduces the Long-Horizon and High-Assurance hybrid-signature profiles' production-grade implementations.

**Year 3–5 evolution**: LPR v2.0 — full post-quantum migration support; full multi-substrate; ZK-proof selective-disclosure profiles.

**Year 5–10 evolution**: LPR v3.0+ — emerging-cryptography support (whatever follows ML-DSA and ML-KEM); native AI-agent-economy primitives; deep integration with the cooperative governance layer.

### Layer 1 — Cryptographic Primitives

**Function**: The lowest-level mathematical primitives the protocol depends on.

**Day-1 primitives**: SHA-256 (RFC 6234), Ed25519 (RFC 8032), CBOR canonical (RFC 8949), JCS (RFC 8785), Merkle aggregation (RFC 6962). All standardized, all production-grade, all globally implementable.

**Year 2–4 additions** (per quantum-PQC dossier): ML-DSA-65 and ML-DSA-87 (NIST FIPS 204), with Composite-ML-DSA-Ed25519 per the IETF draft nearing RFC. SLH-DSA (FIPS 205) for high-assurance backup. ML-KEM (FIPS 203) for any key-encapsulation needs.

**Year 5+ additions**: SHA-3 / SHAKE / BLAKE3 hash agility (per the quantum-PQC dossier — SHA-256 remains acceptable through 2036+, but diversification is a hedge). Post-Dilithium signature schemes if they emerge as superior.

### Layer 0 — Anchoring Substrate (Bitcoin)

**Function**: The public ledger where Merkle roots are committed.

**Day-1 substrate**: Bitcoin main chain via OP_RETURN.
- Following Bitcoin Core v30 (October 10, 2025), the OP_RETURN limit is 100,000 bytes. The LPR v1.0 default payload remains **36 bytes** (4-byte LPR1 prefix + 32-byte Merkle root) for compatibility with Bitcoin Knots and conservative mining policy. An opt-in expanded-payload profile is reserved for use cases that justify the larger payload (e.g., multi-root co-anchoring).
- Anchor frequency: 24 hours (Standard); 10 minutes (Platinum tier); per-Lightning-payment sub-second (future profile).

**Year 2–4 substrate evolution**: Bitcoin Lightning Network co-signing for sub-second pre-commitment (anchored to the eventual Bitcoin block on a deferred schedule).

**Year 5+ substrate evolution**: Optional secondary substrates (Ethereum L1/L2, federated CT-style logs, sovereign-state chains) for diversification — anchored alongside Bitcoin, never replacing it.

---

## 3 · The non-architectural layer: what we explicitly DO NOT do

Per Trail-of-Bits-grade discipline, the architecture is defined as much by what it excludes as by what it includes. The following are NOT in the platform:

- **Custody of customer content.** Hash-only on-chain; off-chain content remains with the customer's chosen custodian. *Never anchor content.*
- **Identity issuance.** LPR certifies what was signed, not who you are. Identity issuance is delegated to DID/identity ecosystems we compose with.
- **Payment-rail functionality.** We are a provenance layer, not a money-movement layer. Stripe, Visa, the banks, and the stablecoin issuers are partners and customers, not competitors.
- **Receipt mutation.** Receipts are immutable. Revisions are new receipts chained to the old. No database edit, ever.
- **Centralized verification.** The verifier must remain operable by anyone, including via independent open-source code. No single point of failure.
- **Operating without cooperative governance after Year 4.** Once member governance is established (Phase 4), the founder and the commercial entity no longer hold unilateral power over the protocol.
- **Token issuance / cryptocurrency.** LedgerProof does not issue a token. The platform's economic model is fee-based, not token-economic. (This decision is revisitable in Year 5+ if a clear utility-token rationale emerges, but Day-1 posture is: no token.)
- **Closed-source verification code.** Verification logic is open-source from Day 1, no exceptions.

---

## 4 · The five-phase technical roadmap

### Phase 1 — Foundation laid (Months 0–18, June 2026 – December 2027)

**Technical milestones**:
- LPR v1.0 specification published July 6, 2026, anchored on Bitcoin.
- Reference SDKs in Python and TypeScript shipped under MIT.
- SEP-1763 MCP interceptor reference implementation published.
- IETF Internet-Draft `draft-dawkins-scitt-lpr-00` submitted to datatracker.ietf.org by Day 5 of launch (target submission date July 11, 2026).
- Foundation-operated calendar at `calendar.ledgerproofhq.io` operational.
- Foundation-operated verifier at `verify.ledgerproofhq.io` operational.
- B1 Anchor API live with paid subscription tiers.
- Riot Games, Columbia J-School, JPMorgan pilots active (per pilot pitches drafted).

**Gate to Phase 2**: IETF -00 visible in datatracker; Foundation 501(c)(3) status pending or granted; coalition holding together; first paying customers in E1/D1.

### Phase 2 — Standards adoption + audit-firm channel (Months 18–36, January 2028 – December 2028)

**Technical milestones**:
- IETF SCITT working-group engagement: target promoting `draft-dawkins-scitt-lpr` from individual to working-group draft.
- LPR v1.1 release: SCITT-profile binding formalized; Long-Horizon profile (Composite ML-DSA + Ed25519) production-grade.
- First Big 4 audit-firm methodology integration.
- DID registry beta operational.
- Multi-region calendar deployment (Americas + EU + APAC by end of phase).
- LPR receipts in production at the first US federal court division pilot.

**Gate to Phase 3**: Working-group output toward RFC; audit-firm methodology in draft; multi-government pilots in production.

### Phase 3 — Network effect ignition + first court precedents (Months 36–60, January 2029 – December 2030)

**Technical milestones**:
- LPR v1.2 release: full PQC migration support; ZK-proof selective-disclosure profiles in beta.
- First IETF RFC published — LPR SCITT profile as Standards-Track or Experimental.
- ABA opinion published on LP-anchored evidence (Year 4 target).
- Public Seal launched with founding coalition of 25+ named institutions.
- One sovereign government adoption (EU or Latin American partner).
- 100+ named member institutions; 25M+ receipts/day.
- Federated calendar-operator network operational with 10+ named third-party operators.

**Gate to Phase 4**: RFC published; sovereign customer named; cooperative-utility transition decision made.

### Phase 4 — The trusted layer (Months 60–84, January 2031 – December 2032)

**Technical milestones**:
- LedgerProof Foundation transitions to member-owned cooperative utility.
- LPR v2.0 release: full post-quantum support across all profiles; emerging cryptography (whatever follows ML-DSA); multi-substrate anchoring formalized.
- Three or more regulatory instruments cite LP by name.
- ISO standard ratified citing LPR as a normative reference.
- Multi-jurisdiction court precedents.
- 500+ member institutions; 100M+ receipts/day.

**Gate to Phase 5**: Cooperative is operational; founder is one of multiple voices; protocol is plural in its governance.

### Phase 5 — Civilizational infrastructure (Years 7–10, January 2033 – December 2035)

**Technical milestones**:
- OECD framework references LP.
- UNCITRAL / ITU instrument references LP.
- Multiple G20 governments name LP in their national digital strategies.
- The LP verifier processes more verifications daily than most search engines process queries.
- The Seal is consumer-recognized at SSL-padlock levels.
- 1,000+ member institutions; 500M+ receipts/day at mature throughput.
- Foundation endowment crosses $500M.

**Year 10+ aspiration**: LP is presumed infrastructure. Like DNS. Like TLS.

---

## 5 · Six Day-1 architectural commitments that lock in the 2036 system

These are the decisions that MUST be embedded in the LPR v1.0 specification text published on July 6, 2026. Each one is the architectural seed for a downstream Phase capability. Each one has been verified against Wave 1 research.

### Commitment 1 — Hybrid-signature support in the receipt schema

The receipt schema MUST include an `additional_signatures` array (zero or more), supporting heterogeneous algorithm identifiers including Ed25519, ML-DSA-65, ML-DSA-87, SLH-DSA, FN-DSA (when finalized as FIPS 206), and Composite-ML-DSA-Ed25519.

*Reason*: Per the quantum-PQC dossier, post-quantum migration is mandated globally between 2027 and 2035. Receipts produced today must support hybrid signing from creation, not be retrofitted later. The IETF Composite ML-DSA draft is nearing RFC and interoperability is demonstrated (SafeLogic at IETF 124).

### Commitment 2 — Substrate-agnostic anchor field

The `anchor` field MUST include a `substrate` string identifier (default: `"bitcoin-mainnet"`). Future substrates (Bitcoin testnet for development, alternative chains for diversification, sovereign-state chains for jurisdictional flexibility) can be added without breaking v1.0 receipts.

*Reason*: Per the Bitcoin substrate dossier, Bitcoin remains the primary substrate, but the architectural option of alternates must exist. Bitcoin Core v30's OP_RETURN expansion to 100KB and the Knots-Core split reinforce the need for substrate flexibility.

### Commitment 3 — SCITT profile compatibility

The LPR v1.0 specification MUST declare itself a candidate SCITT profile and explicitly map every required field to the SCITT architecture's signed-statement model. The IETF -00 submission MUST be filed as a SCITT profile (`draft-dawkins-scitt-lpr-00`), not a standalone Internet-Draft.

*Reason*: Per Domain 2 research, VeritasChain has already filed `draft-kamimura-scitt-vcp-01` as a SCITT profile. The IETF home for cryptographic provenance work is SCITT. Positioning LPR as a SCITT profile composes us with VeritasChain (not in competition) and gives our IETF work a natural working-group home.

### Commitment 4 — Three profiles defined in the v1.0 specification

The v1.0 specification text MUST define three profiles in normative language, even if production-grade implementations of profiles 2 and 3 are delivered in subsequent v1.0.x releases:
- **Standard** — Ed25519 only, optimized for size and throughput; the 99% case.
- **Long-Horizon** — Composite ML-DSA-65 + Ed25519, for sovereign records, court archives, healthcare records, IP filings, AI safety attestations with verification horizons past 2035.
- **High-Assurance** — Composite ML-DSA-87 + Ed25519 + optional SLH-DSA backup, for national-security-grade deployments.

*Reason*: Per the quantum-PQC dossier, this is the architectural solution to the migration question. Defining the profiles in the spec text from Day 1 ensures Long-Horizon customers can begin anchoring future-proof receipts immediately while Standard customers pay no cost.

### Commitment 5 — Re-anchoring service operational commitment

The LPR v1.0 specification MUST include an operational commitment from the LedgerProof Foundation that a re-anchoring service for Standard-profile receipts will be operational no later than **January 1, 2028**, with the Foundation underwriting the cryptographic continuity of receipts produced under v1.0 across post-quantum migration.

*Reason*: Per the quantum-PQC dossier, NSA CNSA 2.0 mandates new NSS systems comply by Jan 1, 2027. The Foundation's re-anchoring commitment must operate from the moment customer-facing demand emerges. This commitment is also the basis for the Foundation's perpetuity claim — receipts produced today remain verifiable in 2076 because the Foundation guarantees the migration path.

### Commitment 6 — Protocol-continuity escrow architecture

The Foundation MUST establish, before the launch on July 6, 2026, a protocol-continuity escrow consisting of:
- The verifier source code in encrypted backups distributed across at least three jurisdictions.
- Calendar-operator private keys (encrypted, threshold-distributed) with recovery procedures published in the Foundation Bylaws.
- The Foundation's operational documentation in time-locked release escrow.

*Reason*: Per the 2036 end-state, the protocol must survive the company. Even if LedgerProof, Inc. and the Foundation both fail, the verifier source code and operator-key recovery procedures must be recoverable by any successor entity. This is what makes the 100-year perpetuity promise survive Trail-of-Bits-grade scrutiny.

---

## 6 · Deferred-but-must-be-designed-for items

These are NOT in v1.0, but the v1.0 architecture MUST have a clean extension path for each. The path is the architectural commitment; the implementation is deferred.

| Item | Designed-for status in v1.0 | Production-readiness target |
|---|---|---|
| Federated calendar-operator network | Calendar-operator protocol specified in v1.0 spec | Phase 2 (Year 2) — initial third-party operators; Phase 4 — 100+ operators |
| Post-quantum signature production tooling | Schema designed in v1.0; hybrid receipts verifiable in v1.0 verifier; production signing in v1.0.1 release | LPR v1.0.1 release Q4 2026 |
| Multi-substrate anchoring | `substrate` field present in v1.0 schema | Phase 3 (Year 3–4) — second substrate added |
| ZK selective-disclosure profiles | Profile-extension mechanism in v1.0 | Phase 2–3 — beta profiles |
| DID registry | DID-compatible `signer_id` field in v1.0 | Phase 2 — registry beta |
| AI-agent identity registry | Agent-actor type in v1.0 (`actor_type: "AI_MODEL"`) | Phase 3 — production registry |
| OS-level integration (Finder, browser extensions, mobile) | API surface and SDK pattern in v1.0 | Phase 2–3 — incremental shipments |
| Stablecoin / RWA / tokenization profiles | Profile-extension mechanism in v1.0 | Phase 2–4 — vertical profiles |
| Sub-block-time pre-commitment via Lightning | Anchor-pending status in v1.0; sub-block path deferred | Phase 3+ |
| Hash agility (SHA-3, BLAKE3) | `hash_algo` field in v1.0; new algorithms permitted via profile extension | Phase 4–5 (SHA-256 remains acceptable through 2036+) |

---

## 7 · Risk register — architectural decisions that, if wrong, foreclose 2036

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Hybrid-signature schema design proves incompatible with the eventual Composite-ML-DSA RFC | Low | High | Track `draft-ietf-lamps-pq-composite-sigs` weekly; update v1.0 schema before publication if the RFC text diverges; ensure our `additional_signatures` array is the same shape as the RFC's eventual binding |
| R2 | Bitcoin Core / Knots split worsens, threatening OP_RETURN viability | Medium | High | Maintain 36-byte default payload (under Knots' stricter limit); design substrate-agnostic architecture; have an alternate substrate option ready by Phase 3 |
| R3 | SCITT working group rejects or redirects our profile draft | Medium | Medium | Engage with SCITT chairs before submission; coordinate with the VeritasChain VCP authors; have the standalone-draft fallback as a contingency |
| R4 | NIST releases superseding PQC algorithm late in our migration window | Low | Medium | Algorithm-identifier registry (Commitment 1 enables this); cross-signing migration path handles superseding algorithms |
| R5 | Microsoft ships Bitcoin-anchored MCP receipts in 2027 (absorbs our position) | Medium | High | Foundation+Inc structure cannot be matched by Microsoft; ship the SEP-1763 reference impl Day 1; secure SCITT working-group standing before Microsoft enters |
| R6 | EU AI Act successor names a competing protocol (C2PA, VCP) by name and excludes LedgerProof | Low | High | Public-comment engagement throughout EU AI Office consultation cycles; positioned as Bitcoin-anchored complement to whatever else is named |
| R7 | Foundation 501(c)(3) status denied by IRS | Low | Medium | Standard Foundation structure designed for approval; attorney engagement Day 1; operate as in-formation until approval |
| R8 | A major receipt-format vulnerability is discovered post-launch | Low | Catastrophic | Pre-launch cryptographer review by Frank's network and/or Peter Todd; published security-disclosure policy; bug-bounty program by Phase 2 |
| R9 | Founder bandwidth exhaustion in Year 1 | Medium | High | The cooperative-utility transition (Phase 4) is precisely the antidote — distributed governance reduces single-point-of-failure on founder |
| R10 | The Foundation's perpetuity claim is challenged in court or regulation | Low | Medium | Endowment-building plan with target $500M by Year 10; protocol-continuity escrow (Commitment 6) makes perpetuity architecturally credible regardless of any single entity |

---

## 8 · The single most important architectural decision in the next 28 days

**Commit, before July 6, 2026, to filing the IETF -00 draft as a SCITT profile (`draft-dawkins-scitt-lpr-00`), not as a standalone Internet-Draft.**

This single decision determines:

- The standards-body trajectory (SCITT working group becomes our institutional home; LedgerProof becomes a named SCITT profile alongside VeritasChain VCP).
- The composability posture (we compose with VeritasChain rather than compete with them, eliminating a category-fight risk).
- The Foundation's IETF engagement path for the next 24 months (working-group participation; co-editor opportunities; potential RFC publication by Phase 3).
- The signal to regulators and audit firms that LedgerProof is an open-standards participant, not a vendor-proprietary system.
- The signal to the cryptographic community that the work is intended for the global commons.

Every other architectural commitment in this brief is contingent on, or strengthened by, this single decision. The work to support it is small (the LPR v1.0 specification language gets a SCITT-profile mapping section; the IETF -00 draft text gets the SCITT framing) but the strategic consequence compounds for a decade.

---

## 9 · Closing — what this brief commits us to

This document is not a marketing plan. It is the technical and institutional commitment LedgerProof makes to the people whose records will, over the next decade, increasingly be anchored under this protocol. Every commitment in Section 5 is verifiable, auditable, and binding under the Foundation's governance documents and the public LPR v1.0 specification.

The decade between 2026 and 2036 will determine whether LedgerProof becomes infrastructure or becomes a footnote. The brief above is the foundation on which the infrastructure case rests.

The protocol is built. The launch is in 45 days. The architecture is honest.

— LedgerProof Foundation (in formation), May 20, 2026

---

## Companion documents

- `research/wave1-macro/01-quantum-pqc-trajectory.md` — Detailed quantum/PQC dossier
- `research/wave1-macro/02-domains-2-through-8-synthesis.md` — Consolidated Wave 1 research synthesis
- `../04-lpr-spec/LPR-1.0-SPECIFICATION.md` — The LPR v1.0 specification (to be updated per Commitments 1–6 of this brief)
- `../04-lpr-spec/IETF-00-DRAFT-DAWKINS-LPR-00.txt` — The IETF Internet-Draft (to be revised as a SCITT profile per Commitment 3)
- `../02-whitepaper/FOUNDING-WHITEPAPER-DRAFT.md` — The public-facing founding whitepaper
- `../03-manifesto/THE-PROVENANCE-MANIFESTO.md` — The coalition-signed Provenance Manifesto
- `../01-foundation/` — Foundation Articles, Bylaws, Board Charter
- `../10-checklist/LAUNCH-CHECKLIST-28-DAYS.md` — Operating checklist for the 28 days to launch

— end of 2036 Platform Architecture Brief —
