# LedgerProof — The Full Stack Revamp Plan v1.0

**Drafted**: Tuesday June 2, 2026 — 13:20 PDT
**Author**: Veronica S. Dawkins, drafted during the Tuesday adapter sprint
**Status**: Strategic planning document — for V's review and revision BEFORE any further execution
**Operating reference**: `14-seed-close-pack/04-atomic-explosion-master-plan.md`
**Trigger**: Futurium post 01 went live this morning. Adapter sprint shipped 4 packages. The institutional surface and the developer surface are now both real. Time to plan the full stack — site, business model, backend, adapter expansion, three-audience strategy, brand evolution.

---

## 0. Executive read — 90 seconds

The Futurium post going live this morning is a real inflection point. The Foundation now has institutional EU presence on the European Commission's stakeholder platform. The four Python adapters shipping today gives the protocol a credible developer-distribution surface. The Foundation and Founding Members pages give the site institutional spine.

What we have now: a credible Article 50 evidence layer with open protocol + Foundation governance + four adapter packages + institutional EU positioning + early Founding Member commercial structure.

What we don't have: a coherent business model that says how this becomes a profitable company without compromising the open protocol. A site that routes three distinct audiences (vendors / developers / customers) to the right conversion path. A backend beyond static pages. A full European adapter coverage. A consistent visual language across the developer + customer + governance surfaces.

This document plans all of that, with one explicit constraint that holds throughout: **the protocol stays open forever. Revenue comes from operational complexity, regulatory credibility, and institutional services on top of the open protocol — not from gating the protocol.** That's the load-bearing decision. Everything else follows.

---

## Part 1: The Anthropic-Pattern Strategic Frame

V's instruction was "use models that have really made waves as an open source like Anthropic." This deserves a precise reading because Anthropic is NOT a pure open-source company, and the parts that look open-source are not where Anthropic makes money.

### What Anthropic actually does

| What Anthropic open-sources | What stays closed | Revenue |
|----------------------------|-------------------|---------|
| Research papers (Constitutional AI, RLHF, interpretability, mechanistic) | Claude model weights and architecture | API usage |
| Claude Agent SDK | Claude.ai platform and product | claude.ai subscriptions |
| Claude Code | Trust & safety infrastructure | Enterprise contracts |
| Model Context Protocol (MCP) | Model training pipelines and data | AWS / GCP / Azure marketplace revenue |
| SDK (Python, TypeScript, etc.) | Internal alignment research methods | API quota tier upgrades |

**The pattern is: open the research and the SDKs and the tooling that builds credibility and developer mindshare. Keep closed the model, the platform, and the business logic that makes money.**

The moat is not the openness. The moat is the model + the safety reputation + the platform + the institutional credibility built by the openness.

### The LedgerProof analog

| What LedgerProof open-sources | What is paid | Revenue |
|------------------------------|--------------|---------|
| Protocol specification (LPR v1.1+) | Hosted operator service (anchoring + HSM + SLA) | Operator subscription |
| Reference SDKs (Python, TypeScript, Rust) | Foundation Membership tiers (Standard, Anchor, Strategic Beta) | Foundation Member dues |
| Reference verifier (single-file static HTML, browser SPA) | Enterprise dedicated infrastructure | Enterprise contracts |
| Adapters (LangChain, LlamaIndex, OpenAI, Anthropic, ...) | Professional services (implementation, audit prep) | Hourly engagements |
| Foundation governance documents | Certification program (LP-Conformant auditor accreditation) | Audit firm certification fees |
| Audit memos | Training & certification for compliance officers | Course fees |
| Conformance test vectors | Compliance dashboard (SaaS) | SaaS subscription |
| Public consultation submissions | Cross-jurisdictional regulator liaison service | Bespoke retainer |

**The moat is not the openness. The moat is the Foundation governance + IETF SCITT-track standing + CEN-CENELEC JTC 21 participation + audit memo credibility + production deployer network + cross-jurisdictional institutional structure.**

The protocol being open is what makes regulators and standards bodies take the Foundation seriously. The Foundation being taken seriously is what makes the paid services valuable to enterprises.

### Three things this is NOT

- **Not pure open-source non-profit** — LedgerProof Inc. is a Delaware C-corporation that generates revenue. The Foundation is a separate US 501(c)(3) public charity. They have distinct governance.
- **Not open-core** — we are NOT going to have an "open Apache 2.0 community edition" vs "paid enterprise edition" of the protocol. The protocol is open. Always. Open-core models invite vendor capture (see MongoDB → SSPL, ElasticSearch → SSPL).
- **Not vendor-locked managed service** — anyone can self-host the entire stack on their own infrastructure. Our paid managed service competes on operational quality, SLA, and integration depth, NOT on protocol exclusivity.

### Reference companies — what we look like

| Company | Open model | Paid model | What we learn |
|---------|-----------|------------|---------------|
| **Confluent** (Apache Kafka) | Kafka core | Confluent Cloud + Enterprise | Most enterprises pay for managed even though Kafka is free. Reliability + ops > free + DIY. |
| **HashiCorp** (Terraform, Vault, etc.) | OSS core | Terraform Cloud + Vault Enterprise | Open-core temporarily; eventually moved Terraform to BSL (controversial). We learn: don't follow this path, stay pure open. |
| **Vercel** (Next.js) | Next.js framework | Vercel hosting | Open framework drives developer mindshare; hosting captures value. Direct analog to our open SDK + paid operator. |
| **MongoDB** | MongoDB Community | MongoDB Atlas + Enterprise + SSPL | Moved to SSPL (custom license) to prevent cloud-provider capture. Controversial. We learn: avoid the cloud-provider capture problem by having operational + governance moat, not licensing moat. |
| **Sigstore** | Pure open, Linux Foundation | None — pure non-profit | Same governance model as our Foundation. Sigstore proves the institutional credibility wedge. But Sigstore has zero revenue mechanism. We add the LedgerProof Inc. layer for that. |
| **Datadog** (uses OpenTelemetry) | OpenTelemetry is open | Datadog SaaS is paid | Open instrumentation standard + paid platform. Direct analog to open protocol + paid hosted operator. |

The closest analog is **Datadog + OpenTelemetry**: open standard creates ecosystem; paid platform captures value through operational quality. Datadog's market cap is ~$45B. The open standard is what made the market; Datadog built the dominant paid platform on top.

LedgerProof Foundation = OpenTelemetry equivalent (open standard, non-profit governance).
LedgerProof Inc. = Datadog equivalent (paid operator platform on top of the open standard).

---

## Part 2: The Revenue Model — Where Profit Comes From

Six concrete revenue surfaces. Each is real, each is defensible, each does NOT compromise the open protocol.

### Revenue surface 1 — Founding Member tiers (already designed)

Three tiers per existing `commercial/founding-members/` page:

- **Standard**: $50-150K commitment + 0.10% warrant + Foundation Advisory Council seat
- **Anchor**: $250-500K commitment + 0.25% warrant + headline press attribution
- **Strategic Beta**: $1M commitment + 0.50% warrant + protocol roadmap input + TSC nomination

Y1 booked ARR target (per CFO model BASE): $9.4M. Founding Member tier is the primary commercial structure for the first 12-18 months.

### Revenue surface 2 — Hosted Operator Service (NEW, build Q3)

Most enterprises will not self-host the full LedgerProof stack — anchoring infrastructure, HSM management, Bitcoin chain operations, SIEM connector maintenance, audit log retention. Operational complexity is too high for the median enterprise IT team.

**The hosted operator service offers:**
- Managed anchoring pipeline (Bitcoin OP_RETURN with RBF + OpenTimestamps fallback)
- HSM-as-a-Service (we operate enterprise-grade HSMs; customer uses our signing endpoints)
- Merkle batch processing at production scale (1K-100K req/s)
- SIEM connector hosting (Splunk, Datadog, ServiceNow, Vanta, Drata adapters maintained by us)
- 99.9% SLA with operational monitoring
- Audit log retention (10-year EU AI Act compliance)

**Pricing structure (proposed)**:
- **Starter**: $2,500/month — up to 10M receipts/month, shared infrastructure, business-hours support
- **Professional**: $10,000/month — up to 100M receipts/month, dedicated tenant, 24x7 support, SOC 2 audit access
- **Enterprise**: Custom — unlimited receipts, dedicated infrastructure, regulator-liaison service, custom SLA

**Free path remains**: self-host the entire stack on your own infrastructure. Our reference batcher service runs as a single binary. Anyone can deploy it on their own Kubernetes cluster.

Y2-Y3 expected revenue contribution: $5-25M ARR.

### Revenue surface 3 — Enterprise Tier (NEW, Q1 2027)

For the largest enterprises (G-SIBs, top-3 EU insurers, big-4 audit firms themselves, EU Commission internal use):
- Dedicated dual-region infrastructure with EU data residency guarantees
- Custom SLA (99.99% available)
- Dedicated technical account manager + dedicated counsel
- Regulator-liaison service (Foundation Executive Director attends supervisory authority briefings on your behalf)
- Custom protocol roadmap input (similar to Strategic Beta Partner but ongoing)
- Audit memo subscription (early access to NCC/ToB/Cure53 reports)
- Cross-jurisdictional compliance support (US, EU, UK, Singapore, Switzerland)

**Pricing**: $500K-$2M per year per enterprise.

Y3 expected contribution: $5-15M ARR from 5-15 enterprise contracts.

### Revenue surface 4 — Professional Services (NEW, ongoing)

For enterprises that want help implementing:
- Integration engineering (4-12 week engagements)
- Audit preparation services (preparing customer for their own external Article 50 audit)
- Regulatory submission ghost-writing (Foundation prepares the customer's CoC submission)
- Compliance program design (working with customer's CCO/DPO on Article 50 program)

**Pricing**: $250-500/hour or fixed-fee engagements ($25K-$250K per engagement).

Y1-Y3 expected: $1-5M annual contribution; not a primary revenue driver but valuable for customer success.

### Revenue surface 5 — Certification Program (NEW, Q2 2027)

Big-4 audit firms (KPMG, PwC, EY, Deloitte) and Tier-1 specialty firms (NCC Group, Trail of Bits, Cure53, Bishop Fox, Latacora) pay to be certified as LP-Conformant auditors. The certification process includes:
- Training on the LPR protocol and verifier
- Conformance test passing
- Foundation approval of audit methodology
- Annual recertification

**Pricing**:
- Tier-1 audit firms: $250K initial certification + $100K annual recertification
- Mid-market firms: $50K initial + $25K annual
- Independent auditors: $5K initial + $2.5K annual (Foundation-subsidized)

Y2-Y3 expected: $1-3M annual contribution from 10-25 certified firms.

The strategic value of this revenue is NOT the revenue itself — it's that LP-Conformant audit firms become a distribution channel that recommends LedgerProof to their clients. The certification is an alignment mechanism.

### Revenue surface 6 — Training & Certification (NEW, Q3 2027)

Paid courses for the practitioner ecosystem:
- **LP for Compliance Officers** — 2-day course, $2,500/seat, focused on Article 50 evidentiary obligations and how to use LedgerProof receipts in supervisory dialogue
- **LP for Engineers** — 3-day course, $3,500/seat, focused on integrating LedgerProof in production
- **LP for Auditors** — 2-day course, $4,000/seat, focused on verifying receipts and evaluating LP-Conformant implementations
- **LP for Lawyers** — 1-day workshop, $1,500/seat, focused on Foundation Member agreement structure and the regulatory framing

Plus an individual certification program: $500 exam fee for "Certified LedgerProof Practitioner."

Y3 expected: $500K-2M annual contribution.

### What stays FREE FOREVER

- **The protocol specification** — LPR v1.1, v1.2, v2.0+. All published openly. Apache 2.0 license on the spec text.
- **The reference SDK** — Python, TypeScript, Rust. Apache 2.0.
- **The reference verifier** — single-file HTML + Vite/TypeScript SPA. Apache 2.0.
- **The adapters** — all framework and SDK adapters. Apache 2.0.
- **Self-hosting capability** — full reference batcher binary, runnable on customer infrastructure.
- **Foundation governance documents** — IP license, board bylaws, transparency reports.
- **Audit memos** — published openly on `security.ledgerproofhq.io`.
- **Test vectors and conformance suite** — open for anyone implementing or verifying.

The free path is real and complete. A determined enterprise with their own SREs can run the entire stack and verify all receipts without paying us a cent. We win by being demonstrably the best operator, not by being the only operator.

### Revenue mix at maturity (Y4-Y5 projection)

| Surface | Estimated % of revenue |
|---------|----------------------|
| Hosted Operator Service | 45% |
| Enterprise Tier | 30% |
| Certification Program | 8% |
| Professional Services | 7% |
| Founding Member dues (recurring) | 5% |
| Training | 5% |

Total addressable revenue at maturity: $200-500M ARR if we capture 5-15% of the EU Article 50 evidence market plus material US/UK/APAC expansion.

---

## Part 3: The Three Audiences — Routing Strategy

Each audience needs a different entry path, different content, different conversion mechanics. The site today routes them all through the homepage. That's wrong.

### Audience A — VENDORS

**Who**: LLM providers (OpenAI, Anthropic, Mistral, Aleph Alpha, Cohere), AI orchestration frameworks (LangChain, LlamaIndex, Semantic Kernel, CrewAI), ML platforms (Databricks, Snowflake, Vertex AI, Bedrock, Azure OpenAI), specialized AI vendors (Synthesia, ElevenLabs, Runway).

**Their pain**: Article 50 affects their customers. Customers ask "are you Article 50 compliant?" and vendors don't have a good answer because compliance is a deployer obligation, not a vendor obligation. Vendors also face their own Article 50(2) obligations if they generate synthetic content.

**What they want**: 
- A credible certification/integration program their sales teams can reference
- Native integration with their product (their customers shouldn't have to write code)
- Co-marketing materials they can use
- A neutral Foundation that doesn't compete with them

**Conversion path**:
1. Vendor lands on `/vendors/` (NEW)
2. Sees the "LP-Conformant Vendor" program
3. Learns about native integration (their SDK calls our adapter or emits receipts directly)
4. Signs up for vendor partnership conversation
5. Outcome: paid certification + co-marketing + reference customer pipeline

**Y1 target**: 5-10 vendor partnerships (Mistral, Aleph Alpha, Cohere, LangChain, LlamaIndex, Semantic Kernel as priority).

### Audience B — DEVELOPERS

**Who**: Application engineers building AI products on top of frameworks or SDKs. Backend engineers integrating compliance into existing systems. ML engineers shipping models to production. Solutions architects at SI/consulting firms.

**Their pain**: Compliance is the legal team's problem until it isn't. When the CRO comes asking for Article 50 evidence in production, they need to ship something fast that doesn't require rewriting the application.

**What they want**:
- Drop-in SDK that integrates in 30 minutes
- Clear documentation with copy-pastable examples
- Working code samples for their specific framework
- A demo they can show their boss
- Access to a developer community that has solved the same problem

**Conversion path**:
1. Developer lands on `/developers/` (NEW landing) OR `/developers/adapters/` (exists)
2. Picks their framework (LangChain, LlamaIndex, OpenAI, Anthropic, etc.)
3. Installs the adapter (`pip install ledgerproof-langchain`)
4. Runs the quickstart in 10 minutes
5. Goes to production with either self-hosted OR paid hosted operator
6. Outcome: free path for self-hosted, paid hosted operator if production-grade ops matter

**Y1 target**: 2,500+ Python SDK downloads, 1,500+ npm downloads, 8+ production deployments.

### Audience C — CUSTOMERS (enterprises)

**Who**: Chief Risk Officers, Chief Compliance Officers, Data Protection Officers, General Counsel, AI Ethics Officers. Procurement teams evaluating AI vendors. Boards of directors who've been told they need an Article 50 plan.

**Their pain**: Aug 2 enforcement is real. Uncertainty about what evidence form satisfies a supervisory authority. Vendor compliance PDFs aren't enough. Internal logs aren't externally verifiable. The CCO doesn't want their first conversation with CNIL to be in an enforcement action.

**What they want**:
- Regulatory defensibility — something a CNIL or BaFin examiner can verify
- Clear pricing and procurement path
- Vendor independence — no SaaS lock-in, no foreign-jurisdiction risk
- Audit trail that survives any single vendor's continued operation
- Foundation backing that makes the protocol survive their own organizational changes

**Conversion path**:
1. Customer lands on `/` (homepage Article 50 positioning — exists)
2. Drills into `/article-50` for deployer brief (exists)
3. Reviews `/foundation` for governance credibility (exists)
4. Goes to `/commercial/founding-members` to evaluate tier (exists) OR `/commercial/enterprise` for dedicated tier (NEW)
5. Reserves tier OR contacts sales for enterprise
6. Outcome: Founding Member commitment OR enterprise contract

**Y1 target**: 15-25 signed Founding Members + 2-5 enterprise contracts.

### Site IA implication

The current site routes all three audiences through the homepage. That's structurally wrong. The homepage should have **three clear audience entry doors** in the hero CTA section:

- **For your engineering team** → `/developers/`
- **For your compliance team** → `/article-50/`
- **For your vendor partnership team** → `/vendors/`

Each audience door routes to a dedicated subsection with content calibrated to their concerns, language, and conversion mechanic.

---

## Part 4: Full Site Information Architecture

Page-by-page inventory. ~45 pages mapped across Tier 1 (must-have), Tier 2 (post-launch), Tier 3 (Q4-Q1 2027).

### Tier 1 — Must-have for July 6 launch (20 pages)

| # | Route | Audience | Purpose | Status |
|---|-------|----------|---------|--------|
| 1 | `/` | All | Article 50 protocol positioning + 3-audience routing | LIVE — needs hero CTA rework |
| 2 | `/article-50` | Customers | Deployer brief on Article 50 obligations + LedgerProof's evidence layer | LIVE — needs minor refresh |
| 3 | `/letter` | All | Founder open letter | LIVE |
| 4 | `/foundation` | Regulators + Customers | Governance + 13 FAQ | LIVE — full |
| 5 | `/foundation/board` | Regulators + Customers | Board composition (post Aug 30) | NEW Tier 1 stub |
| 6 | `/foundation/transparency` | All | Published Foundation receipts | NEW Tier 1 stub |
| 7 | `/commercial/founding-members` | Customers | 3-tier program + reservation form | LIVE — full |
| 8 | `/commercial/enterprise` | Customers | Enterprise dedicated tier | NEW |
| 9 | `/commercial/operator-service` | Customers + Developers | Hosted operator paid service (Starter/Pro/Enterprise) | NEW |
| 10 | `/pricing` | Customers | Clean pricing comparison page | NEW |
| 11 | `/developers/` | Developers | Developer landing hub | NEW |
| 12 | `/developers/quickstart` | Developers | 10-min walkthrough | STUB — full Phase 1 |
| 13 | `/developers/adapters` | Developers | Adapter directory | LIVE |
| 14 | `/developers/langchain-only` | Developers | LangChain-user lock + offer | LIVE |
| 15 | `/developers/sdks` | Developers | SDK landing (Python/TS/Rust) | NEW |
| 16 | `/developers/spec` | Developers | Protocol specification landing | NEW |
| 17 | `/spec/errata/001` | Developers + Regulators | First erratum | LIVE |
| 18 | `/security` | All | Security landing + audit memos | NEW stub |
| 19 | `/security/responsible-disclosure` | Security researchers | Disclosure protocol | NEW stub |
| 20 | `/vendors/` | Vendors | Vendor landing hub | NEW |

### Tier 2 — Post-launch (Aug-Oct, 15 pages)

| # | Route | Purpose |
|---|-------|---------|
| 21 | `/vendors/conformant-program` | LP-Conformant Vendor certification program |
| 22 | `/vendors/integrations` | Native integrations with vendor products |
| 23 | `/vendors/case-studies` | How vendors use LedgerProof |
| 24 | `/developers/community` | Discord, GitHub, contributor program |
| 25 | `/developers/api-reference` | Public API documentation |
| 26 | `/developers/guides` | Production deployment guides |
| 27 | `/developers/examples` | Example applications |
| 28 | `/developers/llamaindex-only` | LlamaIndex-user lock (mirror of langchain-only) |
| 29 | `/developers/openai-only` | OpenAI-user lock (mirror) |
| 30 | `/developers/anthropic-only` | Anthropic-user lock (mirror) |
| 31 | `/regulators/` | Regulator landing |
| 32 | `/regulators/verification-guide` | How to verify an LPR receipt as a supervisory authority |
| 33 | `/regulators/audit-tools` | Open tools for supervisory authorities |
| 34 | `/standards/` | Standards-body engagement landing |
| 35 | `/case-studies/` | Customer case studies |

### Tier 3 — Q4 2026 / Q1 2027 (10 pages)

| # | Route | Purpose |
|---|-------|---------|
| 36 | `/blog/` | Blog landing |
| 37 | `/watchlist/` | Article 50 Watchlist newsletter |
| 38 | `/press/` | Press kit + coverage |
| 39 | `/training/` | Paid training and certification courses |
| 40 | `/certification/` | LP Practitioner certification program |
| 41 | `/foundation/grants` | Foundation grant program |
| 42 | `/foundation/governance-documents` | Bylaws, charters, policies |
| 43 | `/services/professional` | Professional services engagement |
| 44 | `/security/audit-memos` | Published audit memos (NCC, ToB, Cure53) |
| 45 | `/security/bug-bounty` | Foundation-funded bug bounty |

### Content depth per page (rough sizing)

- **Landing hubs** (`/developers/`, `/vendors/`, `/regulators/`, `/`): ~1,000-2,000 words, multiple CTAs, audience-specific routing
- **Deep content** (`/article-50`, `/foundation`, `/commercial/operator-service`): ~3,000-5,000 words, substantive single-purpose
- **Documentation** (`/developers/spec`, `/developers/api-reference`): generated from source where possible, supplemented by hand-written context
- **Form/transaction pages** (`/commercial/founding-members` reservation): ~500-1,000 words + form
- **Quiet pages** (`/foundation/board`, `/foundation/transparency`): ~500-1,500 words, content-light, governance-heavy

### Total content production estimate

Tier 1 net new content: ~25,000 words across 8 new pages (assuming existing pages don't need rewrite).
Tier 2 content: ~30,000 words across 15 pages.
Tier 3 content: ~25,000 words across 10 pages.

Total: ~80,000 words of net new content across the site at full build-out. Realistically Tier 1 should ship by mid-July; Tier 2 by end of October; Tier 3 across Q4.

---

## Part 5: Mockup + Brand Evolution

V said "lets make a much better mock up" and "branding colors, logo stay." So palette and logo are locked. Visual language can evolve.

### What stays

- **Color palette**: cream `#FAF7F0`, navy `#081424`, mint `#20E898` + the surrounding scale (navy-2, navy-3, mint-2, mint-deep, mint-tint)
- **Display typeface**: Iowan Old Style serif (with Palatino Linotype, Book Antiqua, Georgia fallbacks)
- **Body typeface**: Inter / Söhne sans
- **Code typeface**: SF Mono / JetBrains Mono / Fira Code
- **Button shape**: pill (`border-radius: 999px`)
- **Primary button pattern**: navy background + mint text
- **Card pattern**: white on cream with 4pt mint top-border and 1pt line border
- **Link pattern**: 1pt underline at 4pt offset
- **Logo**: existing LedgerProof mark and wordmark

### What needs to evolve

**Typography hierarchy** — current site has H1, H2, H3 doing too much heavy lifting. We need:
- Display 1 (hero H1): 60-72px Iowan, line-height 1.05, letter-spacing -0.02em
- Display 2 (section H2): 36-48px Iowan, line-height 1.1
- Heading 1 (article H1): 28-36px Iowan
- Heading 2 (article H2): 22-28px Iowan
- Heading 3 (article H3): 18-22px Iowan
- Eyebrow: 11-13px Inter caps, letter-spacing 0.12em, mint-deep
- Body large: 19-20px Inter, line-height 1.6
- Body: 17px Inter, line-height 1.65
- Body small: 14-15px Inter, line-height 1.55
- Caption: 12-13px Inter, line-height 1.5, muted

**White space discipline** — current site is good but inconsistent. Standardize:
- Section vertical padding: 80px desktop / 56px mobile (currently varies)
- Hero vertical padding: 120px desktop / 80px mobile
- Card internal padding: 32px desktop / 24px mobile
- Inline form gap: 12px standardized

**Mobile-first responsive** — the current site is mostly desktop-designed with mobile patches. We need a true mobile-first audit:
- Nav hamburger pattern for mobile (currently nav just hides)
- CTAs stack with appropriate touch targets (44pt minimum)
- Tables become accordions on mobile
- Card grids become single-column with proper spacing

### New visual patterns needed

1. **Code blocks with syntax highlighting** — use Shiki or Prism for static syntax highlighting. Navy background + mint accents for keywords + cream text. Copy button. Language tag.

2. **Pricing comparison table** — for `/pricing` and `/commercial/operator-service`. Three or four columns, comparison rows, recommended-tier mint accent, footnote disclaimers.

3. **Tier card** (already exists at `/commercial/founding-members`) — refine: ribbon system for "Most Popular", price emphasis, hover state with subtle elevation.

4. **Customer logo strip** — once we have signed Founding Members. Grayscale logos at consistent height (40px), centered, with subtle hover-color reveal. Don't show fake logos before signed.

5. **Stats dashboard cards** — for `/foundation/transparency` and homepage trust strip. Large display-serif number + caption. Anchored receipt count, audit memos published, Foundation members, IETF participation status.

6. **Documentation page layout** — for `/developers/spec`, `/developers/api-reference`. Two-column with persistent left sidebar nav. Auto-generated table of contents on right. Search box. Version selector.

7. **Interactive verifier widget** — embed the verifier into pages where it adds value. Receipt input + verification result + "verify on Bitcoin" link. Demonstrates the offline-verification property in-page.

8. **Dashboard UI** — for the future customer portal and developer portal. Distinct visual language from marketing pages (denser, more functional). Reference: Stripe Dashboard, Vercel Dashboard, Linear app.

### Visual references

- **Stripe.com** — for institutional pricing-page polish, multi-audience landing routing, dashboard UI
- **Linear.app** — for developer-first feel, code-block treatment, marketing-vs-product visual distinction
- **Vercel.com** — for documentation-site polish, integration directory pattern, developer-marketing voice
- **Anthropic.com** — for editorial restraint, institutional voice, color discipline (their warm palette is conceptually similar to our cream)
- **OpenTelemetry.io** — for open-standard-with-vendor-ecosystem pattern, neutral institutional voice
- **Sigstore.dev** — for Foundation-led open-protocol pattern, governance-page treatment

### The mockup approach

Rather than V approving each page mockup one at a time, propose a **design system + page templates** approach:

1. **Design system page** — internal-only `/design-system` page that shows all the visual patterns (typography hierarchy, button states, card variations, form components, code blocks, dashboard primitives). V reviews this once.

2. **5 page templates** — hero+sections, documentation, dashboard, marketing-form, pricing-comparison. Each template renders multiple example pages with same patterns. V reviews 5 templates instead of 45 mockups.

3. **Page builds use templates** — each new site page uses one of the 5 templates with content slotted in. Faster builds, consistent visuals, easier maintenance.

This is the Stripe/Linear/Vercel approach to site architecture and it's the right one for our scale.

---

## Part 6: Backend Architecture Roadmap

The current backend is minimal: static HTML on Vercel + Supabase for form submissions + the live verify portal + the live publisher portal. The protocol itself runs (we have 50K+ test anchors). But there's no production-grade infrastructure for the paid services we're planning.

### MVP backend — next 60 days (build to support July 6 launch + early paid customers)

**1. Anchoring service (production batcher)**

Current state: prototype runs on a single host. Not production-grade.

Target: Foundation-operated reference anchoring service at `anchor.ledgerproofhq.io`. Features:
- Accepts signed individual receipts via HTTPS POST + Webhook callback
- Aggregates into Merkle trees per configurable window (default 60 min)
- Signs Merkle root with Foundation-controlled key (HSM-backed; root key ceremony Aug 15)
- Anchors root to Bitcoin mainnet via OP_RETURN (RBF + OpenTimestamps fallback)
- Returns inclusion proofs to deployers
- Public API documented and rate-limited

Open question: does the Foundation operate this, or does Inc.? Recommendation: Foundation operates the reference anchor (free, rate-limited for any user), Inc. operates the commercial anchor (SLA-backed, dedicated, integrated with hosted operator service).

**2. Verifier API**

Current state: verifier portal at verify.ledgerproofhq.io does client-side verification. No programmatic API.

Target: REST API at `api.ledgerproofhq.io/v1/verify`. Features:
- POST receipt + get verification result (sync, <100ms p95)
- GET historical receipt by hash (paid: caching layer)
- WebSocket subscribe to anchor events (paid: real-time notifications)
- Public API with rate limits for free tier (100 req/hour), paid tier for higher limits

**3. Developer dashboard (read-only)**

Target: simple SaaS dashboard at `dashboard.ledgerproofhq.io` where deployers can:
- Sign in via GitHub OAuth or email magic-link
- See their emission stats (receipts/hour, batch success rate, anchor confirmation status)
- Download their batch inclusion proofs
- Manage their HSM key references
- View their Founding Member tier status

MVP: read-only. Phase 2 adds write operations (key rotation, anchor cadence configuration).

Tech stack: Next.js + TypeScript + Supabase + Postgres. Hosted on Vercel.

**4. Foundation governance receipt anchoring (automated)**

Every Foundation publication (consultation submission, board minutes, erratum, transparency report, blog post) should auto-anchor as a Foundation receipt. Currently this is manual.

Target: simple admin tool that takes a document URL or hash + metadata + produces a Foundation receipt, signs with Foundation key, anchors with the standard pipeline.

**5. Customer email capture + lead routing (current)**

Existing Supabase backend handles form submissions. Need to add:
- Lead routing logic (Founding Member tier interest → Veronica + CRM; enterprise interest → enterprise@ledgerproof.org; press → press@; etc.)
- Email notification on submission to the appropriate routing
- CRM integration (Attio, Pipedrive, or HubSpot — Attio is recommended for institutional appearance)
- Anti-spam (Cloudflare Turnstile or Supabase native)

### Phase 2 backend — Q3-Q4 (build to support commercial scale)

**6. HSM-as-a-Service**

For customers who don't want to provision their own HSMs. We operate HSMs (AWS CloudHSM in eu-west-1 + eu-central-1 + us-east-1), provision per-customer signing keys, expose signing endpoints.

Pricing: included with hosted operator service Pro+ tier.

**7. Customer billing / subscription**

Stripe or Lemon Squeezy for subscription billing. Integration with the developer dashboard for subscription management.

**8. Customer compliance dashboard (full)**

Not just emission stats — actual compliance posture view:
- Article 50 coverage by sub-obligation (50(1), 50(2), 50(3), 50(4), 50(6))
- Per-deployment receipt density and anchor freshness
- Audit-ready export (one-click PDF for supervisory authority)
- Integration with their SIEM (receipts flow back from their SIEM for re-verification)
- Regulator request handler (auditor logs in with one-time access link, sees receipts for the time window they're auditing)

**9. Foundation member portal**

For Foundation Members (Standard, Anchor, Strategic Beta):
- Member directory
- Advisory Council communications
- Quarterly forum invitations and recordings
- Foundation board materials (where appropriate)
- Annual transparency report access

### Phase 3 backend — Q1-Q2 2027 (institutional infrastructure)

**10. Foundation board governance system**

Online voting, board materials distribution, meeting minutes auto-anchor. Possibly via a vendor like Diligent Boards or similar.

**11. Audit-firm integration**

LP-Conformant auditors (post certification program launch Q2 2027) need tools to:
- Pull verification results for their audit engagements
- Generate audit memo templates with embedded receipt verifications
- Manage their certification status

**12. Cross-jurisdictional regulator access**

Tooling for regulators across jurisdictions (CNIL, BaFin, AGCOM, AP, AESIA, FCA, SEC, OFCOM, etc.) to access verification capabilities without setting up their own infrastructure.

### Tech stack recommendations

**Frontend (marketing site)**: Vercel + Next.js (already using; expand to Next.js for the dashboard and dynamic pages).
**Frontend (apps — dashboard, verifier)**: Next.js + TypeScript + Tailwind (for the design system layer).
**Backend**: Foundation-operated services on Kubernetes (managed via GKE or EKS) for portability across cloud providers. Inc.-operated services on AWS or GCP (more lock-in acceptable for commercial side).
**Database**: Postgres (Supabase managed for fast development; migrate to self-hosted RDS or Cloud SQL at scale).
**Object storage**: S3 or GCS for receipts, audit logs, transparency artifacts.
**HSM**: AWS CloudHSM primary, with Azure Dedicated HSM as failover; YubiHSM2 for development.
**Bitcoin anchoring**: Run our own Bitcoin node OR use BlockCypher/QuickNode for production; we should run our own at production scale for jurisdictional independence.
**Identity / auth**: Auth0 or Clerk for the dashboard; GitHub OAuth for developers; institutional SSO (SAML) for enterprise tier.
**Email**: Postmark or AWS SES for transactional; ConvertKit or Beehiiv for newsletter.
**Monitoring**: Datadog (paid customer) + Prometheus + Grafana (self-hosted for Foundation reference deployments).
**Error tracking**: Sentry.
**Analytics**: Plausible or Fathom (privacy-preserving, EU-acceptable; not Google Analytics for the Foundation site).

### Backend buildout cost estimate

MVP backend (next 60 days): ~$15-25K monthly burn at 3-4 engineer + 1 SRE pace + ~$5K cloud infrastructure. Achievable with seed close.

Phase 2 backend (Q3-Q4): ~$40-60K monthly with full hosted operator service in production.

Phase 3 backend (Q1-Q2 2027): ~$80-120K monthly at the enterprise + audit-firm-integration scale.

---

## Part 7: Adapter Expansion Roadmap — Europe-Focused

V said: "Lets keep going until we have adapters for all of the major players worldwide, but specifically Europe."

### Phase 1 — Shipped today (Python, 4 adapters)

| Adapter | Framework / SDK | Origin | Audience |
|---------|----------------|--------|----------|
| `ledgerproof-langchain` | LangChain + LangGraph | US (LangChain Inc.) | Global, very large |
| `ledgerproof-llamaindex` | LlamaIndex | US (LlamaIndex Inc.) | Global, large |
| `ledgerproof-openai` | OpenAI Python SDK | US (OpenAI) | Global, very large |
| `ledgerproof-anthropic` | Anthropic Python SDK | US (Anthropic) | Global, large + growing fast |

### Phase 2 — Next 30 days (8 additional adapters)

European focus:

| Adapter | Framework / SDK | Origin | Why Europe-critical |
|---------|----------------|--------|---------------------|
| `ledgerproof-mistral` | Mistral Python SDK | French (Mistral AI) | European AI champion; EU sovereignty narrative |
| `ledgerproof-aleph-alpha` | Aleph Alpha Python SDK | German (Aleph Alpha) | German enterprise default; BaFin-credible |
| `ledgerproof-cohere` | Cohere Python SDK | Canadian (EU-friendly) | EU enterprise customers; multilingual strength |
| `ledgerproof-haystack` | Haystack | German (deepset) | German enterprise RAG default |
| `ledgerproof-semantic-kernel` | Semantic Kernel | US (Microsoft) | Microsoft enterprise ecosystem; .NET + Python |
| `ledgerproof-crewai` | CrewAI | US (CrewAI Inc.) | Fast-growing multi-agent framework |
| TypeScript: `@ledgerproof/langchain` | LangChain JS | US | Large JS developer base |
| TypeScript: `@ledgerproof/openai` | OpenAI JS SDK | US | Largest JS LLM SDK |

### Phase 3 — Q3 (8 additional adapters)

| Adapter | Framework / SDK | Origin | Notes |
|---------|----------------|--------|-------|
| `ledgerproof-dspy` | DSPy | US (Stanford) | Academic; growing in research-heavy enterprises |
| `ledgerproof-autogen` | AutoGen | US (Microsoft Research) | Multi-agent research framework |
| `ledgerproof-vllm` | vLLM | US (Berkeley) | Open-source inference server |
| `ledgerproof-bedrock` | AWS Bedrock Python | US (AWS) | Enterprise AWS default |
| `ledgerproof-azure-openai` | Azure OpenAI Python | US (Microsoft) | Enterprise Azure default |
| TypeScript: `@ledgerproof/llamaindex` | LlamaIndex JS | US | JS RAG users |
| TypeScript: `@ledgerproof/anthropic` | Anthropic JS SDK | US | JS Claude users |
| `ledgerproof-elevenlabs` | ElevenLabs Python | Polish/US | Article 50(2) synthetic audio specifically |

### Phase 4 — Q4 (8 additional adapters)

| Adapter | Framework / SDK | Origin | Notes |
|---------|----------------|--------|-------|
| `ledgerproof-huggingface` | Hugging Face Transformers | French/US (Hugging Face) | EU-headquartered AI hub; community-critical |
| `ledgerproof-replicate` | Replicate Python | US | Multi-model hosting |
| `ledgerproof-togetherai` | Together.ai Python | US | Open-source model hosting |
| `ledgerproof-synthesia` | Synthesia | UK | Article 50(2) synthetic video specifically |
| `ledgerproof-runway` | Runway ML | US | Article 50(2) synthetic video |
| `ledgerproof-stability` | Stability AI | UK/US | Article 50(2) synthetic image |
| TypeScript: `@ledgerproof/mistral` | Mistral JS SDK | French | EU JS users |
| Rust: `ledgerproof-rs-langchain-bridge` | LangChain Rust bridge | n/a (community) | High-performance deployments |

### Phase 5 — Q1 2027 (specialized European providers, 6+ adapters)

| Adapter | Framework / SDK | Origin | Notes |
|---------|----------------|--------|-------|
| `ledgerproof-h2o` | H2O.ai | US (with EU presence) | Enterprise ML platform |
| `ledgerproof-databricks` | Databricks Python | US (with EU presence) | Enterprise data + AI |
| `ledgerproof-snowflake` | Snowflake Python (Cortex) | US (with EU presence) | Enterprise data + AI |
| `ledgerproof-silo-ai` | Silo AI (now AMD-owned) | Finnish | Nordic enterprise AI |
| `ledgerproof-bria` | Bria | Israeli (EU customers) | Article 50(2) synthetic image, B2B |
| `ledgerproof-poolside` | Poolside | French | EU code-AI |

### Total adapter count at full coverage

Phase 1 + 2 + 3 + 4 + 5 = **34+ adapter packages** by end of Q1 2027.

Realistically, we'll prune as we learn: some frameworks decline (LlamaIndex if their commercial path falters), new ones emerge. The roadmap is directional, not committed.

### European focus rationale

EU AI Act enforcement happens in Europe first. European AI providers are most directly exposed. Building adapters for European AI providers FIRST signals:
- LedgerProof is EU-native, not just "compliant for EU"
- Foundation is institutionally aligned with European AI sovereignty narrative
- European AI providers have a partner for their own Article 50 customer-facing story

This positions us against US-centric compliance vendors who treat Europe as a secondary market.

### Adapter contribution model

After Phase 2 (when Foundation has internal capacity), open up to external contributors via the Foundation-funded contributor grants program. Anyone can contribute a new adapter; Foundation Technical Steering Committee reviews and accepts; contributor gets a grant ($1-5K), public attribution, and contributor credit on the published adapter. This scales adapter coverage beyond our internal eng capacity.

---

## Part 8: T-Q-R-S Deferred Execution Plan (from this morning)

V approved this morning's next-action sequence: T (verify site) → P (PyPI publish) → Q (GitHub repos) → R (Harrison Chase email) → S (Sprint 2 adapters).

Each is still queued. Status:

| Action | Description | Status | Dependencies | Effort |
|--------|-------------|--------|--------------|--------|
| **T** | Verify Vercel deploy of new site pages | Pending | Vercel auto-deploy from main complete | 5 min preview pass |
| **P** | Publish 4 adapter packages to PyPI | Pending | Foundation PyPI account; package names available | 30-45 min |
| **Q** | Create 4 GitHub repos under Foundation org | Pending | Foundation GitHub org exists; admin access; subtree split from launch repo | 20-30 min |
| **R** | Draft + send Harrison Chase / LangChain BD outreach with working adapter attached | Pending | P + Q complete (real install commands + real GitHub URLs) | 15 min draft + V review + send |
| **S** | Sprint 2: build next 4-8 adapters | Pending | Decision on Europe priority (Phase 2 above) | 30-60 min if parallel agents |

**Recommendation**: postpone T-Q-R-S until after V reviews this Full Stack Plan and confirms direction. The T-Q-R-S sequence assumes the current trajectory; the Full Stack Plan might shift it (e.g., if V wants the hosted operator service to be the lead conversion ahead of the adapters, R changes substantially).

---

## Part 9: Decision Points for V

These are the binary decisions V needs to make so subsequent execution has a coherent target.

### Decision 1 — Business model commitment

**Option A**: Pure open protocol + paid managed service (Datadog/OpenTelemetry analog).
**Option B**: Open-core (community edition free, enterprise edition paid features).
**Option C**: Pure non-profit (no paid services; revenue only from Foundation member dues and grants).

**My recommendation**: **A**. Datadog/OpenTelemetry pattern. The protocol stays open forever; paid services compete on operational quality and institutional credibility, not on protocol exclusivity. Avoids the MongoDB SSPL trap. Aligns with Foundation governance. Allows enterprise scale revenue.

### Decision 2 — Backend MVP timing

**Option A**: Build MVP backend now (next 60 days), commit ~$15-25K/month, ship hosted operator service in beta by Aug 2.
**Option B**: Defer backend MVP to post-Aug-2 launch, focus seed runway on adapter ecosystem + content + audit firm engagement.
**Option C**: Hybrid — Foundation-operated anchor service in MVP, Inc.-operated commercial service deferred to Q3.

**My recommendation**: **C**. Foundation reference anchor service is institutionally credible (lets us claim "production protocol" not just "open spec"). Inc. commercial service waits until we have signed Founding Members committed to paying — don't build what doesn't have demand yet.

### Decision 3 — Adapter Phase 2 priority

**Option A**: Europe-first (Mistral, Aleph Alpha, Haystack, Cohere, Semantic Kernel before TypeScript ports).
**Option B**: TypeScript-first (port the 4 Python adapters to TypeScript before adding new frameworks).
**Option C**: Parallel — half on Europe, half on TypeScript.

**My recommendation**: **A**. Europe-first matches the Article 50 enforcement geography. TypeScript can be Phase 3 in Q3.

### Decision 4 — Mockup approach

**Option A**: Full site redesign sprint — V approves design system once, all 45 pages templatized, rebuild in 6-8 weeks.
**Option B**: Progressive enhancement — keep current pages, improve template-by-template as new pages are built.
**Option C**: Hybrid — design system + 5 templates now, new pages use templates, existing pages migrate over Q3.

**My recommendation**: **C**. Design system + templates gives V design coherence without a 6-week redesign blocking everything else.

### Decision 5 — Three-audience routing

**Option A**: Separate audience hubs — `/vendors/`, `/developers/`, `/commercial/` (current) each with full sub-tree.
**Option B**: Unified entry with audience tabs — homepage routes everyone, each audience sees different content based on their selection.
**Option C**: Audience-routed but with shared core content — `/foundation`, `/security`, `/spec/`, etc. shared across all audience hubs.

**My recommendation**: **C**. Audience hubs with shared core content. Mirrors Stripe's site IA (developers / businesses / partners hubs with shared docs/pricing/about).

---

## Part 10: What I'd Build Next If V Says "Go"

Concrete sequence post-decision:

### Week 1 (Jun 2-8)

1. V reviews this plan, marks decisions on the 5 decision points
2. I create the design-system page (`/design-system` private route) — internal reference for all visual patterns
3. I create the 5 page templates (hero+sections / documentation / dashboard / marketing-form / pricing-comparison)
4. I draft the Tier 1 new pages content (Vendor hub, Operator Service, Enterprise tier, Developer hub, SDK landing, Spec landing, Security landing)
5. I write the rebrand-the-homepage spec (three-audience CTA rework)
6. T-Q-R-S deferred actions execute in parallel where they don't conflict with the above

### Week 2 (Jun 9-15)

7. Build out the 8 Tier 1 new pages using the templates
8. Ship the homepage three-audience rework
9. Phase 2 adapter sprint starts (Mistral + Aleph Alpha + Cohere + Semantic Kernel)
10. Foundation Delaware Articles filed (Jun 15 — KS4)

### Weeks 3-4 (Jun 16-29)

11. Backend MVP buildout begins (Foundation anchor service)
12. Phase 2 adapter sprint completes; ship to PyPI/npm
13. Customer dashboard MVP (read-only)
14. Tier 2 pages begin shipping

### Week 5 (Jun 30 - Jul 6)

15. Seed close Jun 25; backend MVP in production by Jul 1
16. Final pre-launch polish on all Tier 1 pages
17. **July 6 public launch** with full Tier 1 site + 12 adapter packages + Foundation anchor service in production

That's a 5-week sequence from V's decision-confirm to public launch with the full revamped site + expanded adapter ecosystem + production backend. Aggressive but achievable IF V confirms decisions this week and the senior protocol engineer hire lands on schedule.

---

## Closing — what makes this approach defensible

This plan deliberately rejects two appealing-but-wrong moves:

**Rejected: Open-core with paid features inside the protocol.** That would compromise the Foundation independence story. The day we have "free open spec but paid Foundation-only features" is the day CNIL stops treating us as a public-interest project and starts treating us as a vendor.

**Rejected: Pure non-profit with no commercial entity.** Foundations alone don't scale to the level of operational complexity Article 50 enforcement at-scale will require. Sigstore is wonderful and Sigstore has zero commercial entity and Sigstore can't ship a production HSM-as-a-Service to a tier-1 bank. We need the Inc. layer for that.

This plan threads the needle: Foundation owns the protocol forever (cannot be revoked, cannot be paywalled, cannot be exclusivized), Inc. competes on operational quality and institutional services. Anyone can self-host; most won't. The free path is real; the paid path captures the value of operational complexity.

That's Datadog + OpenTelemetry. That's Vercel + Next.js. That's the durable shape.

---

**End of plan. V's review + decisions on the 5 decision points unlocks the next 5 weeks of execution.**
