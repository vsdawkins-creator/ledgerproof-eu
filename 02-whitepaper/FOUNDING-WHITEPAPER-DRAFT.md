# Document Provenance in the AI Era

## An Open Protocol for Cryptographic Authorship and Long-Horizon Verifiability

**LedgerProof Foundation · Veronica S. Dawkins, Founder**
*Draft for publication on or about July 6, 2026 · To be anchored on the Bitcoin blockchain at the time of release*

---

## Abstract

This paper introduces the **LedgerProof Receipt (LPR), version 1.0** — an open, vendor-neutral cryptographic format that binds a document or AI-generated artifact to its asserted authorship, its precise moment of finalization, and its complete chain of subsequent modification, in a form that any party can verify without trusting the document's holder, software vendor, certifying authority, or any single government. LPR is anchored, through Merkle-tree aggregation conforming to RFC 6962, on the Bitcoin blockchain — a substrate chosen because the verification of an LPR receipt twenty years from now must not depend on the survival of any institution that exists today, including the LedgerProof Foundation itself. LPR is structured as a profile of the IETF Supply Chain Integrity, Transparency, and Trust (SCITT) architecture [draft-ietf-scitt-architecture], allowing interoperation with the broader SCITT ecosystem while providing the unique assurance properties of Bitcoin-anchored verification. This paper sets out the threat model, the technical construction, the honest relationship to prior art, the regulatory frame within which LPR enters the world, and the open invitation to the standards bodies, regulators, journalists, courts, auditors, and institutions whose records the protocol exists to serve.

---

## 1 · The threat model

The cost of being wrong about whether a document is authentic has become measurable. In the twenty-four months preceding the publication of this paper, that cost has manifested as wire-fraud losses settled in the billions, contested election filings turned on document timestamps, criminal cases overturned because evidence custody could not be proved past reasonable doubt, scientific retractions where the integrity of the underlying data was either falsified or could not be reconstructed, and regulatory enforcement actions in which the question of *when* a disclosure was made determined the outcome. In parallel, the volume of artificial-intelligence-generated text, image, audio, and structured-document content has reached an order of magnitude where the unconditioned assumption that a document was produced by a human author is no longer reliable.

This is the documentary economy as it exists in mid-2026. It is not the predicted future. It is the present condition.

LPR is constructed against the following threat model.

**T1 — Silent retroactive alteration.** A document produced and stored under any custodial system (a vendor-hosted SaaS, a corporate file server, a regulator's database, a court's electronic filing system) can be altered after the fact by the custodian, by an insider, or by an external actor who has obtained sufficient privilege, *without leaving evidence accessible to outside parties.* The integrity of the record reduces to trust in the custodian. The custodian may not deserve that trust, may not survive long enough to be questioned, or may itself be compelled by litigation, regulation, or coercion to alter the record.

**T2 — Authorship substitution.** A document, including but not limited to AI-generated content, may be presented under an asserted authorship that the document itself cannot independently corroborate. Metadata signed by the document-producing tool is typically stripped at the first point of redistribution.

**T3 — Timestamp manipulation.** The asserted creation, modification, or signature time of a document can be moved forward or backward by any party with write access to the system clock or the file system, by any custodian able to revise database timestamps, and by any signing-authority whose private key has been compromised.

**T4 — Vendor-dependent verification.** A document whose authenticity can be verified only by software, infrastructure, or services controlled by a single vendor is verifiable only as long as that vendor exists, remains honest, remains funded, and remains compliant with applicable law. Vendors do not last twenty years; the documents they certify must.

**T5 — Cryptographic decay.** Cryptographic primitives weaken over time. SHA-256 has not been broken in fifteen years but it cannot be assumed to remain unbroken in fifty. A document whose verification depends solely on a primitive that may not survive its custody horizon is, on a long enough timeline, indistinguishable from an unverified document.

LPR addresses T1 through T4 with the construction described in §3. T5 is addressed through a defined migration architecture described in §4.

## 2 · Why now — the regulatory frame

This paper enters the world six weeks before the August 2, 2026 enforcement date of **Article 50 of Regulation (EU) 2024/1689**, commonly known as the EU AI Act. Article 50 imposes binding transparency obligations on the providers and deployers of AI systems that generate synthetic content, including a requirement that the output be marked in a "machine-readable format" sufficient for downstream parties to detect AI-generated origin. The European Commission's Code of Practice on AI-generated-content marking, published in March 2026 in second-draft form, explicitly concludes that "no single active marking technique suffices" to satisfy the Article 50 reliability requirement; a multi-layered approach combining metadata, watermarking, and cryptographic provenance is the consensus position of the regulatory and standards communities.

Concurrent regulatory developments include: U.S. Securities and Exchange Commission interpretive guidance on the audit-evidence sufficiency of cryptographically anchored records; National Institute of Standards and Technology working drafts on AI content provenance; the Public Company Accounting Oversight Board's consultation on the admissibility of blockchain-anchored records as audit evidence; joint guidance from the cybersecurity agencies of the United States, the United Kingdom, Australia, Canada, and New Zealand on securing autonomous AI-agent systems; and the European Data Protection Board's April 2025 draft guidelines on personal data and the blockchain, which clarify the conditions under which hash-only anchoring may proceed under GDPR Article 17.

The convergence of these instruments establishes, for the first time, that *the integrity of the documentary record is a regulated property of regulated systems.* The question of cryptographic provenance is no longer a question of vendor differentiation. It is a compliance question with deadlines and penalties.

LPR is offered as one open answer to that question. It is not the only possible answer.

## 3 · The LedgerProof Receipt — technical construction

### 3.1 · Overview

An LPR receipt is a small, structured data object that asserts the existence of a document at a specific moment in time, the identity of its author or authorizing system, and the cryptographic linkage to any preceding receipts in the same authorial chain. LPR is constructed from four established primitives:

- **SHA-256** [FIPS 180-4] for content hashing
- **Ed25519** [RFC 8032] for digital signatures of authorship
- **CBOR canonical encoding** [RFC 8949] and **JSON Canonicalization Scheme** [RFC 8785] for deterministic serialization
- **Merkle tree aggregation** following the construction of **RFC 6962** (Certificate Transparency)

The receipt is then anchored, in aggregate, on the Bitcoin blockchain via an OP_RETURN transaction containing the Merkle root.

### 3.2 · The receipt schema

An LPR v1.0 receipt is a canonical CBOR object containing the following fields:

```
LPR-Receipt v1.0:
  lpr_version: 1
  receipt_id: UUID v7
  trace_id: UUID v7              # binds related receipts in an authorial chain
  timestamp_ns: int64            # nanoseconds since Unix epoch
  timestamp_iso: string          # RFC 3339
  artifact:
    content_hash: SHA-256        # of the canonical artifact bytes
    hash_algo: "SHA-256"
    content_type: string         # MIME or named profile
    content_bytes: int           # length of the artifact in bytes
  authorship:
    actor_type: enum             # HUMAN | AI_MODEL | HYBRID | INSTITUTION
    actor_id: string             # public key, DID, or named entity
    actor_assertion: string      # the declaration the actor is making
    tool_chain: array            # optional named tools used (e.g., AI models, with versions)
  chain:
    prev_receipt_hash: SHA-256   # null for the first receipt in a chain
  signature:
    sig_algo: "Ed25519"
    sig_bytes: 64-byte signature # over the canonical CBOR of all preceding fields
    signer_pubkey: 32-byte Ed25519 public key
  additional_signatures:        # OPTIONAL in Core; REQUIRED in Long-Horizon profile
    - sig_algo: string          # e.g. "Composite-ML-DSA-65+Ed25519" or "ML-DSA-65"
      sig_bytes: byte string
      signer_pubkey: byte string
      profile: string           # e.g. "LongHorizon-v1"
  anchor:
    substrate: string            # "bitcoin-mainnet" (default) | "ethereum-mainnet" | ...
    merkle_leaf_hash: SHA-256    # this receipt's leaf in the daily Merkle tree
    anchor_status: enum          # PENDING | ANCHORED
    btc_txid: string             # Bitcoin transaction id when anchored
    btc_block_height: int        # Bitcoin block height when anchored
    merkle_path: array of SHA-256 # inclusion proof
```

A receipt is *signed* by the signer's Ed25519 key at the moment of creation; it is *anchored* on the next Bitcoin block following the receipt's inclusion in the Foundation-operated daily Merkle tree.

### 3.3 · Anchoring

Anchoring follows the public-chain pattern established by OpenTimestamps and subsequent implementations: receipts are accumulated in a Merkle tree constructed under RFC 6962, the root is committed to Bitcoin via an OP_RETURN transaction, and the inclusion proof for any individual receipt is the path from its leaf to the root. The choice of Bitcoin is intentional and conservative. Bitcoin is the only public chain whose security budget, mining decentralization, and operational continuity history suggest a credible probability of being available for verification of a document anchored in 2026 at a verification time of 2076. Other anchoring substrates are not excluded by this specification; a future LPR profile may define alternative anchors. Bitcoin is the default and the recommended substrate for the v1.0 profile.

The Foundation operates one public calendar server. Implementers are free to run their own. The protocol's verification model does not depend on the survival of the Foundation-operated calendar.

### 3.4 · Verification

Verification of an LPR receipt proceeds in five steps, each independently checkable:

1. The receipt's canonical CBOR is recomputed and the Ed25519 signature is validated against the embedded signer public key.
2. The asserted `content_hash` is recomputed from the artifact and compared to the value in the receipt.
3. If `chain.prev_receipt_hash` is non-null, the predecessor receipt is fetched and its canonical hash is verified to match.
4. The Merkle inclusion proof is verified against the published Merkle root.
5. The Merkle root is verified to appear in the Bitcoin OP_RETURN transaction at the asserted block height, and the block is verified against any independent Bitcoin node.

Verification requires no contact with the LedgerProof Foundation, with the original signer, or with any commercial party. The reference verifier is open source. Independent verifiers can be constructed in any language with SHA-256, Ed25519, and a Bitcoin block-header source.

## 4 · Crypto-decay and migration

LPR v1.0 acknowledges that SHA-256 and Ed25519 will not remain the strongest primitives in the cryptographic toolkit for the entire envisioned verification horizon of receipts produced today. The protocol is designed for this reality.

**The current threat horizon.** NIST finalized post-quantum cryptography standards FIPS 203, 204, and 205 in August 2024. The NSA's CNSA 2.0 mandate requires national-security systems to migrate by 2035. The central-case consensus among cryptographers is that a cryptographically-relevant quantum computer (CRQC) — one capable of breaking RSA-2048 and Ed25519 — exists between 2030 and 2035. SHA-256 is substantially more resistant to quantum attack (Grover's algorithm yields only a square-root speedup, reducing 256-bit security to 128-bit effective security, which remains strong by 2036) but is a candidate for future migration.

**The LPR migration architecture.** The `additional_signatures` field in the LPR v1.0 receipt schema (§3.2) is the explicit extension point for this migration. Three profiles are defined at launch:

- **Core (v1.0):** SHA-256 + Ed25519 + Bitcoin OP_RETURN. The baseline.
- **Long-Horizon:** Core plus a composite ML-DSA-65+Ed25519 signature in `additional_signatures`, using the algorithm `"Composite-ML-DSA-65+Ed25519"` defined in [draft-ietf-lamps-pq-composite-sigs]. ML-DSA-65 is NIST FIPS 204 (formerly Dilithium3). Intended for documents that must remain verifiable beyond 2035.
- **High-Assurance:** Core plus hardware-backed signing (HSM/FIPS 140-3 Level 3), sub-hourly anchoring, and multi-calendar verification. Intended for legal, financial, and regulatory submissions.

**Re-anchoring.** Receipts produced under the Core profile are eligible for *re-anchoring* before the CRQC threat horizon. The Foundation commits, in its Bylaws and in the LPR specification §11.1, to operating a free re-anchoring service that upgrades Core receipts to Long-Horizon by adding the composite PQC signature in a new chained receipt. The re-anchoring operation is **non-destructive**: the original receipt remains verifiable on its original terms.

The intent is that an LPR receipt produced in 2026 remains independently verifiable in 2076 under whichever cryptographic primitives are then strongest, with the chain of migration receipts itself verifiable on Bitcoin.

## 5 · Honest relationship to prior art

LPR does not invent the public-chain anchoring pattern. The pattern was established by **OpenTimestamps** (Peter Todd, 2016) and has been used in production by **OriginStamp** (since 2014), **Woleet**, **Simple Proof**, and others. LPR is not a competitor to these systems; it is a *superset profile* designed to compose with them and to extend their scope into authorship signing, AI agent action receipts, and machine-readable Article 50 marking.

Specifically:

- **OpenTimestamps** focuses on timestamping. An LPR receipt that omits authorship signing degrades cleanly into an OpenTimestamps proof. Cross-verification with the OpenTimestamps calendar network is supported.
- **Coalition for Content Provenance and Authenticity (C2PA)** focuses on media-asset manifests carried in-file. LPR receipts may be embedded inside C2PA manifests as a Bitcoin-anchored trust extension, restoring verifiability for the substantial fraction of content where the C2PA manifest is stripped at distribution time.
- **VeritasChain VAP** is an open standard for verifiable AI decision provenance, published by the VeritasChain Standards Organization. LPR is being contributed to VSO as a candidate Bitcoin-anchor profile for VAP.
- **Microsoft Agent Governance Toolkit (April 2026)** provides offline-verifiable Ed25519+JCS receipts for autonomous agent decisions but does not anchor those receipts to a public chain. An LPR receipt can carry an AGT receipt as a wrapped payload, providing the public-chain anchor AGT lacks.
- **ERC-8004 Trustless Agents (Ethereum, January 2026)** provides on-chain trust infrastructure for autonomous agents on EVM-compatible chains. LPR is a peer effort on Bitcoin with overlapping but distinct scope.

The honest read is that LPR is one piece of a larger field whose progress is positive and accelerating. The Foundation's posture is composition, not competition.

## 6 · The Foundation and the operating company

The LedgerProof Foundation is a Delaware nonprofit corporation organized under Section 501(c)(3) of the Internal Revenue Code (status pending IRS determination at the time of publication). The Foundation owns the LPR specification, the reference implementations, and the public verifier infrastructure. The Foundation publishes the specification under Creative Commons Attribution 4.0; the reference implementations under MIT license. The Foundation does not, and will not, charge any party for verification.

**LedgerProof, Inc.** is a Delaware for-profit corporation, separately governed, that provides commercial managed-anchoring infrastructure, audit-grade compliance packs (including for Article 50 compliance), enterprise SLAs, and vertical-specific products (legal-evidentiary, BFSI-compliance, journalism-authentication) on top of the Foundation's open specification. LedgerProof, Inc. holds a perpetual, royalty-free, non-exclusive license to the LPR specification from the Foundation. The boundary between the two entities is governed by the Foundation's Bylaws Article VIII and overseen by an independent Conflicts Committee.

This dual structure is not novel. It is the structure used by the Internet Security Research Group (which operates Let's Encrypt) and by the Mozilla Foundation / Mozilla Corporation. It is adopted here because the verification of a document anchored in 2026 must not depend on the commercial survival of the company that anchored it.

## 7 · The path to standards

The Foundation commits to the following standards engagement:

1. Submission of an Internet-Draft to the IETF as a SCITT profile (`draft-dawkins-scitt-lpr-00`) within the first week of publication of this paper, targeting the IETF SCITT working group [draft-ietf-scitt-architecture].
2. Contribution of LPR as a candidate Bitcoin-anchor profile to the VeritasChain Standards Organization (VAP framework), building on [draft-kamimura-scitt-vcp-01].
3. Contribution of LPR receipt embedding to the Coalition for Content Provenance and Authenticity.
4. Engagement with NIST, ISO TC 307 (Blockchain and DLT), and the European Telecommunications Standards Institute (ETSI) on relevant cryptographic-provenance and electronic-timestamping standards.

The Foundation does not claim authorship of a single global standard. It claims authorship of one Bitcoin-anchored open profile and commits to working with the international standards community on the larger question.

## 8 · An open invitation

The integrity of the documentary record is a public good. It is also, in the present moment, a public emergency. We invite the institutions whose records matter to read the LPR specification, to verify the receipts that accompany this paper, and to consider whether the integrity of their own records would be better served by an open public infrastructure than by the patchwork of vendor-specific proofs the documentary economy has so far accepted.

We invite the standards bodies — IETF, W3C, ISO, NIST, ETSI, ENISA, VSO, C2PA, the IEEE — to engage with LPR as a candidate component of the larger cryptographic-provenance standards architecture the next decade will require.

We invite the courts, the regulators, the auditors, the journalists, the universities, the laboratories, the publishers, the banks, and the AI laboratories whose outputs are now indistinguishable from the human work they imitate, to participate in defining what provenance must mean in the era we are entering.

The infrastructure exists. The specification is open. The verifier is free. The receipts are public. The protocol can be adopted today. The cost of being wrong about whether a document is authentic is, today, measurably higher than the cost of marking it.

We end where we began. The record exists. The integrity is the choice.

---

## References

[FIPS 180-4] National Institute of Standards and Technology. *Secure Hash Standard (SHS)*. Federal Information Processing Standards Publication 180-4. August 2015.

[FIPS 203] National Institute of Standards and Technology. *Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)*. August 2024.

[FIPS 204] National Institute of Standards and Technology. *Module-Lattice-Based Digital Signature Standard (ML-DSA)*. August 2024.

[FIPS 205] National Institute of Standards and Technology. *Stateless Hash-Based Digital Signature Standard (SLH-DSA)*. August 2024.

[CNSA-2.0] National Security Agency. *Commercial National Security Algorithm Suite 2.0 Advisory*. September 2022 (revised 2024).

[draft-ietf-scitt-architecture] Birkholz, H., et al. *An Architecture for Trustworthy and Transparent Digital Supply Chains*. IETF SCITT Working Group. draft-ietf-scitt-architecture-22. 2026.

[draft-ietf-lamps-pq-composite-sigs] Ounsworth, M., et al. *Composite ML-DSA for use in Internet PKI*. IETF LAMPS Working Group. draft-ietf-lamps-pq-composite-sigs-13. 2026.

[draft-kamimura-scitt-vcp] Kamimura, R., et al. *Verifiable Content Protocol (VCP) SCITT Profile*. draft-kamimura-scitt-vcp-01. 2026.

[RFC 3161] Adams, C., et al. *Internet X.509 Public Key Infrastructure Time-Stamp Protocol (TSP)*. August 2001.

[RFC 6962] Laurie, B., Langley, A., Käsper, E. *Certificate Transparency*. June 2013.

[RFC 8032] Josefsson, S., Liusvaara, I. *Edwards-Curve Digital Signature Algorithm (EdDSA)*. January 2017.

[RFC 8785] Rundgren, A., Jordan, B., Erdtman, S. *JSON Canonicalization Scheme (JCS)*. June 2020.

[RFC 8949] Bormann, C., Hoffman, P. *Concise Binary Object Representation (CBOR)*. December 2020.

[EU AI Act] Regulation (EU) 2024/1689 of the European Parliament and of the Council laying down harmonised rules on artificial intelligence. June 2024. *Article 50 enforcement: August 2, 2026.*

[EDPB-Blockchain] European Data Protection Board. *Draft Guidelines on processing of personal data on the blockchain*. April 14, 2025.

[OpenTimestamps] Todd, P. *OpenTimestamps: Scalable, Trustless, Distributed Timestamping with Bitcoin*. 2016.

[C2PA-2.x] Coalition for Content Provenance and Authenticity. *Content Credentials Specification, version 2.x*. 2025–2026.

[VAP-1.1] VeritasChain Standards Organization. *Verifiable AI Provenance Framework Specification, version 1.1*. December 2025.

[MSAGT] Microsoft Open Source. *Agent Governance Toolkit*. github.com/microsoft/agent-governance-toolkit. April 2, 2026.

[ERC-8004] *EIP-8004: Trustless Agents.* Ethereum Improvement Proposals, peer-review draft, January 29, 2026.

[SEP-1763] *Interceptors for Model Context Protocol.* MCP specification proposal, draft. Opened November 4, 2025.

---

*This paper is published under the Creative Commons Attribution 4.0 International license. It is anchored, alongside the LedgerProof Receipt v1.0 specification, the LedgerProof Foundation Charter, and the Provenance Manifesto, in a single Bitcoin OP_RETURN transaction at the time of publication. The receipts for this paper and for each anchored artifact are listed at `https://ledgerproofhq.io/genesis/`.*

— end of draft —

> **FOUNDER ACTION REQUIRED:**
> 1. Polish for voice (the draft is sober but may want one or two of your specific cadences).
> 2. Send to one cryptographer reviewer (Frank's Riot senior-engineering network OR Peter Todd via warm intro) for technical review.
> 3. Generate the canonical PDF and CBOR canonical bytes; compute SHA-256.
> 4. Anchor on Bitcoin at publication (your hand on the keyboard, not Claude's).
