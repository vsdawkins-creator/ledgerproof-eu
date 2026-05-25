# Embedding LedgerProof Receipts as C2PA Assertions

**Document:** LPR C2PA Assertion Specification, v1.0
**Status:** Draft for C2PA CAWG submission
**Editor:** Veronica S. Dawkins, LedgerProof Foundation
**Date:** May 25, 2026
**Audience:** C2PA implementers, Content Authenticity Initiative members, Adobe / Microsoft / Google / BBC / Reuters / AP technical staff

---

## 1 · Why this exists

C2PA Content Credentials provide an excellent mechanism for embedding provenance metadata directly inside a media file. They are the de facto industry standard, with implementations from Adobe (Firefly, Photoshop), Microsoft (Bing Image Creator), Google, Sony, Nikon, BBC, Reuters, and AP.

C2PA has one well-known limitation: **embedded metadata can be stripped.** When a C2PA-credentialed image is screenshotted, re-encoded, uploaded to a social network that strips metadata, or processed by any tool that does not preserve XMP/EXIF, the C2PA assertion is lost. The content remains, but the provenance is gone.

LedgerProof Receipts (LPRs) solve the stripping problem by anchoring a SHA-256 hash of the content to the Bitcoin blockchain. The anchor cannot be stripped because it does not live in the file. Even after the C2PA manifest is removed, the LPR remains discoverable by hashing the surviving content and querying the LedgerProof API.

This document specifies how to embed an LPR reference inside a C2PA assertion so that the two systems work together: C2PA provides in-file disclosure; LPR provides permanent, regulator-grade verifiability.

---

## 2 · Relationship to existing C2PA assertions

This specification defines a new assertion label, `org.ledgerproof.receipt.v1`, that complements (not replaces) the existing C2PA assertions:

| Existing C2PA Assertion | Role | LPR Contribution |
|---|---|---|
| `c2pa.ai.generativeInfo` | Records AI generation details inside the manifest | LPR receipt records the same plus the Bitcoin anchor |
| `c2pa.training-mining` | Disclosure of training data usage rights | Not addressed by LPR |
| `c2pa.actions` | Edit history within a single tool | Not addressed by LPR |
| `org.ledgerproof.receipt.v1` (NEW) | Permanent off-file proof anchor | Enables verification after manifest stripping |

The `org.ledgerproof.receipt.v1` assertion is **redundant by design.** If the C2PA manifest survives, both systems verify. If it does not, LPR alone is sufficient to prove provenance.

---

## 3 · Assertion structure

The `org.ledgerproof.receipt.v1` assertion is a CBOR object with the following fields:

```cbor
{
  "receipt_id":         tstr,    ; LPR receipt identifier (UUID v7)
  "entry_hash":         tstr,    ; SHA-256 of the canonical entry, hex
  "verify_url":         tstr,    ; HTTPS URL where the receipt can be fetched
  "anchor_substrate":   tstr,    ; e.g., "bitcoin-mainnet"
  "anchor_status":      tstr,    ; "PENDING", "ANCHORED", "CONFIRMED"
  "anchor_btc_txid":    tstr,    ; OPTIONAL — Bitcoin transaction ID if anchored
  "anchor_btc_height":  uint,    ; OPTIONAL — Bitcoin block height if confirmed
  "artifact_hash":      tstr,    ; SHA-256 of artifact, hex (MUST match c2pa hash)
  "profile_version":    tstr,    ; e.g., "EU-AI-ACT-50-v1.1"
  "transparency_marker": tstr    ; the disclosure string
}
```

### Example assertion (JSON representation)

```json
{
  "label": "org.ledgerproof.receipt.v1",
  "data": {
    "receipt_id": "018fbc8e-4d2a-7a3f-9b1c-2d4e5f6a7b8c",
    "entry_hash": "da4ce6652880287db3f39cd152f38c633074aa4c62e4e968b7f18264397ad464",
    "verify_url": "https://api-eu.ledgerproofhq.io/v1/verify/0",
    "anchor_substrate": "bitcoin-mainnet",
    "anchor_status": "CONFIRMED",
    "anchor_btc_txid": "5db5c68e7c4c8a3f2e1d9b4a6c5d8e3f2a1b9c8d7e6f5a4b3c2d1e0f9a8b7c6d",
    "anchor_btc_height": 900123,
    "artifact_hash": "a1b2c3d4e5f6789012345678901234567890123456789012345678901234abcd",
    "profile_version": "EU-AI-ACT-50-v1.1",
    "transparency_marker": "LPR-EU-AI-ACT-50"
  }
}
```

---

## 4 · Generation workflow

The intended workflow for a C2PA-aware tool generating AI content:

```
1. Tool generates content (image, audio, video, text).

2. Tool computes artifact_hash = SHA-256(content).

3. Tool issues an LPR receipt:
     POST https://api-eu.ledgerproofhq.io/v1/publish
     content_type: "ai/article-50/v1"
     content: { artifact_hash, deployer_id, ai_system_id, ... }
   Returns: receipt_id, entry_hash, sequence.

4. Tool constructs c2pa.ai.generativeInfo assertion as usual.

5. Tool constructs org.ledgerproof.receipt.v1 assertion with the values
   from step 3.

6. Tool builds the C2PA manifest including both assertions.

7. Tool embeds the manifest in the media file per C2PA spec.

8. Tool delivers the file.
```

---

## 5 · Verification workflow

A verifier confronted with a media file does the following:

```
1. Parse C2PA manifest from file (if present).
2. If org.ledgerproof.receipt.v1 assertion found:
     a. Hash the surviving content; confirm matches artifact_hash.
     b. Fetch verify_url and confirm:
          - receipt_id matches
          - entry_hash matches
          - anchor_status is ANCHORED or CONFIRMED
          - signature on the receipt verifies against publisher key
     c. If all check, content is C2PA + LPR verified.
3. If no C2PA manifest (stripped):
     a. Hash the content.
     b. Query GET /v1/receipts/by-content-hash/{sha256}.
     c. If a receipt is returned, content is LPR-verified despite
        manifest loss.
4. If perceptual_hash is populated on the LPR receipt:
     a. Compute perceptual hash of surviving content.
     b. Query GET /v1/receipts/by-perceptual-hash/{algo}/{hash}.
     c. Match within Hamming distance — establishes content lineage
        even after re-encoding.
```

---

## 6 · Implementer notes

**For Adobe / Firefly:** The org.ledgerproof.receipt.v1 assertion is additive. Existing c2pa.ai.generativeInfo assertions continue to function unchanged. The LPR receipt issuance step (~50ms) can be performed asynchronously after image generation completes, with the assertion attached when the receipt_id returns.

**For Microsoft / Bing:** Bing-generated images already include C2PA manifests. Adding an LPR assertion requires one additional HTTPS POST per generation to the LedgerProof API. At scale, batched issuance (1000 receipts per Merkle root) keeps per-image overhead under 1ms.

**For news organizations (BBC, Reuters, AP):** For AI-assisted text, the workflow generates an `ai/article-50/v1` receipt at draft time and an `ai/human-review/v1` receipt at editorial sign-off. The pair documents the Article 50(4) human review exemption with cryptographic chain of custody.

**For camera manufacturers (Sony, Nikon, Canon):** LPR receipts can also be issued for human-captured content as proof of *non-AI* origin. A receipt with `generation_type` absent (or a future content type `human/capture/v1`) provides the affirmative provenance counterpart to AI disclosure.

---

## 7 · Discovery and metadata-stripping resilience

The LPR receipt is independently discoverable by content hash. This means:

- A journalist who finds a suspicious image with no metadata can compute its hash and query the LedgerProof API. A returned receipt proves the image is AI-generated (and identifies who generated it).
- A regulator investigating a deepfake can do the same with no involvement from the deployer or any C2PA tool.
- A court can verify provenance against an immutable Bitcoin record even if every intermediate platform stripped metadata.

This property — provenance that survives the file — is what no C2PA-only implementation provides today.

---

## 8 · Submission to C2PA CAWG

This specification is intended for submission to the Content Authenticity Working Group within the C2PA. Requested actions:

1. Reserve the assertion label `org.ledgerproof.receipt.v1` in the C2PA assertions registry.
2. Add an informative reference to this document in the next C2PA specification revision.
3. Consider establishing a formal liaison between C2PA and the IETF SCITT working group for AI content provenance standards alignment.

LedgerProof Foundation seeks no exclusivity. Other transparency log providers may publish equivalent assertions (`org.example.receipt.v1`) following the same pattern. The goal is to establish the *pattern* of "off-file persistent proof anchor" as a standard C2PA assertion category.

---

## 9 · Reference implementation

A working reference implementation will be published at:

`https://github.com/vsdawkins-creator/ledgerproof-c2pa-bridge`

The reference will demonstrate end-to-end: AI image generation → C2PA manifest construction with LPR assertion → file embedding → verification including metadata-stripping recovery via content hash lookup.

Target availability: June 30, 2026.

---

## 10 · Contact

- Specification questions: spec@ledgerproofhq.io
- C2PA liaison: c2pa@ledgerproofhq.io
- IETF SCITT alignment: scitt@ledgerproofhq.io

---

*LedgerProof Foundation · May 25, 2026*
*This document is published under CC BY 4.0.*
