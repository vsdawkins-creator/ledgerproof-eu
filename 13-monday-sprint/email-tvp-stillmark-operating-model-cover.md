# TVP + Stillmark — Operating Model Cover Email (DRAFT — hold until after Sarah Guo pressure-test feedback)

**Status**: Draft staged. **Do NOT send** until Sarah Guo pressure-test call lands + her substantive feedback is incorporated into the operating model (or you confirm she found nothing material).

**Drafted**: Wed Jun 3, 2026
**Trigger to send**: After Sarah's call concludes AND model edits are committed (target Wed PM / Thu AM PT)
**Sender**: veronica@ledgerproofhq.io
**Authorization to send**: V will need to give explicit "send these" the same way she did for the Lokke / Sarah / Harrison batch this morning

---

## Send #1 — TVP (Three Village Partners)

**To**: [V to confirm — assumed partner address: anil@tvp.vc OR partner@tvp.vc; verify against last received email from them]
**From**: veronica@ledgerproofhq.io
**Subject**: LedgerProof — 24-month operating model + Series A diligence pack (committed: $6M lead in $12M seed)
**Attachment 1**: `14-seed-close-pack/01-cfo-24-month-model.pdf` (post-Sarah-pressure-test version)
**Attachment 2**: `14-seed-close-pack/02-threat-model-briefing.pdf` (security-first deck — for the partner who will own technical diligence)

---

Anil —

Per our last conversation, here's the 24-month operating model — Base, Stretch, and Downside cases — that we agreed I'd circulate before the partner meeting on [DAY V to insert based on TVP's preferred slot]. Two short notes before you open the deck.

**One — the model has been pressure-tested.** Sarah Guo (Conviction) ran a 45-minute attack on the Stretch case yesterday. The Stretch case in this version reflects her substantive feedback: [V to insert the 1-2 specific holes Sarah found and how we addressed them, in single-sentence form — example: "Sarah pushed back hard on the Aug-Sep visible-enforcement assumption in Stretch; we re-anchored Stretch to Q4 2026 enforcement visibility, which costs ~$1.2M of cumulative Y1 booked ARR vs the original Stretch but is defensible against GDPR-pace enforcement history."]. Sarah is not in the lead pool — her pressure-test was specifically structured not to double-count as TVP diligence.

**Two — what we're proposing.** TVP leads the $12M seed at $6M / 50% with full information rights and a board observer seat. Stillmark co-leads at $4M with same board observer rights. Remaining $2M allocated to strategic angels we'll discuss live. Hercules term sheet ($8M facility, undrawn, 75 bps commitment) signed concurrently for runway insurance. Close target: 25 June 2026 ahead of EU AI Act Article 50 enforcement on 2 August.

The Base case shows $9.4M ARR booked / $6.7M recognized at Year 1 exit (May 2027), $14.2M cash, 14-month runway. The Stretch case extends to $14M booked Y1 with EBITDA breakeven Q1 2028. The Downside case assumes Sarah's worst objection materializes — enforcement velocity tracks GDPR pace (18-24 months) — and still shows survivable burn against the seed + Hercules facility through Q4 2027 before a difficult-but-real Series A bridge decision.

I'll cover the receipt-anchored Foundation governance pieces, the IETF SCITT-track standardization arc, and the 29-adapter distribution surface live. The numbers in the model already net out the Foundation grant ($50K/mo Inc.→Foundation starting Aug 2026) — that's not a hidden cost about to surface.

**What I'd ask you to do before we meet:**

1. Read §A1-A20 of the assumption registry first. Every number in every case ties back to those tags. If any single assumption looks wrong to you, it's faster to flag it before the meeting than during.
2. Skim the threat-model briefing (Attachment 2) for the Stillmark side. They'll have the technical objections; the briefing pre-empts the obvious ones (signing key compromise, Bitcoin anchor fee volatility, SCITT spec drift, GDPR Article 17 erasure interactions).
3. Tell me which case — Base, Stretch, or Downside — you want to anchor the valuation conversation against. I have a view; happy to hear yours first.

Calendly for the partner meeting: [V to insert]

Foundation EU AI Office consultation submission filed Tuesday (2 June). Bitcoin-anchor confirmation pending; verifier output happy to share if useful for the Stillmark side. Adapter packages dry-run-built across all 29 frameworks (LangChain, OpenAI, Anthropic, etc.); PyPI publish this week.

If anything in the model doesn't make sense before we meet, send the page reference and I'll record a 5-minute Loom walking through the math. Faster for both of us than email back-and-forth on financial detail.

Thanks, Anil.

Veronica S. Dawkins
Founder & CEO, LedgerProof Inc. · Founder, LedgerProof Foundation (in formation)
veronica@ledgerproofhq.io
IETF: `draft-dawkins-scitt-ai-article50-00` · spec.ledgerproofhq.io · github.com/ledgerproof

---

## Send #2 — Stillmark

**To**: [V to confirm — assumed partner address: alyse@stillmark.com OR partners@stillmark.com; verify against last received email from them]
**From**: veronica@ledgerproofhq.io
**Subject**: LedgerProof — Bitcoin-anchored AI Act Article 50 protocol; seed co-lead opportunity with 24-month model attached
**Attachment 1**: `14-seed-close-pack/01-cfo-24-month-model.pdf` (post-pressure-test)
**Attachment 2**: `14-seed-close-pack/02-threat-model-briefing.pdf`
**Attachment 3**: One-page Bitcoin-anchoring spec excerpt (the OP_RETURN `LPR1 || merkle_root_32` format documentation, drawn from `04-lpr-spec/`)

---

Alyse — [or whichever Stillmark partner V has been corresponding with]

Sending the seed materials we discussed. The Bitcoin-anchoring path is the part that distinguishes us from the "compliance SaaS for AI Act" cohort, and given Stillmark's Bitcoin-native thesis, that's the part I want to put in front of you specifically.

**The seed shape**: $12M total, $6M lead (TVP), $4M co-lead (we'd like that to be Stillmark), $2M strategic. Hercules $8M facility signed concurrently as undrawn runway insurance. Close 25 June 2026 ahead of EU AI Act Article 50 enforcement on 2 August.

**Why Stillmark specifically as co-lead, not just any seed-stage co-lead:**

1. We anchor receipt Merkle roots to Bitcoin mainnet via OP_RETURN (`LPR1 || merkle_root_32`, 36 bytes total). OpenTimestamps proofs. Verifier path is offline — Bitcoin chain + protocol public key + receipt. No SaaS dependency in the verifier path. This is the architectural commitment that lets a regulator in 2034 still verify a receipt issued in 2026. It's also the architectural commitment that competitors using vendor-trace logs structurally cannot make.
2. Foundation governance events (board minutes, key rotations, charter ratifications) are themselves Bitcoin-anchored as `foundation_governance_event/v1` records. The first one (yesterday's EU AI Office consultation submission) is awaiting block confirmation now. We'll be operating with verifier-checkable governance from day one.
3. We expect Bitcoin Core engagement at the protocol-stewardship level over the next 18 months — both because OP_RETURN footprint matters (we'll be ~144 anchors/day at scale, ~$17K/mo in fees), and because the Foundation's standardization path through IETF SCITT means the protocol is in the public record. Stillmark's network in that direction matters.

**On the model**: same model going to TVP, attached. Numbers were pressure-tested by Sarah Guo (Conviction) yesterday; the Stretch case reflects her substantive pushback. Y1 Base: $9.4M booked / $6.7M recognized / $14.2M cash / 14-mo runway pre-Series A.

**Specific Stillmark diligence pre-empts** (covered in the threat-model briefing, but flagging here so you can scope):

- Bitcoin anchor fee volatility risk: modeled at $17K/mo flat per A10; sensitivity to 5x fee spike covered in Downside case
- Key rotation cadence: interim Foundation Ed25519 signing key disclosed in spec; multisig root-key ceremony scheduled 15 August 2026, Bitcoin-anchored
- Foundation/Inc. separation: Adler & Colvin (501(c)(3)) and Cooley (C-corp) counsel on both sides; the grant agreement ($50K/mo Inc.→Foundation from Aug 2026) is structured to avoid private inurement
- OpenTimestamps dependency: we run our own calendar mirror and have a contingency plan if the public calendar servers degrade

What I'd ask you to do before we meet:

1. Read the threat-model briefing first. If the Bitcoin-anchoring story doesn't survive your technical read, the rest of the seed pitch doesn't matter and we should know that quickly.
2. Confirm whether Alyse [or whichever partner] is the right person for the technical side or whether someone else at Stillmark should be on the partner call.
3. Tell me your view on co-lead structure vs follow-on. The model assumes co-lead; if Stillmark prefers a smaller follow-on alongside TVP's lead, we can absorb that, but I'd want to know before the meeting.

Calendly: [V to insert]

EU AI Office consultation submission filed Tuesday. Adapter packages built across 29 frameworks; PyPI publish this week. LangChain co-publication conversation initiated with Harrison Chase Wednesday (he hasn't replied yet — flagging only because it's relevant if the LangChain partnership lands before our seed close, which would be reportable progress between now and 25 June).

Thanks.

Veronica S. Dawkins
Founder & CEO, LedgerProof Inc. · Founder, LedgerProof Foundation (in formation)
veronica@ledgerproofhq.io
IETF: `draft-dawkins-scitt-ai-article50-00` · spec.ledgerproofhq.io · github.com/ledgerproof

---

## Operator notes (NOT part of the sent emails)

### Pre-send checks before V says "send these"

- [ ] **Sarah Guo's call has concluded** — the [V to insert] placeholder about her pressure-test must be filled with actual findings, not handwave
- [ ] **The model has been edited** to reflect Sarah's substantive pushback (or you've confirmed she found nothing material that needs an edit)
- [ ] **The model PDF exists at** `14-seed-close-pack/01-cfo-24-month-model.pdf` — currently only the .md exists; convert via `tools/pdf-generator/md_to_pdf.py` before sending. Same for `02-threat-model-briefing.pdf`.
- [ ] **Recipient addresses verified** — Anil's actual address at TVP, Alyse's (or whoever) actual address at Stillmark. Best-guess email addresses on cold partners are a credibility hit; we don't have the same justification for guessing here that we had for Harrison.
- [ ] **Calendly URL inserted** in both emails (V to paste her actual booking URL)
- [ ] **Partner-meeting date inserted** in TVP email if a slot is already on the calendar
- [ ] **Threat-model briefing exists** — `02-threat-model-briefing.md` does exist per the file listing; needs PDF conversion + content sanity-check before attaching

### Why these emails together vs sequenced

Two seed conversations should run in parallel if both are real. If TVP and Stillmark are both expected to be co-leads on the same round, they should both have the same operating model the same morning. Sequential sends create the perception of a "first call" partner — fine if intentional, awkward if not.

If V wants to sequence them (send TVP first, gauge response, then send Stillmark 48 hours later), say so before send and I'll rebuild the Stillmark draft to acknowledge the TVP-first dynamic. Default is parallel.

### What I didn't put in these emails (deliberate)

- **No claim about the Foundation Board** — we don't have a ratified board yet. The cover doesn't pretend we do.
- **No claim about LangChain partnership being confirmed** — Harrison hasn't replied. The Stillmark email mentions only that the conversation was initiated, not that LangChain has agreed to anything.
- **No specific Allianz / Klarna / Adyen Founding Member name-drop** — until any of those are signed, name-dropping them in an investor email is the exact C1 discipline failure we're protecting against. Lokke's intro hasn't even come back yet.
- **No claim that the EU AI Office accepted or endorsed** the Tuesday consultation submission — it was filed; whether they read it or weight it is separate. The email says "filed," which is verifiable, and doesn't claim more.

### Day +2 follow-up template (if no response from either by Fri Jun 5 PT)

> [Partner first name] — quick follow-up on the operating model from [day of week of original send]. No urgency on partner meeting timing; just want to confirm the email got through and the attachments opened cleanly. If either is broken on your end let me know and I'll resend. Closing this week with momentum or without; either way I'd rather know which.
> 
> — V

### Day +5 follow-up (if still nothing by Mon Jun 8 PT)

V's call — at that point the soft-touch follow-up has been done. Next escalation is either (a) text Anil / Alyse directly if V has their numbers, or (b) accept that this firm is not going to engage on the current timeline and reroute the allocation. The seed needs to close 25 June; mid-June with no partner-meeting calendar slot means this firm cannot make the timeline regardless of intent.

### Risk: the Sarah Guo pressure-test surfaces something that requires a real model rebuild

If Sarah finds 6+ substantive holes (the threshold in `sarah-guo-pressure-test-script.md` for "rebuild Stretch"), these emails do NOT send Wed/Thu — they get rescheduled while the model rebuild lands. The cover emails as drafted assume Sarah's feedback is incorporable in <12 hours of edit work. If it's not, V hold-sends and tells me; I'll rewrite the cover to acknowledge the model is on a 1-week revision sprint, which is itself a credibility move (we found the holes, we're fixing them, we're not pretending) but is a fundamentally different email.
