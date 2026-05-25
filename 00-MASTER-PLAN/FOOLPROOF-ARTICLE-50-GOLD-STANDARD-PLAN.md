# LedgerProof — Foolproof Plan to Become the EU AI Act Article 50 Gold Standard

**Status:** Master strategic plan
**Author:** Veronica S. Dawkins, Founder/Editor, LedgerProof Foundation
**Drafted:** 25 May 2026
**Strategic horizon:** 25 May 2026 → 2 August 2027 (15 months)
**Critical dates:**

| Date | Event | Days from today |
|---|---|---|
| 3 June 2026 | EU Article 50 consultation closes | **9** |
| 25 June 2026 | TVP seed round target close | 31 |
| 6 July 2026 | LedgerProof public launch | 42 |
| 2 August 2026 | EU AI Act Article 50 enforcement begins | 69 |
| Q3 2026 | First EU pilot anchors on Bitcoin mainnet | 90–180 |
| Q4 2026 | Code of Practice finalization (likely) | 150–250 |
| Q1 2027 | IETF draft → SCITT working group adoption (target) | 180–300 |
| 2 August 2027 | First full enforcement year ends; market settles around defaults | 365 |

---

## 0 · Why "Foolproof" Is the Right Frame

Most go-to-market plans are written to maximize upside. This one is written to **make failure structurally impossible** — because Article 50 enforcement is not a venture race we can lose gracefully. If LedgerProof is not the default Article 50 cryptographic provenance layer when enforcement begins, the window for becoming it will narrow and likely close, with C2PA + a basket of proprietary watermarking vendors filling the vacuum.

Foolproof therefore means:

1. **No single failure mode can kill the protocol.** Bitcoin fee spike, regulator snub, key compromise, Anthropic going dark, a competitor's announcement — none of these should be terminal.
2. **No single competitor can encircle us.** Every adjacent technology (C2PA, SynthID, OpenTimestamps, eIDAS QSP, IETF SCITT) should benefit from LPR adoption, not be threatened by it.
3. **No deployer can adopt LPR by accident and regret it.** The cheapest, easiest, lowest-effort path to Article 50 compliance must produce a valid LPR receipt.
4. **No regulator can prefer a competing standard without explicit, defensible justification.** LPR must already be cited, used, and demonstrated in regulator-facing forums before alternatives are evaluated.

This document is built backwards from those four invariants.

---

## 1 · Threat Model: What Could Kill This Plan

Before describing the plan, we enumerate every realistic way the plan fails. Each threat is paired with a structural mitigation that is *already in the plan below* — not a future hope.

| # | Threat | Likelihood | Severity | Structural mitigation |
|---|---|---|---|---|
| T1 | Commission picks C2PA-only and snubs cryptographic-provenance approach | Low | High | LPR is positioned *as the persistence layer of C2PA*, not as a competitor. C2PA assertion spec, CAWG observer track, eIDAS bridge — all complementary. We win whether they win or not. |
| T2 | A large AI provider (OpenAI, Anthropic, Google) ships proprietary Article 50 compliance | Medium | High | LPR's SDK auto-attaches *under* their APIs. If they ship their own, ours sits underneath theirs and still issues anchors. The deployer gets both for free. We compete by being free + open + permanent, not by features. |
| T3 | Bitcoin fee market spikes; per-anchor cost becomes prohibitive | Medium | Medium | Merkle aggregation already brings per-receipt cost to fractions of a cent at 1M/day. Spec supports multi-substrate fallback (Ethereum, federated CT logs, AWS QLDB) as backup profiles. Production never depends on a single substrate. |
| T4 | A major deepfake / Article 50 scandal happens before we launch, and a competitor gets the press cycle | Medium | Medium | We pre-publish (consultation, IETF draft, signatory application) by 3 June. The paper trail predates any scandal. We are the first protocol the press calls. |
| T5 | GDPR challenge: complaint that LPR anchors infringe data subject rights | Low | High | GDPR-by-construction architecture: legal-entity-only deployer IDs, role-only reviewer identifiers, content never anchored, Article 17 soft-delete preserving chain identity. EDPB-AI Office guidance compatible by design. Publish GDPR threat model. |
| T6 | Patent / IP challenge from a competitor | Low | Medium | Veronica's USPTO provisionals (5 of them) predate any plausible competitor work. IETF draft creates defensive publication. Spec under CC BY 4.0; code under Apache 2.0 = maximum prior-art exposure. |
| T7 | Foundation governance perceived as captured by commercial entity | Low | Medium | Foundation board with majority external members. Public charter. Annual transparency report. Reference operator code open source. Federated operator network — anyone can run an operator. |
| T8 | EU Member State diverges on Article 50 implementation (Spain says X, Germany says Y) | Medium | Low | LPR profile system already supports per-Member-State sub-profiles. AESIA-specific fields, BNetzA-specific fields can ship as optional additions without breaking interoperability. |
| T9 | Key operator key compromise | Low | High | HSM-backed operator keys; multisig custody via Unchained (TVP portfolio); rotation procedure documented; PQC migration path in LPR LongHorizon profile. |
| T10 | Anthropic / OpenAI restrict / change terms affecting our ability to keep building | Low | Low | All artifacts produced are owned by Veronica per current Commercial Terms. Inventor's notebook kept. Patents already filed. Open-source license already executed. Tool-substitutability is high. |
| T11 | TVP round doesn't close | Medium | Medium | Plan is funded for 12 months at current burn without external capital. TVP is the preferred path, not the only path. Alternate investors (Ten31, Stillmark, Fulgur, Bitcoin Frontier Fund, Castle Island, etc.) already pitched. |
| T12 | LedgerProof Inc. fails as a business | Low | High | Bitcoin anchor and IETF specification persist regardless of LedgerProof Inc. Foundation owns the protocol. Federated operator network continues even if reference operator shuts down. *The protocol cannot die with the company.* |

Every one of these mitigations is **built into the buildout below** — not a future commitment.

---

## 2 · The Four Foolproofing Dimensions

LedgerProof must be foolproof across four orthogonal axes simultaneously. Each dimension has its own success criteria and its own concrete deliverables.

### 2.1 Technologically foolproof

**Goal:** No technical failure can deny a deployer Article 50 compliance via LPR, and no improvement in adversarial techniques can render LPR obsolete.

**Success criteria:**
- All four Article 50(2) quality requirements (effective, interoperable, robust, reliable) demonstrably met
- Multi-substrate anchor capability (Bitcoin primary; Ethereum, federated CT logs as profiles)
- PQC migration path documented and tested
- Adversarial threat model published and audited
- GDPR-safe by construction, not by policy
- Performance: 1M receipts/day per operator, sub-100ms publish latency, no degradation under load

### 2.2 Publicly foolproof

**Goal:** Every public stakeholder — citizens, journalists, regulators, courts, researchers — can verify any LPR receipt without becoming a customer, without trusting LedgerProof Foundation, and without specialized knowledge.

**Success criteria:**
- Public verifier endpoint with no authentication, free of charge, forever (legally committed)
- Browser extensions surfacing receipts on any web content
- Mobile share-extensions for verifying any artifact
- Public transparency reports (quarterly)
- Public bug bounty program (six-figure max payouts)
- Independent security audits published annually
- Verifier source code reproducible and open

### 2.3 Competitively foolproof

**Goal:** No competitor can position LPR as a threat to themselves. Every adjacent technology either uses LPR underneath or benefits from LPR existing.

**Success criteria:**
- C2PA: LPR registered as an assertion namespace inside C2PA manifests
- SynthID, Adobe Content Credentials, Truepic, Attestiv: LPR positioned as the persistence layer for their watermarks
- OpenTimestamps, Simple Proof: LPR profile uses OTS-style RFC 3161 timestamping as a fallback option
- IETF SCITT: LPR is a published Profile, not a competing architecture
- eIDAS QSP: LPR-compatible workflows with qualified electronic seals documented
- ISO/CEN-CENELEC AI Act standards: LPR Foundation has observer status in relevant TCs

### 2.4 Partnership foolproof

**Goal:** Every meaningful counterparty in the AI compliance stack has either signed on, is in active conversation, or has been explicitly invited and declined for the record.

**Success criteria:**
- 5–12 named founding adopters at launch (mix of Bitcoin infrastructure, media, legal, enterprise SaaS)
- LangChain or equivalent AI-developer-platform partnership announced by July 6
- Cyber insurance partner (Coalition / Beazley / Munich Re) by Q3 2026
- One named EU Member State authority engaged (AESIA target by July 6; BNetzA / CNIL by Q3)
- One named newsroom adopter in production (Reuters / BBC / AP target by Q3)
- LedgerProof Foundation board of advisors with three named EU-jurisdiction members

### 2.5 Implementation foolproof (the Stripe play)

**Goal:** The path of least resistance for any AI deployer in the EU produces an LPR receipt. They must opt *out*, not *in*.

**Success criteria:**
- One-line install for major AI inference SDKs (OpenAI, Anthropic, Google, Mistral, Hugging Face)
- Zero-config defaults for the most common deployer profile (EU company with LEI, generating text/image/video, no human review)
- Five-minute integration documented for every major application framework (LangChain, LangGraph, Vercel AI SDK, Cloudflare Workers AI, FastAPI, Next.js)
- WordPress, Notion, Sanity, Contentful, Strapi plugins / extensions
- Adobe / Microsoft / Google native via C2PA bridge

---

## 3 · The Foolproofing Matrix

Every shipped artifact below is mapped to one or more of the five dimensions. **No artifact in this plan exists without a foolproofing rationale.**

| Artifact | Tech | Public | Competitive | Partnership | Implementation |
|---|:---:|:---:|:---:|:---:|:---:|
| LPR v1.1 specification | ✅ | ✅ | ✅ | — | — |
| IETF draft submission | ✅ | ✅ | ✅ | ✅ | — |
| C2PA assertion spec + CAWG submission | ✅ | — | ✅ | ✅ | ✅ |
| eIDAS compatibility statement | ✅ | — | ✅ | ✅ | — |
| EU consultation response (3 June) | — | ✅ | ✅ | ✅ | — |
| EU Code of Practice signatory application | — | ✅ | ✅ | ✅ | — |
| AESIA outreach (ES + EN) | — | — | — | ✅ | — |
| Public `GET /v1/verify/:seq` (unauthenticated) | ✅ | ✅ | ✅ | — | — |
| Public `GET /v1/receipts/by-content-hash/:sha256` | ✅ | ✅ | ✅ | — | — |
| `GET /v1/receipts/by-perceptual-hash/:algo/:hash` (TO BUILD) | ✅ | ✅ | ✅ | — | — |
| `pip install ledgerproof` + `ledgerproof.attach(openai)` | ✅ | — | — | — | ✅ |
| Anthropic SDK adapter | ✅ | — | — | — | ✅ |
| Google Gemini SDK adapter | ✅ | — | — | — | ✅ |
| Mistral / Hugging Face / Replicate adapters | ✅ | — | — | — | ✅ |
| LangChain callback (already proposed) | — | — | — | ✅ | ✅ |
| Vercel AI SDK plugin | — | — | — | ✅ | ✅ |
| Cloudflare Workers AI binding | — | — | — | ✅ | ✅ |
| WordPress plugin | — | ✅ | — | — | ✅ |
| Adobe / Microsoft / Google via C2PA bridge | — | ✅ | ✅ | ✅ | ✅ |
| Browser extension (Chrome / Firefox / Safari) | — | ✅ | — | — | — |
| PDF reader hooks (Acrobat, Nutrient) | — | ✅ | — | ✅ | — |
| Mobile share extensions (iOS / Android) | — | ✅ | — | — | — |
| Provenance Search (public) | — | ✅ | ✅ | — | — |
| Market Surveillance Authority dashboard | — | ✅ | ✅ | ✅ | — |
| Enterprise admin console | — | — | — | — | ✅ |
| Board-ready compliance reports | — | — | — | ✅ | — |
| Cyber insurance partnership | — | ✅ | — | ✅ | — |
| Law school curriculum partnership | — | ✅ | — | ✅ | — |
| Adversarial threat model (TO PUBLISH) | ✅ | ✅ | — | — | — |
| GDPR architecture document (already shipped) | ✅ | ✅ | — | — | — |
| Reviewer-competence semantics doc (TO PUBLISH) | ✅ | ✅ | — | — | — |
| Watermarking integration doc (TO PUBLISH) | ✅ | — | ✅ | ✅ | ✅ |
| `transparency_marker` UI integration guide (TO PUBLISH) | — | ✅ | — | — | ✅ |
| LongHorizon-v1 PQC profile spec | ✅ | — | ✅ | — | — |
| Multi-substrate anchor profile (Bitcoin + Ethereum + CT) | ✅ | — | ✅ | — | — |
| Operator key HSM + multisig (Unchained partnership) | ✅ | ✅ | — | ✅ | — |
| Federated operator network (≥3 independent operators) | ✅ | ✅ | — | ✅ | — |
| Coalition of founding adopters (5–12 named) | — | ✅ | ✅ | ✅ | — |
| Public bug bounty | ✅ | ✅ | — | — | — |
| Annual independent security audit (published) | ✅ | ✅ | — | — | — |
| Foundation governance charter with majority-external board | — | ✅ | ✅ | — | — |
| Quarterly transparency reports | — | ✅ | — | — | — |
| UK AI Bill profile (Q3 2026) | ✅ | — | ✅ | — | — |
| US Executive Order profile (Q3 2026) | ✅ | — | ✅ | — | — |
| China / Japan / Canada profiles (Q4 2026) | ✅ | — | ✅ | — | — |

This is **47 artifacts**. The plan is to ship the 12 starred items below by **July 6** and the remainder on the published cadence.

---

## 4 · The Stripe Play: Implementation Foolproofness

This is the single most important section. If LedgerProof is technologically perfect but not effortless to install, we lose. If installation is one line and on-by-default, we win — even if the protocol has imperfections that can be patched later.

### 4.1 The one-line promise

This is the developer experience that must work by **6 July 2026**:

```bash
pip install ledgerproof
```

```python
import openai
import ledgerproof

ledgerproof.attach(
    openai,
    publisher_id="LEI:5493001KJTIIGC8Y1R12",
    deployer_country="DE",
)

# That's it. Every openai.ChatCompletion call from here on
# auto-issues an LPR ai/article-50/v1 receipt anchored to Bitcoin
# through the EU operator at api-eu.ledgerproofhq.io.
```

The developer types **three lines** and is Article 50 compliant. No backend changes. No new endpoints to expose. No additional dependencies beyond the `ledgerproof` package itself. The same model — `attach()` — works for the Anthropic SDK, the Google Gemini SDK, the Mistral SDK, the LangChain client.

### 4.2 What `attach()` does under the hood

1. Monkey-patches the relevant client's completion / message methods to wrap the call in receipt issuance
2. Captures the output text/image/audio/video, computes SHA-256 (and perceptual hash if applicable)
3. Determines `content_category` from the modality (text → `SYNTHETIC_TEXT`, image → `SYNTHETIC_IMAGE`, etc.)
4. POSTs to `https://api-eu.ledgerproofhq.io/v1/publish` with all required `ai/article-50/v1` fields populated
5. Attaches the `receipt_id` and `entry_hash` to the response object as metadata, so the developer can surface them in the UI if desired
6. Caches the deployer's API key + signing key locally; rotates per LPR best practices
7. Fails open by default (logs a warning if LedgerProof is unreachable; deployer can opt to fail-closed for production)
8. Zero performance penalty: receipt issuance is asynchronous and batched (Merkle aggregation at the operator)

### 4.3 The frameworks

The `attach()` pattern is the universal interface. Specific framework integrations build on it:

```python
# LangChain
from langchain.callbacks import LedgerProofCallback
llm = ChatAnthropic(callbacks=[LedgerProofCallback(...)])

# LangGraph
agent = create_react_agent(model, tools, callbacks=[LedgerProofCallback(...)])

# Vercel AI SDK (TypeScript)
import { ledgerproof } from '@ledgerproof/vercel-ai'
const result = await streamText({
  model: openai('gpt-4o'),
  prompt: '...',
  experimental_telemetry: ledgerproof({ publisherId: '...' }),
})

# FastAPI
from ledgerproof.fastapi import LedgerProofMiddleware
app.add_middleware(LedgerProofMiddleware, ...)
```

Each of these is **≤200 lines** of integration code. The hard work is in the core `attach()` implementation; framework adapters are thin wrappers.

### 4.4 The content platform plug-ins

For deployers not writing custom code — the WordPress / Adobe / Notion / Google Docs population — the integration is a plug-in install:

| Platform | UX | Article 50 obligation covered |
|---|---|---|
| **WordPress** | Install plug-in → enter Publisher ID → save. Every AI-assisted post auto-issues. | 50(4) text |
| **Adobe Firefly / Photoshop** | C2PA assertion auto-added (no user action). | 50(2) image / video, 50(4) deepfake |
| **Microsoft Word AI** | Add-in install. Every AI suggestion accepted issues receipt at save. | 50(4) text |
| **Google Docs Gemini** | Workspace add-on. Same pattern. | 50(4) text |
| **Notion AI** | Integration via Notion API; receipt issues when page published. | 50(4) text |
| **Sanity / Contentful / Strapi** | CMS webhook → LPR. | 50(4) text + 50(2) image |
| **Figma / Canva** | Plug-in / app. AI-generated assets get receipts at export. | 50(2) image |
| **Webflow / Squarespace / Shopify** | App store listing. CMS-level hook. | 50(4) text + 50(2) image |

Each plug-in is **≤1 week** of development. The protocol surface is the same regardless of platform.

### 4.5 The verifier surface

For consumers of content — anyone who needs to *check* a receipt — the verifier ecosystem is the public face of LPR. This is what makes receipts socially visible and creates the pressure on non-compliant content:

| Surface | UX |
|---|---|
| **Chrome / Firefox / Safari extension** | Auto-detects LPR-eligible content on any page; badge shows green ✓ if receipt exists, gray ? if not. |
| **PDF reader hooks (Acrobat, Preview, Nutrient)** | Sidebar shows AI provenance and receipt status. |
| **iOS / Android share extension** | Share any image/video/text to "LedgerProof Verify" → returns receipt or absence. |
| **Slack / Teams / Discord bots** | Paste a link or upload; bot replies with receipt status. |
| **Email gateway (Outlook, Gmail)** | Inbound attachments tagged with receipt status. |
| **Provenance Search** | Public web tool: search by URL, by hash, by perceptual hash. |
| **Mastodon / Bluesky / X integrations** | Posts with image/video attachments get a "Verified ↗" link. |

A receipt is only as valuable as the surfaces that can read it. The Stripe play is **inline issuance + ubiquitous verification.**

---

## 5 · Implementation Sequence

Each week below specifies: **what ships, who acts, what verifies the ship, what's the foolproofing rationale.**

### Week 1 — 26 May to 1 June

| Artifact | Owner | Verification |
|---|---|---|
| Send 4 EU/AESIA emails (already drafted) | Veronica | Sent confirmation in iMail |
| Draft + submit Article 50 consultation response via EUSurvey | Veronica + Claude | EUSurvey submission ID returned |
| Publish 5 gap-fix documents (threat model, watermark integration, reviewer semantics, UI guide, perceptual hash plan) | Claude drafts; Veronica approves | Files committed to ledgerproof-eu |
| Build OpenAI `attach()` reference implementation in Python | Senior contractor or Claude | `pytest` smoke test issues receipt against api-eu prod |
| File IETF draft `draft-dawkins-scitt-ai-article50-00` | Veronica | Datatracker confirms upload |
| Update CLAUDE.md and TVP meeting prep | Veronica | TVP call ready by Wed May 27 |

**Foolproofing rationale:** This week creates the *paper trail* that no competitor can erase. By 3 June, LedgerProof is the only Article 50 cryptographic provenance protocol with: (a) a Commission consultation submission, (b) an IETF draft, (c) gap-fix documents, (d) a working SDK demo, (e) outreach to multiple Member State authorities.

### Week 2 — 2 to 8 June

| Artifact | Owner | Verification |
|---|---|---|
| Anthropic SDK `attach()` adapter | Claude / contractor | Live test against Claude API |
| Google Gemini SDK `attach()` adapter | Claude / contractor | Live test |
| Mistral SDK adapter | Claude / contractor | Live test |
| LangChain callback (`langchain-ledgerproof` on PyPI) | Claude / contractor | LangChain integration docs PR |
| Public perceptual-hash verifier endpoint `GET /v1/receipts/by-perceptual-hash/:algo/:hash` | Veronica deploys | Smoke test against Bitcoin-anchored pHash |
| LangChain partnership outreach sent | Veronica | Sent email; LangChain reply confirmation |
| Coalition outreach round 1 (TVP portfolio: Voltage, Unchained, Impervious, Galoy) | Veronica | Email sent confirmation; first replies tracked |

**Foolproofing rationale:** Week 2 turns the protocol into infrastructure. Every major AI SDK has an LPR adapter. LangChain users can integrate in one line. Perceptual hashing closes the robustness gap.

### Week 3 — 9 to 15 June

| Artifact | Owner | Verification |
|---|---|---|
| C2PA assertion spec submitted to CAWG | Veronica | C2PA acknowledgment |
| WordPress plug-in v0.1 (alpha) | Contractor | Install on test WP site, AI content gets receipt |
| Chrome extension v0.1 (alpha) | Contractor | Loads receipts for any tab |
| Vercel AI SDK plug-in | Contractor | Live test on Next.js app |
| Cloudflare Workers AI binding | Contractor | Live test on Workers playground |
| Hugging Face Inference Endpoints sidecar | Contractor | Docker image deployable |
| Pilot customer 1 signed (target: EU media organization) | Veronica + BD | Signed agreement, contract amount, pilot start date |
| Coalition outreach round 2 (Reuters / BBC / AP) | Veronica | Sent; track replies |

**Foolproofing rationale:** Week 3 lights up the platform integration layer (WordPress for 43% of the web, Vercel for the AI-native developer stack) and surfaces the first verifier (Chrome). First named pilot customer = real-world proof, not just a demo.

### Week 4 — 16 to 22 June

| Artifact | Owner | Verification |
|---|---|---|
| Adobe / Microsoft / Google C2PA bridge tested end-to-end | Contractor | Sample asset with both C2PA + LPR verifies in both pipelines |
| Browser extensions for Firefox + Safari shipped | Contractor | Cross-browser test |
| iOS / Android share extension v0.1 | Contractor | Test on devices |
| PDF reader hooks (Acrobat / Nutrient) | Contractor | Open AI-receipted PDF; receipt status shown in viewer |
| Enterprise admin console v0.1 | Contractor | Pilot customer logs in, sees their receipts |
| Pilot customer 2 signed (target: EU SaaS or legal firm) | Veronica | Signed agreement |
| Cyber insurance partnership conversation initiated (Coalition, Beazley, Munich Re) | Veronica + advisor | Meeting booked |

**Foolproofing rationale:** Week 4 covers the verifier surface that makes receipts socially visible. Enterprise console makes LPR look like a real product to the legal team that's signing the check.

### Week 5 — 23 to 29 June

| Artifact | Owner | Verification |
|---|---|---|
| TVP round closes (target) | Veronica | Wire received |
| Federated operator network: second operator stood up (Unchained-custodied or community) | Veronica | Second operator anchors a test receipt to Bitcoin mainnet |
| Multi-substrate fallback profile: Ethereum anchor profile spec drafted | Claude | Spec document committed |
| Provenance Search public web tool v0.1 | Contractor | Live at search.ledgerproofhq.io |
| Market Surveillance Authority dashboard v0.1 | Contractor | AESIA test login |
| Pilot customer 3 signed (target: enterprise SaaS or healthcare AI) | Veronica | Signed agreement |
| Coalition signatory count: ≥5 confirmed | Veronica | Tracker shows ≥5 in "Signed" column |

**Foolproofing rationale:** Week 5 introduces redundancy (second operator) and the public-facing verifier surface (Provenance Search). Capital lands. Pilot count hits 3 (the minimum credible launch narrative).

### Week 6 — 30 June to 6 July (LAUNCH WEEK)

| Artifact | Owner | Verification |
|---|---|---|
| Final regression test of all SDK adapters | Contractor | All adapters pass smoke against prod |
| Launch press release with 5+ named adopters | Veronica + comms | Press release distributed |
| Launch demo: live OpenAI → LPR → Bitcoin anchor → public verify, on stage | Veronica | Demo recorded + livestreamed |
| docs.ledgerproofhq.io fully populated | Claude + Veronica | Docs site live, complete |
| `pip install ledgerproof` + npm `@ledgerproof/sdk` published | Contractor | Both packages available |
| Coalition statement published | Veronica | All signatures posted |
| Bug bounty program launched | Veronica | HackerOne / Immunefi listing live |
| Foundation governance charter published | Veronica | Charter live; board members named |

**Foolproofing rationale:** Launch week ships the public face. Every claim made on July 6 is backed by a deployed artifact, a signed customer, or a published document. No vapor.

### Weeks 7–12 (post-launch, pre-enforcement) — 7 July to 2 August

| Theme | Deliverables |
|---|---|
| Member State expansion | BfDI / CNIL / Garante / AP outreach, ES + DE + FR + IT language versions of materials |
| Code of Practice signatory pursuit | Active engagement with the Code of Practice secretariat once identified through AI Office contact |
| Pilot scale-up | Pilots 1–3 in production; pilots 4–6 in onboarding |
| Annual security audit kick-off | Independent audit firm engaged (Trail of Bits, NCC Group, Cure53) |
| Multi-substrate fallback: Ethereum + federated CT log profiles published | Spec + reference operator code |
| Cyber insurance partnership signed | Premium discount announcement |
| IETF SCITT working group engagement | Draft revision based on community feedback |

**Foolproofing rationale:** Weeks 7–12 hit the enforcement date with a deployment, customer pipeline, regulatory engagement, and security audit all in motion. No single artifact is mission-critical because all of them ship in parallel.

### Quarters 3–4 (August–December 2026)

- Multi-jurisdiction profiles: UK AI Bill, US Executive Order, China provisional measures
- Federated operator network: ≥5 independent operators
- LongHorizon-v1 PQC profile production deployment
- ISO/CEN-CENELEC standards engagement
- Annual transparency report published
- First Code of Practice adequacy assessment
- LPR v1.2 spec draft (incorporating Code of Practice feedback)

### Year 2 (January–August 2027)

- Become default in ≥3 named regulator workflows
- ≥100 named adopters globally
- ≥10M receipts per day across all operators
- IETF SCITT WG adoption of LPR profile
- First enforcement case where LPR receipt is decisive evidence (positive or negative for the deployer)

---

## 6 · Quality Gates and Kill Criteria

A foolproof plan requires explicit *kill criteria* — conditions under which we pivot or pause, not push forward.

| Quality gate | Trigger | Action |
|---|---|---|
| **Q1 (3 June)** Consultation submission accepted | EUSurvey returns submission ID | If failed: paper backup via postal mail to DG CNECT same day |
| **Q2 (15 June)** OpenAI / Anthropic / Google adapters working in production | Live smoke test on prod | If failed: ship Python-only proxy as fallback; document gap publicly |
| **Q3 (25 June)** TVP round closed OR alternate investor committed | Wire received OR signed term sheet | If neither: extend runway via revenue (pilot revenue from 3 customers); delay launch by 2 weeks |
| **Q4 (1 July)** Minimum 5 coalition signatories | Signatory tracker confirms | If <5: ship with whatever we have, frame as "founding wave 1," continue recruiting |
| **Q5 (6 July)** Public launch livestream | Demo runs end-to-end live | If demo fails on stage: ship recorded demo, push live demo to following week |
| **Q6 (Aug 2)** No regulatory cease-and-desist | No formal communication from any regulator demanding suspension | If received: comply immediately, engage counsel, public response within 48h |

**Kill criteria** (conditions that pause the plan or force a pivot):

| Condition | Trigger | Decision |
|---|---|---|
| Bitcoin OP_RETURN deprecated or fees > €5/anchor sustained | Bitcoin Core release notes OR 30-day moving average | Activate Ethereum fallback profile within 30 days; do not abandon Bitcoin profile |
| Commission explicitly endorses competitor protocol by name in final guidelines | Final guidelines text (post-June 3) | Pivot LPR to be a *complement* to that protocol in v1.2; do not abandon |
| Patent challenge filed against core LPR claims | Service of process | Engage IP counsel; defend or design-around within 90 days |
| Operator key compromise | Detected via key transparency or HSM alert | Rotate, revoke, issue post-mortem within 7 days; legacy receipts remain valid via revocation timestamp |

No kill criterion in this plan is "we couldn't get a Twitter mention" or "OpenAI didn't return our email." Those are setbacks, not stop signs. Stop signs are listed above and only above.

---

## 7 · The Twelve-Month Vision (2 August 2026 → 2 August 2027)

By the first anniversary of Article 50 enforcement, LedgerProof has achieved the following measurable end-state:

| Metric | Target | Stretch |
|---|---|---|
| Deployers with at least one issued receipt | 1,000 | 10,000 |
| Receipts issued, cumulative | 10M | 1B |
| Receipts issued per day at peak | 100K | 5M |
| Independent calendar operators | 3 | 10 |
| Named signatories to the LPR adoption coalition | 25 | 100 |
| EU Member States with at least one supervisory-authority-acknowledged engagement | 5 | 15 |
| Code of Practice signatory status | Achieved | — |
| IETF draft state | WG-adopted | Approaching RFC |
| C2PA assertion namespace registered | Yes | LPR cited in C2PA spec body |
| Browser extensions installed | 50K | 500K |
| Cyber insurance premium-discount partnerships | 1 | 3 |
| Public bug bounty payouts (cumulative) | $50K | $250K |
| Independent security audit (published) | 1 | 2 |
| Enforcement matters where LPR receipt was determinative | 1 | 5 |

**Strategic position at +12 months:**

> "LedgerProof is the cryptographic provenance layer used by EU deployers to demonstrate Article 50 compliance. It is the only protocol that is (a) open, (b) Bitcoin-anchored, (c) GDPR-safe by construction, (d) IETF-standardized, (e) C2PA-compatible, (f) eIDAS-compatible, and (g) a signatory to the EU AI Act Code of Practice. Every major AI SDK has an LPR adapter. Every major content platform has an LPR integration. Every Member State market surveillance authority has an LPR dashboard. The Foundation governs the protocol; the commercial entity operates the EU reference operator. Both are profitable. Neither owns the protocol."

That sentence is the goal. Everything in this plan is sequenced to make it true.

---

## 8 · Appendix A — The Regulatory Matrix

| Authority | Country | Jurisdiction over Article 50 | LedgerProof status |
|---|---|---|---|
| EU AI Office (DG CNECT) | EU-wide | Primary | Email sent (drafted in iMail); consultation response planned 3 June |
| Cabinet of EVP Virkkunen | EU-wide | Political owner | CC'd on EU AI Office email |
| AESIA | Spain | National | Email sent (ES + EN drafted in iMail) |
| BfDI | Germany | Data protection (AI Act competent authority under designation) | Outreach Q3 2026 |
| CNIL | France | Data protection (AI Act competent authority under designation) | Outreach Q3 2026 |
| Garante | Italy | Data protection | Outreach Q3 2026 |
| AP (Autoriteit Persoonsgegevens) | Netherlands | Data protection | Outreach Q3 2026 |
| AGCOM | Italy | Media supervisory | Outreach Q3 2026 |
| OFCOM (post-Brexit) | UK | AI Bill (forthcoming) | Outreach Q4 2026 |
| NIST | US | AI Risk Management Framework | Outreach Q1 2027 |

---

## 9 · Appendix B — The Partnership Matrix

| Counterparty | Type | Status | Foolproofing role |
|---|---|---|---|
| **TVP (Trammell Venture Partners)** | Investor | Active conversation, May 27 call | Capital + Bitcoin-native ecosystem |
| **Voltage** | Bitcoin infra | Via TVP intro (held) | Infrastructure peer + future calendar operator candidate |
| **Unchained** | Bitcoin custody | Via TVP intro (held) | Operator key multisig custody |
| **Impervious** | IETF / standards | Via TVP intro (held) | IETF coalition member |
| **Galoy** | Open-source Bitcoin banking | Via TVP intro (held) | Federated operator structure exemplar |
| **LangChain** | AI developer platform | Proposal drafted | Native callback integration; distribution channel |
| **Anthropic** | AI provider | Customer (Claude); no formal partnership yet | SDK adapter |
| **OpenAI** | AI provider | None | SDK adapter |
| **Google Gemini** | AI provider | None | SDK adapter |
| **Mistral** | AI provider | None | SDK adapter |
| **Hugging Face** | AI inference platform | None | Sidecar integration |
| **C2PA / CAI** | Standards body | Assertion spec drafted | Complementary persistence layer |
| **IETF SCITT WG** | Standards body | Draft submitted | Profile within SCITT architecture |
| **Adobe** | Content tool / C2PA member | Via C2PA bridge | Implicit integration through C2PA |
| **Microsoft** | Content tool / C2PA member | Via C2PA bridge | Implicit integration through C2PA |
| **Reuters / BBC / AP** | Media | Coalition outreach planned | Named launch adopter |
| **DLA Piper / Bird & Bird / Hogan Lovells** | Legal | Coalition outreach planned | Named launch adopter |
| **Coalition / Beazley / Munich Re** | Cyber insurance | Outreach Q3 2026 | Premium discount partnership |
| **Bocconi / KU Leuven / IE / Sciences Po** | Law / Tech schools | Outreach Q3 2026 | Curriculum partner |

---

## 10 · Appendix C — Things This Plan Deliberately Does Not Do

To stay foolproof, this plan **avoids** the following adjacent moves that look tempting but expose us to failure:

- ❌ Issuing a LedgerProof token, coin, or any tradable asset
- ❌ Claiming LPR replaces watermarking, C2PA, or any existing technology
- ❌ Soliciting cold investment from undefined LPs or retail
- ❌ Promising specific regulatory outcomes ("LPR will be cited in the final guidelines")
- ❌ Naming individual EU officials in public communications without their consent
- ❌ Building a competing receipt format to C2PA's assertion structure
- ❌ Patenting anything that should remain open under the protocol's grant
- ❌ Operating the only calendar operator (we federate from day one of the launch narrative)
- ❌ Marketing to non-EU markets before EU enforcement settles
- ❌ Hiring before the TVP round closes
- ❌ Spending more than €30K/month on operating costs before pilot revenue exceeds €15K/month

Each of these is an attractive move that introduces a failure mode we don't need to accept.

---

## 11 · Closing

This plan is foolproof in the strict sense: there is no single failure that ends the protocol. There is no single move a competitor can make that excludes us. There is no single regulatory decision that erases our position. There is no single customer loss that breaks the business. There is no single technical failure that destroys the receipt record.

It is foolproof because we have already done the hardest thing — built the only existing open protocol that covers all four Article 50 sub-obligations — and the remaining work is execution against a clear, dated, accountable plan with explicit kill criteria and structural mitigations for every named threat.

Execute it.

---

*LedgerProof Foundation · Master strategic plan v1.0 · 25 May 2026*
*Authored by Veronica S. Dawkins with planning support from Claude.*
*This document is the canonical source of truth for the 25 May 2026 → 2 August 2027 strategic horizon. Sub-plans (consultation response, signatory application, partnership outreach, SDK roadmap, verifier roadmap) inherit from this document and must reconcile to it.*
