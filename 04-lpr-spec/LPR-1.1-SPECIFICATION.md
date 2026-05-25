# LedgerProof Receipt (LPR) — Version 1.1 Specification

**Status:** Draft — proposed amendment to LPR 1.0
**Editor:** Veronica S. Dawkins, LedgerProof Foundation
**Date:** May 25, 2026
**Supersedes:** §8.5 of LPR 1.0 (resolves spec-code divergence)
**Compatibility:** Backwards compatible with LPR 1.0 — all new fields are additive

---

## 1 · Purpose of v1.1

LPR v1.1 extends LPR v1.0 to provide **complete machine-readable coverage of all four transparency obligations** of EU AI Act Article 50:

| Article 50 sub-obligation | LPR v1.0 | LPR v1.1 |
|---|:---:|:---:|
| 50(1) — Interactive AI disclosure (chatbots) | ✗ | ✅ via `ai/chatbot-session/v1` |
| 50(2) — Synthetic media machine-readable marking | partial | ✅ via expanded `ai/article-50/v1` |
| 50(3) — Emotion recognition / biometric notification | ✗ | (deferred to v2.0 — GDPR-sensitive) |
| 50(4) — AI-generated text + human editorial review exemption | partial | ✅ via `ai/human-review/v1` |

v1.1 is the first open protocol to provide machine-readable cryptographic compliance records covering Article 50(1), 50(2), and 50(4).

---

## 2 · Backwards compatibility guarantee

- All v1.0 receipts remain valid under v1.1 verifiers
- All new fields in `ai/article-50/v1` are **optional** at the schema level
- New content types (`ai/human-review/v1`, `ai/chatbot-session/v1`) are independent and do not affect v1.0 verification
- The `transparency_marker` field, while strongly RECOMMENDED for Article 50 conformance, defaults to `"LPR-EU-AI-ACT-50"` if omitted, preserving existing receipts

---

## 3 · Expanded `ai/article-50/v1` schema

### 3.1 New fields (all optional, RECOMMENDED for Article 50 conformance)

```rust
pub struct AiArticle50Content {
    // ── Existing v1.0 fields (unchanged) ──────────────────────────
    pub ai_system_id: String,
    pub ai_system_version: Option<String>,
    pub deployer_id: String,
    pub deployer_name: String,
    pub deployer_country: String,
    pub content_category: ContentCategory,
    pub artifact_hash: String,
    pub artifact_content_type: String,
    pub artifact_bytes: u64,
    pub supervisory_authority: Option<String>,

    // ── NEW in v1.1 ────────────────────────────────────────────────

    /// Distinguishes pure AI generation from manipulation of real source
    /// content. Article 50(2) covers both, but they have different legal
    /// implications (defamation, deepfake liability).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub generation_type: Option<GenerationType>,

    /// For AI_MANIPULATED content: SHA-256 hash of the original source
    /// material that was modified. Enables deepfake accountability —
    /// proves what the original was without storing it.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_content_hash: Option<String>,

    /// Perceptual hash (pHash, dHash, or similar) for image/video/audio
    /// content. Survives re-encoding, compression, and resizing — allows
    /// matching content "in the wild" to its receipt.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub perceptual_hash: Option<PerceptualHash>,

    /// Human-readable disclosure string that SHOULD be embedded in or
    /// alongside the content. Fulfills "clear and distinguishable manner"
    /// requirement of Article 50. Default: "LPR-EU-AI-ACT-50".
    #[serde(default = "default_transparency_marker")]
    pub transparency_marker: String,

    /// Deployer's assertion that this content touches "matters of public
    /// interest" per Article 50(4). MAY be null for content where the
    /// determination is non-obvious; SHOULD be set explicitly for news,
    /// public affairs, political content, regulatory disclosures.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub is_public_interest: Option<bool>,

    /// Enforcement date of the regulation under which this receipt is
    /// being issued. Allows future-dated receipts to coexist with
    /// transitional/retroactive issuance.
    #[serde(default = "default_enforcement_date")]
    pub enforcement_date: String,

    /// Profile version tag — pins this receipt to a specific Article 50
    /// profile revision for forward compatibility.
    #[serde(default = "default_profile_version")]
    pub profile_version: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum GenerationType {
    /// Content created entirely by AI from a prompt; no source material.
    FullyGenerated,

    /// AI applied to real source content (deepfake, voice clone, image
    /// manipulation). When set, `source_content_hash` SHOULD be populated.
    AiManipulated,

    /// Human-created content with AI assistance (Copilot-style, autocomplete,
    /// translation, grammar editing). May invoke Article 50(4) human review
    /// exemption when paired with an ai/human-review/v1 receipt.
    AiAssisted,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerceptualHash {
    /// Algorithm identifier: "pHash", "dHash", "aHash", "wHash", "chromaprint"
    pub algorithm: String,
    /// Hex-encoded hash value
    pub value: String,
    /// Bit length of the hash (typically 64 for pHash, 256+ for chromaprint)
    pub bits: u16,
}

fn default_transparency_marker() -> String { "LPR-EU-AI-ACT-50".to_string() }
fn default_enforcement_date() -> String    { "2026-08-02".to_string() }
fn default_profile_version() -> String     { "EU-AI-ACT-50-v1.1".to_string() }
```

### 3.2 Validation additions (`validate()`)

```rust
// If generation_type == AI_MANIPULATED, source_content_hash SHOULD be set
if matches!(self.generation_type, Some(GenerationType::AiManipulated))
    && self.source_content_hash.is_none()
{
    // Warning, not error — some manipulations have no single source (composites)
    log::warn!("AI_MANIPULATED content without source_content_hash — \
                deepfake liability defense will be weakened");
}

// source_content_hash, if present, must be 64-char lowercase hex SHA-256
if let Some(ref h) = self.source_content_hash {
    if h.len() != 64 || !h.chars().all(|c| c.is_ascii_hexdigit() && !c.is_ascii_uppercase()) {
        return Err(anyhow::anyhow!("source_content_hash must be 64-char lowercase hex SHA-256"));
    }
}

// transparency_marker length bounds (machine-readable strings)
if self.transparency_marker.is_empty() || self.transparency_marker.len() > 128 {
    return Err(anyhow::anyhow!("transparency_marker must be 1-128 chars"));
}

// enforcement_date must be ISO 8601 calendar date
if !self.enforcement_date.chars().all(|c| c.is_ascii_digit() || c == '-')
    || self.enforcement_date.len() != 10
{
    return Err(anyhow::anyhow!("enforcement_date must be ISO 8601 YYYY-MM-DD"));
}
```

---

## 4 · New content type: `ai/human-review/v1`

The **Article 50(4) human editorial review exemption** requires the deployer to prove that AI-generated text was substantially reviewed by a human before publication. A `human-review/v1` receipt issued *after* an `article-50/v1` receipt creates the cryptographic chain of custody.

### 4.1 Schema

```rust
pub struct AiHumanReviewContent {
    /// Hash of the original AI generation receipt being reviewed.
    /// MUST match the `entry_hash` of an existing ai/article-50/v1 entry.
    pub original_entry_hash: String,

    /// Sequence number of the original AI generation receipt
    /// (redundant with hash but enables fast lookup).
    pub original_sequence: u64,

    /// Role identifier of the reviewer.
    /// GDPR-SAFE: MUST be a role identifier ("senior-editor", "legal-counsel",
    /// "compliance-officer"), NOT a person's name or email.
    pub reviewer_role: String,

    /// ISO 3166-1 alpha-2 country code of the reviewer's organization.
    pub reviewer_country: String,

    /// Timestamp of the review event.
    pub review_timestamp: DateTime<Utc>,

    /// Type of review performed.
    pub review_type: ReviewType,

    /// SHA-256 hash of the post-review content. MUST differ from the
    /// original artifact_hash for SUBSTANTIAL_EDIT type (otherwise no edit
    /// actually occurred).
    pub reviewed_artifact_hash: String,

    /// Deployer's assertion that this content touches matters of public
    /// interest per Article 50(4). Determines whether the exemption is
    /// being claimed for a content subject to disclosure.
    pub is_public_interest: bool,

    /// Free-text rationale (RECOMMENDED for legal defensibility).
    /// MUST NOT contain personal data.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub review_rationale: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ReviewType {
    /// Reviewer substantially modified the AI output. Content as published
    /// differs meaningfully from AI generation.
    SubstantialEdit,
    /// Reviewer fact-checked the AI output but made no substantive edits.
    FactualReview,
    /// Reviewer approved publication without modification. WEAKER for
    /// invoking the 50(4) exemption.
    ApprovalOnly,
}

impl AiHumanReviewContent {
    pub const CONTENT_TYPE: &'static str = "ai/human-review/v1";
}
```

### 4.2 Validation

```rust
// reviewer_role is a role identifier, not a name (no @, no spaces typical of names)
if self.reviewer_role.contains('@') {
    return Err(anyhow::anyhow!(
        "reviewer_role must be a role identifier ('senior-editor'), \
         not an email or personal identifier"
    ));
}

// For SUBSTANTIAL_EDIT, the reviewed hash must differ from the original
if matches!(self.review_type, ReviewType::SubstantialEdit) {
    // Lookup original entry, compare artifact_hash to reviewed_artifact_hash
    // If equal: error — "SUBSTANTIAL_EDIT requires reviewed content to differ from original"
}
```

### 4.3 Verification semantics

A verifier asserting Article 50(4) exemption coverage for a published text MUST find:
1. A valid `ai/article-50/v1` receipt for the original AI generation
2. A valid `ai/human-review/v1` receipt referencing that receipt by `original_entry_hash`
3. The review receipt was issued by the same `publisher_id` as the original
4. `is_public_interest == true` (otherwise the exemption is moot — 50(4) doesn't apply)
5. `review_type` is `SUBSTANTIAL_EDIT` or `FACTUAL_REVIEW` (APPROVAL_ONLY is weaker)

---

## 5 · New content type: `ai/chatbot-session/v1`

Article 50(1) requires deployers of interactive AI systems (chatbots, voice agents) to inform users they are interacting with AI. The chatbot session receipt records that this notification occurred.

### 5.1 Schema

```rust
pub struct AiChatbotSessionContent {
    /// Hash of an opaque session identifier. NEVER the raw session ID
    /// or any user identifier. GDPR-SAFE by construction.
    pub session_id_hash: String,

    /// AI system the user was interacting with.
    pub ai_system_id: String,

    /// Deployer of the chatbot.
    pub deployer_id: String,
    pub deployer_name: String,
    pub deployer_country: String,

    /// Timestamp at which the user was notified of AI interaction.
    pub notification_timestamp: DateTime<Utc>,

    /// How the notification was presented to the user.
    pub notification_method: NotificationMethod,

    /// Hash of the notification text shown to the user.
    /// Enables proof of what was disclosed without storing the text.
    pub notification_text_hash: String,

    /// Asserted "obvious" exemption — Article 50(1) does not require
    /// disclosure when AI interaction is "obvious from the point of view
    /// of a reasonably well-informed natural person". If true, deployer
    /// is asserting this exemption applies and notification was waived.
    pub obvious_exemption_claimed: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum NotificationMethod {
    InitialBanner,    // banner shown at session start
    InlineMessage,    // message in the chat itself
    AudioAnnouncement, // for voice agents
    PrePromptDisclosure, // disclosure in account terms accepted before first interaction
}

impl AiChatbotSessionContent {
    pub const CONTENT_TYPE: &'static str = "ai/chatbot-session/v1";
}
```

### 5.2 Aggregation note

Chatbot session receipts can produce high volume (one per session). LPR's existing Merkle aggregation (RFC 6962) supports this: 1M sessions/day fit in a single Bitcoin anchor with a Merkle root of depth ~20. The per-session marginal Bitcoin cost is fractional cents.

---

## 6 · API additions

### 6.1 Public verification endpoint (unauthenticated)

```
GET /v1/verify/{receipt_id}
```

Returns full receipt data including content, signature, Bitcoin anchor status.
**Requires no authentication.** Intended for regulators, journalists, courts,
and any party that needs to verify a receipt without becoming a customer.

Response:
```json
{
  "receipt_id": "...",
  "sequence": 1234,
  "entry_hash": "...",
  "content_type": "ai/article-50/v1",
  "content": { ... full content payload ... },
  "signature": "...",
  "verifying_key_b64": "...",
  "anchor": {
    "status": "ANCHORED",
    "btc_txid": "...",
    "btc_block_height": 900123,
    "merkle_path": [...]
  },
  "verification": {
    "signature_valid": true,
    "hash_valid": true,
    "anchor_confirmed": true,
    "article_50_conformant": true
  }
}
```

### 6.2 Content hash lookup endpoint (unauthenticated)

```
GET /v1/receipts/by-content-hash/{sha256}
```

Returns the receipt(s) whose `artifact_hash` matches the provided SHA-256.
Enables enforcement: a journalist or regulator with a suspicious AI-generated
image can hash it and query the API. Either a receipt exists (compliance
record present) or it does not (compliance record absent).

Response:
```json
{
  "matches": [
    {
      "receipt_id": "...",
      "sequence": 1234,
      "publisher_id": "...",
      "content_type": "ai/article-50/v1",
      "issued_at": "2026-09-15T12:34:56Z",
      "verify_url": "https://api-eu.ledgerproofhq.io/v1/verify/..."
    }
  ],
  "perceptual_matches": [...]  // optional, if perceptual_hash provided
}
```

### 6.3 Optional: perceptual hash lookup

```
GET /v1/receipts/by-perceptual-hash/{algorithm}/{hash}
```

Returns receipts whose `perceptual_hash.value` is within Hamming distance ≤ N
of the provided hash. Defaults: N=10 for 64-bit pHash, N=40 for 256-bit chromaprint.

---

## 7 · Conformance levels

A receipt is **Article 50 Conformant** under LPR v1.1 if it:

1. Is a valid LPR v1.0 Core receipt (signed, chained, anchored)
2. Has `content_type` of `ai/article-50/v1`, `ai/human-review/v1`, or `ai/chatbot-session/v1`
3. Validates against the v1.1 schema for its content type
4. The `transparency_marker` field is present and non-empty (for `ai/article-50/v1`)
5. The corresponding Article 50 sub-obligation fields are populated for the claimed obligation

A receipt is **Article 50 Defensible** (a stronger level, recommended for high-liability contexts) if additionally:

6. `perceptual_hash` is populated for image/audio/video content (enables enforcement matching)
7. `source_content_hash` is populated for `AI_MANIPULATED` content (enables deepfake defense)
8. For text content with `is_public_interest == true`, a corresponding `ai/human-review/v1` receipt exists if the deployer claims the 50(4) exemption

---

## 8 · Migration from v1.0

Deployers using LPR v1.0 receipts MAY continue to issue v1.0 receipts indefinitely. To upgrade:

1. **No code change required** for the v1.0 receipt schema — all v1.1 additions are optional fields
2. **Update SDK** to LPR v1.1 client (Python, Node, Rust)
3. **Populate new fields** as available — start with `transparency_marker` (single line change)
4. **For deepfake content**, set `generation_type = AI_MANIPULATED` and populate `source_content_hash`
5. **For text with human review**, issue a `ai/human-review/v1` receipt after publication

---

## 9 · References

- LPR v1.0 Specification (this directory, `LPR-1.0-SPECIFICATION.md`)
- Regulation (EU) 2024/1689 (EU Artificial Intelligence Act) — Article 50
- IETF SCITT Architecture (draft-ietf-scitt-architecture)
- RFC 6962 — Certificate Transparency (Merkle tree construction)
- C2PA Content Credentials Specification (referenced for assertion compatibility)
- eIDAS Regulation (EU) No 910/2014 — qualified electronic seals

---

*LedgerProof Foundation · LPR v1.1 Draft Specification · May 25, 2026*
*Public review period: until June 15, 2026 · Comments to: spec@ledgerproofhq.io*
