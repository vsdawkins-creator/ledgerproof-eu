# Patent Strategy

## Overall posture: defensive-only Apache/Eclipse model

**Pattern:**
1. File patents under LedgerProof Inc.
2. Grant perpetual, irrevocable, royalty-free license to Foundation
3. Foundation licenses to any LPR-compatible implementation
4. **Defensive termination clause**: any party that sues an LPR-compatible implementation loses their license

Same model: Mozilla, Apache, Eclipse, Linux Foundation, Wikimedia.

## What is NOT patentable (public domain / prior art)
- SHA-256, Ed25519, Merkle trees individually
- Bitcoin OP_RETURN timestamping (OpenTimestamps prior art since 2016)
- Stuart Haber & Scott Stornetta 1991 cryptographic timestamping paper (foundational)
- TLSH, pHash, ssdeep individually
- DIDs, Verifiable Credentials (W3C)
- C2PA assertion format (open coalition)
- RFC 6962 Certificate Transparency

## What IS likely patentable (novel combinations)

### High strategic value

**1. GDPR Article 17 soft-delete with cryptographic chain preservation**
Specific method of nulling personal-data fields while preserving chain identity + schema-level PII rejection at parse time. Solves a genuinely hard problem.

**2. Lineage chains with same-DID-or-delegation succession rules**
LPR 1.2 §3 algorithm. Linear chain + Bitcoin-anchored delegations is novel composition. Git versioning ≠ this. C2PA ≠ this.

**3. Foundation Canonical Registry with FROST-aggregated arbitration receipts**
Recursive structure: using the protocol to resolve disputes about the protocol. WIPO arbitration + FROST + anchoring = novel composition.

**4. Real-time live-stream attestation via continuous Merkle commitments**
Short-interval (5-second) commitments during live calls. The Hong Kong Arup $25M defense. No clear prior art.

**5. Multi-modal absence-of-receipt-as-signal verifier algorithm**
Authorized identity registry + absence detection + similarity hash cross-reference. Election-integrity moat.

### Medium strategic value

**6. Recursive provenance** (SLSA L3 build attestation of verifier anchored as LPR receipt)

**7. 4-layer disclosure system** (visible badge + neural watermark + off-chain CBOR receipt + on-chain anchor)

## The 5 USPTO provisionals already filed (12-month clock)

| # | Provisional | My assessment |
|---|---|---|
| 1 | LPR receipt format + verifier API | CONVERT, sharpen claims |
| 2 | OP_RETURN with LPR1 prefix | WEAK; consider abandoning unless structural innovation can be claimed |
| 3 | Merkle batching for high-throughput AI provenance | CONVERT, sharpened with "for high-throughput AI provenance" qualifier |
| 4 | C2PA assertion bridge | DEFENSIVE ONLY — file then publish under defensive grant |
| 5 | GDPR-by-construction schema validation | CONVERT, strongest of the five |

**ALSO FILE NEW PROVISIONALS** on Candidates 2, 3, 4, 6 above before they appear in LPR 1.2 / 2.0 public specs.

## The Alice (2014) problem

Alice Corp. v. CLS Bank invalidated 60-70% of software patent challenges. "Abstract ideas on a generic computer" not patentable.

- ❌ "Anchoring a hash to a blockchain" — INVALID
- ⚠️ "Validating a chain of receipts" — RISKY, depends on claim language
- ✅ "Schema validation that rejects PII" — SAFE (specific technical improvement)
- ✅ "Real-time stream attestation" — SAFE (specific mechanism for specific problem)

**Choice of counsel matters more than choice of what to file.**

## Recommended counsel

### US
- **Fenwick & West LLP** (recommended — open-source-friendly + cost-controlled)
- Cooley LLP, WSGR, Knobbe Martens as alternatives

### EU
- **Bird & Bird** (London/Brussels — recommended; AI Act expertise + EU patent practice)
- Hogan Lovells as alternative

**Total Year-1 budget: ~$100K** ($60K US + $40K EU + Foundation IP charter)

## 30-day action list (post-close)

| Week | Action |
|---|---|
| 1 | Engage IP counsel; review all 5 provisionals + recommend convert/abandon |
| 2 | File 2-4 new provisionals on strongest novel candidates (live-stream attestation, Canonical Registry) |
| 3 | Draft Foundation Patent Grant modeled on Apache 2.0 + Eclipse Public License |
| 4 | Begin PCT filings for international protection on strongest 2-3 candidates ($5-10K each) |
| Months 2-11 | Convert strongest provisionals before 12-month deadlines ($10-25K each) |
| Month 12 | First non-provisional USPTO review begins |

## Investor framing (if asked tomorrow)

*"We have five USPTO provisionals filed covering the GDPR-safe schema, receipt format, Merkle batching, C2PA bridge, and OP_RETURN format. We're filing additional provisionals on live-stream attestation, Canonical Registry, and lineage chain mechanism in the next 60 days. Patent strategy is defensive — patents owned by LedgerProof Inc., licensed perpetually royalty-free to the Foundation, and from the Foundation to any LPR-compatible implementation, with industry-standard defensive termination clauses. This is the Apache and Eclipse model. We patent so trolls can't, and so a Big Tech fork can't capture the spec. We do not patent to extract rent from implementers."*

That answer signals sophistication. "We have 5 patents, isn't that great?" signals the opposite.

## Investor pressure note
- TVP/Stillmark/Fulgur aligned with defensive-only (they invest in protocol companies)
- Illuminate may push more aggressive assertion (financial-services LPs love bankable IP)
- **HOLD THE LINE ON DEFENSIVE-ONLY**

## Caveat
I am not a patent attorney. Engage real counsel (Fenwick + Bird & Bird recommended above) before any conversion decision.
