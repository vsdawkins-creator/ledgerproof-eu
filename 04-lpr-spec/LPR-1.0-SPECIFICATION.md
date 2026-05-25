# LPR 1.0 — LedgerProof Receipt Specification

**Status:** Draft for public release on July 6, 2026
**Editor:** Veronica S. Dawkins, LedgerProof Foundation
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
**Reference implementations:** MIT License — `github.com/ledgerproof/lpr-{python,typescript}` *(to be published)*
**Profile version:** Core (v1.0) — see §8 for Long-Horizon and High-Assurance profiles
**SCITT relationship:** This specification defines a SCITT-compatible transparency log profile under IETF SCITT Architecture [draft-ietf-scitt-architecture] — see §12

> The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when, and only when, they appear in all capitals.

---

## 1 · Scope

This specification defines the **LedgerProof Receipt (LPR), version 1.0** — an open cryptographic format that binds:

- The content hash of an artifact (document, image, signed AI output, or any byte-sequence with stable canonical form),
- An asserted authorship statement signed by the producing actor (human, AI system, or institution),
- A timestamp accurate to nanoseconds (within the limits of the producing clock),
- A cryptographic chain to predecessor receipts in the same authorial sequence,
- A Merkle-tree inclusion proof anchored on the Bitcoin blockchain.

This specification does not standardize the operating-time clock source (see §6.2), the key-management practices of the signer (see §6.3), or the choice of anchoring substrate beyond the v1.0 default of Bitcoin (see §5.1).

## 2 · Notation and primitives

### 2.1 · Cryptographic primitives

The following primitives are **REQUIRED** for LPR v1.0 conformance:

| Purpose | Algorithm | Reference |
|---|---|---|
| Content hashing | SHA-256 | FIPS 180-4 |
| Authorship signing | Ed25519 | RFC 8032 |
| Canonical serialization | CBOR canonical encoding | RFC 8949 §4.2 |
| JSON canonical form (when CBOR is not used) | JCS | RFC 8785 |
| Merkle aggregation | RFC 6962 Certificate Transparency construction | RFC 6962 §2.1 |

Implementations **MAY** offer additional primitives under future LPR profiles (see §8). An implementation that supports only the primitives in this table **MUST** be considered LPR v1.0 conformant.

### 2.2 · Identifiers

| Field | Format |
|---|---|
| `receipt_id` | UUID v7 [RFC 9562] |
| `trace_id` | UUID v7 [RFC 9562] |
| `signer_id` | 32-byte Ed25519 public key, base64url encoded, OR a Decentralized Identifier (DID) resolving to such a key |
| `btc_txid` | 32-byte Bitcoin transaction id, hex-encoded |

### 2.3 · Numeric conventions

All numeric fields **MUST** be encoded as integers or strings in the canonical encoding. Floating-point numbers **MUST NOT** be used. Timestamps **MUST** appear in two forms in every receipt: `timestamp_ns` (int64 nanoseconds since the Unix epoch) and `timestamp_iso` (RFC 3339 string in UTC).

## 3 · Receipt structure

### 3.1 · Required fields

A conformant LPR v1.0 receipt **MUST** contain the following fields:

```cbor
{
  "lpr_version": 1,
  "receipt_id": <UUID v7>,
  "trace_id": <UUID v7>,
  "timestamp_ns": <int64>,
  "timestamp_iso": <RFC 3339 string>,
  "artifact": {
    "content_hash": <SHA-256 over canonical artifact bytes>,
    "hash_algo": "SHA-256",
    "content_type": <string, MIME or named profile>,
    "content_bytes": <int, length in bytes>
  },
  "authorship": {
    "actor_type": <"HUMAN" | "AI_MODEL" | "HYBRID" | "INSTITUTION">,
    "actor_id": <string>,
    "actor_assertion": <string, the declaration the actor is making>,
    "tool_chain": [<optional tool descriptors, each with name + version>]
  },
  "chain": {
    "prev_receipt_hash": <SHA-256 of the canonical CBOR of the preceding receipt, or null>
  },
  "signature": {
    "sig_algo": "Ed25519",
    "sig_bytes": <64-byte Ed25519 signature>,
    "signer_pubkey": <32-byte Ed25519 public key>
  },
  "additional_signatures": [
    {
      "sig_algo": <string, e.g. "ML-DSA-65" or "Composite-ML-DSA-65+Ed25519">,
      "sig_bytes": <byte string>,
      "signer_pubkey": <byte string>,
      "profile": <string, e.g. "LongHorizon-v1">
    }
  ],
  "anchor": {
    "substrate": <"bitcoin-mainnet" | "ethereum-mainnet" | "ct-log" | string>,
    "merkle_leaf_hash": <SHA-256, the receipt's leaf hash in the daily Merkle tree>,
    "anchor_status": <"PENDING" | "ANCHORED">,
    "btc_txid": <hex string, present when substrate is bitcoin-mainnet and anchored>,
    "btc_block_height": <int, present when substrate is bitcoin-mainnet and anchored>,
    "merkle_path": [<inclusion proof path, when anchored>]
  }
}
```

### 3.2 · `additional_signatures` field

The `additional_signatures` array is **OPTIONAL** in the LPR v1.0 Core profile and **REQUIRED** in the LPR v1.0 Long-Horizon profile (§8.2). Each element:

- **MUST** specify a `sig_algo` identifying the algorithm (e.g., `"ML-DSA-65"`, `"Composite-ML-DSA-65+Ed25519"`, `"SLH-DSA-SHA2-128s"`).
- **MUST** specify a `profile` indicating which LPR profile requires or defines this signature entry.
- **MUST** cover the same canonical scope as the primary `signature` (§3.3), using the same omission rule: `signature`, `additional_signatures`, and `anchor` are excluded from the signed payload.
- **MAY** contain a composite signature as defined in [draft-ietf-lamps-pq-composite-sigs].

An implementation that does not understand an entry in `additional_signatures` **MUST** ignore that entry and **MUST NOT** reject the receipt on that basis. This field is designed for forward compatibility: Core-only verifiers remain fully functional on Long-Horizon receipts.

### 3.3 · Signature scope

The Ed25519 signature **MUST** be computed over the canonical CBOR encoding of the receipt object with the entire `signature` field, the entire `additional_signatures` field, and the entire `anchor` field omitted. That is, the signature attests to:

- `lpr_version`, `receipt_id`, `trace_id`, `timestamp_ns`, `timestamp_iso`
- `artifact` (all subfields)
- `authorship` (all subfields)
- `chain` (all subfields)

This separation ensures that anchoring is a non-mutating post-signing operation: a receipt's signature is valid the moment it is created; anchoring is added later when the next Bitcoin block confirms the daily Merkle tree.

### 3.4 · Canonical encoding

The canonical form of a receipt **MUST** be the deterministic CBOR encoding under RFC 8949 §4.2 (definite-length items, sorted map keys by length-then-lexicographic, integers in shortest form). An equivalent JSON canonical form under RFC 8785 (JCS) **MAY** be used for transport in environments that do not support CBOR; the SHA-256 hash of the receipt for chaining purposes **MUST** always be computed over the canonical CBOR encoding.

## 4 · Chain semantics

### 4.1 · Trace identity

A receipt with a `trace_id` shared with one or more other receipts is part of an **authorial chain**. Chains represent the sequence of authorial events affecting an artifact or a related set of artifacts (e.g., the chain of revisions of a contract, the chain of tool calls in an AI agent session).

### 4.2 · Chain linkage

The first receipt in a chain **MUST** set `chain.prev_receipt_hash` to null. Every subsequent receipt with the same `trace_id` **MUST** set `chain.prev_receipt_hash` to the SHA-256 of the canonical CBOR encoding of the preceding receipt.

### 4.3 · Insertion and deletion detection

The chain linkage construction in §4.2 ensures that:

- Insertion of a receipt into a chain after the fact is detectable because the subsequent receipt's `prev_receipt_hash` will not match.
- Deletion of a receipt from a chain is detectable because the subsequent receipt's `prev_receipt_hash` will reference a hash for which no receipt can be produced.

## 5 · Anchoring

### 5.1 · Substrate

The default and **REQUIRED** anchoring substrate for LPR v1.0 Core is the **Bitcoin main chain** (`substrate: "bitcoin-mainnet"`). Each receipt's `anchor.substrate` field **MUST** be set to identify the anchoring substrate. The following substrate identifiers are defined in v1.0:

| `substrate` value | Description |
|---|---|
| `"bitcoin-mainnet"` | Bitcoin main chain OP_RETURN anchor (default, required for Core conformance) |
| `"ethereum-mainnet"` | Ethereum main chain event log anchor (OPTIONAL, profile-defined) |
| `"ct-log"` | RFC 6962 Certificate Transparency log anchor (OPTIONAL, profile-defined) |

Future LPR profiles **MAY** define additional substrate identifiers. A verifier that does not recognize a `substrate` value **SHOULD** surface a warning but **MUST NOT** treat the receipt as invalid on that basis alone if the Bitcoin anchor is also present and valid.

A receipt carrying two `anchor` entries (one `bitcoin-mainnet`, one additional) **MUST** place additional anchors in an `additional_anchors` array parallel to the primary `anchor` object. The primary `anchor` **MUST** always be Bitcoin mainnet for Core-conformant receipts.

### 5.2 · Merkle aggregation

Receipts produced during a given anchor window **MUST** be aggregated into a Merkle tree following the construction of RFC 6962 §2.1:

```
Leaf(D)    = SHA-256(0x00 || D)
Node(L, R) = SHA-256(0x01 || L || R)
```

The domain-separating prefixes (0x00 and 0x01) are **REQUIRED**. The leaf of receipt R is the SHA-256 of the canonical CBOR encoding of R with `anchor` omitted.

### 5.3 · Anchor frequency

The default anchor window for the Foundation-operated calendar is **24 hours**, with the Merkle root committed in the OP_RETURN of one Bitcoin transaction issued by the Foundation's anchor worker. Alternative anchor frequencies (per-hour, per-10-minutes) **MAY** be defined in LPR profiles for use cases requiring tighter time bounds; the operating expense of more frequent anchoring is borne by the operator.

### 5.4 · OP_RETURN format

The anchor transaction's OP_RETURN output **MUST** contain the bytes:

```
"LPR1" (4 ASCII bytes) || <Merkle root> (32 bytes)
```

for a total of 36 bytes. The 4-byte prefix `LPR1` allows efficient discovery of LPR anchors by block scanners.

### 5.5 · Independent anchoring

An implementer **MAY** operate its own calendar server and anchor LPR receipts on its own Bitcoin address. The Foundation-operated calendar is provided as a convenience; LPR is not dependent on its operation.

## 6 · Verification

### 6.1 · Verification procedure

A receipt is **valid** if and only if all of the following checks pass:

1. The canonical CBOR encoding of the receipt with `signature` and `anchor` omitted is recomputed; the SHA-256 hash matches the input to the Ed25519 signature verification, and the signature verifies against `signer_pubkey`.
2. The artifact's `content_hash` is recomputed by hashing the canonical artifact bytes and matches the value in the receipt.
3. If `chain.prev_receipt_hash` is non-null, the predecessor receipt is independently fetched, its canonical CBOR is hashed, and the resulting SHA-256 matches `chain.prev_receipt_hash`.
4. If `anchor.anchor_status == ANCHORED`, the Merkle inclusion proof is verified against the published Merkle root, and the root is verified to appear in the Bitcoin transaction at `anchor.btc_txid`, included in the block at `anchor.btc_block_height`, against any independent Bitcoin node.

### 6.2 · Clock assertions

LPR v1.0 makes no normative claim about the accuracy of the producing clock; `timestamp_ns` is the signer's asserted timestamp. The Bitcoin anchor provides an *upper bound* on the receipt's creation time (the receipt MUST have existed before the Bitcoin block at `anchor.btc_block_height` was mined). Receipts whose `timestamp_ns` is *later* than the Bitcoin anchor time are inconsistent and **MUST** be rejected by a strict verifier.

### 6.3 · Key compromise

Signature verification establishes that the receipt was signed by the holder of the signer's private key at the time of signing. Verifiers **SHOULD** consult any available key-revocation registry to determine whether the signing key has been reported as compromised before relying on a receipt for high-value purposes.

## 7 · GDPR and personal-data considerations

Implementers **MUST** comply with applicable data-protection law, including but not limited to the European Union's General Data Protection Regulation (GDPR) and the UK Data Protection Act 2018. To facilitate compliance:

- The `artifact.content_hash` **SHOULD** be the hash of an *off-chain* canonical artifact. The artifact itself **MUST NOT** be embedded in the receipt.
- The signer **SHOULD** consider whether `artifact.content_hash` of a document containing personal data is itself personal data within the meaning of GDPR; the European Data Protection Board's April 2025 draft guidelines provide current direction.
- An implementer-operated off-chain storage layer **SHOULD** support deletion of the underlying artifact in response to GDPR Article 17 requests. The on-chain receipt remains, but without the artifact to which it refers, it functions as a hash with no derivable personal data.

## 8 · Profiles and extensions

### 8.1 · LPR v1.0 Core profile

The baseline profile defined by this specification. Requires: SHA-256, Ed25519, CBOR canonical, RFC 6962 Merkle aggregation, Bitcoin mainnet OP_RETURN anchor. All other profiles are supersets of Core.

### 8.2 · LPR v1.0 Long-Horizon profile

Intended for receipts that must remain verifiable beyond the estimated CRQC threat horizon (central-case: 2030–2035; see LedgerProof Foundation 2036 Architecture Brief, §2). This profile:

- **REQUIRES** a composite signature in `additional_signatures` using the algorithm `"Composite-ML-DSA-65+Ed25519"` as defined in [draft-ietf-lamps-pq-composite-sigs].
- **REQUIRES** ML-DSA-65 (NIST FIPS 204, formerly Dilithium3) as the post-quantum component.
- **SHOULD** additionally include a standalone `"ML-DSA-65"` entry for verifiers that cannot process composite signatures.
- **REQUIRES** the receipt carry `"profile": "LongHorizon-v1"` in the profile field.
- All other Core fields remain identical and are verified identically by Core verifiers.

Implementers anchoring documents intended for retention beyond 2035 **SHOULD** use this profile. The LedgerProof Foundation calendar operator **WILL** provide a re-anchoring service (§11.1) that upgrades Core receipts to Long-Horizon profile before the CRQC threat horizon.

### 8.3 · LPR v1.0 High-Assurance profile

Intended for legal-submission, court-admissibility, BFSI, and regulatory-compliance use cases:

- **REQUIRES** a hardware-backed signing key (HSM, TEE, or FIPS 140-3 Level 3 hardware security module) as attested in the `authorship.tool_chain` entry for the signing operation.
- **REQUIRES** sub-hourly anchor frequency (anchor window ≤ 60 minutes).
- **REQUIRES** multi-calendar anchoring: receipt must appear in at least two independent calendar operators' Merkle trees.
- **REQUIRES** the receipt carry `"profile": "HighAssurance-v1"`.
- **SHOULD** include a qualified timestamp per eIDAS 2.0 Article 42 in the `authorship.tool_chain`.

### 8.4 · Future profiles

Future profiles **MAY** define:

- Additional post-quantum signature algorithms (Falcon / FN-DSA per FIPS 206; SPHINCS+ / SLH-DSA per FIPS 205)
- Additional anchoring substrates (Ethereum, federated Certificate Transparency logs)
- Domain-specific extension fields (legal, BFSI, journalism, healthcare, AI agent action)
- Specialized verification procedures (e.g., zero-knowledge inclusion proofs)
- Jurisdictional compliance profiles (EU AI Act Article 50, US federal, APAC)

All profiles **MUST** declare their dependency on LPR v1.0 Core and **MUST** be backward compatible at the verification level: a v1.0 Core verifier presented with a profiled receipt **MUST** be able to verify the Core-level fields and signature even if it cannot interpret the profile-specific extensions.

### 8.5 · LPR v1.0 EU AI Act Article 50 Compliance Profile

**Profile tag:** `"EU-AI-ACT-50-v1"`

Intended for AI-generated content subject to the transparency obligations of Article 50 of Regulation (EU) 2024/1689 (EU AI Act), enforceable from August 2, 2026. Article 50 imposes transparency obligations on providers of AI systems that generate synthetic text, images, audio, or video (Art. 50(2)) and on deployers of AI systems that generate text published for public information purposes (Art. 50(4)); Recital 133 requires provenance metadata to be robust, interoperable, and technically verifiable.

A receipt conforming to this profile **MUST** satisfy all LPR v1.0 Core requirements (§1–§6) and additionally **MUST** include the following fields in the `authorship` object:

```cbor
{
  "authorship": {
    "actor_type": "AI_MODEL",
    "actor_id": <string — see §8.5.1>,
    "actor_assertion": <string — see §8.5.2>,
    "tool_chain": [<tool descriptor — see §8.5.3>],

    "eu_ai_act_50": {
      "profile_version": "EU-AI-ACT-50-v1",
      "ai_system_id": <string — see §8.5.1>,
      "ai_system_version": <string — model version or API version>,
      "deployer_id": <string — see §8.5.4>,
      "deployer_name": <string — human-readable organization name>,
      "deployer_country": <string — ISO 3166-1 alpha-2 country code>,
      "content_category": <string — see §8.5.5>,
      "transparency_marker": "LPR-EU-AI-ACT-50",
      "enforcement_date": "2026-08-02",
      "supervisory_authority": <string, OPTIONAL — named EU supervisory authority, e.g. "BaFin", "CNIL", "ICO">
    }
  }
}
```

#### 8.5.1 · `ai_system_id` format

The `ai_system_id` field **MUST** be a unique string identifying the AI model or system that generated or substantially contributed to the anchored artifact. Acceptable formats, in order of preference:

1. A fully-qualified model identifier using the format `<provider>/<model>/<version>`, e.g.:
   - `openai/gpt-4o/2024-11-20`
   - `anthropic/claude-3-5-sonnet/20241022`
   - `google/gemini-1.5-pro/001`
2. A URL resolving to the AI system's model card, e.g. `https://huggingface.co/meta-llama/Meta-Llama-3-8B`
3. A DID resolving to the AI system's identity document, e.g. `did:web:models.openai.com:gpt-4o`

If the deployer does not have access to the exact model identifier (e.g., when using a third-party API that does not expose version information), the deployer **MUST** use the most specific identifier available and **MUST** note the limitation in `actor_assertion`.

The `actor_id` field (Core) **MUST** be set to the same value as `ai_system_id`.

#### 8.5.2 · `actor_assertion` for Article 50

The `actor_assertion` field **MUST** contain a human-readable declaration conforming to the following template:

```
"This content was generated in whole or in substantial part by the AI system identified in
ai_system_id, deployed by the organization identified in deployer_id, on the date and time
indicated in timestamp_iso. This receipt constitutes a machine-readable transparency marking
as required by Article 50 of Regulation (EU) 2024/1689 (EU Artificial Intelligence Act).
The content hash recorded in artifact.content_hash is the SHA-256 of the canonical form of
the AI-generated artifact as of the moment of issuance. This receipt does not attest to the
accuracy, completeness, or lawfulness of the content."
```

The deployer **MAY** extend this declaration with additional information. The deployer **MUST NOT** remove or contradict any element of the required declaration.

#### 8.5.3 · `tool_chain` requirements

The `tool_chain` array **MUST** include at least one entry identifying the AI system, with the following fields:

```cbor
{
  "name": <string — AI system name, e.g. "GPT-4o">,
  "version": <string — model version>,
  "provider": <string — provider name, e.g. "OpenAI">,
  "api_endpoint": <string, OPTIONAL — the API endpoint used, e.g. "https://api.openai.com/v1/chat/completions">,
  "prompt_hash": <string, OPTIONAL — SHA-256 of the prompt/system prompt, if the deployer chooses to record it>
}
```

Recording `prompt_hash` is **RECOMMENDED** for deployers seeking legal defensibility in high-stakes applications. The prompt hash enables the deployer to later prove the exact instructions given to the AI system, without revealing the prompt content in the on-chain record.

#### 8.5.4 · `deployer_id` format

The `deployer_id` field **MUST** uniquely identify the legal entity that deployed the AI system and caused the content to be generated. Acceptable formats:

1. An EUID (European Unique Identifier) for EU-registered entities, e.g. `EUID:DE:HRB123456`
2. An LEI (Legal Entity Identifier), e.g. `LEI:5493001KJTIIGC8Y1R12`
3. A VAT number for EU entities, e.g. `VAT:DE123456789`
4. A DID, e.g. `did:web:example.com`
5. For non-EU entities: an equivalent national business registration identifier

The `deployer_name` field **MUST** be the legal name of the deploying organization as registered with the relevant authority.

#### 8.5.5 · `content_category` values

The `content_category` field **MUST** be one of the following values, drawn from Article 50's scope:

| Value | Description | Article 50 paragraph |
|---|---|---|
| `"SYNTHETIC_TEXT"` | AI-generated or AI-substantially-modified text | Art. 50(4) |
| `"SYNTHETIC_IMAGE"` | AI-generated or AI-substantially-modified image | Art. 50(2) |
| `"SYNTHETIC_AUDIO"` | AI-generated or AI-substantially-modified audio | Art. 50(2) |
| `"SYNTHETIC_VIDEO"` | AI-generated or AI-substantially-modified video | Art. 50(2) |
| `"DEEPFAKE"` | AI-manipulated content depicting real persons | Art. 50(3) |
| `"SYNTHETIC_MULTIMODAL"` | AI-generated content combining multiple modalities | Art. 50(2) |
| `"AI_ASSISTED_DOCUMENT"` | Document substantially drafted or modified by AI | Art. 50(4) |

#### 8.5.6 · `transparency_marker` field

The `transparency_marker` field **MUST** be set to the string `"LPR-EU-AI-ACT-50"`. This value is a machine-readable marker intended to satisfy the Article 50 requirement for a detectable, machine-readable AI-generated content indicator. The presence of this marker in a valid, Bitcoin-anchored LPR receipt constitutes the transparency marking required by Article 50(2) and Article 50(4).

#### 8.5.7 · Verification procedure for Article 50 receipts

A verifier asserting Article 50 compliance for an LPR receipt **MUST** perform all Core verification steps (§6.1) and additionally:

1. Confirm `authorship.eu_ai_act_50.profile_version == "EU-AI-ACT-50-v1"`.
2. Confirm `authorship.eu_ai_act_50.transparency_marker == "LPR-EU-AI-ACT-50"`.
3. Confirm `authorship.eu_ai_act_50.ai_system_id` is non-empty and conforms to §8.5.1.
4. Confirm `authorship.eu_ai_act_50.deployer_id` is non-empty and conforms to §8.5.4.
5. Confirm `authorship.eu_ai_act_50.content_category` is one of the permitted values in §8.5.5.
6. Confirm the Bitcoin anchor is present and `anchor.anchor_status == "ANCHORED"`.

A receipt that passes all Core checks but fails one or more of these additional checks **MUST** be reported as "Core-valid, EU-AI-ACT-50-non-conformant" and **MUST NOT** be presented as Article 50-compliant provenance.

The LedgerProof Foundation will update this profile within 30 days of the publication of binding technical standards by CEN/CENELEC under the EU AI Act's standardization mandate (Article 40). Profile version `EU-AI-ACT-50-v1` is designed to be superseded by `EU-AI-ACT-50-v2` aligned with those standards once published. This profile does not constitute legal advice; deployers should consult qualified legal counsel regarding their specific Article 50 obligations.

## 9 · Security considerations

### 9.1 · SHA-256 and Ed25519 strength

LPR v1.0 relies on SHA-256 collision resistance and Ed25519 signature security. Both primitives are widely deployed and have no known practical attacks at the time of this specification's publication. Implementers should plan for migration to post-quantum primitives (see §8 and the migration architecture described in the LedgerProof Foundation Founding Whitepaper, §4).

### 9.2 · Signing-key custody

The security of an LPR receipt against authorship spoofing reduces to the secrecy of the signer's Ed25519 private key. Signers handling high-value receipts **SHOULD** consider hardware-backed key storage (HSM, TEE, or hardware security keys).

### 9.3 · Anchor-time misbinding

A malicious signer could attempt to assert a `timestamp_ns` earlier than the actual signing time. This attack is bounded above by the Bitcoin anchor: a receipt **MUST** have been included in a Merkle tree before the Bitcoin block at `anchor.btc_block_height` was mined. Strict verifiers **MUST** reject receipts whose `timestamp_ns` is later than the anchor time.

### 9.4 · Side channels in canonicalization

Implementations **MUST** use constant-time implementations of canonical CBOR encoding and Ed25519 signature verification to avoid timing side-channel attacks against the signing key.

### 9.5 · DOS resistance of the anchor calendar

A Foundation-operated calendar server is a target for denial-of-service. The Foundation operates the calendar on a best-effort basis. Implementers **SHOULD** operate their own calendar for production deployments or pool with multiple calendars for redundancy.

## 10 · Long-Horizon verification

### 10.1 · Procedure

When verifying a receipt carrying `"profile": "LongHorizon-v1"`, a Long-Horizon-capable verifier **MUST** also:

1. Locate the composite or standalone ML-DSA-65 entry in `additional_signatures`.
2. Reconstruct the signed payload (same scope as §3.3 — `signature`, `additional_signatures`, and `anchor` omitted).
3. Verify the ML-DSA-65 signature against the signer's ML-DSA-65 public key.
4. A receipt that passes Core verification but fails ML-DSA-65 verification **MUST** be flagged as "Core-valid, Long-Horizon-failed" and **MUST NOT** be silently accepted for long-horizon purposes.

A Core-only verifier that does not implement ML-DSA-65 **MAY** accept a Long-Horizon receipt as Core-valid, but **MUST** surface a warning that PQC verification was not performed.

---

## 11 · Foundation protocol-continuity commitments

### 11.1 · Re-anchoring service

The LedgerProof Foundation commits to operating a re-anchoring service that, prior to the estimated CRQC threat horizon, will:

1. Accept any previously issued LPR v1.0 Core receipt submitted by its original issuer or by a designated custodian.
2. Issue a new LPR v1.0 Long-Horizon receipt whose `authorship.actor_assertion` attests to the re-anchoring event, and whose `chain.prev_receipt_hash` links to the original receipt.
3. Anchor the resulting chain on Bitcoin and, if available, on at least one additional substrate.
4. Publish the mapping of original `receipt_id` to re-anchored `receipt_id` in a publicly queryable registry.

This service does **NOT** retroactively modify original receipts; it extends the chain. The original receipt's validity is unchanged.

### 11.2 · Protocol-continuity escrow

The LedgerProof Foundation commits to placing the following items in a protocol-continuity escrow arrangement, the terms of which shall be published no later than July 6, 2027:

- The complete LPR v1.0 specification (this document), all reference implementations, and all associated tooling, in perpetual open-source repositories with at least three independent mirrors.
- The Foundation's anchor-worker private key material (in HSM-escrow with two independent custodians) sufficient to verify the authenticity of all receipts anchored under Foundation keys.
- An endowment or insurance instrument sized to fund the Foundation's calendar operation and verifier service for a minimum of twenty-five (25) years, with a target endowment funding one hundred (100) years of operation.

The purpose of this escrow is to ensure that LPR receipts anchored under Foundation infrastructure remain verifiable in perpetuity, independent of the Foundation's continued organizational existence.

### 11.3 · Governance transition

The Foundation intends to transition operational governance of the LPR protocol to a member-owned cooperative utility structure (modeled on DTCC/SWIFT governance) no later than Year 5 of operation (target: 2031). Protocol stewardship of LPR Core will be proposed for transfer to the IETF SCITT working group or a successor body upon the publication of the first IETF RFC incorporating the LPR specification.

---

## 12 · SCITT compatibility

### 12.1 · Relationship to IETF SCITT architecture

The LedgerProof Receipt format is designed to be composable with the IETF Supply Chain Integrity, Transparency, and Trust (SCITT) architecture as described in [draft-ietf-scitt-architecture]. Specifically:

- An LPR v1.0 receipt corresponds to a **SCITT Statement** wrapped in a SCITT-compatible envelope, where the `anchor` constitutes a **SCITT Receipt** (inclusion proof in a transparency log).
- The Foundation-operated calendar server corresponds to a **SCITT Transparency Service**, with Bitcoin OP_RETURN as the underlying append-only log.
- LPR verification (§6 and §10) implements the **SCITT Verification** procedure, with the Bitcoin blockchain as the auditable, append-only, publicly verifiable backing store.

A formal SCITT profile for LPR, `draft-dawkins-scitt-lpr`, is being prepared for submission to the IETF SCITT working group (target submission: Day 5 post-launch). That document will specify the SCITT COSE envelope mapping and SCITT-compliant receipt format for LPR receipts.

### 12.2 · Relationship to VeritasChain VCP

The VeritasChain Verifiable Content Protocol [draft-kamimura-scitt-vcp] defines an overlapping SCITT profile. LPR v1.0 receipts are designed to be composable with VCP: a VCP Statement **MAY** include an LPR receipt as an evidence attachment, and an LPR receipt's `additional_signatures` array **MAY** carry a VCP-format signed statement. The Foundation will seek alignment with the VCP authors to minimize fragmentation.

### 12.3 · Relationship to Microsoft Agent Governance Toolkit

Microsoft's Agent Governance Toolkit (AGT, released April 2, 2026, MIT license) issues Ed25519+JCS receipts for AI agent actions. LPR receipts are compatible with AGT at the signature-algorithm level (Ed25519) and the canonical-form level (JCS via §3.4). An AGT receipt **MAY** be wrapped in an LPR receipt by setting `authorship.actor_type = "AI_MODEL"` and `authorship.tool_chain` to identify the AGT version. This composability is intentional; LPR does not compete with AGT's agent-governance layer.

### 12.4 · Relationship to C2PA

The Coalition for Content Provenance and Authenticity (C2PA) Content Credentials format defines metadata attachment at the file level. LPR receipts are complementary: a C2PA manifest CBOR object **MAY** be the artifact whose `content_hash` is carried in an LPR receipt, enabling Bitcoin-anchored, chain-of-custody verification of a C2PA manifest. The Foundation will publish a reference implementation of this composition pattern at launch.

---

## 13 · IANA / registry considerations

This specification defines the following identifiers that **SHOULD** be registered with the appropriate naming authority once published as an IETF Internet-Draft:

- The OP_RETURN prefix `LPR1` (4 bytes)
- The CBOR tag `TBD` for canonical LPR receipts
- The media type `application/lpr+cbor` and `application/lpr+json` (under RFC 6838)

## 14 · References

### Normative

- [RFC 2119] Bradner, S. *Key words for use in RFCs to Indicate Requirement Levels*. March 1997.
- [RFC 6962] Laurie, B., et al. *Certificate Transparency*. June 2013.
- [RFC 8032] Josefsson, S., Liusvaara, I. *Edwards-Curve Digital Signature Algorithm (EdDSA)*. January 2017.
- [RFC 8174] Leiba, B. *Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words*. May 2017.
- [RFC 8785] Rundgren, A., et al. *JSON Canonicalization Scheme (JCS)*. June 2020.
- [RFC 8949] Bormann, C., Hoffman, P. *Concise Binary Object Representation (CBOR)*. December 2020.
- [RFC 9562] Davis, K., et al. *Universally Unique IDentifiers (UUIDs)*. May 2024.
- [FIPS 180-4] National Institute of Standards and Technology. *Secure Hash Standard*. August 2015.
- [FIPS 203] National Institute of Standards and Technology. *Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM).* August 2024.
- [FIPS 204] National Institute of Standards and Technology. *Module-Lattice-Based Digital Signature Standard (ML-DSA).* August 2024.
- [FIPS 205] National Institute of Standards and Technology. *Stateless Hash-Based Digital Signature Standard (SLH-DSA).* August 2024.

### Informative

- [EU-AIA] Regulation (EU) 2024/1689 — EU Artificial Intelligence Act.
- [EDPB-Blockchain] European Data Protection Board. *Draft Guidelines on processing of personal data on the blockchain.* April 14, 2025.
- [OTS] Todd, P. *OpenTimestamps.* opentimestamps.org. 2016.
- [draft-ietf-scitt-architecture] Birkholz, H., et al. *An Architecture for Trustworthy and Transparent Digital Supply Chains.* IETF SCITT Working Group. Current version: draft-ietf-scitt-architecture-22.
- [draft-ietf-lamps-pq-composite-sigs] Ounsworth, M., et al. *Composite ML-DSA for use in Internet PKI.* IETF LAMPS Working Group. Current version: draft-ietf-lamps-pq-composite-sigs-13.
- [draft-kamimura-scitt-vcp] Kamimura, R., et al. *Verifiable Content Protocol (VCP) SCITT Profile.* IETF SCITT Working Group. Version: draft-kamimura-scitt-vcp-01.
- [CNSA-2.0] National Security Agency. *Commercial National Security Algorithm Suite 2.0 Advisory.* September 2022. Revised 2024.
- [NSM-10] National Security Memorandum 10. *Promoting United States Leadership in Quantum Computing While Mitigating Risks to Vulnerable Cryptographic Systems.* May 4, 2022.
- [LF-2036-ARCH] Dawkins, V. *LedgerProof Foundation 2036 Platform Architecture Brief.* LedgerProof Foundation. July 6, 2026.

— end of specification —

> **FOUNDER ACTION REQUIRED:**
> 1. Technical review by Frank's Riot senior-engineering network OR Peter Todd via warm intro — this spec now carries PQC commitments and SCITT framing that require cryptographer sign-off before IETF submission.
> 2. Compile reference implementations (Python + TypeScript) under MIT against this spec. The SEP-1763 interceptor implementation (`05-sep-1763-impl/`) implements the Core profile; Long-Horizon profile support requires adding ML-DSA-65 signing via `pqcrypto-dilithium` or equivalent.
> 3. Anchor the canonical CBOR of this spec on Bitcoin at publication (Day 27 single-block anchor), alongside the Whitepaper, Manifesto, Foundation Charter, Article 50 readiness statement, and SEP-1763 snapshot.
> 4. Submit IETF -00 draft on Day 5 as `draft-dawkins-scitt-lpr-00` (SCITT profile framing), NOT as a standalone Internet-Draft. See the companion `IETF-00-DRAFT-DAWKINS-LPR-00.txt` for current draft text — that file requires updating to reflect the SCITT profile header and §12 of this specification before submission.
> 5. Day-1 architectural commitments embedded in this revision: (a) `additional_signatures` array for hybrid PQC, (b) `substrate` field on `anchor`, (c) three profiles defined (Core / Long-Horizon / High-Assurance), (d) SCITT compatibility §12, (e) Foundation re-anchoring commitment §11.1, (f) protocol-continuity escrow §11.2. These are non-breaking and backward compatible — all existing verifiers continue to function.
