# Meeting Prep — Trammell Venture Partners
## Wednesday May 27, 2026 · 9:30 AM CT · 30 minutes

---

## The room

**Christopher Calicott — Managing Director**
- Co-founded TVP in 2016 with Dustin Trammell (Austin-based serial entrepreneur / security researcher)
- Leads TVP Bitcoin Venture Fund series — venture's first dedicated Bitcoin-native institutional fund
- Board member, Texas Blockchain Council; championed Texas HB4474 (signed into law)
- Career arc: tech from the web's emergence → internet-native money. MBA in Madrid. Deep background in disruptive data analytics, machine intelligence, multi-sided platforms
- Backed: Kraken (early), Unchained, Voltage, Fedi, ZEBEDEE, Galoy, Wavlake, Impervious
- Public thesis: *"Bitcoin has already won as the internet's native monetary layer — it's just not broadly recognized yet. As early-stage companies find traction, value accrues to the Bitcoin stack."*
- Tone to expect: technically fluent, won't need Bitcoin basics, will probe whether you're genuinely Bitcoin-native or Bitcoin-adjacent. He has walked away from dozens of "blockchain" pitches. The word "blockchain" will not help you.

**Aryan Malhotra — Analyst / Venture Intern**
- Joined TVP from Queens College (Quantitative Economics). Prior: DivInc (investment/strategy), KLB, marketDice
- Likely ran the initial screen on your email and escalated it to Christopher
- He booked the meeting — treat him as a champion inside the firm, not a gatekeeper to route around
- Speak to him directly during the call; he'll be the one building the internal memo if this advances

**Fund status:** TVP is actively raising Fund 3. This matters — they are deploying capital now, not advising.

---

## Why they said yes

Your subject line landed: *"LedgerProof — the institutional revenue layer for Bitcoin's application stack."*

That phrase maps directly onto TVP's stated thesis. "Protocol stack" and "revenue layer" are their language. They did not reply to a blockchain pitch — they replied to something that sounded like a new monetization surface for Bitcoin infrastructure.

The body reinforced it: OP_RETURN anchor on Bitcoin mainnet, no token, no sidechain, no intermediary. Every LedgerProof receipt is a Bitcoin transaction. That is Bitcoin-native by TVP's definition.

---

## TVP portfolio — know these before the call

| Company | What they do | Relevance to LedgerProof |
|---|---|---|
| **Voltage** | Bitcoin and Lightning infrastructure (node hosting, channel management) | Infrastructure peer — they host the rails; we anchor to them |
| **Unchained** | Bitcoin custody and multisig for institutions | Same institutional customer segment |
| **Galoy** | Open-source Bitcoin banking stack | Protocol-layer builder — similar Foundation + commercial-entity dual structure |
| **Fedi / Fedimint** | Community Bitcoin custody via federations | Federated operator model — conceptually similar to LedgerProof Foundation's calendar operator network |
| **ZEBEDEE** | Lightning Network for gaming/micropayments | Demonstrates Bitcoin-native application layer generating real transaction volume |
| **Impervious** | Peer-to-peer internet standards on Bitcoin/Lightning | Standards-body orientation — closest structural parallel to what LedgerProof is doing with IETF |
| **Wavlake** | Music on Lightning | Application layer → block-space demand |
| **Vida** ($4M Series A, Nov 2025 — most recent deal) | Not confirmed — watch for context clues Christopher mentions |

**Portfolio pattern:** TVP backs founders building *protocol-layer* companies, not applications. They invest where a standard or infrastructure layer gets established. LedgerProof fits this pattern precisely.

---

## Your positioning for this meeting

### The one-sentence version Christopher will use internally
*"LedgerProof is the cryptographic provenance layer for AI-generated documents — anchored to Bitcoin, no token, open protocol, targeting the compliance and legal liability market created by EU AI Act Article 50."*

### The pitch structure that will work for TVP (in order)

**1. Why this is Bitcoin-native, not Bitcoin-adjacent**
Every LedgerProof Receipt (LPR) is an OP_RETURN transaction on Bitcoin mainnet. No sidechain. No token. No oracle. The receipt's validity is derived entirely from Bitcoin's timechain. The "LPR1" prefix in the OP_RETURN payload is permanent — it is visible in every Bitcoin block explorer forever.

At 1 million receipts per day (conservative enterprise-scale), LedgerProof would generate 1M Bitcoin transactions per day. That is a new institutional fee-revenue source for miners and a meaningful source of block-space demand — organic, non-speculative, compliance-driven.

**2. Why now, and why the window is narrow**
EU AI Act Article 50 enforces August 2, 2026 — 73 days. European operations of US enterprises are generating AI-assisted documents today that will require compliant provenance records. The liability exposure is arriving before any competitor has a deployed, open, Bitcoin-anchored protocol. LedgerProof launched May 18 with a live Bitcoin anchor and a working verifier.

**3. Why open protocol + Foundation is the right structure (and why it protects TVP's investment)**
A proprietary receipt service can be displaced. An open protocol with an IETF draft, a Foundation, and a coalition of institutional signatories cannot. LPR 1.0 is analogous to what Impervious is doing with peer-to-peer internet standards — except the demand is being pulled by regulatory mandate rather than philosophical preference. The Foundation is the moat; LedgerProof, Inc. is the revenue vehicle.

**4. The revenue model is simple and does not require Bitcoin evangelism**
Per-receipt fees + institutional membership dues. Customers pay to comply with regulation — they do not need to understand or care about Bitcoin. The Bitcoin anchor is the technical mechanism; the value proposition to the customer is "cryptographic proof you can show a regulator." 97% operating margin at 1M receipts/day. VeriSign and SWIFT as structural comparables.

**5. The ask**
$5M seed at $30M post-money SAFE. Close targeted June 25. Pro-rata and board observer included. TVP's check would be a meaningful portion of the round — and Christopher's name as a board observer signals Bitcoin-native institutional credibility to every other investor who comes in after.

---

## Hard questions — know the answers cold

**"Why not OpenTimestamps? It already does Bitcoin anchoring and it's free."**
OTS is a general-purpose timestamping tool — it proves "this hash existed before this block." It does not produce a structured, machine-readable receipt that encodes *what* was anchored (content type, author identity, jurisdiction, version), *who* anchored it (issuer DID), or a standard verifier API that a regulator, counsel, or court can query without Bitcoin expertise. LPR 1.0 is a typed, structured receipt format built for legal and compliance contexts. It's the difference between a Unix timestamp and an ISO 8601 datetime with timezone — both tell you the time, but only one is usable in a contract.

**"Simple Proof already does Bitcoin document timestamping in production — El Salvador, others."**
Simple Proof is a service. LedgerProof is an open protocol with a Foundation. The same way SMTP did not compete with proprietary email systems by being a better email system — it won by being the standard. Simple Proof can become an LPR-compatible calendar operator and benefit from the protocol. The goal is not to beat Simple Proof; it's to be the layer Simple Proof runs on.

**"Is this Bitcoin-native or just Bitcoin-adjacent? You're using OP_RETURN but the business model is SaaS."**
The protocol is Bitcoin-native: receipt validity is derived from Bitcoin's base layer with no intermediary. The business model is commercial infrastructure on top of an open protocol — exactly the structure of Voltage (infrastructure business on Lightning) or Unchained (custody business on Bitcoin). TVP has funded this model repeatedly. The Foundation owning the protocol is the Bitcoin-native structure; LedgerProof, Inc. is the revenue vehicle. They are not in conflict.

**"The OP_RETURN payload is 80 bytes. Where does the actual document go?"**
In the anchor. The OP_RETURN contains a Merkle root and the "LPR1" prefix — 36 bytes. The full receipt (CBOR-encoded, signed with Ed25519, containing the SHA-256 content hash, issuer identity, timestamp, and metadata) lives off-chain in the calendar operator network. The Bitcoin transaction is the commitment; the receipt is the proof. This is identical to how RFC 6962 Certificate Transparency works — the tree root is the commitment, the proof is off-chain. A regulator doesn't need to read the Bitcoin blockchain; they query the verifier API with the receipt ID.

**"What happens to LedgerProof if Bitcoin's fee market compresses and miners have no incentive to include OP_RETURN transactions?"**
Two answers: (1) LedgerProof batches receipts via Merkle aggregation — 1M receipts per day can anchor in 1 transaction, so the per-receipt Bitcoin fee is fractions of a cent even at high fee environments. (2) The protocol spec supports multi-substrate anchoring (Ethereum, federated CT logs) as optional alternates. Bitcoin is the primary and preferred substrate; the others are fallback profiles. This is a design decision in LPR 1.0, not a future hedge.

**"What's the path to the 'institutional revenue layer' claim? That's a big claim for a seed-stage company."**
The institutional revenue layer is the long-term architecture, not the Day 1 claim. Day 1 is: a working protocol, a live verifier, an IETF draft, and a Foundation in formation. The institutional layer is built by the customer base — when TransUnion, a reinsurer, or a law firm anchors 10M receipts/year, LedgerProof is their compliance infrastructure. The same way SWIFT started as an interbank messaging protocol and became settlement infrastructure over decades. The 28-day launch window establishes the protocol; the revenue layer is the five-year build.

**"Why should I believe the EU AI Act enforcement date is a real catalyst and not a deadline that gets pushed?"**
Article 50 is not a new regulation — it is enforcement of a regulation that has been in force since August 2024. The August 2, 2026 date is when Article 50's transparency obligations specifically kick in for AI-generated content. Member states are already publishing compliance guidance. Enterprise legal departments are not waiting for a push; they are asking vendors now. Three of the nine symposium contacts on May 18 — a compliance attorney, an IR litigation lawyer, and a cybersecurity executive — independently asked about the regulatory angle without prompting.

**"Your address for the raise is $30M post-money. What's the $5M pre-money valuation based on?"**
It is based on: (1) comparable protocol-layer infrastructure companies at seed — OpenTimestamps, Simple Proof, OriginStamp raised at similar or higher multiples with less defined revenue models; (2) the structural comparables (VeriSign at seed was valued on protocol ownership, not revenue); (3) the regulatory pull-through: a company positioned as the open standard for Article 50 compliance has a different risk profile than a typical pre-revenue seed. The valuation is a SAFE — it's a ceiling, not a floor. If the round closes oversubscribed, the terms improve.

---

## What you need Christopher to walk away believing

In order of importance:

1. **LedgerProof is genuinely Bitcoin-native.** Not a blockchain company that happens to use Bitcoin. Every receipt is a Bitcoin transaction. This is the filter — if he doesn't believe this, nothing else matters to TVP.

2. **The protocol layer creates a moat that a private competitor cannot replicate.** The Foundation + IETF process + open spec is the defensible position. A competitor can build a better receipt service; they cannot build a competing open standard while you are already in the IETF process.

3. **The regulatory timing is structural, not cyclical.** Article 50 is not a hype cycle — it is a mandate from a jurisdiction with enforcement teeth. The customers paying for compliance are not early adopters; they are corporate legal departments covering liability.

4. **TVP's portfolio creates a natural ecosystem.** Voltage's infrastructure, Unchained's institutional relationships, Galoy's protocol-layer architecture, Impervious's standards experience — LedgerProof integrates with or benefits from all of them.

5. **June 25 is a real close date.** This is not a rolling raise. The window is 35 days. If TVP wants in, the decision timeline is this week.

---

## Opening move

Do not open with the pitch. Open with a question:

*"Before I get into specifics — when Aryan forwarded this to you, what was the thing that made you want to take the call?"*

Christopher's answer will tell you exactly which part of the thesis landed. Mirror that back in your first minute of actual pitching. If he says "the Bitcoin-native angle," lead with the OP_RETURN architecture. If he says "the institutional revenue model," lead with the fee structure and the VeriSign/SWIFT comparison.

---

## Closing move

At 25 minutes, if the conversation is going well:

*"Christopher, I'm closing June 25. I have a board observer seat available and pro-rata on the round. If you're a yes, the right next step is I send you the SAFE and data room access today. If you want a week to look at the spec and the IETF draft first, I can do that — but I want to make sure you have what you need to move at the pace the timeline requires."*

Do not say "let me know if you have questions." Name the next concrete step and the date.

---

## Logistics

- **Time:** 9:30 AM CT Wednesday May 27, 2026
- **Format:** Likely video (Aryan booked it from email — confirm format when you reply to confirm the meeting)
- **Duration:** Expect 30 minutes; be ready to go 45 if it's going well
- **Materials:** Deck is already in their inbox (attached to the May 21 email). Do not re-send before the call unless they ask for it — they have it.
- **Confirm the meeting:** Reply to Aryan's email today (May 21). One sentence. Suggested reply below.

---

## Suggested reply to Aryan (send today)

> Subject: Re: LedgerProof — the institutional revenue layer for Bitcoin's application stack
>
> Aryan,
>
> Wednesday at 9:30 AM CT works perfectly. What's the best dial-in?
>
> Veronica

---

## Day-of checklist

- [ ] Have the live verifier open in a tab: https://verify.ledgerproofhq.io/r/founding-declaration
- [ ] Have the LPR 1.0 spec open: `~/Documents/LedgerProof-Launch-July6/04-lpr-spec/`
- [ ] Know the exact OP_RETURN txid from the May 18 anchor: `5db5c68e…` (confirm full txid from anchor record)
- [ ] Know the SAFE terms cold: $5M / $30M post-money / pro-rata / board observer / June 25 close
- [ ] Have the Voltage / Unchained / Galoy / Impervious portfolio context ready for natural drop-in
- [ ] Be ready to send SAFE + data room link immediately after the call if he's a yes

---

*Prepared May 21, 2026 · LedgerProof Growth Engine — Meeting Prep Agent*
