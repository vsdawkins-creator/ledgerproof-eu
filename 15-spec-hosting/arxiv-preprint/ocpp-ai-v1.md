---
title: |
  An Open Cryptographic Provenance Protocol for AI System Outputs (OCPP-AI):
  Substrate-Agnostic Article 50 Transparency Receipts Compatible with eIDAS 2.0
  and the European Blockchain Services Infrastructure
author:
  - name: Veronica S. Dawkins
    affiliation: LedgerProof Foundation (in formation)
    email: veronica@ledgerproofhq.io
keywords:
  - EU AI Act
  - Article 50
  - cryptographic provenance
  - verifiable credentials
  - eIDAS 2.0
  - European Blockchain Services Infrastructure
  - supply-chain transparency
  - SCITT
  - GDPR-compatible cryptography
arxiv_primary: cs.CR
arxiv_cross_list:
  - cs.CY
  - cs.DC
date: 3 June 2026
license: CC BY 4.0
abstract: |
  Article 50 of Regulation (EU) 2024/1689 (the "EU AI Act") imposes
  transparency obligations on providers and deployers of AI systems with
  respect to natural persons, supervisory authorities, and the public.
  Operational implementation of these obligations requires machine-readable
  evidence that survives the continued cooperation of any single deployer,
  vendor, or jurisdiction. Existing vendor-proprietary logging mechanisms
  fail this requirement by structurally coupling enforcement evidence to
  individual cloud platform operators.

  This paper specifies the Open Cryptographic Provenance Protocol for AI
  System Outputs (OCPP-AI), a substrate-agnostic protocol for machine-
  readable cryptographic receipts addressing Article 50 sub-obligations
  50(1), 50(2), 50(4), and 50(6). The protocol separates an Anchor
  Interface specification (defining the properties any conforming anchor
  substrate must satisfy) from substrate-specific reference implementations
  (Bitcoin OP_RETURN as the current reference implementation; European
  Blockchain Services Infrastructure (EBSI) as the primary
  enterprise-government alternative).

  We demonstrate architectural compatibility with W3C Verifiable Credentials
  2.0 through a published JSON-LD context that wraps OCPP-AI receipts as
  Verifiable Credentials without loss of information, and architectural
  complementarity with Regulation (EU) 2024/1183 (eIDAS 2.0) through a
  composition pattern that enables qualified evidence presentation through
  established Qualified Trust Service Providers without modification of the
  core receipt format.

  The specification preserves GDPR Article 17 erasure mechanics through
  structural exclusion of personal data at the receipt schema validation
  layer and at the anchor payload format. Reference implementations exist
  in Python, TypeScript, and Rust under Apache License 2.0, with twenty-nine
  framework adapters covering the principal AI orchestration ecosystems.

  We propose OCPP-AI for stakeholder consultation at the European Commission
  AI Office, the European AI Board, CEN-CENELEC Joint Technical Committee
  21, and the IETF SCITT Working Group, as an open specification suitable
  for normative or informative reference in published guidelines and
  harmonized standards under the AI Act.
---

# 1. Introduction

## 1.1 The structural problem of Article 50 evidence

The European Union's Artificial Intelligence Act, Regulation (EU) 2024/1689,
becomes applicable on 2 August 2026 for the transparency obligations of
Article 50. These obligations require providers and deployers of AI systems
to (1) disclose to natural persons that they are interacting with an AI
system, (2) mark synthetic media in a machine-readable manner, (3) notify
subjects of emotion-recognition and biometric-categorization systems, and
(4) disclose AI-generated text on matters of public interest, with a
specified exemption for content subject to human editorial review.

Operational implementation of these obligations creates a structural
requirement that the existing AI deployment ecosystem does not satisfy:
**Article 50 evidence must survive the continued cooperation of the
deployer, the vendor, and any single jurisdiction's regulatory authority**,
because the evidence may need to be presented to a national competent
authority of a Member State other than that of the deployer's seat, to a
court considering allegations against a deployer that has ceased to operate,
or to a natural person exercising a right of recourse against a
provider-deployer combination of which neither remains commercially
incentivized to preserve the evidence.

The contemporary practice of compliance logging through vendor-proprietary
mechanisms (CloudWatch, Azure Monitor, Cloud Logging, vendor-specific audit
endpoints) fails this requirement. Such logs are operationally accessible
only with the cooperation of the vendor operating them; they are subject to
data-retention policies set by the vendor; and they are accessible to
supervisory authorities only through processes that depend on the vendor's
continuing presence and cooperation in the jurisdiction.

This structural property of vendor-operated logging has a regulatory
consequence: the enforcement infrastructure of the AI Act is, in the
default deployment pattern, effectively captured by the cloud platform
operators on whose infrastructure the AI systems run. The Union's
regulatory authority over Article 50 is, in this default, conditional on
the continued cooperation of operators outside the Union's jurisdictional
reach.

## 1.2 The architectural requirement

The architectural property that escapes this capture is **independent
verifiability without the cooperation of the deployer, the vendor, or any
single jurisdiction's authority**. A natural person, a supervisory
authority, or a court must be able to verify Article 50 evidence using only
publicly available substrate access and a published verifier specification.
No verifier may be required to obtain credentials from, enter into agreement
with, or otherwise depend on the continuing cooperation of any of the
parties to the original AI system transaction.

This requirement is satisfied by the architectural pattern of cryptographic
attestations published to public, immutable substrates: signed receipts
batched into Merkle trees whose roots are published to a substrate that
satisfies a defined Anchor Interface specification (immutability under
adversarial conditions, public verifiability without authentication,
jurisdictional neutrality, demonstrated operational durability).

This paper specifies such a protocol.

# 2. Related work

## 2.1 Certificate Transparency

The Certificate Transparency framework (RFC 6962, RFC 9162) established
the technical pattern of Merkle-tree-aggregated publication of signed
attestations to publicly verifiable logs. CT logs are a viable substrate
for non-EU evidence applications but do not satisfy the jurisdictional
neutrality requirement of EU AI Act evidence in the form deployed for X.509
certificate transparency, where CT logs are operated by a small number of
commercial certificate authorities. The architectural pattern is preserved;
the substrate is changed.

## 2.2 IETF SCITT

The IETF Supply Chain Integrity, Transparency, and Trust (SCITT) Working
Group has produced a series of specifications for cryptographic supply-
chain attestations, including the SCITT Architecture (draft-ietf-scitt-
architecture) and SCITT Receipts (draft-ietf-scitt-scrapi). OCPP-AI is
formally specified as a SCITT profile in IETF Internet-Draft
`draft-dawkins-scitt-ai-article50-00`, currently under review by the SCITT
Working Group. The profile defines three SCITT statement content types
addressing the Article 50 sub-obligations.

## 2.3 W3C Verifiable Credentials 2.0

The W3C Verifiable Credentials 2.0 Data Model (W3C Recommendation, May
2025) provides a standardized format for machine-readable cryptographic
attestations. Architectural compatibility with VC 2.0 is desirable for
participation in the broader ecosystem of verifiable credentials including
those produced under eIDAS 2.0. OCPP-AI achieves this compatibility through
a published JSON-LD context that wraps OCPP-AI receipts as W3C VC 2.0
credentials without loss of information.

## 2.4 eIDAS 2.0 and the European Digital Identity framework

Regulation (EU) 2024/1183 (eIDAS 2.0) establishes the European Digital
Identity Wallet (EUDI Wallet) framework, which depends architecturally on
W3C Verifiable Credentials and on Qualified Trust Service Providers
(QTSPs). OCPP-AI is not itself an eIDAS-qualified protocol; OCPP-AI
signatures are not Qualified Electronic Signatures (QES) per eIDAS Article
25. The relationship between OCPP-AI and eIDAS 2.0 is therefore one of
architectural complementarity: OCPP-AI provides the Article 50 evidence
layer; eIDAS 2.0 provides the broader qualified-evidence framework; the
two compose through the VC 2.0 wrapping pattern of Section 5.

## 2.5 The European Blockchain Services Infrastructure (EBSI)

The European Blockchain Services Infrastructure (EBSI), operated by the
European Commission and the European Blockchain Partnership Member States,
is a permissioned blockchain network designed for cross-border publication
of trusted credentials by Member State governments and EU institutions.
EBSI is identified by this paper as the primary enterprise-government
alternative anchor substrate satisfying the OCPP-AI Anchor Interface, for
use cases requiring Union-sovereign verification.

# 3. The OCPP-AI specification

## 3.1 Receipt structure

OCPP-AI receipts comprise three structural layers: an envelope establishing
chain identity (sequence, prev_hash, entry_hash, signature, publisher_id,
key_id), a content body conforming to one of four Article 50 sub-obligation
profiles, and an anchor reference resolving to a substrate-level anchor
record. Receipts are encoded using the Concise Binary Object Representation
(CBOR; RFC 8949) deterministic encoding subset and signed using Ed25519
(RFC 8032).

The content body profiles are: **ChatbotSession** (Article 50(1)),
**GeneratedContent** (Article 50(2)), **HumanReview** (Article 50(4)), and
the manner-of-disclosure field present across profiles (Article 50(6)).
Profile schemas constrain field values to bounded vocabularies and reject
personally identifiable data at the schema validation layer, in keeping
with GDPR Article 5(1)(c) data minimization.

## 3.2 Receipt aggregation and anchoring

Receipts are aggregated into batches whose Merkle roots are constructed
per RFC 6962. Each Merkle root is published to a substrate satisfying the
Anchor Interface (Section 4) using the 36-byte OCPP-AI anchor payload
format: a fixed four-byte ASCII prefix `"LPR1"` followed by the 32-byte
SHA-256 Merkle root.

The fixed-length anchor payload format serves three purposes: (i)
machine-distinguishability from non-OCPP-AI uses of the substrate, (ii)
structural exclusion of personal data at the anchor layer, and (iii)
preservation of substrate-level cost amortization across the receipts in a
batch (one anchor publication per ~10-minute aggregation window in
reference implementations).

## 3.3 Verification

Verification of an OCPP-AI receipt proceeds in six steps: (1) parse the
receipt as canonical CBOR, (2) verify the Ed25519 signature against the
publisher's published public key, (3) verify schema conformance of the
content body to one of the Article 4 profiles, (4) resolve the anchor
reference to a substrate-level record, (5) verify the OCPP-AI anchor
payload format including the `"LPR1"` magic prefix, and (6) reconstruct
the Merkle proof from the receipt to the anchor's published Merkle root
per RFC 6962.

No verification step requires authentication to any party. The verifier
requires only public substrate access and the publisher's published public
key.

# 4. The Anchor Interface

The Anchor Interface is the abstract specification of the properties any
acceptable anchor substrate must satisfy. The interface specifies eight
properties (I-1 through I-8), summarized here and specified in full in the
companion document at `https://spec.ledgerproofhq.io/anchor-interface-v1.html`.

**I-1 Immutability under adversarial conditions.** The substrate must
provide a cryptographic guarantee that no party can alter, remove, or
substitute the published anchor record without producing a publicly
observable inconsistency.

**I-2 Public verifiability without authentication.** Any natural or legal
person with internet access must be able to verify the presence and content
of any published anchor record without identifying themselves to the
substrate operator.

**I-3 Jurisdictional neutrality.** The substrate's continued operation must
not depend on the consent or non-interference of any single sovereign state
or single private legal entity; substrate operation must be distributed
across at least three independent jurisdictions.

**I-4 Demonstrated operational durability.** The substrate must have
demonstrated continuous operational availability for at least 36 months
prior to anchor publication.

**I-5 Deterministic resolution of anchor records.** Any independent
verifier must be able to deterministically resolve the anchor record
content and substrate position from the anchor reference.

**I-6 Bounded anchor payload format.** The substrate must accept the fixed
36-byte OCPP-AI anchor payload format.

**I-7 OCPP-AI Anchor Payload Format.** The fixed 36-byte structure
`"LPR1"` || `merkle_root_32`.

**I-8 GDPR Article 17 compatibility.** The anchor payload format must not
permit publication of personal data; receipt-level erasure must not
invalidate the anchor.

## 4.1 Reference implementation: Bitcoin OP_RETURN

The Bitcoin mainnet, with anchor payload publication via the `OP_RETURN`
script opcode, satisfies all eight properties of the Anchor Interface. The
substrate's evaluation against each property is presented in tabular form
in the companion specification. Bitcoin OP_RETURN anchoring is appropriate
for use cases prioritizing maximum operational durability, jurisdictional
neutrality, and independence from any single state's regulatory authority.

## 4.2 Alternative implementation: European Blockchain Services Infrastructure (EBSI)

EBSI satisfies properties I-1 through I-3 and I-5 through I-8 of the
Anchor Interface, with property I-4 under continuing evaluation pending
EBSI's accumulation of the 36-month operational record threshold. EBSI is
appropriate for use cases requiring Union-sovereign verification, where the
deployer is a public-sector entity, or where Member State competent
authorities have indicated a preference for EU-operated anchor substrates
in their supervisory practice.

## 4.3 Dual-anchor deployment

Dual-anchor publication — the same receipt-batch Merkle root published to
both Bitcoin and EBSI in parallel — is the recommended configuration for
deployers operating under EU jurisdictional reach whose AI system outputs
are syndicated across both EU and non-EU jurisdictions. Verifiers may
accept evidence from either anchor; verifiers operated by EU institutions
may require evidence from the EBSI anchor as a matter of supervisory policy
without disadvantaging non-EU verifiers, who may accept the Bitcoin anchor.

# 5. Compatibility with W3C VC 2.0 and eIDAS 2.0

## 5.1 W3C VC 2.0 wrapping

A JSON-LD context published at `https://spec.ledgerproofhq.io/contexts/lpr-v1.jsonld`
maps OCPP-AI content body fields to W3C VC 2.0 credentialSubject
properties. The mapping is one-to-one and reversible; an OCPP-AI receipt
may be losslessly serialized as a W3C VC 2.0 Verifiable Credential and
recovered from that form. When wrapped as a VC, the receipt's `issuer`
property identifies the publishing deployer; the LedgerProof Foundation
does not assert issuer authority over receipts published by deployers.

## 5.2 eIDAS 2.0 architectural complementarity

OCPP-AI signatures are Ed25519 and do not constitute Qualified Electronic
Signatures per eIDAS Article 25. The LedgerProof Foundation is not a
Qualified Trust Service Provider. The relationship between OCPP-AI and
eIDAS 2.0 is therefore one of architectural complementarity rather than
overlap: an OCPP-AI receipt, wrapped as a W3C VC 2.0 credential, may be
presented through an eIDAS-compliant Qualified Trust Service Provider for
use cases requiring qualified evidence. The composition does not modify
the OCPP-AI receipt format; the qualification attaches at the wrapping
layer.

This complementarity preserves the Union's existing investment in eIDAS
infrastructure. OCPP-AI does not duplicate, compete with, or replace eIDAS
trust services. It provides the Article 50 cryptographic provenance
evidence layer that complements them.

# 6. GDPR compatibility

The OCPP-AI receipt schema is constructed to preclude the inclusion of
personal data at the receipt layer. Fields that could otherwise carry
personal data (deployer_id, reviewer_role, review_rationale) are bounded
to specific identifier formats (LEI, VAT identifier, bounded role
vocabulary). Schema validation rejects email addresses, telephone numbers,
government identifiers, and free-text PII patterns.

At the anchor layer, the 32-byte SHA-256 Merkle root carries
cryptographically no recoverable information about underlying receipt
content. The anchor is GDPR-compatible by structure; no party may publish
personal data to the anchor through this protocol.

Receipt-level erasure under GDPR Article 17 is performed at the receipt
store layer. Erasure invalidates the Merkle proof for the erased receipt
without invalidating proofs for other receipts in the same batch. The
anchor is unaffected by erasure. This separation is essential for joint
AI Act / GDPR compliance and is a normative architectural commitment of
the protocol.

# 7. Implementation status and ecosystem

Reference implementations of OCPP-AI are published under Apache License 2.0
at `github.com/vsdawkins-creator/ledgerproof-eu` in Python, TypeScript, and Rust. Twenty-nine
framework adapters cover the principal AI orchestration ecosystems
(LangChain, LlamaIndex, OpenAI SDK, Anthropic SDK, Google AI, Vertex AI,
AWS Bedrock, Azure OpenAI, Mistral, Cohere, Together, Groq, Hugging Face,
AI21, Replicate, xAI, DeepSeek, Qwen, Reka, Voyage, Cerebras, IBM watsonx,
Snowflake Cortex, Perplexity, Fireworks, Aleph Alpha, Haystack, Semantic
Kernel, and Mistral Codestral).

A command-line verifier and a browser-based verifier (operating with no
SaaS dependency) are published under the same license. Conformance test
vectors are published at `https://spec.ledgerproofhq.io/test-vectors-v1/`.

# 8. Governance and standardization

The LedgerProof Foundation, the entity maintaining the reference
implementation, is in formation as a Delaware 501(c)(3) public charity
under Adler & Colvin counsel, with a Dutch Stichting EU subsidiary under
NautaDutilh counsel. The specification is published under CC BY 4.0. The
Foundation does not assert patent encumbrance over the specification and
undertakes that the specification will not be made subject to commercial
licensing.

The Foundation contributes to standardization activity at CEN-CENELEC
Joint Technical Committee 21 (through national mirror committees including
DIN Germany and AFNOR France), at the IETF SCITT Working Group, and at
W3C. The Foundation will support the adoption of this specification or its
successors by other standards bodies including ISO, CEN-CENELEC, IETF, and
W3C if requested.

# 9. Discussion: the Brussels Effect and strategic autonomy

The architectural choices specified in this paper reflect a substantive
position on the proper relationship between AI regulation and the
infrastructure on which AI systems run. We argue that:

(i) The Union's regulatory authority over Article 50 — and therefore the
Brussels Effect for AI regulation — depends on the existence of an
enforcement infrastructure that the Union can operate without depending on
the continuing cooperation of operators outside the Union's jurisdictional
reach.

(ii) The contemporary default of compliance logging through vendor-
proprietary mechanisms forfeits this infrastructure. Article 50 enforcement
under that default is conditional on hyperscaler cooperation.

(iii) The architectural pattern that escapes this conditional dependency
is cryptographic provenance evidence published to public, immutable
substrates satisfying a defined Anchor Interface. The Anchor Interface is
substrate-neutral by design; it admits both substrates operated outside
Union control (Bitcoin) and substrates operated under Union control (EBSI).

(iv) The Union's adoption of an architectural pattern that admits both
forms of substrate, with EBSI as a first-class implementation, preserves
Union strategic autonomy over Article 50 enforcement without sacrificing
the operational durability and jurisdictional neutrality that long-term
evidence preservation requires.

We do not take a position on which substrate should be preferred in
specific use cases. We take the position that the Union's regulatory
framework should not foreclose the choice.

# 10. Conclusion

OCPP-AI is offered as an open specification suitable for normative or
informative reference in published guidelines and harmonized standards
under the EU AI Act. The specification is architecturally compatible with
W3C Verifiable Credentials 2.0, architecturally complementary to eIDAS
2.0, GDPR-compatible by structure, and substrate-agnostic with named
reference implementations including Bitcoin OP_RETURN and the European
Blockchain Services Infrastructure.

The maintainer (LedgerProof Foundation) is in formation under counsel and
does not assert proprietary rights over the specification or commercial
encumbrance on its implementation. Stakeholder consultation is invited
from the European Commission AI Office, the European AI Board, Member
State competent authorities, CEN-CENELEC JTC 21, the IETF SCITT Working
Group, and W3C.

## References

[references listed in arXiv submission format; see companion bibliography]

## Author contact

Veronica S. Dawkins
LedgerProof Foundation (in formation)
veronica@ledgerproofhq.io
https://spec.ledgerproofhq.io
IETF Datatracker: `draft-dawkins-scitt-ai-article50-00`

---

**Submission notes (NOT for inclusion in final manuscript):**

- arXiv primary classification: cs.CR (Cryptography and Security)
- arXiv cross-list: cs.CY (Computers and Society), cs.DC (Distributed, Parallel, and Cluster Computing)
- License selection at submission: CC BY 4.0
- LaTeX formatting: convert to arXiv-acceptable LaTeX before submission (markdown is the working draft; final submission requires `.tex`)
- Companion documents to upload as ancillary materials:
  - Anchor Interface Specification v1.0 (HTML)
  - JSON-LD context file (lpr-v1.jsonld)
  - Three sample receipts (one per Article 4 profile)
  - IETF draft text (`draft-dawkins-scitt-ai-article50-00`)
- Co-author decision (per V's directive 3 June 2026): SINGLE-AUTHOR, GO. Institutional co-authors may be appended during the absorption phase if appropriate.
- Bibliography to add before submission: complete reference list per arXiv format, including the eight RFCs cited, the W3C VC 2.0 Recommendation, the eIDAS 2.0 Regulation, the AI Act Regulation, the GDPR, and selected EBSI architecture documents.
- arXiv submission target: tonight (3 June 2026, before midnight PDT). arXiv processes submissions overnight; preprint typically appears within 24 hours of submission.
