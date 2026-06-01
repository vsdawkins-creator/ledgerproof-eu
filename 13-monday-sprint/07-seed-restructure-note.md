# Seed restructure note to four co-leads — Monday June 1, 2026

**To:** [your individual TVP, Stillmark, Fulgur partner emails], Mark Beeston `<mb@illuminatefinancial.com>`
**Subject:** LedgerProof seed close — proposed two-stage structure + Monday update + asks
**Send via:** your individual email thread with each (NOT a single CC blast — this needs four parallel reply threads)
**Channel cadence:** send Tuesday June 2 at 09:00 PT to TVP + Stillmark; Wednesday June 3 at 08:00 ET to Fulgur + Mark Beeston (better local windows).

---

[Partner first name],

Two weeks to wire and I want to put the structure in front of you proactively rather than negotiate it under a clock. Two things in this note: a Monday-morning operations update; and a proposed restructure of the seed terms.

## Monday-morning update

Three items shipped over the weekend / today:

1. **First public errata published — `spec.ledgerproofhq.io/errata/001` (LPR-ERRATA-001).** A canonical chain integrity issue on Entry #0 surfaced when our public verifier (working correctly) flagged a content-hash mismatch on the genesis entry. I root-caused it in five minutes this morning: the bug is contained to one pre-v1.0 publisher draft artifact; all entries 1+ verify correctly; the verifier's canonicalization is sound; the Rust publisher's canonicalization is sound. Remediation is to enshrine Entry #0 as a permanent forensic artifact (the chain is append-only) and re-issue the canonical founding-declaration receipt on the v1.1 path this week. Trail of Bits engaged today for a 3-day independent audit (originally a 2-week engagement; the scope shrank because the bug was already root-caused).

   The point of mentioning this in our seed conversation: this is what operating an open protocol in public looks like. We will publish every errata, every audit memo, every governance decision as a receipt on our own chain. The chain catching its own bug, transparently, twelve months after issuance, is the property a regulator should care about — and it's the property that makes the structural moat real.

2. **PAT exposure remediated** (a GitHub token had been syncing through Dropbox; scrubbed Friday, revoked github.com-side today, full secret rotation underway with Keychain-only credential storage from here forward). No commits, releases, or production state were ever altered by an unauthorized party — audit log clean — but the surface is now closed.

3. **Adler & Colvin engaged today as Foundation counsel.** 501(c)(3) formation, Day-1 IP license (Inc.→Foundation, perpetual royalty-free) targeted to USPTO by June 15, Form 1023 long-form filed by July 15 with expedited handling. The Day-1 IP license is the document that makes the structure real — it survives Inc.'s failure, acquisition, or change of control.

## Proposed two-stage seed structure

Original term sheet: **$15M at $45M post-money on a SAFE, single tranche, closing June 25.**

Proposed restructure: **$10M at $45M post on June 25 + $5M tranche at $60M post on September 30**, with the tranche conditioned on three milestones:

- (a) Two signed Tier-1 EU FSI design-partner pilots at $1 + warrant + reference rights — public press release at launch
- (b) Trail of Bits public attestation memo published (`security.ledgerproofhq.io/tob/2026-06-canonicalization-audit`)
- (c) Either IETF Working Group adoption sponsor secured for `draft-dawkins-scitt-ai-article50-01` OR CEN-CENELEC JTC 21 New Work Item Proposal accepted

## Why this structure (the honest version)

I am asking you to do less work now and more work in September, in exchange for a higher valuation on the second half. Three reasons it benefits us all:

**1. Price anchor.** A $60M post-money September tranche pre-prices the Series A floor. If we hit the three milestones, a December 7 Series A at $180M post-money is a 3x markup in 76 days, not from a manufactured comparable. That structurally protects everyone's seed-stage entry price.

**2. Founder dilution.** Tranching $5M at a higher post-money reduces seed-round dilution by ~2 percentage points without changing the dollars in the door. With me as a single founder pre-CTO-hire (the CTO-of-Protocol offer goes out next week with a July 31 hard deadline), every preserved point on the cap table matters for the recruiting conversations that follow.

**3. Velocity gating.** The milestones are exactly the three deliverables that prove the Series A narrative is real, not theoretical. The tranche structure forces all four of us to be honest about September execution in a way a single-tranche close doesn't.

The structure does not change the **commitment** — same $15M total, same investor set, same wire timing for the first $10M. It changes the **shape** of the commitment to one that compounds.

## What I'm asking

A 20-minute call this week to confirm the structure is acceptable in principle. Once all four of you are aligned, Cooley (Jodie Bourdet drafting the tranche-trigger clause) updates the SAFE template and the four signatures land on individual subscription agreements (not joint, so any one delay doesn't block the others) by **June 18 — one week before the nominal close**.

If the two-stage doesn't work for your fund's structure, I want to know that today so we can pivot the term sheet rather than discover it on the wire day. If it works, please confirm in writing by Wednesday June 3.

## What's in the diligence pack ready for your full read

DocSend link sent under separate cover. 15 artifacts:

- LPR Specification v1.1 + IETF Internet-Draft
- LPR-ERRATA-001 (today's first public errata)
- Founding-declaration receipt content (issued via publisher portal Wednesday)
- Trail of Bits engagement letter
- Adler & Colvin engagement letter
- Foundation governance memo + Day-1 IP license draft
- Independent board candidate slate (Mishi Choudhary chair, Allison Randal audit, Lokke Moerel compliance)
- Hercules Capital $8M undrawn debt facility term sheet
- Master Plan + Code Plan V2
- 10X Playbook (the Monday-morning operations document)
- Production metrics from `api.ledgerproofhq.io` since May 18
- The 8-item 7-day hot path (status as of Monday EOD)
- 12-week cash flow model (Pilot.com fractional CFO; ready by June 22)
- Foundation Continuity Protocol (signed by interim COO, Foundation Treasurer, CTO-of-Protocol once hired)
- Customer-facing materials: persona-targeted Day-30 cold-email .eml files (`lpr-gtm` generated, brand-validated, hash-stamped, dogfood-anchored)

**Verifier proof we exist:** `verify.ledgerproofhq.io/r/founding-declaration` — live by Wednesday this week as the canonical founding receipt issued on the v1.1 path; Entry #0 (the broken genesis) preserved alongside as a museum-page forensic artifact at `docs.ledgerproofhq.io/entries/0`.

I'm in PT through Wednesday, in CET starting Thursday. Call windows:

- Tuesday June 2: 09:00–11:00 PT and 14:00–17:00 PT
- Wednesday June 3: 08:00–11:00 PT
- Thursday June 4: 14:00–19:00 CET (Frankfurt)

Pick any 20-minute window that works; I'll send the calendar invite.

Best,
Veronica
veronica@ledgerproofhq.io
+1 [TBD]

---

## Sender notes (for Veronica's eyes only — not in the email)

- Personalize the opening to each partner. TVP partner: reference their FSI thesis explicitly. Stillmark partner: reference their Bitcoin-native infrastructure thesis. Fulgur partner: reference their Lightning + open-protocol portfolio framing. Mark Beeston: shorter version of this note, leaning on the FSI-procurement-velocity reframe you've been working with him on.
- DocSend turns on view-tracking — you will see who opens the pack and who skips. Use that signal.
- The Trail of Bits + Adler & Colvin + Hercules emails go out the same day this restructure note goes out. Stagger so the diligence pack opens with the engagement letters already inside.
- If any co-lead replies "we'd prefer to keep the single tranche," do not negotiate over email — get on the phone same-day. The reason to push the structure is to protect the cap table; if they insist on single-tranche, that itself is a signal worth understanding live.
- If TWO or more co-leads push back on the two-stage, abandon it that same day. Single tranche is the fallback; do not let an unsuccessful restructure delay the wire.
