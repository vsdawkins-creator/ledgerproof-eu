# Meeting Prep — Fulgur Ventures
## TBD (this week or next week) · 30 minutes

---

## The room

**Michele Anastasio — Investment Team**
- Fulgur's investment team member who reached out — likely your primary point of contact through diligence
- His name first on the reply email suggests he ran the initial screen and is championing the deal internally
- Treat him as the deal champion: he wants this to work, but needs you to give him the ammunition to convince Oleg

**Oleg Mikhalsky — Partner**
- Co-founded Fulgur Ventures — the senior decision-maker on the call
- Italy-based Bitcoin investor with deep technical background; was involved in early Lightning Network development and infrastructure
- Public posture: more reserved than the US Bitcoin VCs, will ask precise technical questions, less likely to be moved by narrative and more by code/architecture/regulatory specifics
- The European Bitcoin investor perspective: regulatory clarity matters more, market access matters more, time horizons are typically longer
- He's joining means this is real — Fulgur partners do not take exploratory meetings

**Why both names matter:** Michele opened the door; Oleg evaluates. You need to talk to both audiences simultaneously — Michele wants to look smart for championing this; Oleg wants to be convinced by substance, not enthusiasm.

---

## Why they said yes

Fulgur is the **European Bitcoin-native fund** — and LedgerProof is the **only Article 50 protocol with an EU production deployment** as of today. That alignment isn't coincidence; it's the entire reason Fulgur is the natural fit:

- LedgerProof is operationally European (Frankfurt operator, EU data residency)
- The Article 50 enforcement event is European
- The regulatory engagement record is European (EU AI Office, AESIA, planned outreach to BfDI/CNIL/Garante/AP)
- The Foundation will have an EU establishment as a wholly-owned subsidiary

This is the ONE Bitcoin-native fund where "we're operationally European" is a key value driver, not a footnote. Lean into that.

---

## What changed since the outreach

Same delta as for Stillmark — the original outreach materials substantially understate what's actually shipped. Update them on:

- **LPR v1.1 deployed to production in Frankfurt** today — only protocol covering all four Article 50 sub-obligations
- **3 npm packages live globally**
- **Regulator emails sent today** in EN + FR (EU AI Office) and ES + EN (AESIA)
- **IETF draft submitted** to SCITT working group
- **C2PA assertion spec written** for CAWG submission
- **EU AI Code of Practice signatory application** prepared

Fulgur will care about the **regulatory record** more than the other two funds. Show them the email outboxes.

---

## Fulgur portfolio context

| Company | Fulgur role | Notes for LedgerProof |
|---|---|---|
| **Lightning Labs** | Early backer | Bitcoin Lightning infrastructure — same protocol-layer thesis |
| **Voltage** | Co-investor (with TVP) | Bitcoin & Lightning hosting infrastructure |
| **Strike** | Early | Bitcoin payments for institutions |
| **Mash** | Backer | Lightning payments for content / publishing — interesting LedgerProof crossover potential |
| **Various EU Bitcoin infra** | — | Fulgur sees the EU Bitcoin landscape better than any US fund |

**Portfolio pattern:** Fulgur invests where Bitcoin or Lightning is the *infrastructure layer*, and where European jurisdictional positioning matters. They are less likely than US funds to take pure consumer-app bets; they are more likely than US funds to take infrastructure bets that depend on EU regulatory clarity.

**LedgerProof fits because:** Article 50 enforcement is a European regulatory event creating European institutional demand for European-resident Bitcoin-anchored compliance infrastructure. That sentence is the entire reason Fulgur should lead this round.

---

## Your positioning — Fulgur-specific differentiators

What you emphasize with Fulgur that you don't lead with at TVP or Stillmark:

### 1. EU operational reality

LedgerProof is **EU-operational, not US-pretending-to-be-EU**. The Frankfurt deployment is real. The data residency is real. The EU subsidiary is planned. The regulator outreach is in EU languages. The IETF draft cites the EU AI Act by article number. The Foundation will have an EU establishment.

US Bitcoin-VC-backed companies routinely promise "EU expansion" and then take three years to deliver it. LedgerProof started EU-resident.

### 2. The regulatory event is non-discretionary

EU AI Act Article 50 enforces August 2, 2026. €15M fines or 3% global revenue. This is **mandatory compliance for any company deploying AI-generated content in the EU**. There's no opt-out, no "we'll do it next year," no waiver. Every enterprise selling AI services to EU customers must comply.

This is qualitatively different from US AI regulation — which is currently voluntary frameworks (NIST RMF, voluntary commitments, state-by-state laws). Fulgur understands this distinction; their US peers underweight it.

### 3. The Italian / EU jurisdictional angle

If Fulgur leads the round, LedgerProof Inc.'s EU subsidiary becomes natively connected to:
- Italian Garante for data protection diligence (Oleg has relationships)
- Italian Bitcoin community for early pilot customers (Bitstack, Italian banks experimenting with Bitcoin treasury, Italian legal-tech firms)
- The European Bitcoin community at large — Fulgur is the convener of much of the EU Bitcoin VC scene
- Italian and pan-European Lightning Network adoption — relevant for LedgerProof's per-receipt billing layer

Stillmark is UK-based, post-Brexit. **TVP is Texas-based.** Fulgur is the only fund of the three that's *natively inside* the EU regulatory perimeter where LedgerProof will be enforced.

### 4. The Foundation will need EU governance

The Foundation's eventual EU establishment will need:
- An EU board member or advisor familiar with EU regulatory dynamics
- An EU bank account and operational footprint
- EU legal counsel
- EU pilot customer introductions

Fulgur sits on all four of those answers in ways the US funds don't.

---

## Pitch structure for this 30 minutes

**1. Acknowledge the EU jurisdiction directly** (3 min)

Open: *"Of the three Bitcoin-native funds I'm talking with this week, Fulgur is the only one operationally inside the EU jurisdiction where Article 50 will actually be enforced. I want to lead with that — because everything else we'll talk about flows from it."*

**2. Show the protocol is shipped and EU-resident** (5 min)

Same verifier-URL move as Stillmark. Send the link in chat. Add: *"This is hosted in Frankfurt by Fly.io. EU data residency, EU TLS, signed Ed25519 receipt anchored to Bitcoin mainnet OP_RETURN. The Frankfurt deployment has been live for 70+ days."*

**3. The regulatory engagement record** (5 min)

This is Fulgur's specific differential interest. Show them:
- The email outbox screenshot with today's send to `CNECT-AIOFFICE@ec.europa.eu` cc'd to the Cabinet of EVP Virkkunen, in EN + FR
- The same emails to AESIA in ES + EN
- The Gap Analysis document showing how LPR v1.1 maps to the Commission's draft guidelines section by section
- The Code of Practice signatory application drafted and ready

*"There is no other Bitcoin-anchored compliance protocol that has an EU regulatory engagement record. That's not a marketing claim — it's a literal fact based on the IETF draft search and the C2PA member list."*

**4. The Bitcoin-native architecture** (4 min)

Same Bitcoin-native pitch as Stillmark — OP_RETURN, no token, no sidechain, Merkle aggregation. But for Fulgur, emphasize: *"This works on Bitcoin's base layer with the same architectural primitives Lightning Labs uses for HTLCs and Mash uses for payment routing — these are the same kind of low-level primitives Fulgur evaluates."*

**5. The financial picture and the Italian / EU partnership angle** (5 min)

Round terms: $5M at $30M post-money SAFE, June 25 close. Three Bitcoin-native funds at the table; round can comfortably expand to $6–7M.

For Fulgur specifically:
- A Fulgur lead position would make LedgerProof's EU operational positioning *visible* to the rest of the European Bitcoin community
- Fulgur's network gives LedgerProof Italian / EU pilot customer access that US funds can't provide
- The EU subsidiary will need EU-resident board members eventually; Oleg is the natural candidate

**6. The ask** (3 min)

*"Michele, Oleg — I'd like Fulgur to evaluate this for a lead position. The other two funds are credible but the European jurisdictional angle makes Fulgur the strongest natural fit. Tell me what diligence you need to run, and what timeline you'd want for a term sheet decision."*

---

## Hard questions — know the answers cold

**"How do you handle GDPR Article 17 erasure when the receipt is anchored to Bitcoin permanently?"**

This is the question that will come from a European investor. The answer:

The Bitcoin anchor commits to a **Merkle root**, not to the receipt content. The actual content (the deployer's name, the AI system identifier, etc.) lives in the operator's database. When a GDPR Article 17 erasure request comes in, the operator **nulls the content fields** in the database while preserving:
- The receipt's `entry_hash` (the cryptographic identity)
- The `signature`
- The `prev_hash` chain link

The Bitcoin anchor remains valid — it commits to the Merkle root, which still resolves to the (now-nulled) entry. The chain integrity is preserved. The personal data is gone. This is documented in `12-eu-compliance/03-GDPR-ARCHITECTURE-AND-DPA.md` and validated by the EU production deployment's `DELETE /v1/entries/:seq` endpoint, which is publisher-owner-only.

A regulator reviewing this would see: erasure honored within the GDPR-mandated window, chain integrity preserved, no actual personal data ever anchored on-chain (because only the Merkle root goes to OP_RETURN, never the receipt body).

**"What's your relationship to the Italian regulator landscape — Garante, AGCOM, AESIA equivalents?"**

Direct answer: limited so far, but the regulatory engagement record we're building this month is the foundation. We've sent formal communications to AESIA (Spain) and to the EU AI Office in three languages. The Italian Garante and AGCOM are in the Q3 outreach plan documented in the master strategic plan. With Fulgur in the round, those introductions accelerate substantially.

**"What about Italian and EU language localization for the SDK and the docs?"**

The Python SDK, TypeScript SDK, and Cloudflare Workers binding are language-agnostic. The documentation site (Astro Starlight) supports i18n natively. The regulator-facing materials are already prepared in EN/FR/ES; DE, IT, NL are on the Q3 roadmap. With Fulgur's introductions, Italian goes to Q2.

**"How is LedgerProof different from Italian Bitcoin compliance startups already in Fulgur's portfolio or pipeline?"**

There aren't any. The Italian Bitcoin VC scene has not produced an EU AI Act compliance protocol. The EU compliance landscape today is dominated by US-based C2PA tooling (Adobe, Microsoft) and traditional EU PKI vendors (qualified electronic seal providers). LedgerProof is the first Bitcoin-native option, and it's the only option with all four Article 50 sub-obligations covered.

**"What's the relationship between LedgerProof Inc. and the Foundation? Is this a 'Foundation in name only' or genuinely separate?"**

Genuinely separate. The Foundation will have a majority-external board; the protocol specification is published under CC BY 4.0 (so anyone can implement); the reference Rust code is Apache 2.0 (so anyone can run an operator); the federated calendar operator pattern is in the spec from day one. LedgerProof Inc. is the EU reference operator and the per-receipt billing entity, but it does not have veto power over protocol evolution.

A future scenario: an Italian Bitcoin infrastructure company decides to run a competing calendar operator. They use the open specification, register with the Foundation, and start issuing LPR receipts independently. LedgerProof Inc. has zero ability to stop them. **That's the Foundation governance model. The protocol cannot die with the company.**

**"You said three funds are bidding — what's the actual sequence and timing?"**

- TVP first conversation Wednesday May 27 (already scheduled)
- Stillmark — pending Calendly scheduling
- Fulgur — this conversation
- Decision target: term sheet from at least one fund by end of next week; round close June 25
- I'm not running a tight competitive process to extract optimal valuation. I'm running parallel evaluations because three Bitcoin funds independently identified the same fit in the same week. The round size can expand to accommodate all three.

**"What's the operational risk of running on Bitcoin? Bitcoin fees spike, network congestion, etc."**

Two layers of mitigation:
1. **Merkle aggregation** — 1M receipts/day batch into a single OP_RETURN. Per-receipt fee is cents at any realistic Bitcoin fee environment.
2. **Multi-substrate fallback** — the LPR spec documents Ethereum CT-style logs and RFC 3161 qualified timestamp authorities as optional alternates. Bitcoin is the primary substrate; alternates exist for catastrophic Bitcoin-only failures.

Operationally, the Frankfurt deployment has been live for 70+ days without incident. The cost-of-anchor per receipt at current Bitcoin fee levels is well under €0.001 per receipt at scale.

---

## What you need Michele and Oleg to walk away believing

In order of importance:

1. **LedgerProof is operationally EU, not US-claiming-EU.** Frankfurt deployment, EU data residency, EU subsidiary planned, EU regulator engagement record. This is Fulgur's natural fit.

2. **The Article 50 enforcement event is non-discretionary regulatory demand.** Not a hype cycle. Mandatory compliance for every AI deployer with EU exposure starting August 2, 2026.

3. **The Bitcoin-native architecture is genuine.** OP_RETURN anchoring, no token, no sidechain. Same protocol primitives Fulgur evaluates in its existing portfolio.

4. **The Foundation structure protects the long-term moat.** Open spec, open reference code, federated operators. No proprietary lock-in.

5. **The round has room for Fulgur to lead.** With three credible bids in the same week, the round can expand. Fulgur's natural advantage: EU jurisdictional positioning that the US funds can't match.

---

## Opening move

Send the verification URL in chat before starting:

> "Michele, Oleg — before we get into the deck, this is a Bitcoin-anchored LPR receipt issued by our Frankfurt operator earlier today: https://api-eu.ledgerproofhq.io/v1/verify/0
>
> The hosting is Fly.io fra. EU data residency. Ed25519 signature. The OP_RETURN data field on Bitcoin mainnet is `LPR1` + 32-byte Merkle root. The receipt format is the IETF draft I filed this week.
>
> What does Fulgur want me to know about how you evaluate EU-resident Bitcoin infrastructure?"

That last question is specifically Fulgur-flavored — different from the Stillmark opening. It surfaces the EU angle immediately.

---

## Closing move

At ~25 minutes:

> "Michele, Oleg — the round is $5M at $30M post, June 25 close. I'm in conversations with TVP and Stillmark in the same week. Each of you can take a meaningful piece. The reason I'd genuinely like Fulgur to be in this round, and ideally to lead, is that the Article 50 enforcement is happening in your jurisdiction. The EU subsidiary will need EU board representation eventually. Italian and EU pilot customer access matters. Fulgur is the natural fit there in a way the US funds can't replicate.
>
> What diligence do you want to run, and what timeline can you commit to a term sheet decision?"

The explicit naming of "lead" gives Oleg a specific decision to make. The mention of TVP/Stillmark is honest without being manipulative — both are public-knowledge potential investors in this round.

---

## What you absolutely don't do

- **Don't** play the funds off each other on price. Bitcoin-native VC is a small ecosystem; they will compare notes.
- **Don't** disclose TVP's or Stillmark's specific term proposals. You can confirm the round is competitive; you don't reveal counterparty terms.
- **Don't** position this as Italian-or-nothing. Be enthusiastic about Fulgur's fit without alienating the other two.
- **Don't** over-emphasize the Italian angle to the point that Oleg feels you're flattering him. Stick to operational facts.

---

## Logistics

- **Schedule:** Use your own Calendly (Michele asked for time on your calendar) — offer 3–4 slots this week or next, prioritize late this week / early next so it lands close to Stillmark
- **Format:** Video — likely Google Meet or Zoom
- **Duration:** 30 min, prep for 45
- **Time zones:** Italy is CET (UTC+1), so afternoon Italy = morning California — workable
- **Language:** English. Oleg's English is fluent; Michele's likely is too. Don't open in Italian unless they do.

---

## Day-of checklist

- [ ] Verifier URL ready: `https://api-eu.ledgerproofhq.io/v1/verify/0`
- [ ] Frankfurt deployment proof point — health endpoint URL handy
- [ ] EU regulator email screenshots/proofs handy (the four sent today)
- [ ] IETF draft .txt file accessible
- [ ] npm package URLs ready
- [ ] Gap analysis document (`12-eu-compliance/11-EU-ART50-GAP-ANALYSIS.md`) open in a tab
- [ ] EU Code of Practice signatory application document open
- [ ] Know your ask: Fulgur lead position, with TVP + Stillmark as co-investors or follow-ons
- [ ] Be ready to discuss the EU subsidiary structure if asked

---

*Prepared 25 May 2026 · LedgerProof Foundation Investor Relations*
