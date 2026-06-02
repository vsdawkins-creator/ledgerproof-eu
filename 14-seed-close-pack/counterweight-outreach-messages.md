# Counterweight Anchor Outreach Messages

**Generated**: Monday June 1, 2026 — 20:35 PDT
**Author**: Veronica S. Dawkins
**Status**: READY TO SEND — first messages go Wed Jun 3
**Linked**: [`counterweight-anchor-targets.md`](counterweight-anchor-targets.md), [`04-atomic-explosion-master-plan.md`](04-atomic-explosion-master-plan.md) §0 (C8), §8 (KS3), `ops-state.json` KS3
**Window**: T+62 days to Article 50 enforcement (Tue Aug 2, 2026). T+21 days to counterweight LOI deadline (Mon Jun 22, 2026).

---

## Purpose of this file

The targets list (`counterweight-anchor-targets.md`) names who to engage and why. This file is the actual prose I will send — primary outreach, the broker-intro requests, and the Day+5 follow-ups. Each section is ready to copy into LinkedIn, the email client, or a Signal handoff to a broker.

Every message has been written against three constraints:

1. **C1 honored**: no claim that LedgerProof confers presumption of conformity under Article 40. Article 50 is described as a transparency obligation, the protocol as the verifiable evidence trail, regulator engagement as ongoing — never endorsed.
2. **C4 honored**: the protocol is open, verification is local (Merkle proof + Ed25519 signature + Bitcoin anchor — offline, no LP server in the loop). Anchor partners are not signing up for a SaaS dependency. LedgerProof Inc. is the operator of the convenience verification nodes and the SDK; LedgerProof Foundation is the steward of the open protocol and the Bitcoin-anchored ledger. Both entities are named where the distinction matters.
3. **Voice**: direct, specific dates, specific numbers, specific names. No "we're excited." No "we believe AI can be a force for good." Each message reads as a founder writing to another operator about a 21-day window.

The deal-shape ask in each message follows the target sheet exactly: Founding Member tier with a warrant component and a Foundation Advisory Council seat. The warrant is in LedgerProof Inc.; the Council seat is in the Foundation. Both entities are referenced precisely because that distinction is the credibility test — if the message blurs Inc. and Foundation, the GC at the other end will sense it.

---

## A1 — Klarna (Sebastian Siemiatkowski)

Channel: LinkedIn DM, founder-to-founder, no broker. Sebastian replies to direct messages from named founders within 72 hours roughly 40% of the time per recent observed cadence.

### Primary outreach — Wed Jun 3

> Sebastian —
>
> Veronica Dawkins, founder of LedgerProof. Reaching out directly because the window is short and the fit is specific.
>
> EU AI Act Article 50 enforcement starts Tuesday August 2 — 62 days from today. Article 50 is the transparency obligation on deployers of GPAI systems: every AI-touched interaction with an EU resident has to be machine-readable as AI-generated, auditable, and provable to a supervisory authority on request. The penalty ceiling is 3% of global turnover.
>
> Klarna sits squarely inside that scope. The AI customer-service deployment you publicized in 2024, the risk-decisioning models, dynamic credit pricing — each one of those is an Article 50 surface. Your S-1 filing will be read by underwriters who now have a regulatory peg to ask "show me the evidence trail." Today that answer is logs in a CloudWatch bucket. After Aug 2 that answer needs to be cryptographic.
>
> LedgerProof is the open protocol that produces that evidence. Every AI-touched interaction emits a signed receipt; receipts are Merkle-batched and anchored hourly to Bitcoin via OP_RETURN. Verification is local — anyone can re-derive a receipt's validity from the Bitcoin chain, the public key, and the published Merkle root, with no call to our servers. The protocol is stewarded by LedgerProof Foundation (US 501(c)(3) public charity, Delaware, in formation; with Dutch Stichting EU subsidiary in formation, Amsterdam); LedgerProof Inc. is the commercial operator that ships the SDKs and SIEM connectors. Integration into a customer-service AI stack is roughly five minutes via our Python or TypeScript SDK plus a Splunk/Datadog connector.
>
> The specific ask: anchor with us as a Founding Member by Jun 22. $250K commitment, 0.25% warrant in LedgerProof Inc., reference rights on the Jul 6 launch press release, and a seat on the Foundation Advisory Council. We launch publicly Jul 6 — two weeks ahead of Aug 2 enforcement — with you named as a launch anchor. Your prospectus carries the same evidence story to your IPO underwriters.
>
> Twenty minutes on a call this Friday or Monday?
>
> Veronica

### Warm-intro request

N/A — direct to Sebastian via LinkedIn DM. Fallback if no response by Day 5: route through Sequoia (Andrew Reed covers Klarna) via Sarah Guo.

### Day+5 follow-up — Mon Jun 8

> Sebastian —
>
> Following up on Wednesday's note. Aug 2 is 57 days out and our anchor slate locks Jun 22 for the Jul 6 launch press kit.
>
> Other public-listed EU fintechs are in conversation; I would rather Klarna anchor than slot in later as second. Ten minutes this week works on my side any time between 09:00 and 18:00 CET.
>
> If the right path is a different person on your team — Niclas, Selma, or your GC — happy to start there instead.
>
> Veronica

---

## A2 — Adyen (Pieter van der Does)

Channel: email via warm intro broker. Adyen does not respond to founder cold outreach as a matter of corporate culture. Lokke Moerel is primary broker; Mishi Choudhary is the alternate.

### Primary outreach — sent after Lokke or Mishi confirms intro is open (target Thu Jun 4)

> Pieter —
>
> Thank you to Lokke for the introduction. I will keep this concise because the window matters.
>
> I am Veronica Dawkins, founder of LedgerProof. We are the open Bitcoin-anchored cryptographic protocol that produces Article 50 evidence receipts for AI-touched interactions. The protocol is stewarded by LedgerProof Foundation (US 501(c)(3) public charity, Delaware, in formation under Adler & Colvin counsel; with Dutch Stichting EU subsidiary in formation, Amsterdam, under NautaDutilh counsel); LedgerProof Inc. (Delaware) is the commercial operator that ships the SDKs, the SIEM connectors, and the optional verification nodes. The two entities are deliberately separated — Foundation owns the protocol specification, the test vectors, and the Bitcoin anchoring key custody; Inc. is the operator anyone can replace.
>
> Adyen's exposure to Article 50 is structural, not optional. Payment routing decisions, fraud-detection scoring, KYC adjudication, dispute triage — every one of those is now an AI-touched interaction within the meaning of Article 50 from Aug 2, 2026. More importantly, Adyen carries derivative exposure: every one of your roughly 5,000 EU enterprise merchants is itself a deployer who will be asked the same question by their own competent authority within the same window. The merchant who can answer "Adyen emits Article 50-conformant receipts natively" carries that compliance evidence for free.
>
> What I am proposing is anchor partnership at the Founding Member tier:
>
> - $300K commitment to LedgerProof Inc.
> - 0.25% warrant in LedgerProof Inc., struck at the Jun 25 seed close price
> - Reference rights for the Jul 6 launch press release and the post-launch case study
> - A Foundation Advisory Council seat (Foundation governance, no fiduciary exposure to Inc.)
> - A reciprocal commitment: Adyen exposes a single receipt-emission endpoint inside one merchant-facing AI feature of your choice, scoped narrowly enough that your engineering review can complete by mid-July
>
> Verification is local. The protocol does not require a call to LedgerProof servers — any party with the Bitcoin chain, the published Foundation root key, and the receipt itself can verify offline. That property is the deliberate condition for credible EU regulatory positioning.
>
> Aug 2 is 62 days from today. The seed closes Jun 25. The Jul 6 launch press kit locks Jun 22. Forty-five minutes on a call this week or next would let me walk Ingo or Alexa through the technical surface and your compliance side through the Foundation governance structure in parallel.
>
> Veronica S. Dawkins
> Founder, LedgerProof

### Warm-intro request to Lokke Moerel — Wed Jun 3

> Lokke —
>
> Following on our last note about the Foundation Advisory Council. I need one warm intro this week, ideally before Friday.
>
> Pieter van der Does at Adyen. We are pursuing Adyen as a Founding Member anchor for the Jul 6 launch — $300K + warrant + reciprocal API commitment — and I want to put the conversation directly with Pieter (or Ingo if you think he is the right first stop) rather than route through Amsterdam corporate development, which will burn the 21-day window.
>
> One paragraph from you forwarded with my draft below would be enough. If you would prefer to put it to Alexa von Bismarck on the compliance side first, that also works. What's the right first move?
>
> If you are not the cleanest path on this one I will pivot to Mishi for the Adyen intro and keep your bandwidth for the Allianz/Sirma path, which is the higher-leverage ask.
>
> Veronica

### Day+5 follow-up — sent only if Pieter does not respond by Day 5; route via Ingo Uytdehaage

> Ingo —
>
> Following up on the introduction Lokke made to Pieter on June 4 regarding LedgerProof's Article 50 anchor partnership. Realize the timing is tight.
>
> The technical surface — five-minute SDK integration, local verification, no LedgerProof-server dependency — is the part that usually answers your team's first questions. Twenty minutes with your engineering side this week would let me put it to the right reviewer directly.
>
> Veronica

---

## A3 — ING Bank (Steven van Rijswijk)

Channel: email via the Stichting banking-relationship contact already opened. The Foundation Stichting EUR account application is in flight at ING Wholesale Banking; that relationship is the natural ride-along path. Target broker: the ING Wholesale Banking relationship manager assigned to the Stichting account (name placeholder: TBD, confirm with Amsterdam counsel by EOD Tue Jun 2).

### Primary outreach — Thu Jun 4

> Steven —
>
> Thank you for the introduction from [TBD — Foundation Stichting banking relationship lead at ING Wholesale]. I am Veronica Dawkins, founder of LedgerProof.
>
> ING is already engaged with us in a different posture: we are in onboarding for the LedgerProof Foundation Stichting EUR account through your Wholesale Banking group. The Foundation (US 501(c)(3) Delaware, in formation, with Dutch Stichting EU subsidiary forming in Amsterdam) is the steward of an open cryptographic protocol for EU AI Act Article 50 evidence — every AI-touched interaction emits a signed receipt, receipts are Merkle-batched and anchored hourly to Bitcoin, verification is fully local without calling LedgerProof's servers. The Foundation owns the specification, the test vectors, and the anchoring key custody; LedgerProof Inc. (Delaware) is the commercial operator that ships the SDKs and the SIEM connectors.
>
> I am writing because the banking-relationship dialogue is one half of a conversation that should be one whole. ING has direct Article 50 exposure across its own AI deployments — fraud and AML scoring, credit decisioning, customer-service automation, KYC adjudication. Aug 2, 2026 is 62 days away and DNB has signaled that AI governance is going to be a 2026-2027 supervisory dialogue priority alongside DORA implementation. Every G-SIB in the EU is going to be asked the same evidence question; one of them is going to be first to have a cryptographic answer.
>
> What I am proposing is that ING extend the existing Foundation banking relationship into a Founding Member commitment at the LedgerProof Inc. side:
>
> - $150K commitment to LedgerProof Inc.
> - 0.10% warrant in LedgerProof Inc., struck at the Jun 25 seed close price
> - Reference rights on the Jul 6 launch announcement
> - A Foundation Advisory Council seat — which lets ING co-shape protocol governance alongside the other Founding Members and provides a natural reporting line into the DNB supervisory dialogue
> - Preferred pricing on protocol services for ING subsidiaries
>
> The intentional smallness of the financial commitment reflects that I am not asking ING to procure a vendor on a 21-day cycle. I am asking ING to commit to an open protocol the Foundation stewards — a different procurement path, with the banking relationship already underway as the natural integration point.
>
> Thirty minutes with you or Marnix this week or next would let me walk through the protocol surface and the Foundation governance independently of the Inc. commercial side. The DNB-facing story is the part I would like to discuss directly.
>
> Veronica S. Dawkins
> Founder, LedgerProof
> Stichting in formation, Amsterdam

### Warm-intro request — to the Stichting banking relationship lead (TBD) — Wed Jun 3

> [Name] —
>
> Quick ask alongside the Stichting account application. I would like to extend the LedgerProof relationship with ING into a parallel conversation on the commercial side — Founding Member commitment of $150K plus warrant plus Foundation Advisory Council seat — and the right first conversation is with Steven van Rijswijk's office, or Marnix van Stiphout if Steven's calendar is the bottleneck.
>
> Aug 2 is the Article 50 enforcement date and our launch press cycle is locked for Jul 6, so the conversation needs to happen this week or next. Could you forward to whichever of Steven's or Marnix's chief of staff is the cleanest doorway, with a one-paragraph endorsement of the Stichting onboarding so far?
>
> If the cleaner path is via ING Labs or Andrew Bester on the commercial side, I will follow your lead. Happy to draft anything you need.
>
> Veronica

### Day+5 follow-up — Tue Jun 9

> Steven —
>
> Following up on last Thursday's note. The Foundation Stichting onboarding is progressing on the banking side; the commercial Founding Member conversation is the half I would still like to put to you or Marnix directly.
>
> Twenty minutes any time this week works. Happy to come on with our Foundation counsel if helpful — the Stichting independence structure is usually the part that needs to be in the room with your legal side.
>
> Veronica

---

## A4 — Wise (Kristo Käärmann)

Channel: LinkedIn DM, founder-to-founder, no broker. Kristo replies to direct founder messages with reasonable cadence, particularly when the topic is cross-border / EU regulatory.

### Primary outreach — Thu Jun 4

> Kristo —
>
> Veronica Dawkins, founder of LedgerProof. Reaching out directly — I think the timing on this is short enough that it does not warrant a brokered intro.
>
> EU AI Act Article 50 enforcement starts Tuesday August 2, 62 days from today. It is the transparency obligation on deployers of GPAI systems — every AI-touched interaction with an EU resident has to be machine-readable as AI-generated, auditable, and provable to a supervisory authority. Wise is in scope structurally: roughly ten million EU customers, FX prediction models, fraud scoring, KYC automation, customer-service AI. The UK domicile does not exempt the exposure for EU-customer-touch surface area.
>
> LedgerProof is the open Bitcoin-anchored protocol that produces evidence for that exposure. Every AI-touched interaction emits a signed receipt; receipts are Merkle-batched and anchored hourly to Bitcoin via OP_RETURN. Anyone can verify a receipt locally with no call to our servers — Bitcoin chain plus published Foundation root key plus the receipt itself is sufficient. Protocol stewarded by LedgerProof Foundation (US 501(c)(3) public charity, Delaware, in formation; with Dutch Stichting EU subsidiary in formation, Amsterdam); LedgerProof Inc. is the commercial operator that ships the SDKs and SIEM connectors. Five-minute integration into a Python or TypeScript stack.
>
> The specific ask: anchor with us as a Founding Member by Jun 22. $250K commitment, 0.25% warrant in LedgerProof Inc., reference rights on the Jul 6 launch press release, a seat on the Foundation Advisory Council with an explicit UK-jurisdiction representation role on Council governance. Wise is the natural UK voice on a Foundation whose other Council members are EU-domiciled — the post-Brexit framing actually works in your favor here: UK fintech committed to EU regulatory rigor on its own initiative.
>
> Twenty minutes this week? Engineer-to-engineer with Harsh on the technical side first if you prefer; the SDK and the local-verification proof are usually the parts that move fastest with technical leadership in the room.
>
> Veronica

### Warm-intro request

N/A — direct to Kristo via LinkedIn DM. Fallback if no response by Day 5: route through Taavet via Estonia / Skype-mafia network (Sarah Guo has cross-connect).

### Day+5 follow-up — Tue Jun 9

> Kristo —
>
> Following up on last Thursday's note. Aug 2 is 56 days out and we lock the Jul 6 launch press slate Jun 22.
>
> If Harsh is the cleaner first conversation for the technical side, glad to start there directly — happy to put the SDK and the local-verification surface in front of him this week. Twenty minutes is enough to know whether we should go further.
>
> Veronica

---

## A5 — Allianz (Sirma Boshnakova)

Channel: email via Lokke Moerel warm intro. This is the single critical-path human dependency in the Tier-A slate — Allianz collapses without Lokke. Brunswick Group EU is the secondary path; DGAP / German Council on Foreign Relations AI working group is the tertiary path.

### Primary outreach — sent only after Lokke confirms intro is delivered (target Thu Jun 4 or Fri Jun 5)

> Sirma —
>
> Thank you to Lokke for the introduction. She has been advising me on the LedgerProof Foundation governance structure and indicated that the Article 50 evidence question is one you are already considering on the AGCS and Trade boards.
>
> I am Veronica Dawkins, founder of LedgerProof. We are the open Bitcoin-anchored cryptographic protocol that produces verifiable evidence for AI-touched interactions in the meaning of EU AI Act Article 50. Enforcement begins Tuesday August 2, 2026, 62 days from today. The protocol is stewarded by LedgerProof Foundation (Dutch Stichting, in formation under Amsterdam counsel and with Mishi Choudhary as prospective board chair); LedgerProof Inc. (Delaware) is the commercial operator that ships the SDKs and SIEM connectors. The two entities are deliberately separated — Foundation owns the specification, the test vectors, and the Bitcoin anchoring key custody, and is structurally non-controlled by Inc.
>
> The reason I am reaching out to Allianz specifically: insurance is one of the highest AI-density sectors in EU financial services. Underwriting decisioning, claims triage, fraud scoring, dispute adjudication, customer-service automation — every one of those is an Article 50 surface from Aug 2. EIOPA's 2026-2027 supervisory cycle is going to put insurer AI deployment under direct scrutiny. The first EU insurer to commit publicly to cryptographic AI evidence is going to be read as the AI-governance leader of the sector — and the press cycle on that move runs against AXA, Generali, and Munich Re's own AI-strategy narratives.
>
> I am not asking Allianz to procure a commercial vendor on a 21-day cycle — that is not a realistic ask for a group of your scale, and the procurement teams should not be expected to compress what is properly a multi-quarter review. What I am asking for is a Letter of Intent to Evaluate, co-signed by you and by me, publishable as part of the Jul 6 launch press kit, that commits Allianz to a structured 12-week evaluation of the protocol with intent to convert to a Founding Member commitment if the evaluation is positive. The soft commercial target on conversion is approximately $400K.
>
> The Letter of Intent to Evaluate carries no fiduciary commitment from Allianz beyond the public statement of intent. It does carry the asymmetric upside that Allianz is publicly positioned as the EU insurer leading the Article 50 evidence question ahead of EIOPA's supervisory window. Lokke has reviewed the Foundation governance structure and can vouch directly for the independence boundary between Foundation and Inc., which I anticipate is the first question your board will ask about competitive-information concerns.
>
> Forty-five minutes on a call this or next week would let me walk through the protocol surface, the Foundation governance independently of Inc., and the LoI-to-Evaluate draft language. Anett Loose or Christopher's office on the call would be welcome.
>
> Veronica S. Dawkins
> Founder, LedgerProof

### Warm-intro request to Lokke Moerel — Wed Jun 3

> Lokke —
>
> The ask I flagged on Friday — the Sirma Boshnakova intro at Allianz — is the single most load-bearing intro in the Jul 6 launch sequence on my side. I want to put it to you formally so you can decide this week.
>
> What I am asking Allianz for is a Letter of Intent to Evaluate, co-signed by Sirma and me, publishable for the Jul 6 press kit, committing Allianz to a 12-week structured evaluation of the protocol with intent to convert to a Founding Member commitment (~$400K) if the evaluation is positive. No fiduciary commitment from Allianz beyond the public statement of intent. The Foundation independence structure — which is the question her board will ask first — is something you can vouch for directly from the work you have already reviewed on the Stichting side.
>
> I would like to send the message to Sirma this week, ideally Thursday or Friday, so the first conversation can land Mon Jun 8 or Tue Jun 9. That gives us a workable 14-day window to LoI-to-Evaluate signature by Jun 22.
>
> Can I forward you the draft text for your eyes before I send? If you would rather make the introduction yourself with a one-paragraph endorsement, the draft is ready for that path too.
>
> Veronica

### Day+5 follow-up — Tue Jun 9 (only if Lokke's intro lands but Sirma does not respond)

> Sirma —
>
> Following up on Lokke's introduction last week. I realize the timing is compressed.
>
> The Letter of Intent to Evaluate is structured deliberately so that the Allianz side carries no procurement burden inside the Jul 6 window — only a 12-week evaluation commitment that starts after launch. If the cleaner first conversation is with Anett or Christopher's office, glad to start there. Thirty minutes any time this week.
>
> Veronica

---

## Mistral coupling — supply-side mirror (Arthur Mensch)

Channel: LinkedIn DM via Cédric O warm intro. Different ask than the Tier-A slate: Mistral is a SELLER of AI capability that would EMIT receipts for model outputs, not a BUYER demonstrating Article 50 compliance. The press value is the supply-side signal — once Mistral commits to emitting receipts for La Plateforme outputs, Hugging Face and Aleph Alpha follow within weeks.

### Primary outreach — sent after Cédric confirms intro is delivered (target Thu Jun 4)

> Arthur —
>
> Thank you to Cédric for the introduction. I am Veronica Dawkins, founder of LedgerProof.
>
> Reaching out because the supply-side question on Article 50 is one that Mistral is uniquely positioned to answer ahead of the rest of the EU AI sector. Article 50 enforcement starts Tuesday August 2, 62 days from today. The transparency obligation falls on deployers, but the easiest path for a deployer to meet the obligation is to consume model outputs that are natively cryptographically attributable.
>
> LedgerProof is the open Bitcoin-anchored protocol that produces those attributable receipts. Every model output emits a signed receipt that binds the prompt, the model identifier, the output, and a timestamp; receipts are Merkle-batched and anchored hourly to Bitcoin via OP_RETURN; verification is fully local — anyone with the Bitcoin chain, the Foundation root key, and the receipt can verify offline with no call to LedgerProof servers. Protocol stewarded by LedgerProof Foundation (US 501(c)(3) public charity, Delaware, in formation; with Dutch Stichting EU subsidiary in formation, Amsterdam); LedgerProof Inc. ships the SDKs and SIEM connectors.
>
> The ask is specific: Mistral commits to emit LPR receipts natively for all La Plateforme outputs by Aug 2, 2026. Co-announce Jul 6 alongside our launch. Mistral becomes the supply-side reference for cryptographic AI attribution — the EU sovereign-AI alliance positioning writes itself, and every Mistral customer inherits Article 50 evidence by default for the model-output portion of their deployment.
>
> Different structure than enterprise anchor partnerships because the role is different: there is no warrant or financial commitment ask on the Mistral side. What I would propose is a joint technical statement of work scoped to receipt emission on La Plateforme, co-signed engineering commitment to ship the integration by Jul 27, and joint press release Jul 6. Optionally a Foundation Advisory Council seat representing the model-provider perspective on protocol governance.
>
> Twenty or thirty minutes this week to put the technical surface in front of your engineering side directly? Cédric has the briefing materials and can be on the call if useful.
>
> Veronica

### Warm-intro request to Cédric O — Wed Jun 3

> Cédric —
>
> The brief I sent last week on LedgerProof — the open Bitcoin-anchored protocol for Article 50 evidence — has reached the point where I need to engage Mistral specifically as a supply-side reference. Different from the enterprise anchor partnerships we discussed; the Mistral role is to emit receipts on La Plateforme outputs natively, not to procure as a buyer.
>
> Would you be willing to make the introduction directly to Arthur this week? I have drafted the message I would send below. The ask carries no financial commitment on Mistral's side — joint engineering statement of work, co-announce Jul 6, optional Foundation Advisory Council seat for the model-provider perspective. EU sovereign-AI positioning is the part Arthur will recognize fastest.
>
> If you would prefer to introduce me to Audrey or to Mistral's commercial side first, happy to follow that path. The 21-day window puts the first conversation in the Mon Jun 8 to Wed Jun 10 range.
>
> Veronica

### Day+5 follow-up — Tue Jun 9

> Arthur —
>
> Following up on Thursday's note via Cédric. Aug 2 is 56 days out and our launch announcement slate locks Jun 22.
>
> If the engineering side is the cleaner first conversation, happy to put the technical surface — receipt format, local verification, Bitcoin anchoring frequency — in front of whoever leads La Plateforme infrastructure this week. Twenty minutes is enough.
>
> Veronica

---

## Send sequence — what goes when, in what order, with what cadence

The sequence is built around three constraints: (1) warm-intro brokers need lead time before the primary outreach goes out, (2) Lokke is the single critical-path human and cannot be over-asked in one note, (3) Wednesday is the first send day and Friday is the close-of-week pulse check.

### Wednesday June 3 — broker requests + direct sends

Morning (08:00 - 10:00 PDT):

1. Send the Lokke Moerel intro request (Allianz / Sirma path). This is the single most load-bearing message of the day — Allianz collapses without it.
2. Send the Cédric O intro request (Mistral / Arthur path). Lower stakes, parallel track.
3. Send the Klarna primary outreach DM to Sebastian (direct, no broker).
4. Send the Stichting-banking-lead intro request (ING / Steven path).

Afternoon (14:00 - 17:00 PDT):

5. Send the Wise primary outreach DM to Kristo (direct, no broker). Hold until after lunch so the LinkedIn notification lands in his Stockholm-equivalent morning (Wise is London).
6. Decide on Adyen intro broker (Lokke vs Mishi). If Lokke responds to the Allianz request by EOD Wed and signals capacity for a second intro, route Adyen through her. If not, send the Mishi intro request Wed evening.

### Thursday June 4 — Adyen + Mistral + ING primary

Morning (08:00 - 12:00 PDT):

7. Send the Adyen primary outreach to Pieter (only if Lokke or Mishi has confirmed intro is delivered by Wed EOD).
8. Send the Mistral primary outreach to Arthur (only if Cédric has confirmed intro is delivered by Wed EOD).
9. Send the ING primary outreach to Steven (only if the Stichting banking lead has confirmed intro is delivered by Wed EOD).

Afternoon: hold outbound. Watch inbound channel for responses to Wed messages (Klarna and Wise direct DMs, broker confirmations).

### Friday June 5 — close-of-week pulse

10. Pulse check on all six target threads. Status update to chief of staff side: which targets have responded, which brokers have confirmed, which are still pending.
11. If Sirma has not received the Allianz primary outreach by EOD Fri because Lokke has not delivered the intro, escalate to Brunswick Group EU as backup path Mon Jun 8.
12. If Pieter has not received the Adyen primary outreach by EOD Fri, escalate to Mishi as backup path Mon Jun 8.

### Saturday June 6 — quiet

No outbound. Family time. Inbound monitored only for hot replies (Sebastian, Kristo, Arthur are the three most likely to respond on a weekend if they engage at all).

### Sunday June 7 — outbound personalization for Monday calls

Tailor whatever first-call decks are needed based on Wed-Fri response signal. Sebastian and Kristo decks need the AI-narrative alignment angle; Pieter and Steven decks need the procurement-pathway clarity; Sirma needs the LoI-to-Evaluate language pre-redlined; Arthur needs the technical engineering brief.

### Monday June 8 — first counterweight calls land

Target: three of five Tier-A first calls land by EOD Mon Jun 8. Backup intro paths activated for any target where the primary intro has not delivered by Fri Jun 5.

### Tuesday June 9 — Day+5 follow-ups go out

Day+5 follow-up messages sent for any Wed Jun 3 primary outreach that has not received a response. That is Klarna (Sebastian), Wise (Kristo), and conditionally the broker-routed targets where the primary outreach went out Thursday — those Day+5 follow-ups land Tue Jun 9 for Wed Jun 3 sends and Wed Jun 10 for Thu Jun 4 sends.

### Day 7 onward — stop sending, start closing

After Tue Jun 9, no further outbound to non-responders without a fresh signal or a new broker path. Founder time pivots to call execution and SOW redline on the responders. Cold persistence past Day 7 burns reputation; the calendar reflects that.

---

## What to do if a target responds positively — 15-minute triage flow

When a positive response lands (Sebastian replies "let's talk," Kristo replies "Harsh will reach out," Sirma's office replies via Lokke "Sirma's chief of staff will schedule"), the 15-minute triage is:

### Minute 0-2: log the response

Open `ops-state.json` or the seed-close-pack response tracker. Log: target, named-person who responded, channel, response timestamp, response text (verbatim or paraphrased if long). This is the audit trail and also the input to the chief-of-staff side's daily reporting cadence.

### Minute 2-4: classify the response

Three categories.

- **Green** — "yes, let's talk" or "yes, my team will reach out." Move to scheduling immediately.
- **Yellow** — "interesting, send more material" or "let me forward internally." Move to material-send within 4 hours.
- **Red** — "not the right fit" or "not the right timing." Acknowledge, ask permission to re-engage in 90 days, log and close.

### Minute 4-7: green-path scheduling

For Green responses:

- Reply within 15 minutes with two or three specific call windows in their time zone (08:00-10:00, 11:00-13:00, 16:00-18:00 local). Do not ask "what works for you" — propose specifics.
- CC the chief of staff side on the reply so calendar can be held.
- Default call length: 25 minutes (Klarna, Wise, Mistral founder-to-founder), 45 minutes (Adyen, ING, Allianz enterprise side).
- Default agenda paragraph in the reply: "I'll spend the first eight minutes on the Foundation governance and the protocol surface, then twelve minutes on the specific commitment ask, then leave space for your team's first questions."

### Minute 7-11: yellow-path material send

For Yellow responses:

- Reply within 30 minutes with three attached or linked materials, no more:
  1. The two-page Foundation governance summary (PDF)
  2. The five-page protocol technical brief (PDF) — receipt format, local verification proof, Bitcoin anchoring
  3. The one-page commercial summary specific to their target tier ($150K / $250K / $300K / LoI-to-Evaluate)
- Do not attach the full master plan, the 24-month financial model, or the audit memo. Three documents only. More than three triggers "let me get back to you after I read everything" which is the Yellow-to-Red conversion path.
- Close the reply with one specific ask: "Could we hold 20 minutes next week — Wednesday or Thursday — for your first questions?"

### Minute 11-13: red-path acknowledgment

For Red responses:

- Reply within 60 minutes with three sentences: thank you for the candor, here is the timing trigger that may shift the calculus (Aug 2 enforcement landing or first competent-authority enforcement action), may I re-engage in 90 days?
- Log in the re-engagement tracker for the date 90 days forward.
- Do not pivot to a different person at the same company in the same week — that path is the credibility-burn path. Wait at least 30 days before any lateral move inside the same company.

### Minute 13-15: cascade the response

For all three colors, the cascade is the same:

- Slack the chief of staff side with the response classification and the immediate next action.
- Update `ops-state.json` KS3 mitigation tracker.
- If Green, update the seed-close-pack response tracker with the scheduled call time. If Yellow, update with the material-send timestamp and the requested call window. If Red, update with the 90-day re-engagement date.
- If this is the first Green response of the cohort, ping Brunswick (or whichever PR firm signed by then) with the heads-up that a counterweight anchor is in the funnel — they need lead time on the press kit positioning that has the right logo in the headline slot.

### What NOT to do in the 15-minute window

- Do not forward the response to investors as a "look at this" — investor signaling is for the seed close memo Jun 25, not for daily-pulse anchor responses. Premature signal collapses negotiating leverage on every other target.
- Do not commit to redlined contract terms inside the response thread. The first call is for scope alignment; redlines come after the first call and run through Foundation and Inc. counsel.
- Do not engage on press-release positioning specifics inside the response thread. The press cut is locked at Jun 22; we will not pre-negotiate the press-release headline with the first responder because that constrains the second and third.
- Do not over-promise SDK delivery dates inside the first response. The SDK roadmap is bound by the senior protocol engineer hire (JD lands week of Jun 8) and the contractor stack already engaged. The first response should say "our SDK is in active development and integration is five minutes once available; happy to walk through the technical timeline on the call" — not a specific ship date.

---

## What I want from Veronica before Wednesday morning

1. **Sirma intro language**: confirm with Lokke that the Allianz intro request below reads correctly to her, or hand back the revision. Wednesday 08:00 PDT send window depends on Tue night sign-off.
2. **Stichting banking lead name**: confirm the name and email for the ING Wholesale Banking relationship manager assigned to the Foundation Stichting account. Currently a placeholder; cannot send the ING intro request without it.
3. **Adyen broker decision**: Lokke vs Mishi. Default is Lokke; if she signals capacity strain on Wed after the Allianz request lands, pivot to Mishi without waiting.
4. **Mistral coupling go/no-go**: confirmed in the targets-list discussion as a parallel track. This file assumes go. If reconsidered, the Cédric O intro request gets pulled from the Wed morning send slot.
5. **Press-release headline slot**: when the first Green response lands, who is the named anchor in the Jul 6 launch release headline? Klarna first if both Klarna and Wise convert? Or by sector relevance? Decide before the first call so the call itself can carry that intent.

---

## Message variants — alternates by counterparty signal

If a target's response signal lands in a specific posture (regulatory-anxious, technically-skeptical, press-cautious), the primary outreach message can be substituted with one of the variants below. Each variant preserves the load-bearing structure — Article 50 enforcement date, Foundation/Inc. distinction, local-verification property, specific dollar ask, Jun 22 deadline — but reframes the lede paragraph to address the most likely first objection.

### Variant V1 — regulator-anxious lede (use if the target's legal side is known to be sensitive on competent-authority signaling)

> [Name] —
>
> I want to be careful about how I describe what LedgerProof is and is not, because the regulatory positioning is the part that goes wrong if it is overstated.
>
> LedgerProof is not endorsed by the European Commission, by the EU AI Office, by ESMA, by EIOPA, by DNB, by BaFin, by ACPR, by AESIA, or by any other competent authority. The protocol is open and Bitcoin-anchored; it produces verifiable evidence receipts that a deployer can show on request when a competent authority asks for transparency-obligation documentation under Article 50. The receipts do not confer presumption of conformity under Article 40 — that is a separate question that runs through CEN-CENELEC harmonized standards and is years from settled. What the receipts confer is an audit trail that a competent authority can independently re-verify from public sources (Bitcoin chain + Foundation root key + the receipt itself), without any dependence on calls to LedgerProof's infrastructure.
>
> That distinction is deliberate. We are building infrastructure that survives an adversarial competent-authority inspection, not marketing claims that need regulator validation.
>
> [Continue with the standard target-specific ask paragraph from the primary outreach above.]

### Variant V2 — technically-skeptical lede (use for engineering-led targets, default for Mistral or for Wise/Harsh path)

> [Name] —
>
> Cutting to the technical surface because that is where this conversation is decided.
>
> Receipts: deterministic canonical encoding of (request_id, model_id, prompt_hash, output_hash, timestamp_ns, deployer_id, regulatory_context). Ed25519 signature over the canonical bytes, Foundation-root-key-derived. Receipts batched into a Merkle tree per anchoring window (default 60 minutes; configurable down to 10 minutes for high-volume deployers). Tree root anchored to Bitcoin via OP_RETURN at the end of each window. Verification path: caller hashes the receipt, walks the Merkle inclusion proof, validates the Ed25519 signature against the published Foundation root key, checks the Bitcoin transaction for the anchor — fully offline, no LedgerProof server in the path. SDK is roughly 800 lines of TypeScript or 1,100 lines of Python; SIEM connectors (Splunk, Datadog, Elastic, ServiceNow, Vanta, Drata) ship as separate adapters.
>
> Latency budget on the deployer-side hot path: under 12 milliseconds median (Merkle accumulator update only; signing is batched and happens out-of-band). Stream-aware signing for chunked HTTP and SSE responses via incremental SHA-256 in Kong/Envoy `access` and `log` phases — no body buffering, no response-path latency added.
>
> [Continue with the standard target-specific ask paragraph from the primary outreach above.]

### Variant V3 — press-cautious lede (use for Adyen culture; conservative on public commitments)

> [Name] —
>
> Aware that Adyen culture is conservative on public commitments, so I want to make the ask structure explicit before describing what we are.
>
> The Founding Member commitment to LedgerProof comes in two parts that can be decoupled. The financial commitment and warrant — $300K and 0.25% in LedgerProof Inc., struck at the Jun 25 seed close price — is a private transaction with private documentation. The public-attribution component — your logo on the Jul 6 launch press release and the post-launch case study — is a separate decision that can be deferred. Adyen can commit privately as a Founding Member with the public-attribution component held until your communications side is comfortable with the framing, or until a later milestone (Aug 2 enforcement, first competent-authority enforcement action, Q4 earnings).
>
> The reason I lead with that: the press-counterweight calculus on our side and the press-readiness calculus on yours are separable questions, and the deal does not require them to land on the same date.
>
> [Continue with the standard target-specific ask paragraph from the primary outreach above.]

---

## If a broker request gets declined

Each warm-intro path has at least one fallback. If the primary broker declines or signals capacity strain, the routing decisions are pre-made so they do not consume Wednesday morning.

### If Lokke declines the Allianz intro

Path A: Brunswick Group EU. Brunswick has a standing Allianz relationship and can broker the Sirma introduction within 5-7 business days. The cost is a 1-week timeline slip on the Allianz primary outreach — primary message goes Wed Jun 10 instead of Thu Jun 4, first call lands Mon Jun 15 instead of Mon Jun 8, LoI-to-Evaluate signature by Jun 22 becomes very tight but still achievable if Sirma is responsive on the first call.

Path B: DGAP / German Council on Foreign Relations AI working group. Slower (10-14 days) and routes through institutional politics, but produces a credibly-pedigreed introduction that lands with Sirma's board-level network rather than her direct office. Use only if Brunswick path is also unavailable.

Path C: drop Allianz from the Tier-A slate. Backfill with one of the Tier-B targets — BBVA (Madrid) via Domínguez Álvarez at AESIA is the fastest plausible substitution. Cycle time is 10-14 weeks, so the realistic ask shifts from LOI to a Letter of Intent to Evaluate, similar shape to Allianz. The press value is lower but non-zero.

### If Cédric declines the Mistral intro

Path A: direct LinkedIn DM to Arthur. Lower probability of response without a warm intro (Arthur receives high LinkedIn volume), but the founder-to-founder credibility on AI sovereignty is the part that may break through cold outreach. Send with a short note explicitly naming the supply-side mirror framing.

Path B: route through Audrey at Mistral commercial side via DigitalEurope membership. Slower (5-7 days) and lands the conversation on the commercial side rather than at Arthur directly. Acceptable for the supply-side coupling because the engineering commitment can run on the commercial track without founder-level engagement.

Path C: drop Mistral from the parallel coupling and shift the supply-side mirror ask to Aleph Alpha (Heidelberg) — Jonas Andrulis is reachable via the German enterprise tech network and the supply-side framing applies symmetrically.

### If Mishi declines the Adyen intro

Path A: DigitalEurope membership channel. We are joining DigitalEurope post-Foundation-formation; Adyen is already a member. The intro path through the Brussels DigitalEurope secretariat is slower (10-14 days) but produces an introduction that lands with Adyen's regulatory affairs side directly.

Path B: drop Adyen from the Wed Jun 3 slot and replace with Stripe (San Francisco) via Sarah Guo / Sequoia network. Stripe procurement cycle is 12-16 weeks — too slow for Jun 22 — but a Stripe Letter of Intent to Evaluate could land for Sep press cycle and back-fills the Adyen-shaped role over the medium term.

### If the Stichting banking lead declines the ING intro

This is the lowest-risk fallback because the Stichting banking relationship is already underway and the relationship lead has zero incentive to decline the intro — extending the relationship is in their interest. If the request is declined nonetheless, the fallback is the ING Labs leadership via Mathias Lafeldt's DACH/BENELUX engineering network, which lands the conversation on the innovation side rather than commercial. Slower (10-14 days) and a different first-call posture (technical evaluation rather than commercial Founding Member ask), but workable.

---

## Reply-text scaffolds for the first inbound call

When the first call is scheduled and the calendar invite goes out, the meeting reply that confirms the time should carry a structured agenda paragraph so the counterparty's team can pre-position the right people. The scaffold below is the default for each tier of target.

### Scaffold S1 — Klarna, Wise, Mistral (founder-to-founder, 25 minutes)

> [Name] —
>
> Confirmed for [date / time / time zone]. I will send a calendar invite with a [Zoom / Google Meet / Signal] link from my side.
>
> Agenda I have in mind, happy to adjust:
>
> - 0:00 - 0:08: Foundation governance, protocol surface, what the receipts look like
> - 0:08 - 0:18: the specific Founding Member commitment ask and the Jun 22 timeline
> - 0:18 - 0:25: your team's first questions
>
> If [engineer name on their side] should be on the call for the technical surface, glad to extend to 35 minutes. Otherwise I will plan for the 25-minute structure.
>
> Veronica

### Scaffold S2 — Adyen, ING (enterprise procurement-aware, 45 minutes)

> [Name] —
>
> Confirmed for [date / time / time zone]. I will send a calendar invite from my side with a [Zoom / Webex / Teams] link compatible with your environment.
>
> Agenda I have in mind, please adjust:
>
> - 0:00 - 0:12: Foundation governance and the Inc.-vs-Foundation independence boundary
> - 0:12 - 0:24: protocol technical surface — receipt format, local verification, Bitcoin anchoring frequency, SDK integration shape
> - 0:24 - 0:36: the Founding Member commitment ask, the warrant mechanics, the procurement path that fits inside your internal review cycle
> - 0:36 - 0:45: your team's first questions
>
> Welcome on the call from your side: anyone from compliance / legal / engineering. We will not redline anything on this call; the purpose is scope alignment. Redlines run through Foundation counsel (Amsterdam) and Inc. counsel (Wilson Sonsini, Palo Alto) after the call.
>
> Veronica

### Scaffold S3 — Allianz (LoI-to-Evaluate-focused, 45 minutes)

> Sirma —
>
> Confirmed for [date / time / time zone]. Lokke welcome to join if useful.
>
> Agenda:
>
> - 0:00 - 0:10: Foundation governance, Foundation/Inc. independence, the Council seat structure
> - 0:10 - 0:22: protocol surface, what the evidence looks like in an EIOPA-facing supervisory dialogue
> - 0:22 - 0:35: the Letter of Intent to Evaluate — what it commits Allianz to (12-week structured evaluation), what it does not (no fiduciary procurement burden), and the draft language already prepared for the press kit
> - 0:35 - 0:45: your team's first questions, ideally with Anett or Christopher's office on the line for the compliance and underwriting perspectives
>
> No redlines on this call. The LoI-to-Evaluate draft is ready and will run through your legal side after the call.
>
> Veronica

---

## Quality bar — what each message must clear before send

Every message in this file should be re-read against the following five-point checklist immediately before sending. The checklist is the same regardless of which message and which target.

1. **No claim of regulator endorsement.** The phrase "endorsed by," "approved by," "blessed by," "in conformity with" applied to a competent authority does not appear. Article 40 presumption of conformity is not mentioned. Article 50 is described as the transparency obligation we produce evidence for, not as something LedgerProof guarantees compliance with. (C1)

2. **No SaaS-dependency framing.** Local verification — Bitcoin chain + Foundation root key + receipt — is named explicitly at least once per message. The phrase "no call to LedgerProof servers" or equivalent appears at least once per primary outreach. (C4)

3. **Foundation and Inc. named distinctly.** The Foundation is the protocol steward; Inc. is the commercial operator. Warrant is in Inc.; Advisory Council seat is in the Foundation. The distinction matters because the General Counsel at the other end is testing for sloppiness in exactly this place.

4. **Specific dates, specific numbers, specific names.** Aug 2 enforcement date is named. The 62-day countdown is named. The dollar ask is named. Jun 22 deadline is named. The named-individual recipient is named at the top. No "we look forward to" or "we are excited to" anywhere.

5. **No counterweight framing visible.** The word "counterweight," the word "Tencent," the word "Riot," and any framing that suggests the target is being recruited to balance another partner's press exposure — none of these appear in any message to any target. The asymmetric press calculus is our internal logic; the target sees only the Article 50 enforcement window and the founder-grade direct ask.

If any of the five points fails on a re-read, the message does not go out until it is rewritten to clear.

---

## Post-call follow-up — within 90 minutes of the first call ending

Whatever the first-call outcome, a structured follow-up note goes out within 90 minutes of the call ending. The note carries three load-bearing functions: it documents the verbal scope alignment for both legal sides, it advances the redline process to the named counsel on both sides, and it sets the next-touch cadence in writing so neither side has to chase the other.

### Follow-up template for first-call positive outcome (Green)

> [Name] —
>
> Thank you for the [25 / 45] minutes. Documenting what I heard so we are aligned in writing.
>
> Scope: [one or two sentences capturing the specific Founding Member tier and any modifications agreed verbally — e.g., $300K commitment, 0.25% warrant, Foundation Advisory Council seat, public attribution component decoupled per Adyen V3 framing].
>
> Next steps on my side: I am forwarding this thread to [Inc. counsel name at Wilson Sonsini] and [Foundation counsel name in Amsterdam] today. They will produce a clean draft of the Founding Member commitment letter and the warrant document by [date — typically T+5 from call] and circulate to your legal side directly. The Foundation Advisory Council seat term sheet is a separate one-pager and travels with the package.
>
> Next steps on your side as I understood them: [one or two sentences capturing what they committed to internally — e.g., "you will route to Selma and Niclas this week for compliance and CFO sign-off"].
>
> Timing: the seed close is Jun 25 and the Jul 6 launch press kit locks Jun 22. Signature of the commitment letter by [target date — Jun 22 for Klarna/Wise/Adyen, Jun 22 for the LoI-to-Evaluate for Allianz, Jul 1-8 acceptable for ING] keeps both threads on the calendar we discussed.
>
> If anything in this note misreads what we agreed, please send the correction back this evening — I would rather catch the misread now than at redline.
>
> Veronica

### Follow-up template for first-call yellow outcome (more material requested)

> [Name] —
>
> Thank you for the [25 / 45] minutes. Sending the three follow-up materials you asked for:
>
> 1. [Document name 1] — [one sentence on what it is]
> 2. [Document name 2] — [one sentence on what it is]
> 3. [Document name 3] — [one sentence on what it is]
>
> Holding the rest of the documentation tree back deliberately so your team can review the load-bearing three first. Happy to send anything additional once your reviewers have a specific question to test against.
>
> Next touch: I would propose 20 minutes [day, day, or day] next week to put your team's first questions to me directly. Sending two or three concrete time options in a separate calendar reply.
>
> Veronica

### Follow-up template for first-call slipping (no decision in the room)

> [Name] —
>
> Thank you for the time. Capturing where this stands so we have a clean trail.
>
> What I heard: [one or two sentences — the specific objection, the missing piece of information, the internal stakeholder who needs to be in the next conversation].
>
> What I propose: [the specific next step — e.g., a second call with the named stakeholder added, a written response to the objection, a different commitment structure that addresses the constraint].
>
> Timeline reality: the Jun 22 anchor-slate lock is firm on our side because the Jul 6 launch press kit cannot move. If the right path puts the next conversation past Jun 22, the realistic outcome is a post-launch Founding Member commitment with a Q3 or Q4 public attribution component rather than a launch-day announcement. That is a fine outcome — it does not foreclose the partnership, only reshapes the launch-week framing.
>
> Veronica

---

## Voice notes for Veronica — phrases to avoid mid-message

A short list of phrases that have crept into earlier drafts and should not appear in any version of any message in this file. Re-reading for these before send is the fastest quality check.

- "We are excited to" / "I am excited to" — replace with the specific reason for writing.
- "We believe AI can be" — no founder-level conviction statements on AI as a category. Speak only about the protocol surface and the regulatory exposure.
- "Industry-leading" / "best-in-class" / "world-class" — these phrases are noise to any GC reading the message.
- "Trust" as a marketing word — trust is a property of the cryptographic verification, not a brand attribute. If "trust" appears, replace with the specific verification primitive that establishes it.
- "Game-changing" / "transformative" / "revolutionary" — the protocol is plumbing, not a category-creating thesis. The thesis lives in the press kit. The outreach lives in the calendar.
- "Sync" as a verb — use "call" or "meeting." Sync reads as junior.
- "Reach out" except as a self-description (I am reaching out). Do not ask the target to "reach out" to my team; they should reply directly to me.
- "Touch base" — same reasoning as sync.
- "Just" as a softener — "just wanted to" / "just following up" — delete the just every time it appears.
- "Hope this finds you well" — no opening pleasantries. The named address line and the first sentence about Article 50 carry the whole opener.
- "Looking forward to" — replace with the specific next step (call window, document delivery, signature date).

---

## File location

`/Users/veronicadawkins/Documents/LedgerProof-Launch-July6/14-seed-close-pack/counterweight-outreach-messages.md`

Linked from: `counterweight-anchor-targets.md`, `04-atomic-explosion-master-plan.md` §0 (C8), §8 (KS3), `ops-state.json` KS3 mitigation tracker.
