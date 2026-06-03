# EU AI Act Article 50 Compliance Tracker — scaffold

**Status**: Track 2.1 scaffold. Wed Jun 3, 2026. Sprint deliverable.

## What this is

A multilingual (DE/FR/IT/ES/NL/PL/EN) public web dashboard scoring major European enterprises against the transparency obligations of EU AI Act Article 50. Designed to become **the canonical citation source for the post-Aug 2 enforcement press cycle**, equivalent to what enforcementtracker.com became for GDPR.

## Files

| File | Purpose |
|---|---|
| `index.html` | Single-page static dashboard. Self-contained: HTML + CSS + JS in one file (~12 KB). No build step. Hosts anywhere (Vercel, Netlify, CloudFront, GitHub Pages, S3). |
| `data/companies.json` | The scoring data. 10-company seed for v0; schema documented in the file itself. |
| `data/i18n.json` | 7-language translations of every UI string. New language = add language code to the strings dictionary. |

## How to view locally

```bash
cd 19-mass-adoption/tracker
python3 -m http.server 8000
# open http://localhost:8000/
```

Or use any static server. No npm, no build, no dependencies.

## What's in the v0 scaffold

10 seed companies across 7 sectors (banking, payments, BNPL, insurance, enterprise software, automotive, media, telecom) covering 4 Member States (DE, NL, FR, ES, LU) + Sweden. Each company has:

- Legal name + LEI
- Headquarters Member State
- Industry
- 4 Article 50 sub-obligation scores (0-5 each, per the published rubric)
- Overall exposure band (low / moderate / high / critical)
- Named national competent authority
- Public-evidence URL

## Scoring rubric

Embedded in `companies.json` under `scoring_rubric`:

- 0 = no evidence of disclosure infrastructure
- 1 = generic AI-use acknowledgment, no specific mechanism
- 2 = generic notice present, not consistently applied
- 3 = sub-obligation-specific mechanism present but incomplete
- 4 = sub-obligation-specific mechanism present and consistently applied
- 5 = machine-readable cryptographic evidence in conformance with an open standard

This rubric is defensible because it scores **publicly-verifiable evidence only**. The scoring does not allege non-compliance — it scores the presence and quality of disclosure infrastructure. Companies wishing to provide additional evidence can contact the Foundation; their score updates with the next weekly publication.

## Path to v1 (next 14 days)

1. **Expand to 100 companies** — V or analyst sources from FTSE 100 + EuroStoxx 600 + named AI-using enterprises. Manual research per company, ~30 min each. ~50 hours total work, distributable.
2. **Add national-language analyst notes** — short paragraph per company in 7 languages explaining the score, citing the public evidence URL.
3. **Add weekly delta tracking** — `data/companies-2026-06-10.json`, `data/companies-2026-06-17.json`, etc. so we can show "improved this week" / "regressed this week" trend arrows.
4. **Methodology page** at `/methodology/` — translated documentation of the scoring approach for press defensibility.
5. **Companies-section "claim your record" form** — companies can submit additional evidence via a form that emails the Foundation; we re-assess and update with the next publication.
6. **Sector-aggregate roll-up views** — "Average score for EU banking sector" / "Average score for EU automotive sector" — these are the headline numbers Politico EU will quote.
7. **Press kit** — pre-rendered PNG of the table per language, sized for social-media share. Each weekly publication ships with the press kit auto-generated.

## Deployment notes

- Site is fully static. Recommend Vercel or Netlify for instant CI/CD from this directory.
- Domain target: `compliance.ledgerproofhq.io` (subdomain of the main commercial site).
- HTTPS via Let's Encrypt (auto on Vercel/Netlify).
- Robots.txt should permit indexing — we WANT this in search results for "EU AI Act Article 50 compliance" and similar.
- Sitemap.xml: include each language version as a canonical alternate.

## What this scaffold does NOT do (yet)

- No deep analyst notes per company (placeholder URLs only; v1 work)
- No URL-based detection of AI usage on company sites (that's the self-assessment tool, T2.B in V's strategy doc)
- No back-end (everything is static JSON; sufficient for v0-v3)
- No CMS for analysts to edit data (analysts edit `data/companies.json` directly; v2 may add a Notion-backed pipeline)
- No internationalization of legal/sectoral terminology beyond UI strings (Industry name translation is in i18n.json; analyst notes would also need translation in v1)

## Defensibility / no-libel posture

- We score publicly-verifiable evidence of disclosure infrastructure. We do not allege regulatory non-compliance.
- Every score is reproducible from the cited public evidence URL.
- Companies can submit additional evidence at any time and we update the score in the next publication.
- Scoring is uniform across companies in the same sector.
- Methodology is published in full.

This is the same defensibility posture that enforcementtracker.com has used for GDPR for 8 years without successful legal challenge.
