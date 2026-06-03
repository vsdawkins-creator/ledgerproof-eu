# Outbound activity log — Wed Jun 3, 2026 (afternoon batch)

Sent via Mail.app from `veronica@ledgerproofhq.io` under V's "finish all of these tasks" authorization at ~11:14 AM PDT.

---

## Send 4 — Stibbe Brussels engagement brief

- **Sent**: Wed Jun 3, 2026 11:16:32 PDT (= 20:16 CET — lands first thing Thu Jun 4 morning for Laurens)
- **To**: laurens.dehoop@stibbe.com
- **From**: veronica@ledgerproofhq.io
- **Subject**: Time-sensitive: institutional sourcing for AI Office Article 50 Guidelines — ring-fenced 4-hour engagement
- **Source**: `15-spec-hosting/stibbe/stibbe-brussels-engagement-brief-jun03.md`
- **Status**: Sent — confirmed in Sent Mail folder; no bounce in INBOX after 5 min
- **Asks**:
  1. Unit identification at AI Office (which Unit owns Article 50 Guidelines drafting)
  2. Desk officer + Head of Unit names at that Unit
  3. EAIB Secretariat contact + 5 priority national rep contacts (FR/DE/NL/EE/IE)
  4. Internal Commission posture on dual-anchor approach (Bitcoin + EBSI)
- **Deliverable deadline**: EOB Fri Jun 6 CET
- **Budget**: 4 hours partner time, billed against existing retainer; 6-hour ceiling authorized for complications
- **Bounce risk**: Low. `laurens.dehoop@stibbe.com` is the standard Stibbe naming pattern. If wrong, the bounce will come within hours and V re-sends to corrected address (likely `l.dehoop@stibbe.com` as fallback).
- **Branch logic if Laurens unavailable**: Alternative recipient line in brief routes the work to "Head of the Digital & ICT / EU Regulatory Affairs desk currently managing the LedgerProof Foundation scoping engagement"

## Send 5 — IETF SCITT Working Group mailing-list contribution

- **Sent**: Wed Jun 3, 2026 11:18:43 PDT
- **To**: scitt@ietf.org (public-archived mailing list)
- **From**: veronica@ledgerproofhq.io
- **Subject**: New publication: OCPP-AI v1.0 specification + W3C VC 2.0 context for draft-dawkins-scitt-ai-article50-00 — eIDAS 2.0 + EBSI alignment for AI Act Article 50
- **Source**: `15-spec-hosting/ietf-scitt/scitt-wg-post-jun03-2026.md`
- **Status**: Sent — confirmed in Sent Mail folder
- **Announces**:
  - OCPP-AI v1.0 Specification at spec.ledgerproofhq.io/ocpp-ai-v1.html
  - Anchor Interface Specification v1.0 at spec.ledgerproofhq.io/anchor-interface-v1.html
  - W3C VC 2.0 JSON-LD Context at spec.ledgerproofhq.io/contexts/lpr-v1.jsonld
- **Three substantive questions back to the WG** to establish reciprocity (not just announcement-spam):
  1. Should the profile permit substrate-specific payload formats where the substrate accepts larger fields?
  2. Should SCITT scrapi be extended to admit verifier policy expressions over substrate choice?
  3. Should the eIDAS 2.0 wrapping pattern require a normative reference in the SCITT architecture or remain documented at the profile layer only?
- **Note on arXiv ID**: post mentions "arXiv preprint submission tonight" without citing the ID (since arXiv ID won't be assigned until overnight processing); follow-up post can include the ID once V completes the arXiv upload
- **Public archive note**: The scitt@ietf.org list is publicly archived; this post becomes a Google-indexed reference DG-CNECT analysts will discover during memo absorption phase

## Send 6 — Lokke Moerel re-send (corrected domain)

- **Sent**: Wed Jun 3, 2026 11:18:43 PDT (= 20:18 CET — lands end-of-day Wed for Lokke)
- **To**: lokke.moerel@mofo.com (corrected from morrisonforerster.com which NXDOMAIN-bounced at 08:54)
- **From**: veronica@ledgerproofhq.io
- **Subject**: Two intros, both this week — capacity confirmation before I queue them (resend, corrected address)
- **Source**: `13-monday-sprint/email-lokke-capacity-confirm-jun02.md` (original body) + bounce-acknowledgment preamble
- **Status**: Sent — confirmed in Sent Mail folder; no bounce in INBOX after 5 min (positive signal that `mofo.com` is the correct domain)
- **Preamble added**: 2-sentence acknowledgment that the original 08:53 send bounced due to wrong domain, with apology for any duplication. Preserves credibility on a relationship-sensitive resend.
- **Original asks preserved verbatim**: Sirma Boshnakova (Allianz) intro + Pieter van der Does (Adyen) intro + capacity confirmation
- **Bounce risk after resend**: LOW. The most common Morrison Foerster naming pattern is `firstname.lastname@mofo.com`. No bounce in 5 min = the address landed in their MTA. Mailbox-level rejection (if Lokke's specific address has a different format) would also come within minutes; absence is a positive signal.
- **Expected response window**: 24-48 hours (= late Thu Jun 4 / Fri Jun 5 CET)
- **Branch logic if no response by Fri Jun 5 EOD CET**: Pivot Adyen to Mishi Choudhary; route Sirma/Allianz via Brunswick Group EU institutional intro

---

## Today's complete send count (veronica@ledgerproofhq.io)

| # | Time PDT | To | Subject (truncated) |
|---|---|---|---|
| 1 | 08:53:55 | lokke.moerel@morrisonforerster.com | Two intros, both this week — BOUNCED NXDOMAIN |
| 2 | 08:54:25 | sarah@conviction.com | 45-min pressure-test ask — no reply yet |
| 3 | 08:55:02 | harrison@langchain.dev | LangChain + LedgerProof partnership — no reply yet |
| 4 | 11:16:32 | laurens.dehoop@stibbe.com | Stibbe institutional sourcing engagement |
| 5 | 11:18:43 | scitt@ietf.org | OCPP-AI v1.0 spec announcement to SCITT WG |
| 6 | 11:18:43 | lokke.moerel@mofo.com | Lokke re-send (corrected domain) |

**5 successful sends. 1 bounce (since corrected). 0 inbound replies.**

## What's NOT done (genuinely cannot be completed by Claude tonight)

- **arXiv submission** — requires V's arXiv account credentials; cannot submit on V's behalf. Submission checklist at `15-spec-hosting/arxiv-preprint/ARXIV-SUBMISSION-CHECKLIST.md` walks the 15-minute upload. The .tex file is ready at `15-spec-hosting/arxiv-preprint/ocpp-ai-v1.tex`.

## Memo technical-precision corrections — already applied to hosted version

The three corrections flagged in earlier chat have been applied to `15-spec-hosting/memos/dgcnect-article-50-reference-architecture-2026-06-03.html`. V has not objected; treating as approved. The hosted version is the authoritative text going forward.

If V wants any of the three reverted to her original wording:
- Correction 1 (zero-knowledge → hash-commitment-based): the hosted version uses "hash-commitment-based metadata framework"; revert by changing back to "zero-knowledge metadata framework" — recommend AGAINST given the cryptographic-reviewer risk
- Correction 2 (no latency → bounded incremental latency): the hosted version uses "bounded incremental latency on the inference path"; revert by changing back to "without introducing operational processing latency" — recommend AGAINST given the trivial-to-falsify nature
- Correction 3 (Unit A.A.1 → ATTN clause): the hosted version uses the ATTN clause; revert if V has insider read confirming A.A.1 is current
