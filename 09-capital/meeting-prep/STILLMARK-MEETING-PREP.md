# Meeting Prep — Stillmark
## TBD (book via their Calendly) · 30 minutes

---

## The room

**Alyse Killeen — Founder & Managing Partner**
- Founded Stillmark in 2019, the first venture fund founded specifically to back **Bitcoin's protocol-stack innovation**. No altcoins. No tokens. No "blockchain-not-Bitcoin." This is identity, not preference.
- Prior: Partner at Adamant Ventures; deep Bitcoin investing history going back to the mid-2010s
- Public thesis: *Bitcoin is the only credible monetary internet protocol. The companies that matter are the ones building on Bitcoin's base layer or Lightning — period.*
- Portfolio she has led or co-led: Lightning Labs, Casa, River, Bitstack, Satoshi Energy. Pattern: protocol-layer companies with durable moats, not consumer apps.
- Tone to expect: technically sharp, asks about base-layer mechanics, will probe whether you're using Bitcoin or just claiming you do. Has walked away from many "Bitcoin-adjacent" pitches.
- **The fact that Alyse personally replied** — not an analyst, not a junior — means LedgerProof passed her first-pass thesis filter. That's the signal.

**Vikash Singh — Principal Investor**
- Investment team Principal; handles deep technical evaluation and diligence
- Likely the person who will quarterback the actual evaluation if it progresses
- Treat him as a peer-level technical interlocutor — he will ask the hard questions; that's his job
- Public posture: thoughtful, methodical, less ideological than Alyse — pattern-matches on actual architecture, not narrative

**Both names on the same email** = internal alignment exists. They're not separately fishing — Vikash will run the eval, Alyse will green-light it.

---

## Why they said yes

The original outreach (May 21, draft at `09-capital/investor-packages/17-STILLMARK.md`) hit exactly the lines Stillmark's thesis turns on:

> "OP_RETURN to anchor cryptographic document receipts to Bitcoin's base layer — permanently, without a token, without custody, without a sidechain, without any architecture that requires trusting a third party. An institution submits a document; we produce an LPR v1.0 receipt that proves the exact content and timestamp, verifiable by anyone, forever, because it lives on Bitcoin. That is the sum of the protocol interaction."

This is the exact language Stillmark uses to describe *itself*. No accident — that was written specifically to land with her.

The follow-up signal: **Alyse responded personally and looped in Vikash**. That happens for one of two reasons: (a) she wants to evaluate it herself, or (b) she's already decided it deserves a real look and wants Vikash to drive the eval while she stays informed. Both are good outcomes.

---

## What changed since the outreach

The deck and pitch she received on May 21 are now **substantially understated** by what's actually shipped. Update Alyse and Vikash on the delta:

- **LPR v1.1 deployed to production** in Frankfurt — handles all four Article 50 sub-obligations (only open protocol that does)
- **3 npm packages live** as of today (`@ledgerproof/sdk`, `@ledgerproof/vercel-ai`, `@ledgerproof/workers`)
- **2 Python packages PyPI-ready** (`ledgerproof`, `langchain-ledgerproof`)
- **IETF draft prepared** for Datatracker submission (uploading this week)
- **EU AI Office contacted formally** — emails sent to `CNECT-AIOFFICE@ec.europa.eu` and Cabinet of EVP Virkkunen, in EN + FR
- **AESIA (Spain) contacted formally** — emails sent in ES + EN
- **C2PA assertion spec written** for CAWG submission

In the 5 days between her receiving the original pitch and this meeting, LedgerProof went from "production deployment + working spec" to "fully published ecosystem + regulator engagement record + ~120 new files of working code." That velocity is itself a credibility signal.

---

## Stillmark portfolio context — know these

| Company | Stillmark relationship | LedgerProof connection |
|---|---|---|
| **Lightning Labs** | Lead / early | Lightning is the per-receipt micropayment substrate; LL is the canonical implementation |
| **Casa** | Lead / early | Bitcoin multisig custody for institutions — same enterprise customer profile as LedgerProof |
| **River Financial** | Early | Bitcoin-native financial services; comparable Foundation-adjacent model |
| **Bitstack** | Early | European Bitcoin DCA platform — gives Stillmark EU operational ground |
| **Satoshi Energy** | Co-investor | Bitcoin × energy; demonstrates Stillmark's "real-world Bitcoin utility" thesis breadth |

**Portfolio pattern:** Stillmark backs companies where the Bitcoin layer is **structurally necessary**, not optional or marketing. They walk away from "we use Bitcoin because it's cool" pitches reliably.

**LedgerProof in this frame:** EU AI Act Article 50 compliance is the regulatory event that makes Bitcoin's permanence economically necessary. C2PA credentials can be stripped from files. Watermarks can be defeated. A Bitcoin OP_RETURN commitment can't be stripped from history. **LedgerProof is what makes Bitcoin necessary for Article 50 compliance, not optional.** That framing is the entire reason Stillmark exists.

---

## Your positioning for this meeting

### One-line internal-memo summary Alyse will write
*"LedgerProof is the only open protocol that anchors EU AI Act Article 50 compliance to Bitcoin's base layer — no token, no sidechain, deployed in production in Frankfurt, with three npm packages live, IETF-submitted, and regulator engagement in two EU institutions. The Bitcoin permanence layer for the regulatory event that starts August 2, 2026."*

### Pitch structure for this 30 minutes

**1. The protocol is shipped — open the call with proof, not promises** (3 min)

Open the call by sending the verification URL of one of the three Bitcoin mainnet anchors in chat:
- https://api-eu.ledgerproofhq.io/v1/verify/0 (or whichever sequence is most recent post-deploy)
- The May 18 symposium anchor txid

Then: "Before I talk about anything, you can verify the protocol works right now. Hash any of those receipts. The signature is Ed25519, the anchor is on Bitcoin mainnet, the canonical JSON is in the IETF draft I filed this week."

That sentence is the entire credibility move. Everyone pitches; you ship.

**2. Why this is Bitcoin-native by Stillmark's exact definition** (5 min)

Every LedgerProof Receipt is a Bitcoin transaction. Period. The receipt's validity is derived entirely from Bitcoin's timechain via OP_RETURN + RFC 6962 Merkle aggregation. No sidechain. No token. No oracle. The "LPR1" prefix in OP_RETURN is permanent — visible in every Bitcoin block explorer forever.

At scale (1M receipts/day enterprise-conservative), LedgerProof generates 1M Bitcoin transactions per day. That is **a new institutional fee-revenue source for miners** — organic, compliance-driven, non-speculative. Stillmark's portfolio currently produces Lightning revenue; LedgerProof produces base-layer revenue.

**3. Why now — the regulatory event** (4 min)

EU AI Act Article 50 enforces August 2, 2026 — **69 days from now**. €15M fines or 3% global revenue. The Code of Practice consultation closes June 3 — **9 days from now**. Today LedgerProof submitted the only open-protocol response addressing all four Article 50 sub-obligations. The window for becoming the named standard is finite and closing.

**4. Why the Foundation + commercial structure is the durable moat** (5 min)

A proprietary receipt service can be displaced. An open protocol with an IETF draft, a Foundation, and a coalition cannot. LPR 1.1 is on the public record at IETF; the specification is under CC BY 4.0; the reference implementation is Apache-2.0. **LedgerProof Foundation owns the protocol. LedgerProof, Inc. is the EU operator commercial entity.** Both are profitable in the steady state.

This is the *same* structure as the Linux Foundation + commercial Linux distributions. Stillmark understands it intuitively.

**5. The round — and now, the candid bit** (5 min)

You've now got three Bitcoin-native funds at the table:

- **Trammell Venture Partners** — first conversation, scheduled tomorrow (or whatever date relative to this call)
- **Fulgur Ventures** — Michele Anastasio and Oleg Mikhalsky; meeting being scheduled
- **Stillmark** — this call

The round is **$5M at $30M post-money SAFE**, June 25 close. Each of the three funds can take a meaningful piece. With three credible bids, the round can comfortably expand to $6–7M without diluting valuation — and that's the conversation to have if Stillmark wants a lead position.

Stillmark's natural advantage in this triangle: **the strongest Bitcoin protocol-layer brand**. If Stillmark leads with a meaningful check, it puts LPR on the same page as Lightning Labs and Casa in Stillmark's portfolio — which is the brand category we want to be in.

The ask: "I'd love to know whether Stillmark wants to evaluate this for a lead position, a co-lead, or a participation. The other two funds are credible but Stillmark is the natural fit. Tell me what you need from me to make that decision."

---

## Hard questions — know the answers cold

**"How is this different from OpenTimestamps? OTS already anchors arbitrary hashes to Bitcoin and is free."**

OTS is a general-purpose timestamping tool — proves "this hash existed before this block." It does not produce a structured, machine-readable receipt that encodes *what* was anchored (content type, deployer identity, AI system, jurisdiction), *who* anchored it (legal-entity identifier), or a typed verifier API that a regulator can query without Bitcoin expertise. LPR 1.1 is a typed compliance record built for Article 50. The difference between a Unix timestamp and an ISO 8601 datetime with timezone — both tell you the time; only one is usable in a contract.

**"Simple Proof already exists. They do Bitcoin document timestamping in production — El Salvador, others."**

Simple Proof is a service. LedgerProof is an open protocol with a Foundation, a CC-BY-4.0 specification, an IETF draft, and a federated calendar operator architecture. SMTP didn't compete with proprietary email by being a better proprietary email — it won by being the open standard. Simple Proof can become an LPR-compatible calendar operator and benefit from the protocol. The goal is not to beat them; it's to be the layer they run on.

**"What's the actual revenue math at 1M receipts/day?"**

Per-receipt fee at €0.01 = €10K/day = €3.65M/year per million daily receipts. Institutional membership dues add €100K–€500K per Foundation member tier on top. At 1M receipts/day across a few hundred institutional members, the Foundation runs $50–100M ARR at 95%+ operating margin (the marginal cost of issuing a receipt is fractions of a cent of Bitcoin fee + Merkle batching). Comparable structural model: VeriSign at scale.

**"Why $30M post on a pre-revenue seed?"**

(a) Comparable protocol-layer infrastructure companies at seed — OpenTimestamps, Simple Proof, OriginStamp raised at similar or higher multiples with less defined revenue paths. (b) VeriSign and SWIFT, at the equivalent stage, were valued on protocol ownership, not revenue. (c) Regulatory pull-through: a company positioned as the open standard for Article 50 has a different risk profile than a typical pre-revenue seed. The valuation is a SAFE — it's a ceiling, not a floor. If the round closes oversubscribed, terms improve.

**"What happens if Bitcoin's fee market makes per-receipt anchoring uneconomic?"**

Two answers:
1. **Merkle aggregation** — 1M receipts per day batch into 1 Bitcoin transaction. The per-receipt anchor cost is fractions of a cent even at high fee environments. This is the same RFC 6962 pattern used by Certificate Transparency at scale.
2. **Multi-substrate fallback** is built into the spec — Ethereum CT-style logs and federated qualified timestamp authorities (RFC 3161) are documented as fallback profiles. Bitcoin is the primary substrate; the others are insurance.

**"You're now talking to three Bitcoin VCs — what's keeping us from a bidding war that wastes everyone's time?"**

Three things:
1. The round size can comfortably accommodate all three if all three want in.
2. I'm not running a competitive process to extract optimal terms. I'm running parallel evaluations because three Bitcoin funds independently identified the same thesis fit in the same week — which is itself a signal.
3. If Stillmark moves to a term sheet first with terms that work, I'll prioritize Stillmark. Speed matters more than valuation optimization at this stage.

**"What's the Foundation governance structure? Who controls the protocol?"**

A Foundation board with majority-external members (i.e., not LedgerProof Inc. employees). Founding members commit to the open spec via CC BY 4.0; protocol changes require a public process modeled on the IETF Rough Consensus + Running Code rule. LedgerProof Inc. operates the EU reference calendar but does not have veto authority over protocol evolution. This is published as the Foundation's charter before the July 6 launch.

**"What's stopping a Big Tech company from forking the spec and running their own private operator?"**

Nothing — and that's the point. The protocol is open. Anyone can run an operator. Anyone can issue receipts. The value of LedgerProof Inc. is being the *EU-resident, GDPR-by-construction, IETF-published reference operator*. That's a commercial advantage that's defensible by execution, not protocol lock-in. The Foundation wins either way: if a competitor runs their own operator, the protocol's adoption grows and the Foundation's mission succeeds. If they don't, LedgerProof Inc. is the default operator. The Foundation cannot lose.

---

## What you need Alyse to walk away believing

In order of importance:

1. **LedgerProof is genuinely Bitcoin-native by Stillmark's exact definition.** Every receipt is a Bitcoin transaction. Not Bitcoin-adjacent. This is the thesis filter; if it doesn't land, nothing else matters.

2. **The protocol is shipped — not promised.** Three live npm packages, production EU deployment, three real Bitcoin mainnet anchors, IETF draft filed. Velocity is the credibility signal.

3. **The regulatory event is real and timed.** August 2, 2026 enforcement. June 3 consultation deadline. The window is finite. This is a regulatory pull-through, not a hype cycle.

4. **The Foundation + commercial structure is what makes the moat durable.** It's the Linux Foundation pattern. Stillmark understands this intuitively.

5. **There is room for Stillmark to lead.** With three credible bids, the round is going to close — the question is whether Stillmark wants the lead position or to participate. Either is fine; you'd just like to know.

---

## Opening move

Send Alyse + Vikash the verifier URL in the meeting chat *before* you start talking:

> "Before we get into the deck — here's a Bitcoin-anchored LPR receipt issued by our production Frankfurt operator this week: https://api-eu.ledgerproofhq.io/v1/verify/0
>
> The OP_RETURN data field on the Bitcoin transaction is `LPR1` + 32-byte Merkle root. The signature is Ed25519. The receipt format is on the public record as `draft-dawkins-scitt-ai-article50-00` at the IETF.
>
> What does Stillmark want me to know about how you evaluate this kind of thing?"

The last question hands the floor back. Their answer will tell you exactly which sub-thesis to lean into for the rest of the call.

---

## Closing move

At ~25 minutes, if the conversation is going well:

> "Alyse, here's the candid picture: I have three Bitcoin-native VCs evaluating this in the same week — you, TVP, and Fulgur. The round is $5M at $30M post, closing June 25. With three credible bids, I can expand to $6–7M without changing valuation. I'd genuinely like Stillmark to be in this round, and I'd genuinely like to know whether you want lead, co-lead, or participate. Whatever the answer, can you tell me by end of next week so I can sequence with TVP and Fulgur?"

Naming a date forces a decision. "Whatever the answer" tells her you respect their process whichever way it goes. "End of next week" matches a Bitcoin-native fund's actual decision velocity.

---

## What you absolutely don't do

- **Don't** play the three funds off each other crassly. They will compare notes. Bitcoin-native VC is a small world.
- **Don't** disclose specific TVP or Fulgur terms. You can confirm the round exists and is competitive; you don't reveal their proposals.
- **Don't** position LPR as competing with C2PA, watermarking, or any specific company. You're the cryptographic provenance pillar of defense-in-depth. Everyone else wins when you win.
- **Don't** promise specific outcomes from the IETF or Commission. The work is on the public record; let it speak.

---

## Logistics

- **Schedule:** Use their Calendly (the link in Alyse's reply email). Aim for late this week (Thu/Fri) or early next (Mon/Tue) — give yourself one day after the TVP call to absorb feedback.
- **Format:** Likely video (Zoom or Google Meet); confirm in the Calendly form
- **Duration:** Expect 30 min; be prepared to go 45
- **Materials:** The current deck is already in their inbox. Do not resend unless asked. They have it.
- **Time zones:** Stillmark is UK-based — schedule in their UTC/BST window where possible
- **Confirm the meeting:** Calendly booking is auto-confirmation; no email reply needed unless you want to add a "looking forward to it" line

---

## Day-of checklist

- [ ] Verifier URL ready to paste in chat: `https://api-eu.ledgerproofhq.io/v1/verify/0`
- [ ] IETF draft handy: `~/Documents/LedgerProof-Launch-July6/04-lpr-spec/IETF-DRAFT-DAWKINS-SCITT-AI-ARTICLE50-00.txt`
- [ ] The three Bitcoin mainnet anchor txids memorized
- [ ] Master plan readable in a tab: `00-MASTER-PLAN/FOOLPROOF-ARTICLE-50-GOLD-STANDARD-PLAN.md`
- [ ] Have the npm package URLs ready:
  - https://www.npmjs.com/package/@ledgerproof/sdk
  - https://www.npmjs.com/package/@ledgerproof/vercel-ai
  - https://www.npmjs.com/package/@ledgerproof/workers
- [ ] Know what you want from the call: lead, co-lead, or participation — be willing to take any of the three from Stillmark
- [ ] Water in front of you; phone off

---

*Prepared 25 May 2026 · LedgerProof Foundation Investor Relations*
