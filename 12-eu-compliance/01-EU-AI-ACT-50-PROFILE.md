# LPR v1.0 — EU AI Act Article 50 Compliance Profile

**Profile identifier:** `EU-AI-ACT-50-v1`
**Status:** Draft — for inclusion in LPR 1.0 specification §8.5
**Regulatory basis:** Regulation (EU) 2024/1689 (EU AI Act), Article 50 — Transparency obligations for certain AI systems
**Enforcement date:** August 2, 2026
**Editor:** Veronica S. Dawkins, LedgerProof Foundation

---

## 1 · Purpose

Article 50 of the EU AI Act imposes transparency obligations on providers and deployers of AI systems that generate or manipulate synthetic content. Specifically:

- **Article 50(2):** Providers of AI systems that generate synthetic text, images, audio, or video content must ensure outputs are marked in a machine-readable format that is detectable as AI-generated.
- **Article 50(4):** Deployers of AI systems that generate text published for public information purposes must disclose that the text is AI-generated.
- **Recital 133:** Provenance metadata must be robust, interoperable, and technically verifiable.

This profile defines the additional receipt fields and verification procedures required for an LPR v1.0 receipt to constitute a compliant AI-generated content provenance record under Article 50. A receipt conforming to this profile MAY be presented to EU supervisory authorities as evidence of Article 50 compliance for the specific document anchored.

---

## 2 · Profile specification (§8.5 addition to LPR 1.0 spec)

### 8.5 · LPR v1.0 EU AI Act Article 50 Compliance Profile

**Profile tag:** `"EU-AI-ACT-50-v1"`

A receipt conforming to this profile MUST satisfy all LPR v1.0 Core requirements (§1–§6) and additionally MUST include the following fields in the `authorship` object:

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

The `ai_system_id` field MUST be a unique string identifying the AI model or system that generated or substantially contributed to the anchored artifact. Acceptable formats, in order of preference:

1. A fully-qualified model identifier using the format `<provider>/<model>/<version>`, e.g.:
   - `openai/gpt-4o/2024-11-20`
   - `anthropic/claude-3-5-sonnet/20241022`
   - `google/gemini-1.5-pro/001`
2. A URL resolving to the AI system's model card, e.g. `https://huggingface.co/meta-llama/Meta-Llama-3-8B`
3. A DID resolving to the AI system's identity document, e.g. `did:web:models.openai.com:gpt-4o`

If the deployer does not have access to the exact model identifier (e.g., when using a third-party API that does not expose version information), the deployer MUST use the most specific identifier available and MUST note the limitation in `actor_assertion`.

The `actor_id` field (Core) MUST be set to the same value as `ai_system_id`.

#### 8.5.2 · `actor_assertion` for Article 50

The `actor_assertion` field MUST contain a human-readable declaration conforming to the following template:

```
"This content was generated in whole or in substantial part by the AI system identified in
ai_system_id, deployed by the organization identified in deployer_id, on the date and time
indicated in timestamp_iso. This receipt constitutes a machine-readable transparency marking
as required by Article 50 of Regulation (EU) 2024/1689 (EU Artificial Intelligence Act).
The content hash recorded in artifact.content_hash is the SHA-256 of the canonical form of
the AI-generated artifact as of the moment of issuance. This receipt does not attest to the
accuracy, completeness, or lawfulness of the content."
```

The deployer MAY extend this declaration with additional information. The deployer MUST NOT remove or contradict any element of the required declaration.

#### 8.5.3 · `tool_chain` requirements

The `tool_chain` array MUST include at least one entry identifying the AI system, with the following fields:

```cbor
{
  "name": <string — AI system name, e.g. "GPT-4o">,
  "version": <string — model version>,
  "provider": <string — provider name, e.g. "OpenAI">,
  "api_endpoint": <string, OPTIONAL — the API endpoint used, e.g. "https://api.openai.com/v1/chat/completions">,
  "prompt_hash": <string, OPTIONAL — SHA-256 of the prompt/system prompt, if the deployer chooses to record it>
}
```

Recording `prompt_hash` is RECOMMENDED for deployers seeking legal defensibility in high-stakes applications. The prompt hash enables the deployer to later prove the exact instructions given to the AI system, without revealing the prompt content in the on-chain record.

#### 8.5.4 · `deployer_id` format

The `deployer_id` field MUST uniquely identify the legal entity that deployed the AI system and caused the content to be generated. Acceptable formats:

1. An EUID (European Unique Identifier) for EU-registered entities, e.g. `EUID:DE:HRB123456`
2. An LEI (Legal Entity Identifier), e.g. `LEI:5493001KJTIIGC8Y1R12`
3. A VAT number for EU entities, e.g. `VAT:DE123456789`
4. A DID, e.g. `did:web:example.com`
5. For non-EU entities: an equivalent national business registration identifier

The `deployer_name` field MUST be the legal name of the deploying organization as registered with the relevant authority.

#### 8.5.5 · `content_category` values

The `content_category` field MUST be one of the following values, drawn from Article 50's scope:

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

The `transparency_marker` field MUST be set to the string `"LPR-EU-AI-ACT-50"`. This value is a machine-readable marker intended to satisfy the Article 50 requirement for a detectable, machine-readable AI-generated content indicator. The presence of this marker in a valid, Bitcoin-anchored LPR receipt constitutes the transparency marking required by Article 50(2) and Article 50(4).

---

## 3 · Verification procedure for Article 50 receipts

A verifier asserting Article 50 compliance for an LPR receipt MUST perform all Core verification steps (§6.1) and additionally:

1. Confirm `authorship.eu_ai_act_50.profile_version == "EU-AI-ACT-50-v1"`.
2. Confirm `authorship.eu_ai_act_50.transparency_marker == "LPR-EU-AI-ACT-50"`.
3. Confirm `authorship.eu_ai_act_50.ai_system_id` is non-empty and conforms to §8.5.1.
4. Confirm `authorship.eu_ai_act_50.deployer_id` is non-empty and conforms to §8.5.4.
5. Confirm `authorship.eu_ai_act_50.content_category` is one of the permitted values in §8.5.5.
6. Confirm the Bitcoin anchor is present and `anchor.anchor_status == "ANCHORED"`.

A receipt that passes all Core checks but fails one or more of these additional checks MUST be reported as "Core-valid, EU-AI-ACT-50-non-conformant" and MUST NOT be presented as Article 50-compliant provenance.

---

## 4 · Example conformant receipt (EU-AI-ACT-50-v1)

```json
{
  "lpr_version": 1,
  "receipt_id": "018fbc8e-4d2a-7a3f-9b1c-2d4e5f6a7b8c",
  "trace_id": "018fbc8e-0000-7000-8000-100000000001",
  "timestamp_ns": 1753920000000000000,
  "timestamp_iso": "2026-07-31T08:00:00.000000000Z",
  "artifact": {
    "content_hash": "a1b2c3d4e5f6...64hexchars...",
    "hash_algo": "SHA-256",
    "content_type": "AI_ASSISTED_DOCUMENT",
    "content_bytes": 48293
  },
  "authorship": {
    "actor_type": "AI_MODEL",
    "actor_id": "anthropic/claude-3-5-sonnet/20241022",
    "actor_assertion": "This content was generated in whole or in substantial part by the AI system identified in ai_system_id...",
    "tool_chain": [
      {
        "name": "Claude 3.5 Sonnet",
        "version": "20241022",
        "provider": "Anthropic",
        "api_endpoint": "https://api.anthropic.com/v1/messages"
      }
    ],
    "eu_ai_act_50": {
      "profile_version": "EU-AI-ACT-50-v1",
      "ai_system_id": "anthropic/claude-3-5-sonnet/20241022",
      "ai_system_version": "20241022",
      "deployer_id": "LEI:5493001KJTIIGC8Y1R12",
      "deployer_name": "Example Insurance AG",
      "deployer_country": "DE",
      "content_category": "AI_ASSISTED_DOCUMENT",
      "transparency_marker": "LPR-EU-AI-ACT-50",
      "enforcement_date": "2026-08-02",
      "supervisory_authority": "BaFin"
    }
  },
  "chain": { "prev_receipt_hash": null },
  "signature": { "sig_algo": "Ed25519", "sig_bytes": "...", "signer_pubkey": "..." },
  "anchor": {
    "substrate": "bitcoin-mainnet",
    "merkle_leaf_hash": "...",
    "anchor_status": "ANCHORED",
    "btc_txid": "...",
    "btc_block_height": 900000
  }
}
```

---

## 5 · Implementation note for the publish API

The `POST /receipts` endpoint at `api.ledgerproofhq.io` MUST accept an `eu_ai_act_50` object in the request body when `jurisdiction_profile: "EU-AI-ACT-50-v1"` is specified. The API MUST validate all required fields before issuing the receipt. See `12-eu-compliance/API-SPEC.yaml` for the full OpenAPI specification.

---

## 6 · Regulatory notes

**This profile does not constitute legal advice.** The EU AI Act's Article 50 obligations are subject to guidance from the European AI Office (est. February 2024) and national competent authorities. Deployers should consult qualified legal counsel regarding their specific Article 50 obligations.

The LedgerProof Foundation will update this profile within 30 days of the publication of binding technical standards by CEN/CENELEC under the EU AI Act's standardization mandate (Article 40). Profile version `EU-AI-ACT-50-v1` is designed to be superseded by a `EU-AI-ACT-50-v2` aligned with those standards once published.

---

*LedgerProof Foundation · Draft · May 2026*
