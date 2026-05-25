# LedgerProof — Tech Build Manifest

**Companion to:** `FOOLPROOF-ARTICLE-50-GOLD-STANDARD-PLAN.md`
**Author:** Veronica S. Dawkins, LedgerProof Foundation
**Drafted:** 25 May 2026
**Scope:** Every piece of technology required to deliver the foolproof plan, with priority, ownership, effort estimate, sequencing, and foolproofing rationale.

---

## Reading guide

| Priority | Meaning |
|---|---|
| **🔴 P0** | Launch-blocking. Must ship by **6 July 2026** or the launch narrative fails. |
| **🟠 P1** | Enforcement-blocking. Must ship by **2 August 2026** or first compliance customers can't transact. |
| **🟡 P2** | Q3-Q4 2026. Required for the 12-month vision; not for launch. |
| **🟢 P3** | Year 2 (2027). Strategic, not urgent. |

| Status |
|---|
| ✅ Shipped (in production OR committed to repo and tested) |
| 🟦 In progress (work started, not done) |
| ⬜ Not started |
| 🟣 External (vendor, partner, or third-party effort) |

| Build mode |
|---|
| **F** Founder (Veronica) — architectural decisions, code review, key signing |
| **C** Contractor (senior, billable) — implementation work |
| **P** Partner (TVP portfolio, C2PA member, etc.) — external counterparty execution |
| **O** Open-source community — third-party contributors |

Effort is in **person-weeks** at one full-time engineer equivalent. Costs assume €4,000/week for senior contractor (Rust/Python/TypeScript), €3,000/week for plugin/frontend, €2,500/week for documentation/devops. These are EU rates; halve for self-built.

---

## A · Core protocol & backend

The protocol surface itself. Foolproofing dimension: **Technological**.

| # | Artifact | Status | Priority | Build | Effort | Cost (€) | Target |
|---|---|:---:|:---:|:---:|:---:|---:|:---:|
| A1 | LPR v1.0 base protocol | ✅ | — | F | 0 | — | Done |
| A2 | LPR v1.1 schema extensions (Rust) | ✅ | — | F | 0 | — | Done |
| A3 | `ai/human-review/v1` + `ai/chatbot-session/v1` content types | ✅ | — | F | 0 | — | Done |
| A4 | Public `GET /v1/verify/:seq` endpoint | ✅ | — | F | 0 | — | Done |
| A5 | Public `GET /v1/receipts/by-content-hash/:sha256` | ✅ | — | F | 0 | — | Done |
| A6 | Public `GET /v1/receipts/by-perceptual-hash/:algo/:hash` | ⬜ | 🔴 P0 | C | 1.5 | 6,000 | Week 2 |
| A7 | Perceptual-hash computation library (pHash, dHash, chromaprint) | ⬜ | 🔴 P0 | C | 1.0 | 4,000 | Week 2 |
| A8 | Rate limiting (`tower-governor`) | ⬜ | 🔴 P0 | C | 0.5 | 2,000 | Week 1 |
| A9 | v1.1 schema deployed to production (api-eu) | ⬜ | 🔴 P0 | F | 0.5 | — | Week 1 |
| A10 | EU anchor worker + hot wallet (Phase 2) | ⬜ | 🟠 P1 | C+F | 2.0 | 8,000 + wallet funding | Week 4 |
| A11 | LPR1 OP_RETURN verifier (web) | ⬜ | 🟠 P1 | C | 1.5 | 6,000 | Week 4 |
| A12 | Operator HSM integration (production-grade key custody) | ⬜ | 🟠 P1 | C+P (Unchained) | 2.0 | 8,000 + custody fees | Week 5 |
| A13 | Multi-substrate anchor profile (Ethereum fallback) | ⬜ | 🟡 P2 | C | 3.0 | 12,000 | Q3 |
| A14 | Federated CT log fallback profile | ⬜ | 🟡 P2 | C | 2.5 | 10,000 | Q3 |
| A15 | LongHorizon-v1 PQC profile (ML-DSA-65 composite) | ⬜ | 🟡 P2 | C | 4.0 | 16,000 | Q4 |
| A16 | Operator-to-operator sync protocol | ⬜ | 🟡 P2 | C+F | 3.0 | 12,000 | Q4 |
| A17 | Operator registry / public trust list | ⬜ | 🟡 P2 | C | 1.5 | 6,000 | Q4 |

**Section A subtotal:** 11.5 weeks of contractor work, **~€46,000** to launch.
**Through 12 months:** ~€106,000.

---

## B · SDK adapters — the Stripe play

The one-line install surface. Foolproofing dimension: **Implementation (the Stripe play)**.

| # | Artifact | Status | Priority | Build | Effort | Cost (€) | Target |
|---|---|:---:|:---:|:---:|:---:|---:|:---:|
| B1 | Core Python SDK `ledgerproof` (PyPI) + `attach()` pattern | ⬜ | 🔴 P0 | C | 1.5 | 6,000 | Week 1 |
| B2 | OpenAI SDK adapter | ⬜ | 🔴 P0 | C | 0.5 | 2,000 | Week 1 |
| B3 | Anthropic SDK adapter | ⬜ | 🔴 P0 | C | 0.3 | 1,200 | Week 2 |
| B4 | Google Gemini SDK adapter | ⬜ | 🔴 P0 | C | 0.3 | 1,200 | Week 2 |
| B5 | Mistral SDK adapter | ⬜ | 🟠 P1 | C | 0.3 | 1,200 | Week 2 |
| B6 | Hugging Face Inference sidecar (Docker container) | ⬜ | 🟠 P1 | C | 1.0 | 4,000 | Week 3 |
| B7 | Node.js / TypeScript SDK `@ledgerproof/sdk` (npm) | ⬜ | 🔴 P0 | C | 1.5 | 6,000 | Week 2 |
| B8 | OpenAI Node adapter | ⬜ | 🔴 P0 | C | 0.3 | 1,200 | Week 2 |
| B9 | Anthropic Node adapter | ⬜ | 🔴 P0 | C | 0.3 | 1,200 | Week 2 |
| B10 | Rust SDK (already in quantum-edge-2) — package + publish | ⬜ | 🟠 P1 | C | 0.5 | 2,000 | Week 3 |
| B11 | Go SDK | ⬜ | 🟡 P2 | C | 2.0 | 8,000 | Q3 |
| B12 | Browser-side JavaScript verifier library | ⬜ | 🔴 P0 | C | 1.0 | 4,000 | Week 3 |
| B13 | Replicate / Modal / RunPod adapters | ⬜ | 🟡 P2 | C | 1.5 | 6,000 | Q3 |

**Section B subtotal to launch:** 6.7 weeks, **~€26,800**.
**Through 12 months:** ~€44,200.

The launch-blocking subset (P0): B1, B2, B3, B4, B7, B8, B9, B12 = **5.7 weeks of contractor work, ~€22,800.**

This is the most leveraged spend in the entire plan. Every other artifact downstream of "one-line install" depends on this shipping clean.

---

## C · Framework integrations

Higher-level integrations that sit above SDK adapters. Foolproofing dimensions: **Implementation + Partnership**.

| # | Artifact | Status | Priority | Build | Effort | Cost (€) | Target |
|---|---|:---:|:---:|:---:|:---:|---:|:---:|
| C1 | LangChain callback `langchain-ledgerproof` (PyPI) | ⬜ | 🔴 P0 | C | 1.0 | 4,000 | Week 2 |
| C2 | LangGraph decorator | ⬜ | 🟠 P1 | C | 0.5 | 2,000 | Week 3 |
| C3 | Vercel AI SDK plug-in `@ledgerproof/vercel-ai` (npm) | ⬜ | 🔴 P0 | C | 1.0 | 4,000 | Week 3 |
| C4 | Cloudflare Workers AI binding | ⬜ | 🟠 P1 | C | 1.0 | 4,000 | Week 3 |
| C5 | FastAPI middleware | ⬜ | 🟠 P1 | C | 0.5 | 2,000 | Week 4 |
| C6 | Express / Next.js middleware | ⬜ | 🟠 P1 | C | 0.5 | 2,000 | Week 4 |
| C7 | Django middleware | ⬜ | 🟡 P2 | C | 0.5 | 2,000 | Q3 |
| C8 | Spring Boot interceptor (Java) | ⬜ | 🟡 P2 | C | 1.0 | 4,000 | Q3 |
| C9 | .NET / ASP.NET Core middleware | ⬜ | 🟡 P2 | C | 1.0 | 4,000 | Q3 |
| C10 | Ruby on Rails gem | ⬜ | 🟢 P3 | O | 0.5 | community | Year 2 |

**Section C subtotal to launch:** 3.5 weeks, **~€14,000**.
**Through 12 months:** ~€28,000.

---

## D · Content platform plug-ins

For deployers who don't write custom code. Foolproofing dimension: **Implementation + Public**.

| # | Artifact | Status | Priority | Build | Effort | Cost (€) | Target |
|---|---|:---:|:---:|:---:|:---:|---:|:---:|
| D1 | WordPress plug-in v0.1 (alpha) | ⬜ | 🔴 P0 | C | 1.5 | 4,500 | Week 3 |
| D2 | WordPress plug-in v1.0 (WordPress.org store) | ⬜ | 🟠 P1 | C | 1.0 | 3,000 | Week 6 |
| D3 | Notion integration (via Notion API) | ⬜ | 🟠 P1 | C | 1.5 | 4,500 | Week 5 |
| D4 | Sanity studio plug-in | ⬜ | 🟡 P2 | C | 1.0 | 3,000 | Q3 |
| D5 | Contentful extension | ⬜ | 🟡 P2 | C | 1.0 | 3,000 | Q3 |
| D6 | Strapi plug-in | ⬜ | 🟡 P2 | C | 1.0 | 3,000 | Q3 |
| D7 | Microsoft Word add-in (Office Store) | ⬜ | 🟠 P1 | C | 3.0 | 9,000 | Week 8 |
| D8 | Google Docs Workspace add-on (Workspace Marketplace) | ⬜ | 🟠 P1 | C | 3.0 | 9,000 | Week 9 |
| D9 | Figma plug-in (Community) | ⬜ | 🟡 P2 | C | 1.5 | 4,500 | Q3 |
| D10 | Canva app | ⬜ | 🟡 P2 | C | 2.0 | 6,000 | Q3 |
| D11 | Webflow extension (Webflow App Marketplace) | ⬜ | 🟡 P2 | C | 1.5 | 4,500 | Q3 |
| D12 | Squarespace integration | ⬜ | 🟡 P2 | C | 1.5 | 4,500 | Q3 |
| D13 | Shopify app (Shopify App Store) | ⬜ | 🟡 P2 | C | 2.0 | 6,000 | Q3 |
| D14 | Adobe Creative Cloud panel (Photoshop / Illustrator / Premiere) | ⬜ | 🟡 P2 | C | 4.0 | 12,000 | Q4 |

**Section D subtotal to launch:** 1.5 weeks (WordPress alpha only), **~€4,500**.
**Through 12 months:** ~€76,500.

WordPress alpha is the only launch-day deliverable here. Microsoft / Google / Adobe extensions are large-effort and not launch-blocking; they ship Q3.

---

## E · C2PA bridge

Cross-pollinates LPR with the existing Adobe/Microsoft/Google/BBC/Reuters ecosystem. Foolproofing dimensions: **Competitive + Partnership + Implementation**.

| # | Artifact | Status | Priority | Build | Effort | Cost (€) | Target |
|---|---|:---:|:---:|:---:|:---:|---:|:---:|
| E1 | C2PA assertion spec (`org.ledgerproof.receipt.v1`) | ✅ | — | F | 0 | — | Done (committed) |
| E2 | C2PA assertion library (compute the assertion CBOR) — Python | ⬜ | 🔴 P0 | C | 1.0 | 4,000 | Week 3 |
| E3 | C2PA assertion library — JavaScript/TypeScript | ⬜ | 🟠 P1 | C | 1.0 | 4,000 | Week 4 |
| E4 | LPR-to-C2PA verifier translator (read manifest → find LPR assertion → verify) | ⬜ | 🟠 P1 | C | 1.5 | 6,000 | Week 4 |
| E5 | C2PA + LPR end-to-end test harness (Adobe Firefly / Microsoft Bing) | ⬜ | 🟠 P1 | C | 1.0 | 4,000 | Week 5 |
| E6 | C2PA CAWG submission (governance, not code) | ⬜ | 🟠 P1 | F | 0.5 | — | Week 3 |
| E7 | LPR as a registered C2PA "Trust Service" (Q3 deliverable) | 🟣 | 🟡 P2 | F+P | 2.0 | governance | Q3 |

**Section E subtotal to launch:** 4.5 weeks, **~€18,000**.

---

## F · Verifier surface (consumer-facing)

The "everywhere you might see content" layer. Foolproofing dimension: **Public**.

| # | Artifact | Status | Priority | Build | Effort | Cost (€) | Target |
|---|---|:---:|:---:|:---:|:---:|---:|:---:|
| F1 | Chrome extension v0.1 (LPR badge on any web page) | ⬜ | 🔴 P0 | C | 2.0 | 6,000 | Week 3 |
| F2 | Firefox extension | ⬜ | 🟠 P1 | C | 0.5 | 1,500 | Week 4 |
| F3 | Safari extension (App Store) | ⬜ | 🟠 P1 | C | 1.5 | 4,500 | Week 5 |
| F4 | iOS share extension | ⬜ | 🟡 P2 | C | 2.5 | 10,000 | Q3 |
| F5 | Android share extension | ⬜ | 🟡 P2 | C | 2.5 | 8,000 | Q3 |
| F6 | Slack bot (lookup receipt by URL/hash) | ⬜ | 🟡 P2 | C | 1.0 | 3,000 | Q3 |
| F7 | Discord bot | ⬜ | 🟡 P2 | C | 1.0 | 3,000 | Q3 |
| F8 | Microsoft Teams bot | ⬜ | 🟡 P2 | C | 1.5 | 4,500 | Q3 |
| F9 | PDF reader integration: Acrobat plug-in | ⬜ | 🟡 P2 | C | 2.5 | 7,500 | Q4 |
| F10 | PDF reader integration: Nutrient SDK extension | ⬜ | 🟡 P2 | C | 1.5 | 4,500 | Q4 |
| F11 | PDF reader integration: macOS Preview QuickLook | ⬜ | 🟡 P2 | C | 1.5 | 4,500 | Q4 |
| F12 | Outlook add-in (verify inbound attachments) | ⬜ | 🟡 P2 | C | 2.0 | 6,000 | Q4 |
| F13 | Gmail browser extension (verify inbound attachments) | ⬜ | 🟡 P2 | C | 1.5 | 4,500 | Q4 |
| F14 | Provenance Search public web tool | ⬜ | 🟠 P1 | C | 3.0 | 9,000 | Week 5 |
| F15 | Mastodon / Bluesky verifier bot | ⬜ | 🟡 P2 | C | 0.5 | 1,500 | Q3 |

**Section F subtotal to launch:** 5 weeks, **~€15,000** (Chrome + Firefox + Safari + Provenance Search).
**Through 12 months:** ~€78,000.

---

## G · Regulator & enterprise dashboards

What national authorities and enterprise legal teams see. Foolproofing dimensions: **Public + Partnership + Implementation**.

| # | Artifact | Status | Priority | Build | Effort | Cost (€) | Target |
|---|---|:---:|:---:|:---:|:---:|---:|:---:|
| G1 | Market Surveillance Authority dashboard v0.1 (read-only) | ⬜ | 🟠 P1 | C | 3.0 | 9,000 | Week 5 |
| G2 | MSA dashboard v1.0 (with bulk query + alerts) | ⬜ | 🟡 P2 | C | 4.0 | 12,000 | Q3 |
| G3 | Enterprise admin console v0.1 (deployer-side audit log) | ⬜ | 🔴 P0 | C | 3.0 | 9,000 | Week 4 |
| G4 | Enterprise admin console v1.0 (SSO, role-based access, exports) | ⬜ | 🟠 P1 | C | 3.0 | 9,000 | Week 8 |
| G5 | Bulk verification API (media monitoring services, civil society) | ⬜ | 🟠 P1 | C | 1.5 | 6,000 | Week 6 |
| G6 | Receipt-density public stats dashboard | ⬜ | 🟡 P2 | C | 2.0 | 6,000 | Q3 |
| G7 | Evidence bundle export (court-ready PDF generation) | ⬜ | 🟠 P1 | C | 2.0 | 6,000 | Week 7 |
| G8 | Board-ready compliance reports (PDF + dashboard) | ⬜ | 🟡 P2 | C | 2.0 | 6,000 | Q3 |
| G9 | AI Act Service Desk API integration (if exposed by EC) | 🟣 | 🟡 P2 | F+P | 1.0 | partner | Q3 |

**Section G subtotal to launch:** 4.5 weeks, **~€18,000** (G1 + G3 + G5 partial).
**Through 12 months:** ~€63,000.

---

## H · Federated operator infrastructure

The redundancy that makes LedgerProof outlive any single entity. Foolproofing dimension: **Technological + Public**.

| # | Artifact | Status | Priority | Build | Effort | Cost (€) | Target |
|---|---|:---:|:---:|:---:|:---:|---:|:---:|
| H1 | Second independent calendar operator stood up | ⬜ | 🟠 P1 | C+P | 2.0 | 6,000 + ops fees | Week 5 |
| H2 | Operator deployment runbook (open source) | ⬜ | 🟠 P1 | F | 1.0 | — | Week 4 |
| H3 | Cross-operator verification protocol | ⬜ | 🟡 P2 | C | 3.0 | 12,000 | Q3 |
| H4 | Operator trust list registry (federation governance) | ⬜ | 🟡 P2 | C | 2.0 | 6,000 | Q3 |
| H5 | Third operator (community-run or partner-run) | ⬜ | 🟡 P2 | P | partner | partner | Q4 |
| H6 | Cross-operator anchor batching (cost optimization) | ⬜ | 🟢 P3 | C | 4.0 | 16,000 | Year 2 |

**Section H subtotal to launch:** 3 weeks, **~€6,000**.
**Through 12 months:** ~€40,000.

---

## I · Documentation, marketing, and trust infrastructure

The public-facing layer. Foolproofing dimensions: **Public + Implementation**.

| # | Artifact | Status | Priority | Build | Effort | Cost (€) | Target |
|---|---|:---:|:---:|:---:|:---:|---:|:---:|
| I1 | docs.ledgerproofhq.io (Docusaurus or similar) | ⬜ | 🔴 P0 | C | 2.0 | 5,000 | Week 4 |
| I2 | Interactive API explorer (Swagger / Redocly) | ⬜ | 🔴 P0 | C | 0.5 | 1,250 | Week 5 |
| I3 | SDK quickstart guides (per language) | ⬜ | 🔴 P0 | F+C | 1.0 | 2,500 | Week 5 |
| I4 | Integration tutorials (per framework / platform) | ⬜ | 🟠 P1 | F+C | 2.0 | 5,000 | Week 6 |
| I5 | Receipt anatomy explainer (visual / interactive) | ⬜ | 🟠 P1 | C | 1.5 | 3,750 | Week 6 |
| I6 | Marketing site v2 (ledgerproofhq.io) | ⬜ | 🔴 P0 | C | 2.0 | 5,000 | Week 6 |
| I7 | Status page (status.ledgerproofhq.io) | ⬜ | 🟠 P1 | C | 0.5 | 1,250 | Week 5 |
| I8 | Bug bounty platform setup (HackerOne or Immunefi) | ⬜ | 🟠 P1 | F | 0.5 | platform fees | Week 6 |
| I9 | Public transparency dashboard (receipt counts, uptime, erasure requests) | ⬜ | 🟡 P2 | C | 1.5 | 3,750 | Q3 |

**Section I subtotal to launch:** 9.5 weeks of mixed contractor work, **~€23,750**.
**Through 12 months:** ~€27,500.

---

## J · Multi-jurisdiction profiles (Year 2)

The expansion surface. Foolproofing dimension: **Competitive (long-term moat)**.

| # | Artifact | Status | Priority | Build | Effort | Cost (€) | Target |
|---|---|:---:|:---:|:---:|:---:|---:|:---:|
| J1 | UK AI Bill profile (`ai/uk-ai-bill/v1`) | ⬜ | 🟡 P2 | F+C | 2.0 | 8,000 | Q3 |
| J2 | US Executive Order 14110 profile (`ai/us-eo-14110/v1`) | ⬜ | 🟡 P2 | F+C | 2.0 | 8,000 | Q3 |
| J3 | China provisional measures profile (`ai/china-genai/v1`) | ⬜ | 🟢 P3 | F+C | 3.0 | 12,000 | Year 2 |
| J4 | Japan AI Strategy profile (`ai/japan-ai/v1`) | ⬜ | 🟢 P3 | F+C | 2.0 | 8,000 | Year 2 |
| J5 | Canada AIDA profile (`ai/canada-aida/v1`) | ⬜ | 🟢 P3 | F+C | 2.0 | 8,000 | Year 2 |

**Section J:** ~**€44,000** through Year 2.

---

## Cost totals

| Window | Engineering cost | Foundation cost | Total |
|---|---:|---:|---:|
| **Launch (now → 6 July)** | ~€155,000 | — | ~€155,000 |
| **Launch → enforcement (6 July → 2 Aug)** | ~€60,000 | — | ~€60,000 |
| **Enforcement → end of 2026** | ~€155,000 | ops/hosting €30K | ~€185,000 |
| **2027 (Year 2)** | ~€100,000 | ops/hosting €100K | ~€200,000 |
| **Total 12-month forecast** | **~€370,000** | **~€30,000** | **~€400,000** |
| **18-month forecast (through Aug 2027)** | **~€470,000** | **~€130,000** | **~€600,000** |

This is well inside the **€5M seed round** target. At a typical seed-stage burn rate, you have **2.5–3 years of runway** at this build pace.

---

## What MUST exist by July 6 (the launch-day technical narrative)

The 🔴 P0 set, ranked by criticality:

| Rank | Artifact | If not shipped, what breaks |
|---:|---|---|
| 1 | **B1** Python SDK + `attach()` pattern | The entire Stripe play. Without this there is no demo. |
| 2 | **B2** OpenAI adapter | The demo. The press release. The Anthropic / Google ones follow from this. |
| 3 | **A9** v1.1 schema deployed to prod | All v1.1-using SDK adapters fail in production. |
| 4 | **A8** Rate limiting | First DDoS or accidental high-volume customer takes us down. |
| 5 | **A6+A7** Perceptual hash endpoint + library | The "Article 50(2) robustness" claim cannot be defended. |
| 6 | **B7+B8+B9** Node SDK + adapters | Half the AI developer ecosystem lives in TypeScript. |
| 7 | **B12** Browser-side verifier library | Required by F1 (Chrome extension) and the launch demo |
| 8 | **C1** LangChain callback | Required for the LangChain partnership story |
| 9 | **C3** Vercel AI SDK plug-in | Required for the modern Next.js developer story |
| 10 | **D1** WordPress plug-in alpha | Required for the "43% of the web" press angle |
| 11 | **E2** C2PA assertion library (Python) | Required for the C2PA bridge story |
| 12 | **F1** Chrome extension v0.1 | The single most visible public-facing verifier |
| 13 | **F14** Provenance Search public web tool | Required for journalist / regulator outreach |
| 14 | **G3** Enterprise admin console v0.1 | Required for pilot customer onboarding |
| 15 | **I1+I3+I6** Docs site + SDK quickstarts + marketing site | Required for any developer to actually use any of the above |

**That's 15 artifacts at ~€72,000 of engineering across 18 contractor-weeks.**

If you have **one full-time senior Python/TypeScript contractor + one part-time frontend/extensions contractor**, that's exactly the right team to ship the July 6 launch.

---

## What MUST exist by August 2 (the enforcement-day customer narrative)

Adds the following 🟠 P1 artifacts on top of the launch-day set:

| Artifact | Why |
|---|---|
| **A10** EU anchor worker + hot wallet | First customer anchor on Bitcoin mainnet under enforcement |
| **A11** LPR1 verifier web | Customers verifying their own anchors |
| **A12** Operator HSM + multisig | Key custody story for enterprise sales |
| **B5+B6** Mistral + Hugging Face adapters | Cover the non-frontier AI ecosystem |
| **B10** Rust SDK packaged | Cover the systems-programming customer segment |
| **C2** LangGraph decorator | Cover agentic AI workflows |
| **C4** Cloudflare Workers AI binding | Cover the edge inference segment |
| **C5+C6** FastAPI + Express/Next.js middleware | Cover the backend deployer segment |
| **D2** WordPress plugin v1.0 (store-published) | Distribution at scale |
| **D3** Notion integration | Cover the modern knowledge-work segment |
| **D7+D8** Microsoft Word + Google Docs add-ins | Cover the enterprise document segment |
| **E3+E4+E5** C2PA bridge JS + verifier translator + E2E test | Adobe/Microsoft/Google partnership story |
| **F2+F3** Firefox + Safari extensions | Cross-browser parity |
| **G1** MSA dashboard v0.1 | At least one Member State authority engaged |
| **G4** Enterprise admin console v1.0 | Production-grade customer onboarding |
| **G5** Bulk verification API | Media monitoring + civil society |
| **G7** Evidence bundle export | First enforcement-readiness deliverable |
| **H1+H2** Second operator + deployment runbook | Federated narrative |
| **I4+I5+I7+I8** Tutorials + status page + bug bounty live | Trust narrative |

**That's an additional ~17 weeks at ~€60,000** between July 6 and August 2.

---

## What gets built in 2026 Q3-Q4

Everything in 🟡 P2: rounded out content platforms (D4-D14), iOS/Android share extensions (F4-F5), regulator dashboard v1.0 (G2), federated operator network (H3-H5), multi-substrate (A13-A14), PQC (A15), multi-jurisdiction (J1-J2).

Roughly **~€155,000** of engineering over those two quarters.

---

## What gets built in 2027 (Year 2)

🟢 P3: China/Japan/Canada profiles, Ruby/Go SDKs, cross-operator anchor batching, advanced enterprise features.

Roughly **~€100,000** of engineering through Year 2.

---

## Who builds what — recommended team composition

To ship the launch-day P0 set in 6 weeks, the right team is:

| Role | Person | Hours/week | Cost (€/week) |
|---|---|---:|---:|
| **Founder / architect** | Veronica | 60+ | (founder time) |
| **Senior Rust / cryptography contractor** (the one who did the audit) | Already known | 40 | 4,000 |
| **Senior Python contractor** (SDKs + adapters) | New hire / contractor | 40 | 4,000 |
| **Senior TypeScript contractor** (Node SDK + Vercel + Cloudflare + browser extension) | New hire / contractor | 40 | 4,000 |
| **Frontend / extensions contractor** (Chrome / Firefox / Safari + dashboard) | New hire / contractor | 30 | 3,000 |
| **DevOps / infra contractor** (Fly deploys, operator infra, status page) | New hire / contractor | 20 | 2,000 |
| **Technical writer** (docs.ledgerproofhq.io) | New hire / contractor | 20 | 2,500 |

**Total burn during launch sprint:** **~€19,500/week** for 6 weeks = **~€117,000** plus a buffer brings it to the ~€155,000 estimated.

This is the team size that makes the foolproof plan execute. **Smaller and you slip; larger is unnecessary.**

---

## What you (Veronica) personally need to do vs. delegate

| Founder-only | Must-do | Can delegate (with sign-off) |
|---|---|---|
| All specification work (architectural decisions) | EU AI Office submission | SDK adapter implementation |
| Patent inventor's notebook | TVP follow-up + close | Browser extension code |
| Foundation governance | Coalition signatory recruiting | WordPress / Notion plug-ins |
| Investor relations | Press / launch comms | Documentation site (with your review) |
| Key holder for operator | Pilot customer relationships | C2PA bridge implementation |
| IP / legal counsel relationships | Member State authority outreach | All testing / QA |

**Veronica's time is the bottleneck on the founder-only column. Everything in the right-hand column must be off your plate.** That's what the team above is for.

---

## How this maps back to the master plan

| Master plan dimension | Tech sections that serve it |
|---|---|
| Technological foolproof | A (core), H (federation), E (C2PA bridge), partly F (verifier) |
| Publicly foolproof | F (verifier), G (dashboards), I (docs/trust), partly H |
| Competitively foolproof | E (C2PA), J (multi-jurisdiction), A13-A14 (multi-substrate) |
| Partnership foolproof | C (frameworks), G (regulator), E (C2PA), partly D |
| Implementation foolproof (Stripe play) | B (SDKs), C (frameworks), D (platforms) |

Every section is load-bearing for at least one dimension. Nothing in this manifest is decorative.

---

## Decision points

You need to decide three things this week to make the launch achievable:

1. **Hiring authorization.** Will you authorize bringing on the 4 senior contractors above for a 6-week launch sprint at ~€60K of pre-TVP-close cash? (If no: extend the launch timeline by 4–6 weeks; ship a smaller P0 set.)
2. **Build vs. buy on browser extensions.** Will you build the Chrome/Firefox/Safari extensions in-house, or contract to an extension shop like SmilePack / Browser.do? (Cost similar; speed favors contracting.)
3. **WordPress as a launch-day artifact.** Is the 43%-of-the-web argument strategically worth the €4,500 + 1.5 weeks for an alpha plug-in, or do you push WordPress to August?

Answer those three and the engineering plan locks down.

---

*LedgerProof Foundation · Tech build manifest v1.0 · 25 May 2026*
*This document is the canonical engineering scope for the FOOLPROOF-ARTICLE-50-GOLD-STANDARD-PLAN.md master plan. Every artifact has a priority, owner type, effort estimate, and target ship week. Reconcile any engineering work back to this manifest.*
