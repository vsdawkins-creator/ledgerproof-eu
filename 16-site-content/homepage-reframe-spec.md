# Homepage Reframe Spec — `ledgerproofhq.io/`

**Drafted**: Mon Jun 1, 2026 — 22:05 PDT
**Author**: Veronica S. Dawkins (drafted via the Atomic Explosion sprint)
**Target ship**: Wed Jun 3 EOD PT (before counterweight outreach lands)
**Scope**: The marketing-facing homepage at the root of `ledgerproofhq.io`. NOT a full site rebuild — a single-page reframe.
**Operating reference**: `14-seed-close-pack/04-atomic-explosion-master-plan.md` + `memory/context/brand-system.md`

---

## The problem this fixes

The current homepage leads with *"Cryptographic attestation for the documents that carry institutional consequence"* and features the LedgerProof Locker as the primary product. That's the legacy document-attestation positioning.

Every other artifact in this repo — the IETF draft, the operating model, the audit briefing, the counterweight outreach, the Foundation governance docs, the Article 50 landing page — is positioned around the **Article 50 transparency protocol** play.

If V routes Klarna, Adyen, ING, Wise, or Allianz to `ledgerproofhq.io/` on Wed Jun 3, they land on the wrong product. The reframe must ship before that.

## Strategic positioning (the lede in 50 words)

LedgerProof is the open Bitcoin-anchored protocol that produces cryptographic transparency receipts for AI-touched interactions under EU AI Act Article 50. Foundation-stewarded, locally verifiable, no SaaS dependency. Article 50 enforcement begins August 2, 2026.

## Hero section (above the fold)

**Eyebrow** (mint color, small caps): `OPEN PROTOCOL · IETF SCITT TRACK · LIVE`

**H1** (serif display, navy):
> Transparency evidence for the AI you already ship.

**Subhead** (sans, ink-soft, ~22pt):
> EU AI Act Article 50 enforcement begins August 2, 2026. LedgerProof is the open cryptographic protocol that produces verifiable receipts for every AI-touched interaction — Foundation-stewarded, anchored to Bitcoin, verifiable offline by any auditor, regulator, or you.

**Three primary CTAs** (pill buttons, navy bg + mint text, all same width, horizontal row on desktop, stacked mobile):
1. `Become a Founding Member` → `/commercial/founding-members`
2. `See it work in 10 minutes` → `/developers/quickstart`
3. `Read the open protocol` → `/spec` (or IETF draft if `/spec` not ready)

**Trust strip** (mint thin rule + small ink-soft text, below CTAs):
> IETF SCITT-track draft on Datatracker · Cryptographic audit memo publishing August 31 · Foundation Form 1023 in process

## Section 2 — What it is (the protocol explanation)

**Eyebrow**: `THE PROTOCOL`

**H2** (serif):
> One receipt per AI-touched interaction. Anchored to Bitcoin. Verifiable forever.

Three-column "what happens" pattern (mint top-border cards, white on cream):

| 01 Emit | 02 Anchor | 03 Verify |
|---------|-----------|-----------|
| Your AI system emits a signed receipt for each interaction. Five-minute SDK install (Python or TypeScript). Receipts include the model identifier, the prompt and response hashes, the timestamp, and the deployer context — no PII required. | Receipts batch into a Merkle tree at the operator side. The tree root anchors to Bitcoin mainnet via OP_RETURN at a configurable cadence (default 60 minutes). The anchor is permanent. | Any auditor, regulator, or customer can verify a receipt offline: Bitcoin chain + the published protocol public key + the receipt itself. No call to LedgerProof servers required. Reference verifier is open-source and runs in the browser. |

**Quiet line below** (ink-soft, italic):
> Verification is structurally independent of LedgerProof. If we disappear tomorrow, every receipt ever issued remains verifiable.

## Section 3 — Why now (Article 50 context)

**Eyebrow**: `AUGUST 2, 2026`

**H2** (serif):
> Article 50 is the transparency floor. We make the floor auditable.

**Body** (~150 words):
EU AI Act Article 50 obligates deployers of GPAI systems to make AI-touched interactions transparent to regulators and to the natural persons interacting with the system. Enforcement begins Tuesday August 2, 2026.

The obligation is real. The evidence format is not yet specified. Today's compliance answer is logs in a CloudWatch bucket or a vendor PDF that the regulator cannot independently verify. After August 2, that answer needs to be cryptographic, machine-readable, and auditable in seconds.

LedgerProof is the protocol that produces that evidence. It is open. It is permissionless. It is Bitcoin-anchored. It is offline-verifiable. We do not offer presumption of conformity (that flows through CEN-CENELEC harmonized standards under Article 40 — a separate process we participate in). We offer the cryptographic evidence trail that a competent authority can re-verify from public sources.

**CTA inline**:
> See the Article 50 deployer brief →  *[/article-50]*

## Section 4 — Two entities (Foundation + Inc.)

**Eyebrow**: `STRUCTURE`

**H2** (serif):
> The protocol is owned by the Foundation. The operator is one of many.

**Two-column comparison** (white cards):

| LedgerProof Foundation | LedgerProof Inc. |
|------------------------|------------------|
| US 501(c)(3) public charity (Delaware, in formation) with Dutch Stichting EU subsidiary (Amsterdam) | Delaware C-corporation |
| Owns the protocol specification, conformance test vectors, reference verifier, and reference operator | Commercial operator — ships the SDKs, the SIEM connectors, and hosted services |
| Governance: independent board, advisory council, IRS Form 1023 in process | Governance: standard venture-backed company |
| Funded by: IP license from Inc., grants, capped Foundation member dues | Funded by: seed close June 25, customer revenue |
| Mandate: maintain the protocol as public-interest infrastructure | Mandate: build the leading operator implementation |

**Quiet line below**:
> The protocol's permissionless openness limits the operator's monopoly economics. That's by design.

**CTA**: `Read the Foundation governance` → `/foundation`

## Section 5 — Who's deploying

**Eyebrow**: `DEPLOYERS`

**H2** (serif):
> Founding Members ship the protocol in production from Day 1.

**Logo strip** (or named list if logos not confirmed by ship):

Before Jul 6 launch: hold this section as a placeholder with text like *"Founding Member logos publish at July 6 launch. Reserve your tier by June 22 to be among them."*

After Jul 6 launch: actual logos from confirmed Founding Members.

**CTA**: `Become a Founding Member` → `/commercial/founding-members`

## Section 6 — Open by default (developer hook)

**Eyebrow**: `OPEN`

**H2** (serif):
> Built on open code. Audited by independent firms. Anchored to Bitcoin.

Three-row content list (mint dots, navy text):

- **IETF SCITT-track** — `draft-dawkins-scitt-ai-article50-00` published on Datatracker. Working group adoption in progress.
- **Open-source SDKs** — Python (`pip install ledgerproof`), TypeScript (`npm install @ledgerproof/sdk`), Rust. Apache 2.0 license. Receipts produced and verified offline.
- **Independent cryptographic audit** — NCC Group, Trail of Bits, and Cure53 engagements opening week of June 8. Combined audit memo publishes August 31 at `security.ledgerproofhq.io`.

**CTA**: `Try the 10-minute quickstart` → `/developers/quickstart`

## Section 7 — Final invitation (the founder line)

**Quiet section** (cream-on-cream, no card, italic serif):

> *"The compliance regimes that produce real public benefit are open ones. The protocol that proves AI compliance to regulators, customers, and auditors should be open, permissionless, and free of single-vendor capture. That's the protocol we're building. If you're a deployer who needs Article 50 evidence by August 2, an engineer who wants to read the spec, or a regulator who wants to verify a receipt for yourself — you're welcome here."*
>
> — Veronica S. Dawkins, Founder

CTA row (same three buttons as hero):
1. `Become a Founding Member`
2. `See it work in 10 minutes`
3. `Read the open protocol`

## Footer

- **Foundation**: about · governance · board · transparency reports · contact
- **Protocol**: spec · errata · test vectors · IETF draft · GitHub
- **Developers**: quickstart · SDKs · plugins · open issues
- **Commercial**: Founding Members · enterprise · pricing · contact
- **Security**: audit memos · responsible disclosure · `security@ledgerproof.org`
- **Legal**: privacy · terms · IP license

Bottom row: copyright LedgerProof Foundation 2026 · Built in public. Anchored to Bitcoin.

## What to KEEP from the current homepage

- The brand system: cream `#FAF7F0`, navy `#081424`, mint `#20E898`, serif display
- The button shape (pill, navy bg, mint text)
- The card pattern (white-on-cream, 4pt mint top-border)
- The trust-strip pattern under hero
- The footer structure (links columns)

## What to REMOVE / MOVE

- **Remove from homepage**: LedgerProof Locker headline + three-pillar section. The Locker is a separate product surface that moves to `/locker` as a Q3 2026 product page.
- **Remove from homepage**: the document-targets list (contracts, BOR letters, personnel files, etc.). This is legacy document-attestation positioning that doesn't match the Article 50 thesis.
- **Remove from homepage**: the activation-email reservation form for Jul 6. That stays, but moves to `/commercial/founding-members` as the standard-tier signup flow.
- **Move to `/locker`**: anything Locker-specific.
- **Move to `/letter`**: the longer narrative founder voice. Homepage keeps a short founder quote in Section 7.

## What to ADD (referenced from homepage but lives on other pages)

- `/foundation` page (drafted at `16-site-content/foundation.md`)
- `/commercial/founding-members` page (drafted at `16-site-content/founding-members.md`)
- `/developers/quickstart` page (drafted at `16-site-content/developers-quickstart.md`)
- `/security` page (post-Aug 31 audit memo publication; ship structure now, content lands Aug 31)

## Implementation notes for whoever rebuilds the page

- The page lives at `index.html` in the `ledgerproof-site` repo (Vercel-deployed).
- Brand CSS already exists at `/assets/brand.css`. Use the existing tokens.
- Existing `<style>` block in current `index.html` has the brand variables — copy them, don't rewrite.
- Existing pill-button pattern (`.btn-primary`) — copy, don't reinvent.
- Existing card pattern (mint top-border) — copy from the Article 50 page if it's there.
- Mobile: stacked CTAs, single-column cards, hero subhead becomes single-column block.
- Performance: no JS frameworks. Pure HTML + CSS. Match the current site's "no SPA" discipline.

## Out of scope for this reframe (handle separately)

- Domain `ledgerproof.org` brand alias work (PR #1 already in flight on the verifier repo)
- `/spec` page rebuild (defer to standards engineer post Jul 13 hire)
- `/security` page content (lands Aug 31 with audit memo)
- Adding a blog or news section (defer; the Watchlist newsletter handles this surface on Beehiiv)

## Success criteria

Wed Jun 3 EOD PT: the reframe ships. Verification:
1. Open `ledgerproofhq.io/` in a private browser window
2. The H1 reads "Transparency evidence for the AI you already ship" (not "Cryptographic attestation for documents...")
3. The three hero CTAs all link to the correct destinations
4. The page loads in under 2 seconds on a 3G connection
5. Mobile rendering passes the eye-test
6. All three CTAs work end-to-end (target pages exist or 404 cleanly with a sensible message)

If `/founding-members`, `/developers/quickstart`, or `/foundation` are not yet shipped, the CTAs land on a "coming July 6" stub page with the correct URL — better than a 404 — and a single email-capture form for follow-up.
