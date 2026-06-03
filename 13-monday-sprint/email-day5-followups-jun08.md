# Day +5 follow-up emails — Mon Jun 8, 2026 (DRAFT — hold until needed)

**Status**: Staged drafts. **Do NOT send** any of these until Mon Jun 8 EOD PT and only if the corresponding original send has NOT received a reply by then.

**Decision rule per recipient**:
- If they've replied at all (even "let me think about it"): do NOT send the follow-up. The thread is alive.
- If they've replied with a "no": do NOT send the follow-up. Respect the no.
- If silence past Mon Jun 8 09:00 PT: send.

**Authorization to send**: Requires fresh V authorization the same way the original 3 sends required it. The drafts here are pre-baked, not pre-approved.

---

## Follow-up #1 — Lokke Moerel (Day +5 from Jun 3 original)

> **IMPORTANT**: This assumes the original Jun 3 send to Lokke ACTUALLY REACHED HER. The original 08:53:55 PDT send to `lokke.moerel@morrisonforerster.com` BOUNCED (NXDOMAIN — the domain doesn't exist). The correct Morrison Foerster domain is `mofo.com`. Until V confirms Lokke's actual address and a successful re-send lands in her inbox, the Day +5 timer hasn't started for her. This follow-up template assumes a successful re-send happened on whatever day V confirms.

**Send window**: Day +5 from successful re-send (NOT from original Jun 3 attempt)
**To**: [V to insert — likely `lokke.moerel@mofo.com`; V to verify against prior correspondence]
**From**: veronica@ledgerproofhq.io
**Subject**: Re: Two intros, both this week — checking on capacity (no urgency, just timing)

---

Lokke —

Quick follow-up on the capacity-confirm note from [day of week of successful re-send]. No urgency, just want to make sure the email got through cleanly — I made an address typo on my first attempt and want to be sure the corrected one landed.

If the Sirma Boshnakova (Allianz) intro is something you have bandwidth for in the next 2-3 weeks, that's our most time-sensitive ask given the August 2 EU AI Act enforcement date. The Pieter van der Does (Adyen) intro is less time-sensitive — I have a Mishi Choudhary pivot ready if you'd rather pass on that one.

If both are out of capacity right now, just say so. I'll route Allianz via Brunswick Group EU and Adyen via Mishi without further hassle.

Either way, thank you for the original 2024 conversation about Foundation governance — the Stichting / 501(c)(3) split structure we're using traces directly to your read on Dutch foundation law.

— V

Veronica S. Dawkins
veronica@ledgerproofhq.io

---

## Follow-up #2 — Sarah Guo (Day +5 from Jun 3 original)

**Send window**: Mon Jun 8, 09:00 PT (only if no reply by then)
**To**: sarah@conviction.com
**From**: veronica@ledgerproofhq.io
**Subject**: Re: 45-min ask: pressure-test our operating model — last chance before TVP/Stillmark see it

---

Sarah —

Quick follow-up on the pressure-test ask from Wed. No urgency on your end; I know your inbox.

Updated context: TVP + Stillmark are now scheduled to receive the operating model this Wednesday [V to update date based on actual TVP/Stillmark meeting calendar]. If you can spare 30 minutes (down from the original 45 ask) between now and Tuesday EOD PT, that's the realistic window for your pressure-test to actually affect what they see. After that, the model ships as-is.

If 30 min is still too much, even a 15-min "what's the single worst objection an LP would raise on the Stretch case" would help. Voice memo on Signal works too if synchronous is hard.

If this isn't a fit, no follow-up needed — I'll route the pressure-test to Mark Beeston at Fund Recs.

Thank you for what you've already given the AI ecosystem with Conviction. The work matters.

— Veronica

veronica@ledgerproofhq.io

---

## Follow-up #3 — Harrison Chase (Day +5 from Jun 3 original)

**Send window**: Mon Jun 8, 09:00 PT (only if no reply by then)
**To**: harrison@langchain.dev (or `harrison@langchain.com` — V to confirm which the original was sent to and whether it bounced)
**From**: veronica@ledgerproofhq.io
**Subject**: Re: LangChain + LedgerProof — adapter now on PyPI, easier to evaluate

---

Harrison —

Following up on the partnership note from last Tuesday. No urgency on your end; I know LangChain's inbox is loud right now.

Update that may simplify a quick evaluation on your side before any partnership conversation: the adapter is now installable via `pip install ledgerproof-langchain` (just landed on PyPI). Docs at [V to insert PyPI URL once published, e.g. `https://pypi.org/project/ledgerproof-langchain/`]. Full integration example in the README. Article 50 receipt schemas (`chatbot_session/v1`, `generated_content/v1`, `human_review/v1`) all working against a current LangChain 0.x build.

If a 15-minute call is easier than the original 30-minute one for the first touch, that works too. If LangChain doesn't see Article 50 as a category that matters to your Q3 roadmap, that's also useful for me to know — I'd rather route the partnership conversation to a primary alternate (LlamaIndex Inc., Jerry Liu) than stay in your inbox waiting.

The May AI Act crosswalk post on the LangChain blog is the cleanest analysis I've read of what an orchestration framework actually owns under each article. Whatever the partnership outcome, thank you for that work.

— Veronica

veronica@ledgerproofhq.io
IETF: `draft-dawkins-scitt-ai-article50-00`

---

## Operator notes

### Per-recipient decision tree before sending

```
For each recipient:
  Has she/he replied? → DO NOT SEND. Thread alive.
  Has she/he sent a clear "no"? → DO NOT SEND. Respect the no.
  Has the address been verified deliverable? (no bounce) → CHECK BEFORE SEND
  Has it been 5+ days since deliverable send? → SEND
  Otherwise → WAIT
```

### Pre-send checks for each follow-up

**Lokke specifically — DO NOT SEND** until V has:
1. Confirmed Lokke's correct email address (likely `lokke.moerel@mofo.com`)
2. Re-sent the original Jun 3 capacity-confirm email to the corrected address
3. Confirmed the re-send did not bounce
4. Waited 5 business days from the re-send (NOT from Jun 3)

**Sarah specifically — Check before sending:**
- Has any time slot from the original Wed/Wed/Thu offer been confirmed? If yes, no follow-up.
- Has Sarah been quoted in public anywhere this week saying she's traveling / on a partner offsite? If yes, extend deadline by 5 more days.

**Harrison specifically — Check before sending:**
- Has the LangChain Twitter/blog posted anything about partnership announcements this week? If yes, our note may have hit during a launch week — extend deadline by 3 more days.
- Has the adapter actually shipped to PyPI by Mon Jun 8? If NOT, the "update that may simplify your evaluation" framing breaks — rewrite the follow-up to drop the PyPI claim.
- Verify which email address the original landed at — Harrison's actual address may be `@langchain.com` not `@langchain.dev`. If the original bounced, this follow-up to a new address looks like cold-outreach not follow-up.

### Day +10 follow-up (if Day +5 also goes unanswered)

V's call at that point — I won't pre-draft a Day +10. Three touches with no response is a clear signal; a fourth is harassment. The Day +10 decision is:

- Lokke: drop and reroute to Brunswick Group EU
- Sarah: drop and reroute to Mark Beeston
- Harrison: drop and reroute to Jerry Liu at LlamaIndex Inc.

These are documented pivots from earlier planning, not improvisations.

### What I deliberately did NOT do in these drafts

- **No guilt language** ("I haven't heard back...") — reads as needy on a Day +5 touch
- **No fake urgency** beyond the actual TVP/Stillmark and Aug 2 enforcement dates that exist anyway
- **No "circling back" / "bumping this" / "just checking in"** — empty calories
- **No claim that other recipients have already agreed** — that's manipulation
- **No re-attaching the original ask** — they got it; if they cared they'd have replied. Shorter is more respectful of their time.

The follow-ups give each recipient an easy out ("if this isn't a fit, just say so") because that's what shortens the loop. An honest no this week is more valuable to us than a polite-yes-but-actually-no in three weeks.
