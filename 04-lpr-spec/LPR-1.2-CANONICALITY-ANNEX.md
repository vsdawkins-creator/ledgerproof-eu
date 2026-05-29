# LPR 1.2 — Canonicality Annex

**Document:** LedgerProof Receipt Specification, version 1.2 (Canonicality Annex)
**Status:** Draft for public review on July 6, 2026 launch; final by Q3 2026
**Editor:** Veronica S. Dawkins, LedgerProof Foundation
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
**Relationship to LPR 1.0/1.1:** Additive annex. All v1.1 receipts MUST verify identically under v1.2 implementations.
**Reference implementations:** MIT License — `github.com/ledgerproof/lpr-{python,typescript,rust}`
**SCITT relationship:** Compatible with [draft-ietf-scitt-architecture]; mechanisms in §3 and §4 are profile-level extensions to the SCITT-compatible base profile defined in LPR 1.0 §12.

> The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when, and only when, they appear in all capitals.

---

## 1 · Abstract

LPR 1.0 binds AI-generated and human-authored content to a permanent, machine-verifiable receipt anchored to the Bitcoin blockchain. LPR 1.1 added the EU AI Act Article 50 profile (`EU-AI-ACT-50-v1.1`) and GDPR Article 17 erasure semantics.

This annex (LPR 1.2) adds four mechanisms that allow verifiers to establish which of several receipts referencing similar content is **canonical** — that is, which version is the original, authoritative version asserted by the verifiable real-world author. The four mechanisms operate at increasing levels of evidence strength:

1. **Lineage chains** (§3) — receipts that explicitly reference prior versions, forming a Merkle DAG of authorized edits.
2. **Multi-modal similarity hashing** (§4) — receipts include locality-sensitive hashes (text, image, audio, video, code) so that near-duplicate content is detectable even when byte-level hashes differ.
3. **Witness attestation** (§5) — third parties may counter-sign receipts after issuance; the attestation graph itself is anchored.
4. **Canonical Registry with arbitration** (§6) — for disputes that cannot be resolved by mechanisms 1–3, the LedgerProof Foundation operates a threshold-signed dispute resolution process whose outcomes are themselves anchored receipts.

This annex specifies the wire format, validation rules, and verifier behavior for all four mechanisms. It also specifies the backward-compatibility contract that LPR 1.2 implementations MUST honor for receipts issued under LPR 1.0 and 1.1.

---

## 2 · Scope and non-goals

### 2.1 In scope

- Canonical CBOR encoding of new entry fields.
- Validation rules for lineage chains, similarity hashes, attestations, and canonical claims.
- Verifier API enhancements.
- Backward-compatibility requirements.
- Cryptographic specifications for FROST threshold signatures used in Foundation resolutions.

### 2.2 Out of scope (deferred to future versions)

- **Branching lineage chains** (DAG with multiple parents). LPR 1.2 chains are linear. Branching and merging is deferred to LPR 1.3.
- **Cross-protocol bridges** (C2PA assertion mapping for canonicality). The C2PA assertion `org.ledgerproof.receipt.v1` is updated in a separate document.
- **Privacy-preserving receipts** (zero-knowledge proofs of canonicality without revealing content). Deferred to LPR 2.0.
- **Post-quantum signature migration**. Specified separately in LPR 2.0 Post-Quantum Annex.

---

## 3 · Mechanism 3: Lineage chains

### 3.1 Wire format

The `LprEntry` structure defined in LPR 1.0 §4 is extended with four OPTIONAL fields. When ANY of these four fields is present, ALL of them MUST be present:

```cbor
LprEntry-v1.2 = LprEntry-v1.1 .and {
    ? previous_receipt_id : tstr      ; UUID v7 in canonical string form
    ? chain_root_id       : tstr      ; UUID v7 of the first receipt in this chain
    ? lineage_position    : uint      ; 1 for chain root; n+1 for the n-th revision
    ? supersedes          : bool      ; true (default) → predecessor deprecated;
                                       ; false → coexists as a parallel version
}
```

All four fields contribute to the canonical byte representation as defined in LPR 1.0 §5. When a field is absent, it MUST NOT appear in the canonical output. Canonical key ordering is preserved.

### 3.2 Chain root semantics

A receipt whose `previous_receipt_id` is absent is a **chain root**. Its implicit `chain_root_id` equals its own `receipt_id`, and its implicit `lineage_position` equals 1. These implicit values MUST NOT be serialized into the canonical output of the entry.

A chain root receipt MAY later be referenced by successor receipts, at which point the chain becomes explicit.

### 3.3 Successor validation rules

When a calendar operator receives an entry submission that includes `previous_receipt_id`, the operator MUST perform the following validation BEFORE issuing the receipt:

1. **Predecessor existence.** The receipt identified by `previous_receipt_id` MUST exist in the operator's database OR be retrievable from any LPR-compatible federation peer.
2. **Predecessor anchor status.** The predecessor's anchor status MUST be at least `ANCHORED` (i.e., included in a Bitcoin transaction broadcast to the network). It is NOT REQUIRED to be `CONFIRMED`.
3. **Issuer identity.** The submitter's `issuer_did` MUST equal the predecessor's `issuer_did`, OR a valid `identity_delegation` entry MUST exist authorizing the submitter to extend the predecessor's chain. See §3.5 for delegations.
4. **Lineage position arithmetic.** `lineage_position` MUST equal `predecessor.lineage_position + 1`.
5. **Chain root consistency.** `chain_root_id` MUST equal `predecessor.chain_root_id` if the predecessor is itself a successor, OR `predecessor.receipt_id` if the predecessor is a chain root.
6. **Linearity.** No other receipt MAY reference the same `previous_receipt_id`. Operators MUST reject submissions that would create a branch. (See §2.2 — branching is deferred to LPR 1.3.)

A failure of any rule MUST cause the operator to return HTTP 422 with the error code from §3.7.

### 3.4 Temporal validation

Receipt B claims to be a successor of Receipt A. By Bitcoin's totally-ordered block sequence, A's anchor MUST occur in a strictly earlier block than B's anchor. The operator MAY accept B's submission while A is still `PENDING`, but the resulting receipts MUST NOT both anchor in the same Bitcoin block.

If two successors would otherwise be eligible for the same anchor block, the operator MUST defer B to the next anchor cycle to preserve temporal ordering.

### 3.5 Identity delegation

An issuer MAY delegate the authority to extend their chain to another DID via an `IdentityDelegation` entry:

```cbor
IdentityDelegation = {
    "delegation_id"     : tstr       ; UUID v7
    "delegator_did"     : tstr
    "delegate_did"      : tstr
    "scope"             : {
        "chain_root_id" : tstr       ; the chain being delegated
        "expires_at"    : tstr       ; ISO 8601; MUST be in the future
        ? "supersession_allowed" : bool ; default false — delegate may extend
                                          ; but not deprecate predecessor
    }
    "signature"         : tstr       ; Ed25519 over canonical payload, by delegator
    "issued_at"         : tstr
}
```

`IdentityDelegation` entries are themselves anchored as ordinary LPR entries with `kind = "identity_delegation/v1"`.

### 3.6 Walking a chain

The verifier API provides three endpoints for chain traversal:

| Method | Path | Behavior |
|---|---|---|
| GET | `/v1/chains/{receipt_id}/history` | Returns the ordered list of receipts from the chain root to the receipt identified by `receipt_id`, inclusive. |
| GET | `/v1/chains/{chain_root_id}/forward` | Returns all successors of the chain root in lineage order. |
| GET | `/v1/chains/{chain_root_id}/canonical` | Returns the current canonical head — the highest-`lineage_position` non-superseded successor signed by the original issuer or an authorized delegate. |

All chain-walk responses MUST include each receipt's anchor status and identity verification status.

### 3.7 Error codes (mechanism 3)

| Code | Meaning |
|---|---|
| `LPR1200_PREDECESSOR_NOT_FOUND` | `previous_receipt_id` references an unknown receipt. |
| `LPR1201_PREDECESSOR_NOT_ANCHORED` | Predecessor's anchor status is `PENDING_OPERATOR`. |
| `LPR1202_UNAUTHORIZED_SUCCESSION` | Issuer DID does not match and no delegation exists. |
| `LPR1203_INVALID_LINEAGE_POSITION` | Position not equal to predecessor's + 1. |
| `LPR1204_INVALID_CHAIN_ROOT` | Chain root inconsistent with predecessor. |
| `LPR1205_BRANCH_NOT_ALLOWED` | Another receipt already references this predecessor (linearity violation). |
| `LPR1206_DELEGATION_EXPIRED` | Delegation exists but `expires_at` is in the past. |
| `LPR1207_TEMPORAL_ORDERING_VIOLATION` | Successor would anchor in a non-later block than predecessor. |

---

## 4 · Mechanism 4: Multi-modal similarity hashing

### 4.1 Wire format

The `LprEntry` structure is extended with an OPTIONAL `similarity_hashes` map:

```cbor
LprEntry-v1.2 = LprEntry-v1.2 .and {
    ? similarity_hashes : {
        ? "tlsh-1"     : tstr         ; TLSH-3.x output, 70 hex characters
        ? "ssdeep-1"   : tstr         ; ssdeep CTPH output
        ? "phash-1"    : tstr         ; 64-bit pHash, 16 hex characters
        ? "audio-fp-1" : tstr         ; Chromaprint output, base32 encoded
        ? "video-kf-1" : [tstr]       ; array of pHashes, one per keyframe
        ? "code-ast-1" : tstr         ; SHA-256 of canonicalized AST, 64 hex
    }
}
```

When `similarity_hashes` is present, its keys MUST be a subset of the algorithm identifiers registered in the LPR Similarity Algorithm Registry (§4.6). New algorithms MAY be added without a spec revision by registering them.

### 4.2 Algorithm selection

The submitting SDK SHOULD compute similarity hashes based on the entry's `content_type`:

| Content type pattern | Algorithms to compute |
|---|---|
| `text/*`, `application/json`, `application/xml` | `tlsh-1`, `ssdeep-1` |
| `image/*` | `phash-1` |
| `audio/*` | `audio-fp-1` |
| `video/*` | `video-kf-1` + `phash-1` of cover frame |
| `application/x-{lang}` (code) | `code-ast-1` for supported languages |
| All other types | none required |

SDKs MUST be able to compute these hashes without network calls. Implementations MAY defer to server-side computation for content types they do not support, in which case the submission omits `similarity_hashes` and the operator populates them at indexing time.

### 4.3 TLSH specification

LPR 1.2 uses TLSH v3.x as specified in [trendmicro/tlsh]. The output is a 70-character hexadecimal string. Two TLSH hashes are compared via the TLSH `diff` function, which returns an integer distance. Distances below 30 indicate likely-identical content; distances below 100 indicate substantial similarity.

The recommended threshold for "near-duplicate" warning in verifier UIs is **distance ≤ 30**, with the displayed similarity percentage computed as `max(0, 100 - distance) / 100`.

### 4.4 Similarity search API

```
POST /v1/similarity/search
Content-Type: application/json

{
  "content_type": "text/plain",
  "similarity_hash": {
    "type": "tlsh-1",
    "value": "T1...."
  },
  "threshold": 30,           // optional; default 30
  "limit": 5                 // optional; default 5, max 100
}
```

Response:

```json
{
  "hits": [
    {
      "receipt_id": "018f...",
      "distance": 12,
      "similarity": 0.88,
      "issuer_did": "did:web:example.com",
      "issued_at": "2026-05-20T14:23:00Z",
      "anchor_status": "CONFIRMED"
    }
  ],
  "search_method": "brute_force"   // future values: "hnsw", "lsh", ...
}
```

### 4.5 Verifier integration

When a verifier resolves a receipt that has `similarity_hashes` set, the verifier MUST attempt a similarity search against the operator's index and SHOULD include up to 5 nearest hits in the verification response. The verifier UI MUST surface the following determinations:

| Result | UI rendering |
|---|---|
| No hits within threshold | No warning. |
| Hit with same `issuer_did` | Informational badge: "Earlier version exists." |
| Hit with different `issuer_did`, earlier anchor | **Warning badge**: "Possible derivative or unauthorized modification — original by [issuer] at [timestamp]." |
| Hit with different `issuer_did`, later anchor | **Informational badge**: "Similar content later anchored by [issuer]." |

### 4.6 Similarity Algorithm Registry

The LedgerProof Foundation maintains a registry at `https://spec.ledgerproofhq.io/registry/similarity` documenting each registered algorithm's identifier, parameters, reference implementation, and acceptable distance thresholds. The registry is itself versioned and signed by the Foundation.

To register a new algorithm:
1. Submit a registration request to the Foundation Technical Steering Committee.
2. Provide an interoperable reference implementation in at least two languages.
3. Provide a test vector suite of at least 100 (hash, content) pairs.
4. Submit through the standard pull-request process at `github.com/ledgerproof/similarity-registry`.

### 4.7 Error codes (mechanism 4)

| Code | Meaning |
|---|---|
| `LPR1210_UNKNOWN_SIMILARITY_ALGORITHM` | Algorithm not in registry. |
| `LPR1211_MALFORMED_SIMILARITY_HASH` | Hash bytes do not match the algorithm's format. |
| `LPR1212_SIMILARITY_INDEX_UNAVAILABLE` | Operator's similarity index is temporarily offline. Verifier MUST return a `503` and the receipt SHOULD still verify on content hash alone. |

---

## 5 · Mechanism 5: Witness attestation

### 5.1 Wire format

An **attestation** is a separate entry kind that references an existing receipt:

```cbor
Attestation-v1 = {
    "kind"              : "attestation/v1"
    "attestation_id"    : tstr                ; UUID v7
    "target_receipt_id" : tstr
    "target_entry_hash" : tstr                ; SHA-256 of target's canonical
                                              ; entry, 64 hex characters
    "attestor_did"      : tstr
    "attestation_type"  : tstr                ; see §5.2 for registered values
    ? "statement"       : tstr                ; max 4096 UTF-8 bytes
    "issued_at"         : tstr                ; ISO 8601
    "signature"         : tstr                ; Ed25519 over canonical
                                              ; payload, by attestor_did
}
```

Attestations are anchored alongside fresh entries in the same Merkle tree (LPR 1.0 §6). The leaf hash function is identical: SHA-256 over canonical bytes with the domain-separated leaf prefix `0x00`.

### 5.2 Registered attestation types

LPR 1.2 defines six attestation types. Additional types MAY be registered via the same process as the Similarity Algorithm Registry (§4.6).

| Type | Semantic |
|---|---|
| `co-sign` | Attestor co-authored or co-approved the original content. |
| `witness` | Attestor observed the content at the claimed time but does not claim authorship. |
| `notary` | Attestor is an authorized notary public asserting the document's authenticity. |
| `regulator` | Attestor is an accredited regulator acknowledging compliance review. |
| `publisher` | Attestor is the editorial publisher (newsroom, journal, broadcaster). |
| `received` | Attestor acknowledges receipt of the content (legal service of process). |

### 5.3 Attestation validation

When an operator receives an attestation submission, the operator MUST:

1. Verify that the `target_receipt_id` exists and its `target_entry_hash` matches the SHA-256 of the target's current canonical entry. (If the target has been modified by a soft-delete per LPR 1.0 §11, the attestation MUST be rejected with `LPR1221_TARGET_MODIFIED`.)
2. Verify the attestor's signature against the canonical payload using the public key resolved from `attestor_did`.
3. Reject duplicate attestations: at most one attestation of a given `(target_receipt_id, attestor_did, attestation_type)` triple MAY exist. Subsequent submissions return `LPR1222_DUPLICATE_ATTESTATION`.

### 5.4 Attestation revocation

Attestations MAY be revoked by their original attestor by submitting a `attestation_revocation/v1` entry:

```cbor
AttestationRevocation-v1 = {
    "kind"                : "attestation_revocation/v1"
    "revocation_id"       : tstr
    "target_attestation_id" : tstr
    "revoker_did"         : tstr             ; MUST equal original attestor_did
    "rationale"           : tstr             ; max 2048 UTF-8 bytes
    "issued_at"           : tstr
    "signature"           : tstr
}
```

A revoked attestation is not deleted — both the attestation and the revocation remain anchored. Verifiers MUST render revoked attestations with appropriate UI distinction (e.g., strikethrough) and MUST NOT count them toward trust-score calculations.

### 5.5 Attestation API endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/attestations` | Submit a new attestation. |
| GET | `/v1/receipts/{id}/attestations` | List active attestations on a receipt. |
| GET | `/v1/receipts/{id}/attestations/all` | List active and revoked attestations. |
| POST | `/v1/attestations/{id}/revoke` | Submit a revocation. |

### 5.6 Error codes (mechanism 5)

| Code | Meaning |
|---|---|
| `LPR1220_TARGET_NOT_FOUND` | `target_receipt_id` references an unknown receipt. |
| `LPR1221_TARGET_MODIFIED` | `target_entry_hash` does not match the current canonical entry. |
| `LPR1222_DUPLICATE_ATTESTATION` | An attestation with the same triple already exists. |
| `LPR1223_INVALID_ATTESTOR_SIGNATURE` | Signature verification failed. |
| `LPR1224_UNKNOWN_ATTESTATION_TYPE` | Type not in the registered list. |
| `LPR1225_REVOCATION_BY_NON_AUTHOR` | Revocation `revoker_did` does not match original attestor. |

---

## 6 · Layer 3: Canonical Registry and Foundation Arbitration

### 6.1 Overview

For the rare case where mechanisms 3–5 leave genuine ambiguity about which receipt is canonical, the LedgerProof Foundation operates a threshold-signed dispute resolution process. The Foundation's resolutions are themselves anchored as ordinary LPR entries, are publicly auditable, and are counter-signable by Foundation members.

### 6.2 Canonical Claim entry

An issuer asserts canonicality for a receipt they own:

```cbor
CanonicalClaim-v1 = {
    "kind"        : "canonical_claim/v1"
    "claim_id"    : tstr
    "receipt_id"  : tstr                     ; the receipt being claimed canonical
    "claimant_did" : tstr                    ; MUST equal receipt's issuer_did
    "statement"   : tstr                     ; max 4096 UTF-8 bytes
    "evidence"    : [tstr]                   ; optional: array of supporting
                                              ; receipt_ids (lineage chain,
                                              ; attestations, similarity matches)
    "issued_at"   : tstr
    "signature"   : tstr
}
```

The claim becomes effective immediately. If no dispute is submitted within 30 days of anchoring, the claim is considered **uncontested** and the receipt's canonical status is `canonical_uncontested`.

### 6.3 Canonical Dispute entry

A different issuer may dispute an existing claim:

```cbor
CanonicalDispute-v1 = {
    "kind"               : "canonical_dispute/v1"
    "dispute_id"         : tstr
    "target_claim_id"    : tstr
    "disputant_did"      : tstr
    "competing_receipt_id" : tstr            ; the receipt the disputant
                                              ; asserts is actually canonical
    "rationale"          : tstr              ; max 8192 UTF-8 bytes
    "evidence"           : [tstr]            ; array of supporting receipt_ids
    "issued_at"          : tstr
    "signature"          : tstr
}
```

A dispute MUST be submitted within 30 days of the original claim's anchor. Submissions after 30 days are rejected with `LPR1232_DISPUTE_WINDOW_EXPIRED`.

A dispute transitions the original claim's status to `disputed` and opens a 30-day arbitration window during which the Foundation Arbitration Panel collects evidence and produces a resolution.

### 6.4 Foundation Arbitration Resolution

The Foundation Arbitration Panel is composed of N Foundation board members or designated delegates. Resolutions require a threshold of T out of N partial signatures combined via FROST [draft-irtf-cfrg-frost]. The default threshold is **3-of-5**, configurable in Foundation bylaws.

```cbor
ArbitrationResolution-v1 = {
    "kind"             : "arbitration_resolution/v1"
    "resolution_id"    : tstr
    "dispute_id"       : tstr
    "outcome"          : tstr                ; see §6.5
    "canonical_receipt_id" : tstr            ; the receipt deemed canonical
    "rationale"        : tstr                ; max 16384 UTF-8 bytes;
                                              ; published rationale
    "panel_did"        : tstr                ; the Foundation panel's DID
    "frost_signature"  : tstr                ; aggregated FROST-Ed25519
                                              ; signature over canonical payload
    "panel_member_count" : uint              ; number of partial signatures
                                              ; aggregated (MUST ≥ threshold)
    "issued_at"        : tstr
}
```

The resolution is itself anchored as a normal LPR entry. Its canonical bytes include the aggregated FROST signature but not the individual partial signatures; partial signatures are retained by the Foundation as audit evidence and MAY be disclosed under the Foundation's transparency policy.

### 6.5 Resolution outcomes

| Outcome | Semantic |
|---|---|
| `canonical_upheld` | Original claim stands; the disputant's competing receipt is NOT canonical. |
| `canonical_overturned` | Disputant's competing receipt is canonical; original claim is reversed. |
| `no_clear_canonical` | Panel found insufficient evidence; neither is declared canonical; both render with neutral status. |
| `withdrawn` | Both parties jointly withdrew the dispute; reverts to pre-dispute state. |

### 6.6 Arbitration timeline

| Day | Event |
|---|---|
| 0 | Canonical claim anchored. |
| 0–30 | Dispute window open. |
| Day of dispute submission | Status → `disputed`; arbitration window opens. |
| +30 from dispute | Panel resolution due. If not issued: status → `no_clear_canonical` by default. |
| +14 from resolution | Resolution itself counter-signable by Foundation members; counter-signatures anchored. |

### 6.7 FROST threshold signature specification

LPR 1.2 specifies **FROST-Ed25519** [draft-irtf-cfrg-frost] for Foundation Arbitration Panel signatures. Parameters:

- Curve: edwards25519
- Hash: SHA-512
- Threshold: T (default 3); total participants: N (default 5)
- Identifier: `frost-ed25519-sha512`
- Aggregation: as specified in FROST §5
- Verification: the aggregated signature verifies against a single Ed25519 public key (the Foundation Arbitration Panel public key), making FROST signatures indistinguishable from ordinary Ed25519 signatures to downstream verifiers

### 6.8 Canonical Registry API

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/canonical/claim` | Submit a canonical claim. |
| POST | `/v1/canonical/dispute/{claim_id}` | Submit a dispute. |
| POST | `/v1/canonical/resolve/{dispute_id}` | Submit an arbitration resolution. Authorized: Foundation Arbitration Panel only. |
| GET | `/v1/canonical/{receipt_id}` | Current canonical status. |
| GET | `/v1/canonical/disputes/open` | List of open disputes for panel review. |

### 6.9 Error codes (Layer 3)

| Code | Meaning |
|---|---|
| `LPR1230_NOT_OWNER` | Claimant DID does not match receipt issuer. |
| `LPR1231_DUPLICATE_CLAIM` | Canonical claim already exists for this receipt. |
| `LPR1232_DISPUTE_WINDOW_EXPIRED` | Dispute submitted more than 30 days after claim anchor. |
| `LPR1233_FROST_SIGNATURE_INVALID` | Aggregated signature fails Ed25519 verification. |
| `LPR1234_FROST_THRESHOLD_NOT_MET` | `panel_member_count < threshold`. |
| `LPR1235_RESOLUTION_BY_NON_PANEL` | Resolution submitted by non-authorized DID. |
| `LPR1236_DISPUTE_NOT_OPEN` | Dispute is already resolved or withdrawn. |

---

## 7 · Cross-mechanism considerations

### 7.1 Determining the canonical receipt — precedence order

When a verifier must determine the canonical receipt for a piece of content, the following precedence order applies (highest precedence first):

1. **Foundation Arbitration Resolution** (`canonical_upheld` or `canonical_overturned`) — overrides all other signals.
2. **Uncontested canonical claim** (§6.2 with no dispute after 30 days) — overrides chain and attestation signals.
3. **Lineage chain head** (§3.6 `/v1/chains/{root}/canonical`) — overrides earlier orphan receipts.
4. **Attestation graph weight** (§5) — receipts with more attestations of types `notary`, `regulator`, or `publisher` rank higher than receipts with only `co-sign` or zero attestations.
5. **First anchor wins** (LPR 1.0 §6) — Bitcoin block height ordering.

Verifiers MUST display the precedence reason alongside the canonical determination so users understand *why* a particular receipt was selected.

### 7.2 Soft-delete interactions (GDPR Article 17)

When a receipt's content is soft-deleted per LPR 1.0 §11:

- Lineage chains remain intact (chain references are by receipt_id, not content).
- Similarity hashes remain in the index but the verifier UI MUST mark them as "linked to erased content."
- Existing attestations remain valid but the verifier UI MUST note "attestation targets erased content."
- Canonical claims remain in force but the verifier UI MUST display "canonical claim for erased content."

### 7.3 Operator federation

When a receipt is created at Operator A and later attested at Operator B, the attestation MUST reference the receipt by `receipt_id` and `target_entry_hash`. Operator B MUST be able to resolve the receipt via the federation discovery protocol defined in LPR 1.0 §13.

Similarity searches MAY be scoped to a single operator (faster) or to the federation as a whole (more complete). Verifier UIs SHOULD indicate the scope of the similarity search performed.

---

## 8 · Security considerations

### 8.1 Identity binding strength

The strength of canonicality determination is fundamentally bounded by the strength of identity binding. A receipt signed by a self-asserted `did:web` is weaker evidence than a receipt signed by an eIDAS-qualified electronic seal. Verifier UIs MUST display the identity verification level prominently:

- ⚪ Self-asserted (no verification)
- 🟡 Domain-controlled (did:web with valid TLS)
- 🟢 Cryptographically rooted (did:key, did:btcr)
- 🔵 Qualified electronic signature (eIDAS-equivalent)
- ⬛ Government identity (national ID, OIDC bridge)

### 8.2 Replay attacks against lineage

An attacker who copies content from a chain root and submits a new chain root with the same content but different identity creates a competing chain. Mechanism 4 (similarity hashing) detects this; the verifier surfaces both chains with their respective identity levels, allowing the user to determine which to trust.

### 8.3 Foundation capture

The Canonical Registry's effectiveness depends on the Foundation Arbitration Panel being independent and not capturable. Mitigations:

- Multi-jurisdiction Foundation structure (US 501(c)(3) + Swiss Verein + Singapore non-profit).
- Charter restrictions on board composition (no single entity controls more than one seat).
- FROST threshold signing — no single panel member can produce a resolution.
- Full publication of resolution rationale.
- Public counter-signature window (§6.6 day +14).

### 8.4 Threshold parameter selection

The default 3-of-5 threshold balances availability against capture resistance. Foundations may configure higher thresholds (5-of-7, 7-of-9) for higher-stakes deployments. The threshold MUST be published in the Foundation's bylaws and MUST NOT be changed retroactively for already-issued resolutions.

### 8.5 Quantum considerations

All mechanisms in this annex use Ed25519 signatures. A future post-quantum migration (LPR 2.0 PQ Annex) MUST preserve the canonicality determinations made under LPR 1.2 by either:

- Re-anchoring resolution receipts with hybrid Ed25519 + Dilithium signatures; or
- Maintaining a Foundation-anchored attestation that the LPR 1.2 resolution is valid under both classical and post-quantum assumptions.

The PQ Annex specifies the exact migration procedure.

---

## 9 · Backward compatibility

### 9.1 v1.0 and v1.1 receipt verification

A receipt issued under LPR 1.0 or 1.1 MUST verify identically under LPR 1.2. Specifically:

- New fields (`previous_receipt_id`, `chain_root_id`, `lineage_position`, `supersedes`, `similarity_hashes`) when absent MUST NOT appear in the canonical byte representation.
- The canonical JSON output for a v1.0/1.1 receipt under v1.2 code MUST be byte-identical to the same receipt under v1.0/1.1 code.
- This requirement is enforced by a frozen regression corpus of at least 1,000 v1.0/1.1 receipts replayed through v1.2 verifier code in continuous integration. Byte-mismatch on any receipt MUST fail the build.

### 9.2 v1.2 receipt verification by v1.0/1.1 implementations

A v1.0 or v1.1 verifier MAY encounter receipts with v1.2 fields. v1.0/1.1 verifiers MUST:

- Ignore unknown fields (`previous_receipt_id`, `chain_root_id`, `lineage_position`, `supersedes`, `similarity_hashes`) without erroring.
- Successfully verify the content hash, anchor proof, and signature.
- Optionally surface "v1.2 canonicality data present but not interpreted by this verifier" to users.

### 9.3 Migration path

Operators MAY upgrade from v1.1 to v1.2 without re-anchoring existing receipts. The migration consists solely of:

1. Database schema migration (`0042_canonicality.sql` adding nullable columns and new tables).
2. SDK upgrade (clients may opt into v1.2 features at their own pace).
3. Verifier UI upgrade (rendering the new canonicality signals).

No data backfill is required. Receipts issued before the migration date have NULL values in the new columns, which the verifier renders as "canonicality data not provided."

---

## 10 · Test vectors

Reference test vectors for each mechanism are published at:

- Lineage chains: `github.com/ledgerproof/lpr-test-vectors/v1.2/lineage/`
- Similarity hashing: `github.com/ledgerproof/lpr-test-vectors/v1.2/similarity/`
- Attestations: `github.com/ledgerproof/lpr-test-vectors/v1.2/attestation/`
- Canonical Registry: `github.com/ledgerproof/lpr-test-vectors/v1.2/canonical/`

Each test vector includes:
- Input: canonical entry bytes
- Expected output: SHA-256 hash, Ed25519 signature (using a known test key), and full verifier response.

All compliant implementations MUST pass all published test vectors.

---

## 11 · IANA / registry considerations

This annex defines the following registries to be maintained by the LedgerProof Foundation:

1. **Similarity Algorithm Registry** (§4.6) — at `https://spec.ledgerproofhq.io/registry/similarity`
2. **Attestation Type Registry** (§5.2) — at `https://spec.ledgerproofhq.io/registry/attestation-types`
3. **Resolution Outcome Registry** (§6.5) — at `https://spec.ledgerproofhq.io/registry/resolution-outcomes`

Registry changes require Foundation Technical Steering Committee approval and a 30-day public comment period.

---

## 12 · References

### 12.1 Normative

- [RFC 2119] Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997.
- [RFC 8174] Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words", BCP 14, RFC 8174, May 2017.
- [LPR-1.0] Dawkins, V. S., "LedgerProof Receipt Specification, version 1.0", LedgerProof Foundation, March 2026.
- [LPR-1.1] Dawkins, V. S., "LedgerProof Receipt Specification, version 1.1 — EU AI Act Article 50 Profile", LedgerProof Foundation, May 2026.
- [draft-irtf-cfrg-frost] Connolly, D., et al., "Two-Round Threshold Schnorr Signatures with FROST", IRTF, 2024.
- [trendmicro/tlsh] Oliver, J., Cheng, C., and Y. Chen, "TLSH — A Locality Sensitive Hash", 4th Cybercrime and Trustworthy Computing Workshop, 2013.

### 12.2 Informative

- [C2PA] Coalition for Content Provenance and Authenticity, "C2PA Technical Specification 1.4", 2024.
- [draft-ietf-scitt-architecture] Birkholz, H., et al., "An Architecture for Trustworthy and Transparent Digital Supply Chains", IETF SCITT WG.
- [W3C-DID] W3C, "Decentralized Identifiers (DIDs) v1.0", 2022.
- [W3C-VC] W3C, "Verifiable Credentials Data Model v2.0", 2024.

---

## 13 · Authors and acknowledgements

**Editor:** Veronica S. Dawkins, LedgerProof Foundation, <spec@ledgerproofhq.io>

**Acknowledgements:** This annex was developed under review by [TBD external cryptographer], [TBD external counsel for the arbitration framework], and the LedgerProof Foundation Technical Steering Committee.

---

*End of LPR 1.2 Canonicality Annex.*
*This document supersedes no prior text in LPR 1.0 or 1.1. It is purely additive.*
