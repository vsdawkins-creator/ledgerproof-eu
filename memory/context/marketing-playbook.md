# Marketing Playbook

## Core message
**"LedgerProof is the trust anchor for everyone else's systems."**

Variants of this line should be the takeaway left in any room.

## Framing rules

### Penalty math — ALWAYS lead with 3% turnover
NOT €15M. €15M is rounding error to Tier-1 banks. €4.7B (JPM 3% of turnover) is a board-reportable risk event.

### "Per article" cumulative violations
Each non-compliant output is a separate violation. Doesn't cap at €15M total. Bank generating 100K unmarked AI documents/quarter → potentially €1.5B exposure (capped at 3% turnover practically).

### Strict liability
No intent required. The system either marks or doesn't. Either is a fact.

### Aug 2 deadline urgency
"68 days until enforcement" gets attention. Countdown format works.

## Three campaigns to run

### Campaign 1 — The Exposure Calculator
**URL:** `compliance.ledgerproofhq.io`
**What:** CFO enters company revenue + AI usage volume. Output: "Your 2026 Article 50 exposure: estimated €620M. LedgerProof annual cost: €150K. ROI: 4,133×."
**Why:** Stripe Atlas-style sales tool. Run once, customer sold.

### Campaign 2 — Countdown-to-enforcement microsite
**URL:** `aug2.ledgerproofhq.io`
**What:** Live countdown to Aug 2, industry-by-industry exposure breakdown, named enforcement actions, "Get compliant in 72 hours" CTA
**Why:** Urgency + shareability. Exposure-by-industry gets shared.

### Campaign 3 — "Did You Mark That?" video series
**Format:** 20-second LinkedIn/X/YouTube Shorts
**Scenarios:**
- Bank's wealth-management report with AI-generated charts → "Did you mark that?"
- Media outlet's election explainer with AI graphics → "Did you mark that?"
- Pharma drug-information document with AI summaries → "Did you mark that?"
**Each ends with:** exposure calculation + LedgerProof URL
**Why:** Cheap to produce, viral among compliance executives.

## The single most leveraged move

**Get one named enforcement action.**

EU Commission has telegraphed they'll name the first Article 50 target within 90 days of Aug 2. When that headline drops, every F500 EU subsidiary CFO gets a Slack ping at 9am from outside counsel: "This is us in 18 months unless we move now."

### Pre-positioned assets needed
- Landing page already built: `first-enforcement.ledgerproofhq.io`
- Press kit ready
- 3 customer testimonials pre-cleared for use
- 72-hour implementation guarantee ready to announce

**Cannot control when headline drops. CAN control whether we own the conversation when it does.**

10× marketing budget for the 24-hour window after that headline.

## Watermarking story

### Visible mark (mandatory for Article 50)
- ⓘ or 🤖 or LedgerProof badge, 24px bottom-right, 80% opacity
- Click-through to verifier
- Human disclosure compliance

### Invisible neural watermark (the moat)
- Survives screenshots, crops, re-encodes, watermark-strip attacks
- Recommended approach: Tree-Ring or Stable Signature (open-source from Meta)
- SynthID is Google-proprietary — cross-bridge instead of embed
- 6-8 engineer-weeks to integrate

### Dual-mark composition (4-layer system)
1. Visible disclosure badge (human-readable)
2. Neural watermark (forensic recovery)
3. Off-image LPR receipt (machine-readable source of truth)
4. Off-chain CBOR + on-chain Bitcoin anchor (tamper evidence)

If you screenshot, strip C2PA, crop the badge — neural watermark survives. **This is the moat against "I just screenshot it."**

## Deepfake control story (4 mechanisms)

1. **Pre-emptive** — economics force major AI vendors to anchor. Absence-of-receipt becomes a signal.
2. **Reactive** — browser extensions verify every image on every page. Auto-scan + cross-reference with SynthID detector.
3. **Real-time stream attestation** — Hong Kong Arup defense. 5-second Merkle commitments during live calls.
4. **Authorized-identity registry** — public figures register verified identity. Absence of LPR receipt from registered identity = presumptive deepfake.

For 2027 elections (France/Germany/EU Parliament): authorized identity registry is the only realistic defense against Slovakia-style attack.

## NanoBanana / AI vendor integration story

### How the protocol lives inside a big AI company
- Inline SDK at generation (Pattern A — gold standard)
- ~8ms added latency, invisible to users
- ~$0.0003 per output at 50M/day batched scale
- 3-week integration with existing engineering velocity

### Vendor → user value transfer
- Vendor solves their own 50(2) compliance
- Vendor hands users free 50(4) compliance via "Share with provenance" button
- Receipt inheritance: Receipt #1 (NanoBanana) ← Receipt #2 (user's LinkedIn share)
- Becomes vendor differentiator: "Our AI gives your users free compliance"

## Counter-positioning vs C2PA-alone

Every C2PA-like in-file system has the same flaw: **strippable on screenshot/re-encode**.

The pitch: "C2PA wins the in-file disclosure war. But every C2PA manifest can be stripped. The market just adopted the half that gets stripped. The unstripable half — the permanent anchor — is the urgent gap. LedgerProof is exactly that gap."

LedgerProof is NOT a C2PA competitor. LedgerProof is the **anchor layer that makes C2PA verifiable after the manifest is gone**.

## 5 catalyst events to cite

Use these in any "why now" conversation:
1. Slovakia election (Sep 2023) — democratic impact precedent
2. Hong Kong Arup $25M (Feb 2024) — corporate-loss precedent
3. Taylor Swift deepfake (Jan 2024) — celebrity/political precedent
4. iOS 18 C2PA (late 2024) — consumer infrastructure precedent
5. Big-3 AI Code of Practice (Q4 2025) — vendor commitment precedent

Six months from now, add the first EU enforcement action as #6.
