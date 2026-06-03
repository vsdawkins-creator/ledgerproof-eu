# Commercial site landing-page wireframe

**Status**: Track 2.2 deliverable. Wed Jun 3, 2026.

## What this is

Single-page static wireframe of the new `ledgerproofhq.io` commercial landing page, built around the fear-led hero V specified:

> **Header:** Live high-contrast countdown clock to 2 Aug 2026.
> **Core hook:** "Will your enterprise partners drop your AI integration on August 2? Test your Article 50 compliance footprint instantly."
> **CTA:** Localized self-assessment input field for application endpoint URL.

## Files

- `index.html` — Single-file static page (~18 KB). Self-contained HTML+CSS+JS. No build step. View locally with `python3 -m http.server 8001` and open `http://localhost:8001/`.

## Layout (top to bottom)

1. **Black topbar** — brand mark, navigation (Tracker / Docs / Foundation / Security), language switcher (currently stub)
2. **Hero section (fear-led, dark gradient)**
   - Live countdown bar — large amber day-count + context line ("until EU AI Act Article 50 becomes legally enforceable on 2 August 2026")
   - H1 — "Will your enterprise partners **drop your AI integration** on August 2?" (the drop-your-AI line in brand amber for emphasis)
   - Subhead — frames the supply-chain vulnerability ("Procurement teams across European banks, insurers, payment processors, and Fortune 500 vendors are auditing their AI suppliers *now*")
   - CTA form — URL input + "Run exposure check →" button + privacy disclaimer + secondary link to public Compliance Tracker
3. **Exposure preview band** (amber-bordered, soft background)
   - "Most-exposed Fortune Europe this week" eyebrow in critical-red
   - 8 named EU enterprises with colored exposure dots (Critical / High)
   - Link through to full Compliance Tracker
4. **Three-up value props** (white, calm after the fear)
   - Open specification, no vendor lock-in
   - Substrate-agnostic, EU-sovereign-ready (Bitcoin + EBSI)
   - GDPR-compatible by structure
5. **Credibility band** (Foundation green)
   - IETF SCITT Working Group draft link
   - EU AI Office consultation reference
   - Specification URL
   - Source code repository
6. **Footer** (black)
   - Foundation status, license attributions, secondary links

## What's wired vs. stubbed

| Element | Status |
|---|---|
| Live countdown to Aug 2, 2026 | ✅ Functional JS, updates every minute |
| Exposure check form submission | ⚠ Stubbed (alert() with captured URL) — wires to the self-assessment tool in T2.3 |
| Language switcher | ⚠ Cosmetic only — will hook into i18n.json once site is unified with Tracker |
| Exposure preview chips | ⚠ Hard-coded from tracker data — will fetch from `companies.json` in v1 |
| All navigation links | Placeholder paths (`/compliance/`, `/docs/`, `/foundation/`, `/security/`, `/press/`, `/legal/`) — wire up at deploy time |

## Brand language used

- Foundation green `#0b3d2e` (deep) and `#0d4a37` (slightly lighter) — primary brand color
- Amber `#f59e0b` and `#fbbf24` — accent / countdown / CTA button
- Fear gradient: black to deep ox-blood — hero background
- White / soft-blue-grey body — calm value props after the fear hit
- Critical red `#b91c1c` — used sparingly, only for exposure indicators

## Why this layout

**The fear hits in the first 1.5 seconds.** Topbar → countdown number → hook. A visitor who lands on the page sees the day-count and the "drop your AI integration" headline before they've scrolled. The supply-chain framing (enterprise partner dropping you) is the fear V correctly identified as the actual EU mover: not "you might get fined" but "your customer's procurement will audit you and remove you."

**The CTA is the conversion event** — every visitor either pastes a URL (high-intent lead) or clicks through to the tracker (mid-intent). Both are captured.

**The exposure preview band turns abstract fear into specific names.** Eight publicly-listed EU enterprises in colored chips. The visitor's pattern-match is immediate: "if Deutsche Bank and SAP are critical-/high-exposure, my company probably is too." Then the click-through to the tracker turns suspicion into evidence.

**The three-up value props after the fear give the reader something to do.** Once they've absorbed the urgency, they need to understand why the protocol is the answer. Open spec / EU-sovereign-ready / GDPR-compatible covers the three EU compliance officer objections in 3 sentences.

**The credibility band is brief because the page leads with fear, not credentials.** IETF / EU AI Office consultation / spec URL / source code — enough to ground the claim that we're real. No founder name, no investor logos, no advisory board — those slow the conversion path.

## Path to v1 (next 7 days)

1. **Wire CTA form** to compliance.ledgerproofhq.io/check?url= (the self-assessment tool, T2.3 in V's strategy)
2. **Implement language switcher** properly — hook into the same i18n.json the Tracker uses; ship EN/DE/FR/IT/ES/NL/PL on day one
3. **Fetch exposure preview chips** from `compliance.ledgerproofhq.io/data/companies.json` so the homepage updates automatically when the tracker updates each Monday
4. **Add OpenGraph + Twitter Card meta** — the Aug 2 countdown + hook + amber-on-black design needs to render as a share card that drives clicks
5. **Add structured data** — Organization, WebSite, BreadcrumbList for Google rich-result eligibility
6. **Add favicon set** — current page lacks favicons; designer to produce
7. **Lighthouse pass** — current page should score 95+ on Performance/Accessibility/SEO; verify and fix

## Path to v2 (next 30 days)

1. **A/B test the hook line** — variant A: "Will your enterprise partners drop your AI integration on August 2?" vs variant B: "Your enterprise customer's procurement team is auditing your Article 50 compliance right now."
2. **Add sector-specific landing pages** — `/banking/`, `/insurance/`, `/payments/`, `/automotive/`, `/media/` — each with sector-specific exposure stats from the Tracker
3. **Add testimonial / case study slot** when the first Founding Member converts (currently 0)
4. **Add live exposure-check counter** — "847 European companies have run an exposure check this week" — social proof + visit recency
5. **Localize copy** — the EN copy here is the master; translation pipeline will need to handle nuance, especially in DE/FR where the fear framing needs cultural adaptation (Germans respond to "compliance violation"; French respond to "procurement audit"; Italians respond to "regulator notice")

## Deployment

- Static site. Recommend Vercel for instant deployment from this directory.
- Custom domain `ledgerproofhq.io` (apex) — this REPLACES the current commercial site at that domain
- HTTPS via Let's Encrypt (automatic on Vercel)
- Should redirect from `www.ledgerproofhq.io` → apex

## Risk to flag

The hard-coded company names in the exposure preview band ("Deutsche Bank AG", "SAP SE", etc.) are public statements that those companies are critical-/high-exposure per our methodology. This is defensible because:

1. The scoring rubric is published in the Tracker
2. The score is reproducible from publicly-verifiable evidence URLs
3. We are stating the presence/quality of disclosure infrastructure, not alleging non-compliance
4. Companies can submit additional evidence and we update the score

But V should be aware that landing-page mention of named companies is more visible than tracker-page-only mention. If any of these companies sends a takedown request, we respond by (a) pointing to the public methodology, (b) accepting additional evidence they provide, (c) updating the score with the next publication. We do NOT remove names absent factual challenge to the methodology.
