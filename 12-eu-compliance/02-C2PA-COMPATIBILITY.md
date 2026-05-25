# LedgerProof + C2PA — Compatibility and Composition Guide

**Version:** 1.0 Draft
**Date:** May 2026
**Author:** LedgerProof Foundation

---

## Summary

This document describes how LedgerProof Receipt (LPR) v1.0 and the Coalition for Content Provenance and Authenticity (C2PA) Content Credentials standard are complementary, non-competing, and composable. It defines the recommended integration pattern for organizations using both standards and explains what each provides that the other does not.

**Bottom line:** C2PA provides rich structured metadata about how content was created. LPR provides an immutable Bitcoin-anchored timestamp and tamper-evidence proof that the C2PA manifest itself has not been altered since creation. Together they are stronger than either alone.

---

## 1 · What C2PA provides

C2PA (c2pa.org, backed by Adobe, BBC, Google, Microsoft, Sony, and others) defines a standard for embedding provenance metadata into media files. A C2PA manifest:

- Records the creation and editing history of a media asset
- Identifies the software, AI model, or human that created or modified the content
- Supports cryptographic signing by the content creator
- Can be embedded in JPEG, PNG, video, audio, and document files

**What C2PA does NOT provide:**

- Immutable external anchoring. A C2PA manifest is embedded in the file — if the file is modified, the manifest is invalidated. But there is no external record that the manifest existed at a specific point in time, independent of the file.
- Resistance to stripping. Social media platforms, CDNs, and document processors routinely strip C2PA manifests during upload or processing. Studies by the Coalition itself document manifest stripping rates above 95% on major platforms.
- Long-horizon verifiability. C2PA relies on PKI certificate chains. If a signing certificate expires or is revoked, verifying a historical C2PA manifest requires trusting certificate archival infrastructure operated by private parties.
- Regulatory chain of custody. A C2PA manifest establishes what created the content, but not a legally defensible chain of custody proving the content was in a specific state at a specific moment that cannot be contested.

---

## 2 · What LPR provides

An LPR v1.0 receipt:

- Provides a Bitcoin-anchored, tamper-evident timestamp proving a specific artifact existed in a specific state at a specific moment
- Persists independently of the artifact — the receipt survives even if the original file is deleted, modified, or its C2PA manifest stripped
- Requires no trusted third party for verification — any Bitcoin node and the verifier API are sufficient
- Is designed for long-horizon verifiability (100+ years) via the post-quantum migration path in LPR Long-Horizon profile

**What LPR does NOT provide (that C2PA does):**

- Rich structured metadata embedded in the file format
- Editing history and provenance chain of individual modifications
- Native file-format embedding (JPEG, MP4, etc.)
- Integration with camera and capture devices at point of creation

---

## 3 · The composition pattern

**Pattern: Anchor a C2PA manifest hash in an LPR receipt**

```
┌─────────────────────────────────────┐
│           ORIGINAL ASSET            │
│   (JPEG / PDF / audio / document)   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│           C2PA MANIFEST             │  rich metadata: who created it,
│   (embedded in or attached to file) │  what tools, what AI model,
│   Signed by creator's certificate   │  editing history
└──────────────┬──────────────────────┘
               │  SHA-256 hash of the
               │  canonical C2PA manifest
               ▼
┌─────────────────────────────────────┐
│           LPR v1.0 RECEIPT          │  artifact.content_hash = SHA-256
│   artifact.content_type =           │  of the C2PA manifest CBOR
│   "application/c2pa+cbor"           │
│   Bitcoin-anchored timestamp        │  proves the C2PA manifest existed
│   Ed25519 signature by deployer     │  in this exact state at this time,
│   Chain of custody preserved        │  regardless of what happened to
└──────────────┬──────────────────────┘  the original file
               │
               ▼
     ┌─────────────────────┐
     │   BITCOIN MAINNET   │  permanent, publicly verifiable,
     │   OP_RETURN ANCHOR  │  requires no trusted third party
     └─────────────────────┘
```

In this pattern:
1. The content creator produces the asset and attaches a C2PA manifest in the normal way
2. The deployer (or the creator) calls `POST /receipts` at `api.ledgerproofhq.io` with `content_type: "application/c2pa+cbor"` and the SHA-256 hash of the C2PA manifest's canonical CBOR encoding
3. The returned LPR receipt is stored alongside the original asset
4. If the C2PA manifest is later stripped from the file, the LPR receipt independently proves what the C2PA manifest contained at the time of anchoring

---

## 4 · Technical implementation

### 4.1 · Computing the C2PA manifest hash

The canonical form of a C2PA manifest for LPR anchoring is the manifest's CBOR encoding as defined in C2PA specification §15 (JUMBF box). The SHA-256 is computed over the raw bytes of the manifest JUMBF box, excluding any embedded binary content payloads that are separately addressable (thumbnails, referenced assets). The `content_type` field in the LPR receipt MUST be set to `"application/c2pa+cbor"`.

```python
import hashlib

def c2pa_manifest_hash(manifest_jumbf_bytes: bytes) -> str:
    """Compute the SHA-256 hash of a C2PA manifest JUMBF box for LPR anchoring."""
    return hashlib.sha256(manifest_jumbf_bytes).hexdigest()
```

### 4.2 · API call

```http
POST https://api.ledgerproofhq.io/receipts
Content-Type: application/json
Authorization: Bearer <API_KEY>

{
  "content_hash": "<sha256 hex of C2PA manifest>",
  "content_type": "application/c2pa+cbor",
  "content_bytes": 4821,
  "actor_type": "AI_MODEL",
  "actor_id": "openai/gpt-4o/2024-11-20",
  "actor_assertion": "C2PA manifest for AI-generated document anchored per EU AI Act Article 50",
  "jurisdiction_profile": "EU-AI-ACT-50-v1",
  "eu_ai_act_50": {
    "ai_system_id": "openai/gpt-4o/2024-11-20",
    "deployer_id": "LEI:5493001KJTIIGC8Y1R12",
    "deployer_name": "Acme Insurance GmbH",
    "deployer_country": "DE",
    "content_category": "AI_ASSISTED_DOCUMENT"
  }
}
```

### 4.3 · Verification workflow

When a regulator or auditor needs to verify Article 50 compliance for a document:

1. Retrieve the LPR receipt ID (stored in the document management system or embedded in document metadata)
2. Call `GET https://verify.ledgerproofhq.io/r/<receipt_id>`
3. The verifier confirms: Bitcoin anchor present, timestamp, deployer identity, AI system identifier, Article 50 transparency marker
4. Optionally: retrieve the original C2PA manifest and verify its SHA-256 matches `artifact.content_hash` in the LPR receipt

This verification requires no contact with Adobe, the C2PA Coalition, or any certificate authority — only the LedgerProof verifier and a Bitcoin node.

---

## 5 · Addressing C2PA's stripping problem

The most significant limitation of C2PA is that manifests are routinely stripped by:
- Social media platforms on upload (Facebook, X/Twitter, Instagram, LinkedIn)
- Content delivery networks during optimization
- Document processing pipelines (PDF converters, email gateways)
- Version control systems during binary handling

The LPR + C2PA composition pattern directly addresses this: once a C2PA manifest is anchored in an LPR receipt, the receipt exists independently on the Bitcoin blockchain and in LedgerProof's calendar infrastructure. Stripping the C2PA manifest from the file does not invalidate the LPR receipt. The receipt proves the manifest existed and contained specific provenance metadata at a specific time, regardless of what happened to the file subsequently.

---

## 6 · Standards convergence

The LedgerProof Foundation is in contact with the C2PA technical working group. The Foundation's position is that C2PA and LPR are complementary layers of a complete provenance stack and that the two standards should converge on:

1. A standardized field in the C2PA `action` assertion for an LPR receipt ID (`lpr_receipt_id`)
2. A C2PA validator extension that optionally verifies the LPR receipt referenced in the manifest
3. A shared vocabulary for `content_category` values aligned with both C2PA's `action` types and LPR's Article 50 content categories

The Foundation will propose this alignment to the C2PA technical working group following the July 6 launch.

---

## 7 · For EU enterprises requiring both C2PA and Article 50 compliance

If your organization uses C2PA for content provenance and must comply with EU AI Act Article 50, the LPR + C2PA composition pattern satisfies both requirements:

- C2PA satisfies the file-level provenance metadata requirement
- LPR receipt satisfies the machine-readable transparency marking requirement (Article 50 transparency_marker field) and provides the immutable, regulatorily-accessible proof of the C2PA manifest's content at issuance

A single LPR receipt referencing the C2PA manifest hash with `jurisdiction_profile: "EU-AI-ACT-50-v1"` is sufficient to demonstrate Article 50 compliance for the anchored document.

---

*LedgerProof Foundation · Version 1.0 Draft · May 2026*
*For technical questions: protocol@ledgerproofhq.io*
