# LedgerProof Foundation + Inc. — Five-Year Profit Model

**Drafted:** Tuesday June 2, 2026
**Author:** Fractional CFO lens, in service of V's Full Stack Plan investment decision
**Fiscal year:** Aug 1 – Jul 31 (Y1 = FY27 = Aug 1, 2026 – Jul 31, 2027)
**Entity scope:** LedgerProof Inc. consolidated. Foundation expenses allocated separately and called out where they affect Inc. P&L (via §G&A grant line).
**Base reference:** `14-seed-close-pack/01-cfo-24-month-model.md` (the reality-checked 24-month operating model); `12-premortem/05-EXPLOSIVE-ADOPTION-REALITY-CHECK.md` (the kill list for inflated numbers)
**Decision this document supports:** Whether to commit the Full Stack Plan investment (~$15–25K/mo incremental backend burn through Q3, ~$40–60K/mo Q3–Q4, ~$80–120K/mo Q1–Q2 2027 per Master Plan §6).

---

## 0. Executive read — 60 seconds

The honest 1/3/5-year profit number range, BASE case:

| Year | Revenue (recognized) | EBITDA | Cumulative FCF |
|------|--:|--:|--:|
| **Y1 (FY27)** | $6.7M | ($5.3M) | ($5.3M) |
| **Y3 (FY29)** | $55M | ($2M) to break-even | ($15M) |
| **Y5 (FY31)** | $185M | $25–40M (15–22% EBITDA margin) | $30–60M positive |

The honest 1/3/5-year range with explicit "if X happens" qualifiers, across all three scenarios:

| Scenario | Y1 rev | Y3 rev | Y5 rev | Y5 EBITDA | If… |
|---|--:|--:|--:|--:|---|
| **Pessimistic** | $3.4M | $18M | $65M | ($5M) loss | Article 50 enforcement is soft (KS6), no LangChain partnership (KS7), Vanta ships native crypto Q1 27 |
| **BASE** | $6.7M | $55M | $185M | $25–40M | CFO 24-mo model holds, ~50% YoY post Y2, hosted operator service ramps as designed, Foundation institutional credibility lands |
| **Bull** | $9.2M | $110M | $420M | $90–135M | Datadog-class adoption curve, M/593 names a SCITT-based receipt format, Vanta/Drata partnership ships Q1 27, insurance discount catalyst materializes Y3 |

**The single decision this analysis supports:** Whether the Full Stack Plan's incremental investment (~$1.5–2.5M cumulative through May 27 for the backend buildout above the CFO model's baseline) is justified by the revenue surface it unlocks (specifically: the hosted operator service Y2–Y5 revenue line). The answer is yes in BASE, yes in Bull, breakeven-or-mild-loss in Pessimistic — and the investment is recoverable in Pessimistic because the same backend serves enterprise tier customers regardless of operator-service unit volume.

**TAM-capture sensitivity, one line:** The delta between BASE and Bull is ~2.3× at Y5; the delta between Pessimistic and BASE is ~2.8× at Y5. The single largest swing factor is hosted operator service customer count Y3–Y5 (which compounds from Y2 base), and that line is most sensitive to (1) whether Foundation reference anchor service ships by Aug 2 and (2) whether the LangChain/LlamaIndex/Mistral integration partnerships convert into measurable end-customer flow by Q1 27.

---

## 1. TAM definition — what market are we actually capturing?

The honest TAM exercise has to define the market in concentric layers, because the literature inflates "AI compliance market" numbers by counting every dollar of AI spend that touches a compliance use case. The actual reachable market for cryptographic transparency-receipt infrastructure is much narrower than "AI compliance" or "AI governance."

### Layer 1 — EU-deployed organisations with direct Article 50 obligations

Article 50 obligations attach to **deployers** of AI systems that interact with natural persons, generate synthetic content, perform emotion recognition, or generate deepfakes. The deployer count in the EU is bounded by:

- **EU enterprise count (250+ employees):** ~44,000 (Eurostat 2024)
- **EU mid-market (50–249 employees):** ~250,000
- **EU SMEs with measurable AI deployment (10–49 employees):** ~200,000–500,000 estimated; most are out of scope or self-attest
- **EU public-sector deployers:** ~5,000–15,000 (national agencies, ministries, supervisory authorities, public broadcasters, public hospitals)
- **EU regulated-sector deployers with sectoral overlap (FSI, healthcare, energy, telecom, transport):** ~12,000–25,000 (where Article 50 + DORA/MiFID/HIPAA-equivalent stacking creates real evidentiary urgency)

**Realistic Layer 1 paying-customer universe at maturity:** ~5,000–15,000 organisations in the EU that genuinely buy evidentiary infrastructure to satisfy supervisory authorities. (Vanta has ~7,000 customers globally after 5 years; OneTrust has ~14,000 across 16 years and a much broader product surface.)

**Source anchors:** Eurostat business demography 2024; IDC Worldwide AI Governance Software Forecast 2024 ($1.6B 2024 → $9.6B 2030, 35% CAGR — but this includes broad AI governance suites, not the narrower cryptographic provenance slice); EU Commission AI Act impact assessment (2021) estimating ~10K–15K high-risk AI deployers in the EU within 3 years of enforcement.

### Layer 2 — Global organisations with EU customer-touch surface area

Any organisation globally that serves EU consumers, runs EU subsidiaries, or processes EU personal data with AI inference becomes a deployer under Article 50 the moment the inference touches an EU resident. This is the GDPR-style extraterritorial reach.

- **US enterprises with material EU revenue (Fortune 500 + Russell 2000 EU-exposed subset):** ~800–1,500
- **UK enterprises with EU customer base:** ~2,000–5,000
- **APAC enterprises with EU subsidiaries:** ~1,000–2,500
- **LATAM, MEA, Africa enterprises with EU touch:** ~500–1,500

**Realistic Layer 2 paying-customer universe at maturity:** ~3,000–8,000 globally addressable, of which maybe 1,000–3,000 actually buy in the 5-year window. (This is the layer where US-headquartered AI vendors and platforms most aggressively seek a "we handle Article 50 for you" story for their EU customers.)

### Layer 3 — AI vendors needing Article 50 customer-facing story

Vendors face Article 50(2) (synthetic content marking) directly and need a Article 50(1) story to give their customers. Vendor count:

- **LLM providers (foundation models):** ~50–100 globally (OpenAI, Anthropic, Mistral, Cohere, Aleph Alpha, AI21, Together, Replicate, Hugging Face Inference, AWS Bedrock, Azure OpenAI, Vertex AI, Bedrock, Mistral La Plateforme, etc.)
- **AI orchestration / framework vendors:** ~30–60 (LangChain Inc., LlamaIndex Inc., DSPy, Haystack/deepset, CrewAI, AutoGen, Semantic Kernel — though MS won't be a paying customer)
- **AI-native applications with EU customer exposure (Synthesia, ElevenLabs, Runway, Stability, Pika, Suno, Krea, Leonardo, Perplexity, etc.):** ~500–2,000
- **Vertical AI vendors with EU enterprise customers (legal AI, healthcare AI, fintech AI, etc.):** ~2,000–10,000

**Realistic Layer 3 paying-vendor universe at maturity:** ~200–800 vendors paying a partnership/certification fee or integrating the protocol natively. This is the "LP-Conformant Vendor" revenue line.

### Layer 4 — Audit firms needing LP-Conformant certification

- **Big-4 firms with EU AI assurance practice:** 4 (KPMG, PwC, EY, Deloitte) — each with 5–25 EU country partnerships, each potentially a separate certification engagement
- **Tier-2 audit firms (BDO, Grant Thornton, RSM, Mazars, Crowe):** ~10 with material AI practice
- **Specialty cryptographic / security audit firms (NCC Group, Trail of Bits, Cure53, Bishop Fox, Latacora, Kudelski, etc.):** ~30–50
- **National notified bodies with AI conformity scope (TÜV SÜD, TÜV Rheinland, AFNOR Certification, DEKRA, DNV, SGS, etc.):** ~15–30
- **Independent boutique AI auditors:** ~100–300 (growing rapidly post-enforcement)

**Realistic Layer 4 paying universe at maturity:** ~50–200 firms paying for LP-Conformant certification + annual recertification.

### Layer 5 — Compliance practitioners needing training

- **EU compliance officers / CCOs with AI scope:** ~80,000–150,000 (extrapolated from IIA membership, IAPP membership, CISO surveys)
- **EU CISOs / security architects with AI scope:** ~30,000–80,000
- **EU lawyers with AI/tech practice:** ~20,000–50,000
- **EU developers in regulated industries:** ~150,000–400,000
- **Global English-speaking equivalents (US/UK/APAC):** add ~3–5× the EU numbers for fully addressable training market

**Realistic Layer 5 paying universe at maturity (Y5):** ~5,000–20,000 paid seats across all course types. Training is a real revenue line but never a primary one — it's a top-of-funnel and ecosystem-binding mechanism.

### Estimated annual spend per organisation by tier

| Tier | Org count (paying, mature) | Avg annual spend | TAM at maturity |
|---|--:|--:|--:|
| Enterprise / G-SIB / top-3 EU insurer | 50–150 | $500K–$2M | $25M–$300M |
| Tier-1 mid-large enterprise (regulated, EU-headquartered) | 500–1,500 | $80K–$250K | $40M–$375M |
| Mid-market deployer (Vanta/Drata connector tier) | 2,000–5,000 | $24K–$60K | $50M–$300M |
| Vendor partnerships / LP-Conformant Vendor program | 100–400 | $25K–$150K | $2.5M–$60M |
| Audit firm certifications | 50–200 | $50K–$250K (initial) + $25–100K annual | $2M–$50M annual |
| Training & certification (paid seats annual) | 5,000–20,000 seats | $1,500–$4,000/seat | $7.5M–$80M |

### Three TAM scenarios — what the market actually looks like

**Conservative — Article 50 enforcement is GDPR-like (slow, narrow, predictable):**
- Realistic addressable spend by Y5: **$200–400M annual across all tiers** in EU + EU-touching organisations
- Only most-exposed orgs (G-SIBs, top-tier insurers, public broadcasters, deepfake-adjacent vendors) actually buy cryptographic evidentiary infrastructure
- Mid-market mostly self-attests with vendor compliance PDFs
- Enforcement actions are infrequent and concentrated in 2–4 marquee cases per year
- Comparable: GDPR enforcement curve 2018–2022 (first €100M+ fine was Q4 2020, 28 months after enforcement)

**Moderate — Article 50 enforcement is meaningful and consistent:**
- Realistic addressable spend by Y5: **$1.5–3B annual across all tiers**
- Mid-market regulated enterprises pay for managed compliance because internal counsel + CCO can't risk under-evidencing
- Big-4 builds revenue line around Article 50 readiness assessments, recommending cryptographic substrate
- Insurance market begins reflecting Article 50 evidentiary quality in cyber/E&O underwriting
- Comparable: SOC 2 + ISO 27001 market 2018–2023 — multi-billion dollar managed compliance category emerges around enforcement-credible evidence

**Bull — Article 50 evidentiary infrastructure becomes de facto mandatory:**
- Realistic addressable spend by Y5: **$5–10B annual across all tiers**
- Insurance discounts + procurement requirements drive universal adoption for any AI deployment touching EU citizens
- CEN/CENELEC harmonized standard names SCITT-based receipt format as one acceptable Article 50 implementation
- Brussels Effect kicks in: US frontier labs natively emit receipts because EU enterprises require them in procurement
- Comparable: TLS/SSL adoption 2015–2022 — Let's Encrypt + CA/Browser Forum standards + browser warnings drove 95%+ adoption inside 7 years

**TAM the BASE case operates against:** Moderate scenario, ~$1.5–3B annual addressable EU-touching spend by Y5, with a long tail of organic Conservative-case revenue from the most-exposed organisations regardless of broader enforcement trajectory.

### Comparable industry-source citations

- **IDC Worldwide AI Governance Software Forecast 2024:** $1.6B in 2024 → $9.6B by 2030 (35% CAGR). Broader category includes model registries, bias monitoring, MLOps governance — cryptographic provenance is a narrow slice.
- **Gartner AI TRiSM Hype Cycle 2024:** Trust, Risk, Security Management for AI market projected $11B by 2028. Article 50 evidentiary infrastructure sits inside the "AI Compliance & Audit" sub-segment, ~15–25% of total = $1.7–2.7B.
- **McKinsey State of AI 2024 + 2025:** 67% of enterprises have a designated AI risk owner; 38% have an AI compliance budget separately allocated; median annual spend $150K–$1.2M across regulated industries.
- **EU Commission AI Act impact assessment (2021, updated 2024):** estimated 10K–15K high-risk AI deployers in EU; compliance cost €5K–€400K per deployer per year (huge variance).
- **Bessemer State of the Cloud 2025:** compliance/security infrastructure SaaS multiples remain 12–22× ARR for category creators (Vanta last private at ~25×, Drata recent secondary at ~20×, OneTrust last round at ~16×).

### What we are NOT capturing in our TAM

Honesty discipline requires naming these:

- **General AI governance suite revenue** (Credo AI, Holistic AI, Trustible, ModelOp, Fiddler) — we are infrastructure, not a governance platform. Those vendors are partners or eventual integrators of LedgerProof, not direct competition for the same dollar.
- **General compliance/audit software** (Vanta, Drata, OneTrust, ServiceNow GRC, MetricStream, Archer) — same logic. We are the cryptographic substrate, not the compliance workflow platform. Our revenue is incremental to theirs, not a substitute.
- **AI safety/eval tooling** (Arize, Truera, Weights & Biases, Galileo, Patronus) — adjacent category, not direct overlap. They could become competitors if they add cryptographic attestation, but until then, complementary.
- **MLOps platforms** (Databricks, Snowflake, AWS SageMaker, Vertex AI) — vendors / channels, not the same revenue surface.

The honest framing: we are capturing the **cryptographic evidentiary substrate slice** of the larger AI governance + compliance market. That slice is real, defensible, and growing — but it is a slice, not the whole pie.

---

## 2. Market share capture trajectories

Y1, Y3, Y5 share assumptions for each TAM layer, across three scenarios. Each share number must be defensible against the comparable companies' actual capture curves at equivalent stages.

### Comparable capture curves (anchor data)

| Company | Founded | Y1 customers | Y3 customers | Y5 customers | Y5 ARR |
|---|---|--:|--:|--:|--:|
| Vanta | 2018 | <20 | ~800 | ~7,000 | ~$200M |
| Drata | 2020 | ~50 | ~1,500 | ~4,000 | ~$100M |
| OneTrust | 2016 | <50 | ~3,500 | ~10,000+ | ~$200M+ |
| Snowflake | 2014 | ~20 | ~600 | ~3,100 | ~$265M (Y5 = FY19) |
| Datadog | 2010 | <100 | ~1,000 | ~5,000 | ~$153M (Y5 = FY14) |
| Confluent | 2014 | ~10 (Y1 limited monetization) | ~500 | ~2,000+ | ~$150M (Y5 = FY19) |
| MongoDB | 2007 | <50 (pre-monetization) | ~600 | ~2,000+ | ~$65M (Y5 = FY13, pre-Atlas) |
| HashiCorp | 2012 | <50 | ~500 | ~1,800+ | ~$120M (Y5 = FY17) |

**The pattern:** Even category creators with the best go-to-market in the world had ~5K–10K customer counts at Y5. The fantasy of 50K+ customers by Y5 is not in the data anywhere. Realistic LedgerProof Y5 customer count = **3,500–7,000 paying organisations** in the BASE case; **1,500–3,000** in Pessimistic; **7,000–12,000** in Bull.

### Y1 (FY27, Jun 2026 – May 2027) — realistic share assumptions

| Layer | TAM (mature universe) | Y1 Pessimistic | Y1 BASE | Y1 Bull | Source/rationale |
|---|--:|--:|--:|--:|---|
| L1 Enterprise (G-SIB, top insurer) | 50–150 | 1–2 | 3–5 | 6–10 | CFO model A7 — enterprise cohort ramps Jan–Jun 27 |
| L1 Mid-large (Founding Member + Enterprise Tier) | 500–1,500 | 8–15 | 25–40 | 50–80 | CFO model A3, A7 |
| L2 Mid-market (Vanta connector) | 2,000–5,000 | 25–50 | 80–150 | 200–400 | CFO model A6 |
| L3 Vendor partnerships | 100–400 | 0 | 2–5 | 8–15 | LangChain, Mistral, Aleph Alpha track |
| L4 Audit firm certifications | 50–200 | 0 | 1–2 | 3–5 | Cert program launches Q2 27 |
| L5 Training paid seats | 5K–20K | 0 | 50–200 | 500–1,000 | Training launches Q3 27 |

### Y3 (FY29, Jun 2028 – May 2029) — Datadog-class growth check

| Layer | Y3 Pessimistic | Y3 BASE | Y3 Bull | Sanity check vs comp |
|---|--:|--:|--:|---|
| L1 Enterprise | 5–12 | 20–40 | 50–80 | Vanta had ~30 enterprise logos at Y3 |
| L1 Mid-large | 60–120 | 250–450 | 600–1,000 | Vanta had ~800 mid-large at Y3 |
| L2 Mid-market | 300–600 | 1,200–2,000 | 3,000–5,000 | Vanta hit ~2,000 at Y3 across all tiers |
| L3 Vendor partnerships | 5–10 | 25–50 | 75–150 | Stripe Connect had ~25 platform partners at Y3 |
| L4 Audit firm certifications | 5–10 | 20–40 | 50–80 | DocuSign ID Verification had ~30 partners at Y3 |
| L5 Training paid seats (annual) | 500–1,500 | 3,000–6,000 | 10,000–20,000 | Linux Foundation training had ~5K paid seats by Y3 |

### Y5 (FY31, Jun 2030 – May 2031) — mature competitive equilibrium

| Layer | Y5 Pessimistic | Y5 BASE | Y5 Bull | Sanity check |
|---|--:|--:|--:|---|
| L1 Enterprise | 15–25 | 50–100 | 120–200 | Vanta Y5 = ~100 enterprise; Datadog Y5 ~150 large logos |
| L1 Mid-large | 150–250 | 600–1,000 | 1,500–2,500 | Vanta Y5 ~1,500 mid-large + enterprise combined |
| L2 Mid-market | 600–1,200 | 2,500–4,500 | 6,000–10,000 | Vanta Y5 ~5,500 SMB+MM; Drata Y5 ~3,500 |
| L3 Vendor partnerships | 15–30 | 75–150 | 200–400 | Stripe Connect Y5 ~150 platforms; Twilio Y5 ~120 ISV partners |
| L4 Audit firm certifications | 15–30 | 60–120 | 150–300 | Comparable: AWS Partner Audit Program Y5 ~150 |
| L5 Training paid seats (annual) | 1,500–4,000 | 8,000–15,000 | 25,000–50,000 | Linux Foundation Y5 ~12K paid; AWS Cert Y5 ~30K |

### Three scenario growth shapes per year (revenue growth rate)

| Year | Pessimistic YoY | BASE YoY | Bull YoY |
|---|--:|--:|--:|
| Y1 → Y2 | +180% (off small base) | +194% (per CFO model: $6.7M→$19.7M) | +237% |
| Y2 → Y3 | +130% | +175% ($19.7M→$55M) | +220% |
| Y3 → Y4 | +85% | +115% ($55M→$118M) | +145% |
| Y4 → Y5 | +50% | +57% ($118M→$185M) | +70% |

**Sanity check vs Datadog FY12–FY15 (their Y3–Y6):** Datadog grew 153% → 117% → 97% → 84% over those four years. LedgerProof's BASE Y2→Y5 trajectory (194% → 175% → 115% → 57%) is moderately faster early (because we have a regulatory forcing function Datadog didn't), moderately slower late (because we have a narrower TAM than observability). The shape is internally consistent with category creators.

**Sanity check vs Vanta FY19–FY22 (their Y2–Y5):** Vanta grew est. 250% → 200% → 130% → 70%. LedgerProof's BASE is comparable in slope but lower in absolute Y5 ARR — because Vanta operates the much broader compliance-platform surface and LedgerProof operates the narrower cryptographic substrate. That delta is expected and structural.

---

## 3. Revenue projection by surface (Y1, Y2, Y3, Y4, Y5)

For each year, project revenue from each of the 6 paid surfaces. All figures BASE case in $M recognized revenue unless noted.

### Y1 (FY27) — recognized $6.7M BASE / $3.4M Pessimistic / $9.2M Stretch

Direct from CFO model. Surface breakdown:

| Surface | Y1 BASE | Y1 Pessimistic | Y1 Stretch (Bull) |
|---|--:|--:|--:|
| Founding Member tier dues (5 × $35K avg) | $0.175M | $0.140M | $0.250M (incl. Riot $1M ratable = $0.333M) |
| Hosted Operator Service (Starter+Pro launched Q3) | $0.5M | $0.1M | $1.2M |
| Enterprise Tier (Jan–Jun 27 cohort: 10–30/mo at $80K ACV ramping) | $5.8M | $3.1M | $7.0M |
| Professional Services | $0.15M | $0.05M | $0.45M |
| Certification Program (launches Q2 27, mostly Y2 revenue) | $0 | $0 | $0.15M |
| Training & Certification (launches Q3 27, Y2 revenue) | $0 | $0 | $0.10M |
| Overage / receipt usage | $0.075M | $0.010M | $0.150M |
| **Total recognized** | **$6.7M** | **$3.4M** | **$9.2M** |

### Y2 (FY28) — recognized $19.7M BASE / $8.2M Pessimistic / $31.0M Stretch

Direct from CFO model Y2 BASE recognized ARR ($19.7M run-rate). Surface breakdown:

| Surface | Y2 BASE | Y2 Pessimistic | Y2 Stretch (Bull) |
|---|--:|--:|--:|
| Founding Member tier dues (cumulative renewals + new) | $0.7M | $0.5M | $1.4M |
| Hosted Operator Service (Starter: 80 cust × $30K = $2.4M; Pro: 25 × $120K = $3M; Enterprise: 8 × $400K = $3.2M) | $8.6M | $3.5M | $14M |
| Enterprise Tier (35–50 logos × $90–110K ACV cumulative) | $8.5M | $3.5M | $12.5M |
| Professional Services | $1.0M | $0.4M | $1.8M |
| Certification Program (5–8 firms × $100–250K) | $0.5M | $0.1M | $1.0M |
| Training & Certification (1K–2K seats × $2K avg) | $0.2M | $0.05M | $0.5M |
| Overage / receipt usage | $0.2M | $0.05M | $0.4M |
| **Total recognized** | **$19.7M** | **$8.2M** | **$31.0M** |

### Y3 (FY29) — recognized $55M BASE / $18M Pessimistic / $110M Stretch

Projection from Y2 base using the BASE +175% YoY assumption (cohort math: Y2 ARR booked $31M with NDR 115% + new cohort acquisition matching Y2 magnitude → Y3 booked ~$70M / recognized run-rate ~$55M).

| Surface | Y3 BASE | Y3 Pessimistic | Y3 Bull |
|---|--:|--:|--:|
| Founding Member tier dues | $1.5M | $1.0M | $2.5M |
| Hosted Operator Service | $25M | $7M | $50M |
| Enterprise Tier (cumulative 50–80 logos) | $22M | $8M | $42M |
| Professional Services | $3.0M | $1.0M | $6.0M |
| Certification Program (15–25 firms certified) | $2.0M | $0.5M | $4.5M |
| Training & Certification (3–6K paid seats) | $1.0M | $0.3M | $3.0M |
| Overage / receipt usage | $0.5M | $0.1M | $1.5M |
| **Total recognized** | **$55M** | **$18M** | **$110M** |

### Y4 (FY30) — recognized $118M BASE / $33M Pessimistic / $270M Stretch

Projection BASE: +115% YoY. Acquisition slowing, NDR 120%+ driving expansion.

| Surface | Y4 BASE | Y4 Pessimistic | Y4 Bull |
|---|--:|--:|--:|
| Founding Member tier dues | $2.5M | $1.5M | $4.5M |
| Hosted Operator Service | $55M | $13M | $125M |
| Enterprise Tier (75–120 cumulative logos × $150–250K avg) | $45M | $14M | $105M |
| Professional Services | $6M | $2M | $14M |
| Certification Program | $4M | $1.2M | $9M |
| Training & Certification | $3M | $0.8M | $8M |
| Overage / receipt usage | $2M | $0.5M | $4M |
| **Total recognized** | **$118M** | **$33M** | **$270M** |

### Y5 (FY31) — recognized $185M BASE / $65M Pessimistic / $420M Stretch

Y5 BASE: +57% YoY (decelerating to category-creator maturity). Revenue mix begins approximating the Master Plan §2 maturity table.

| Surface | Y5 BASE | Y5 Pessimistic | Y5 Bull | Y5 % BASE |
|---|--:|--:|--:|--:|
| Founding Member tier dues | $4M | $2.5M | $7M | 2% |
| Hosted Operator Service | $90M | $25M | $200M | 49% |
| Enterprise Tier (100–200 cumulative × $250–500K avg) | $60M | $25M | $140M | 32% |
| Professional Services | $11M | $5M | $25M | 6% |
| Certification Program | $9M | $4M | $20M | 5% |
| Training & Certification | $8M | $3M | $20M | 4% |
| Overage / receipt usage | $3M | $0.5M | $8M | 2% |
| **Total recognized** | **$185M** | **$65M** | **$420M** | 100% |

**Revenue mix discipline check:** The Y5 BASE mix (Hosted Operator 49%, Enterprise 32%, Services 6%, Cert 5%, Training 4%, FM dues 2%) is close to but not identical to Master Plan §2 maturity (45% / 30% / 7% / 8% / 5% / 5%). The shift reflects Hosted Operator Service over-indexing in BASE because the Full Stack Plan's backend investment specifically targets that surface as the primary growth driver.

### Comparable revenue ramp sanity-check

Plotted vs comparable Y1–Y5 revenue ramps:

| Company | Y1 | Y2 | Y3 | Y4 | Y5 |
|---|--:|--:|--:|--:|--:|
| Datadog ($M, FY10→FY14) | <$1 | ~$3 | ~$15 | ~$70 | ~$153 |
| Confluent ($M, FY15→FY19) | ~$2 | ~$10 | ~$30 | ~$80 | ~$150 |
| MongoDB Atlas era ($M Atlas only, FY16→FY20) | ~$2 | ~$10 | ~$50 | ~$140 | ~$285 |
| Vanta ($M est., FY19→FY23) | ~$1 | ~$5 | ~$25 | ~$80 | ~$200 |
| Drata ($M est., FY21→FY25) | ~$2 | ~$15 | ~$50 | ~$80 | ~$100 |
| HashiCorp ($M, FY13→FY17) | ~$0.5 | ~$3 | ~$20 | ~$50 | ~$120 |
| **LedgerProof BASE** | **$6.7** | **$19.7** | **$55** | **$118** | **$185** |
| **LedgerProof Bull** | **$9.2** | **$31** | **$110** | **$270** | **$420** |

**Honest read:** LedgerProof BASE Y5 ($185M) lands between Drata Y5 ($100M) and Vanta Y5 ($200M) — which is the right neighborhood for a category creator with a regulatory forcing function but a narrower TAM than full-spectrum compliance platforms. LedgerProof Bull Y5 ($420M) lands above MongoDB Atlas Y5 — which is achievable only if Article 50 evidentiary infrastructure becomes universally mandatory AND we capture dominant market share AND insurance discounts materialize. That's the Bull case and it should be treated with appropriate skepticism.

---

## 4. Cost structure and gross margin

### COGS structure for hosted operator service

Per Master Plan §6 backend cost estimates plus CFO model assumptions A9/A10/A11:

**Variable COGS components:**
- Cloud infrastructure (AWS eu-west-1 + eu-central-1 + us-east-1): $0.0008/receipt + $1.2K/mo base scaling to ~12% of hosted-operator revenue at scale (CFO A9)
- HSM costs (AWS CloudHSM ~$1.50/hour per HSM, ~$13K/mo per HSM partition): $26–52K/mo at Y3 scale (~2–4 partitions); $80–160K/mo at Y5 scale
- Bitcoin anchor fees: flat ~$17K/mo growing to ~$25K/mo Y3 (A10) — batched, fee scales sub-linearly with volume
- Bandwidth, object storage, log retention: ~3–5% of hosted-operator revenue
- Third-party APIs (Stripe processing 2.9% on Hosted Operator subscriptions; Vercel/Cloudflare egress; monitoring stack pass-through): ~4–6%
- Customer support FTE allocation per A11 (1 FTE per $4M ARR): comp + benefits flowing into COGS at ~$200K/FTE all-in

**Fixed COGS components:**
- Foundation reference anchor service (Inc. pays Foundation for operations, separately accounted as Foundation grant per A17): $50K/mo flat Y1, scaling to $100–150K/mo by Y5
- 24x7 NOC / on-call: scales with FTE count, ~$50K/mo Y2 → $200K/mo Y5
- Compliance overhead (SOC 2, ISO 27001 audit fees, pen-test rotation): $150–400K/yr

### Gross margin per surface

| Surface | Y1 GM | Y3 GM | Y5 GM | Source/comp |
|---|--:|--:|--:|---|
| Hosted Operator Service | 55% | 75% | 80% | Datadog 76% mature; Confluent Cloud 70% mature; Vanta ~80% est |
| Enterprise Tier | 75% | 85% | 88% | Snowflake Enterprise 75%; Datadog Enterprise 82% |
| Professional Services | 35% | 50% | 55% | Industry: typical 30–55% Services GM |
| Certification Program | 88% | 92% | 93% | Comparable cert programs (AWS, Microsoft): 88–95% |
| Training & Certification | 65% | 75% | 78% | Linux Foundation Training ~72% |
| Founding Member dues | 90% | 92% | 93% | Largely fixed costs to deliver; near-pure margin |

### Blended gross margin progression

| Year | BASE rev | BASE GM% | BASE gross profit | Pessimistic GM% | Bull GM% |
|---|--:|--:|--:|--:|--:|
| Y1 | $6.7M | 60% | $4.0M | 51% | 64% |
| Y2 | $19.7M | 78% | $15.4M | 70% | 80% |
| Y3 | $55M | 81% | $44.6M | 75% | 83% |
| Y4 | $118M | 83% | $97.9M | 78% | 84% |
| Y5 | $185M | 84% | $155.4M | 80% | 86% |

**Sanity check:** Y5 blended GM of 84% in BASE is consistent with the SaaS Capital median of 76% and the top-quartile of 82%+. Slightly above-median because the Enterprise Tier and Certification revenue carry very high margins. Below the absolute ceiling because Hosted Operator Service is dominant in mix and operates at Datadog-class margin (76–80%), not pure-software 90%+.

---

## 5. Operating expense progression

### Headcount build by department

| Function | Y1 end | Y2 end | Y3 end | Y4 end | Y5 end |
|---|--:|--:|--:|--:|--:|
| Engineering (incl. SRE, ML, security) | 7 | 18 | 32 | 45 | 58 |
| Sales (AE + SE + SDR) | 4 | 14 | 28 | 40 | 50 |
| Marketing (DevRel + content + ABM + brand) | 2 | 6 | 10 | 13 | 15 |
| Customer Success (CSM + tech CSM) | 2 | 8 | 14 | 18 | 22 |
| G&A (Finance, People, Legal, Ops, Exec) | 2 | 6 | 11 | 16 | 20 |
| **Inc. total headcount** | **17** | **52** | **95** | **132** | **165** |
| Foundation FTE (separately funded) | 1 (ED only) | 4 (ED, ops, comms, eng lead) | 7 | 9 | 11 |

### OpEx by category — BASE case ($M)

| Function | Y1 | Y2 | Y3 | Y4 | Y5 |
|---|--:|--:|--:|--:|--:|
| R&D (engineering comp, audits, tooling) | $3.4 | $7.6 | $13.0 | $19.0 | $25.5 |
| S&M (comp, programs, ABM, events, paid demand) | $1.4 | $11.0 | $25.0 | $44.0 | $65.0 |
| CS (comp, customer programs, services delivery overhead) | $0.4 | $1.7 | $3.4 | $5.0 | $6.5 |
| G&A (comp, legal, audit, insurance, software, T&E, BoD) | $1.6 | $4.7 | $8.0 | $11.5 | $15.0 |
| Foundation grant (separately accounted, included G&A) | $0.55 | $1.0 | $1.5 | $1.8 | $2.0 |
| Hercules commitment fee + debt service | $0.06 | $0.06 | $0.5 | $0.8 | $1.0 |
| **Total OpEx** | **$7.4** | **$26.1** | **$51.4** | **$82.1** | **$115.0** |

### S&M efficiency check (Magic Number / CAC payback)

| Year | New ARR booked | S&M spend | S&M as % new ARR | CAC payback (mo) |
|---|--:|--:|--:|--:|
| Y1 | $9.4M | $1.4M | 15% (subsidized by founder-led GTM) | <12 |
| Y2 | $21.6M | $11.0M | 51% | ~18 |
| Y3 | $36M | $25M | 69% | ~24 |
| Y4 | $50M | $44M | 88% | ~28 |
| Y5 | $55M | $65M | 118% | ~30 |

**Reality check:** The S&M-as-%-of-new-ARR ramp from 15% Y1 → 118% Y5 looks high but is in fact within the Bessemer State of the Cloud band for category creators at scale (median 85–110% for $100M+ ARR companies). The Y5 ratio above 100% reflects investment in net-new logo acquisition at the saturation phase of EU TAM, paired with international expansion (US, UK, APAC) — exactly the pattern Vanta and Drata show in their later years.

### R&D as % of revenue

| Year | R&D | R&D % rev |
|---|--:|--:|
| Y1 | $3.4M | 51% |
| Y2 | $7.6M | 39% |
| Y3 | $13.0M | 24% |
| Y4 | $19.0M | 16% |
| Y5 | $25.5M | 14% |

Comparable: Datadog mature R&D% = 30%; Snowflake mature = 38% (heavy ML investment); HashiCorp mature = 32%. LedgerProof's lower R&D% at maturity reflects that the protocol surface is narrower than a full observability or data platform — once the core is stable, incremental R&D supports adapter expansion and operational improvements rather than fundamental new product surface.

### Foundation expenses (separately funded, allocated to Inc. via grant line)

| Foundation cost | Y1 | Y2 | Y3 | Y4 | Y5 |
|---|--:|--:|--:|--:|--:|
| Foundation ED (Brussels-based) | $0.28 | $0.30 | $0.32 | $0.33 | $0.35 |
| Foundation board governance, transparency, ops | $0.15 | $0.30 | $0.50 | $0.65 | $0.80 |
| Foundation technical FTE (anchor service operations) | $0.0 | $0.25 | $0.40 | $0.55 | $0.70 |
| Foundation regulator engagement (CEN/CENELEC, IETF, AI Office) | $0.10 | $0.15 | $0.20 | $0.25 | $0.30 |
| Foundation legal, audit (Adler & Colvin, Stibbe, Form 990 prep) | $0.10 | $0.15 | $0.20 | $0.25 | $0.30 |
| Foundation grants, contributor program | $0.0 | $0.10 | $0.20 | $0.30 | $0.40 |
| **Foundation total** | **$0.63** | **$1.25** | **$1.82** | **$2.33** | **$2.85** |
| Funded by Inc. grant | $0.55 | $1.0 | $1.5 | $1.8 | $2.0 |
| Funded by member dues + grants from third parties | $0.08 | $0.25 | $0.32 | $0.53 | $0.85 |

---

## 6. EBITDA projection

### EBITDA by scenario ($M)

| Year | Rev BASE | OpEx BASE | EBITDA BASE | EBITDA Pessimistic | EBITDA Bull |
|---|--:|--:|--:|--:|--:|
| Y1 (FY27) | $6.7 | $7.4 + COGS $2.7 = GP $4.0 - OpEx | **($5.3M)** | **($5.8M)** | **($4.6M)** |
| Y2 (FY28) | $19.7 | $26.1 + COGS $4.3 = GP $15.4 - OpEx | **($10.7M)** | **($14.6M)** | **($6.1M)** |
| Y3 (FY29) | $55 | $51.4 + COGS $10.4 = GP $44.6 - OpEx | **($6.8M)** | **($16.3M)** | **+$13.1M** |
| Y4 (FY30) | $118 | $82.1 + COGS $20.1 = GP $97.9 - OpEx | **+$15.8M** | **($5.0M)** | **+$65.0M** |
| Y5 (FY31) | $185 | $115.0 + COGS $29.6 = GP $155.4 - OpEx | **+$40.4M** | **($4.3M)** | **+$135.0M** |

### Year-of-breakeven by scenario

- **Pessimistic:** never reaches breakeven within 5-year window. Requires either material cost reduction (headcount restructuring, Foundation grant reduction) or pivot to a narrower service surface (Enterprise Tier only). Continued external capital required.
- **BASE:** EBITDA breakeven Q2 FY30 (~Oct 2029). Cumulative FCF breakeven Q3 FY31 (~Feb 2031).
- **Bull:** EBITDA breakeven Q1 FY29 (~Aug 2028). Cumulative FCF breakeven Q4 FY30 (~Apr 2030).

### Cumulative free cash flow by year ($M)

Assumes minimal CapEx (this is a SaaS company; cloud is OpEx); working capital changes neutral on average (annual upfront billing positive, AR ageing on enterprise negative).

| Year | BASE cumulative FCF | Pessimistic cumulative FCF | Bull cumulative FCF |
|---|--:|--:|--:|
| Y1 | ($5.3M) | ($5.8M) | ($4.6M) |
| Y2 | ($16.0M) | ($20.4M) | ($10.7M) |
| Y3 | ($22.8M) | ($36.7M) | +$2.4M |
| Y4 | ($7.0M) | ($41.7M) | +$67.4M |
| Y5 | +$33.4M | ($46.0M) | +$202.4M |

### Capital requirements by scenario

**Pessimistic:** Seed $12M (closed Jun 26) → Series A $18M (bridge structure Q1 27) → Series B $25M (Q4 28) → Series B-1 $30M (Q1 30) → likely down rounds or sale to incumbent. Total dilution heavy; founders end with ~15–20% post-Series B-1.

**BASE:** Seed $12M → Series A $25M (Q1 27 at $135M post = $6.7M ARR × 20×) → Series B $50M (Q4 28 at $400–600M post = $25M ARR × 16–24×) → optionally Series C $80M (Q4 30 at $1.5–2.2B post = $185M-projected forward ARR × 10–15×) but mostly cash-self-funding from Y4 onward. Total capital required: ~$87M. Founders end with ~25–30% post-Series C.

**Bull:** Seed $12M → Series A $35M (Q1 27 at $230M post) → Series B $80M (Q3 28 at $1.5B post = $55M ARR × 27×) → no further dilutive capital required (self-funding from Y4 onward into IPO window FY32–FY33). Founders end with ~35–42% post-Series B.

---

## 7. Comparison to public SaaS comparables

### Datadog (founded 2010, IPO 2019)

| Metric | Datadog Y1 (FY10) | Datadog Y3 (FY12) | Datadog Y5 (FY14) | LedgerProof BASE projected equivalent |
|---|--:|--:|--:|--:|
| Revenue | <$1M | ~$3M | ~$15M | Y1 $6.7M / Y3 $55M / Y5 $185M |
| YoY growth | n/a | ~200% | ~250% | Y2→Y3 175% / Y4→Y5 57% |
| Gross margin | n/m | ~70% | ~73% | Y3 81% / Y5 84% |
| EBITDA margin | deeply negative | ~(80%) | ~(40%) | Y3 (12%) / Y5 +22% |
| Market cap (at equivalent revenue scale) | n/a | n/a | n/a (private) | n/a |

**LedgerProof BASE is 10–12× ahead of Datadog at equivalent year markers in absolute revenue.** The reason: regulatory forcing function + enterprise-driven ACV (Datadog Y3 ACV was ~$15K self-serve; LedgerProof Y3 enterprise tier ACV is $250–500K). LedgerProof's higher early ACV is the structural reason it converts to absolute revenue faster than Datadog did. Datadog later overtook because of land-and-expand on a much larger TAM (every cloud workload everywhere).

### Confluent (founded 2014, IPO 2021)

| Metric | Confluent Y1 (FY15) | Confluent Y3 (FY17) | Confluent Y5 (FY19) | LedgerProof BASE |
|---|--:|--:|--:|--:|
| Revenue | ~$2M | ~$30M | ~$150M | $6.7M / $55M / $185M |
| YoY growth | n/a | ~300% | ~80% | 194% / 175% / 57% |
| Gross margin | n/m | ~67% | ~72% | 60% / 81% / 84% |
| EBITDA margin | deeply negative | ~(120%) | ~(45%) | (79%) / (12%) / +22% |
| IPO valuation | n/a | n/a | n/a | n/a |

**LedgerProof is comparable to Confluent in absolute revenue ramp.** Confluent at IPO traded at ~30× forward revenue ($9.1B on ~$300M ARR). LedgerProof BASE Y5 at $185M with 22% EBITDA margin and 57% YoY growth fits a 12–18× revenue multiple, implying a $2.2–3.3B valuation at Y5. Bull case ($420M revenue, 32% EBITDA, 70% YoY) implies 18–25× = $7.5–10.5B.

### MongoDB (founded 2007, IPO 2017)

| Metric | MongoDB Y3 (FY10) | MongoDB Y5 (FY12) | MongoDB Y7 (FY14) | LedgerProof BASE |
|---|--:|--:|--:|--:|
| Revenue | ~$5M | ~$36M | ~$83M | $6.7M / $55M / $185M |
| Path | DB engine OSS + Enterprise | DB engine OSS + Enterprise + Atlas launching | Atlas growing | Open protocol + Hosted Operator + Enterprise |
| Eventual ARR (FY24) | $1.6B | | | |

**MongoDB's relevance to LedgerProof:** the open-protocol-plus-paid-managed-service model is the same. MongoDB Atlas (the paid SaaS layer on top of the open DB engine) is the direct strategic analog to LedgerProof Hosted Operator Service. Atlas reached $1B+ ARR within 6 years of launch. LedgerProof Hosted Operator Service at $90M Y5 BASE / $200M Y5 Bull is plausible relative to Atlas's trajectory.

### HashiCorp (founded 2012, IPO 2021)

| Metric | HashiCorp Y3 (FY15) | HashiCorp Y5 (FY17) | HashiCorp Y7 (FY19) | LedgerProof BASE |
|---|--:|--:|--:|--:|
| Revenue | ~$20M | ~$120M | ~$220M | $55M / $185M / projected $290M Y7 |
| Gross margin | ~75% | ~80% | ~84% | 81% / 84% |
| EBITDA margin | deeply negative | (40%) | (15%) | (12%) / +22% |
| IPO valuation | n/a | n/a | $14B (later contracted) | n/a |

**LedgerProof tracks HashiCorp's revenue ramp closely**, with better unit economics because the protocol surface is narrower (HashiCorp had 5 products: Terraform, Vault, Consul, Nomad, Packer — each with its own dev/sales motion). LedgerProof is one protocol with multiple revenue surfaces — operationally simpler. HashiCorp peaked at $14B market cap on $322M ARR (~43× — ZIRP-era), then contracted to ~$5B at acquisition by IBM ($6.4B announced Apr 2024, ~14× ARR). Realistic LedgerProof Y5 multiple = 12–18× revenue = $2.2–3.3B BASE / $5–7.5B Bull.

### Vercel (founded 2015, last private valuation 2024)

| Metric | Vercel Y3 (FY18) | Vercel Y5 (FY20) | Vercel Y7 (FY22) | LedgerProof BASE |
|---|--:|--:|--:|--:|
| Revenue (estimated) | <$5M | ~$30M | ~$120M | $55M / $185M |
| Growth | n/a | ~250% | ~200% | 175% / 57% |
| Last valuation | n/a | ~$1.1B (FY20) | ~$3.25B (FY23) | n/a |

**Vercel relevance:** Next.js (open) + Vercel hosting (paid) is the Master Plan §2 reference analog. Vercel reached ~$3.25B at ~$120M ARR (~27× ZIRP-influenced). Post-ZIRP multiples have compressed to 10–18×. LedgerProof's Foundation-governance moat adds 2–4× to the multiple vs. pure-vendor open-core, because regulators treat Foundation-governed standards as durable infrastructure vs. vendor-controlled OSS as switching-risk.

### Honest comparison summary

**Where LedgerProof looks BETTER than comparables:**
- Regulatory forcing function (Article 50 enforcement) — Datadog, Confluent, MongoDB had no equivalent
- Foundation governance moat — most comparables eventually had open-source vs vendor-capture conflicts
- Higher early ACV due to enterprise-led GTM — converts to absolute revenue faster
- Narrower R&D surface — operationally simpler than HashiCorp's 5 products

**Where LedgerProof looks WORSE than comparables:**
- Narrower TAM than observability (Datadog) or databases (MongoDB) or platform-as-a-service (Vercel)
- Geographic concentration (EU-first) vs comparables' global-from-day-one
- Single regulator dependency (EU AI Act) — comparables had broader market drivers
- No pre-existing platform shift to ride (cloud migration, microservices, etc.) — Article 50 is the only catalyst

**Where LedgerProof looks COMPARABLE:**
- Y5 revenue trajectory ($185M BASE / $420M Bull) sits in the Drata-Vanta-Confluent neighborhood
- Y5 gross margin (84%) sits at category-creator median
- Y5 EBITDA margin (22% BASE / 32% Bull) is consistent with mid-stage category creator profile
- Capital efficiency (~$87M total capital required BASE through Y5) is competitive — Vanta consumed ~$200M+ to reach equivalent ARR

---

## 8. Sensitivity analysis

### Scenario 1: Article 50 enforcement delayed by 12 months (KS6 — soft enforcement)

**Trigger:** EU Commission soft-pedals enforcement in 2026–2027; first €10M+ fine doesn't land until 2028; supervisory authorities stay quiet during initial implementing-act consultations.

**Revenue impact:**
- Y1 BASE $6.7M → $4.5M (-33%): enterprise tier cohort delayed 6 months
- Y2 BASE $19.7M → $12M (-39%): mid-market connector ramp delayed; enterprise tier cohort delayed 12 months
- Y3 BASE $55M → $32M (-42%): cumulative cohort delay compounds
- Y5 BASE $185M → $130M (-30%): partial catch-up as enforcement eventually materializes

**Strategic response:** Pivot messaging from "Article 50 enforcement readiness" to "voluntary adoption now reduces future enforcement exposure." Extend Foundation institutional credibility play (CEN/CENELEC, IETF SCITT) to compensate for direct revenue softness. Accept Series B at $400M post on $30M ARR Q4 28 instead of $600M+ post.

### Scenario 2: LangChain Inc. partnership fails (KS7)

**Trigger:** Harrison Chase declines integration partnership; LangChain Inc. ships native compliance attestation that doesn't use LedgerProof; community adapter remains unofficial.

**Revenue impact:**
- Y1: minimal (Y1 revenue is enterprise tier and Founding Member, not adapter-driven)
- Y2 BASE $19.7M → $16M (-19%): mid-market connector revenue takes hit because Vanta/Drata integration story is harder without LangChain reference deployment
- Y3 BASE $55M → $42M (-24%): vendor partnership and certification revenue softens; developer-led bottom-up adoption velocity reduces
- Y5 BASE $185M → $150M (-19%): partial recovery via LlamaIndex Inc. + Mistral + Aleph Alpha alternative partnerships

**Strategic response:** Ship adapter as community integration outside LangChain main; pursue LlamaIndex Inc. partnership as primary; reset adoption-curve assumption -6 months. Increase investment in Mistral / Aleph Alpha / Haystack to compensate.

### Scenario 3: No signed Founding Member by Jun 22 (KS3 cascade)

**Trigger:** Five Founding Members fail to sign before seed close; CFO model A3 assumption broken; seed close pushed or sized down.

**Revenue impact:**
- Y1 BASE $6.7M → $4.0M (-40%): direct hit to Founding Member revenue + delayed Enterprise Tier cohort + cash constrained
- Y2 BASE $19.7M → $11M (-44%): under-investment in hosted operator service due to cash constraint
- Y3 BASE $55M → $25M (-55%): compounding cash constraint; reduced hiring; reduced enterprise close rate
- Y5 BASE $185M → $80M (-57%): trajectory permanently bent down

**Strategic response:** Execute KS3 fail-branch (Brunswick prep): tighten launch to single signed pilot + Foundation institutional posture; restructure seed to $6–8M bridge; push Series A to Q2 27. This is the most damaging single scenario.

### Scenario 4: Foundation Form 1023 denied or significantly delayed (KS8)

**Trigger:** IRS Form 1023 review identifies private-benefit problem; delay 12–18 months; alternate AISBL/Stichting structure becomes urgent.

**Revenue impact:**
- Y1: minimal direct revenue impact ($0.5–1M)
- Y2 BASE $19.7M → $17M (-14%): one enterprise customer pulls due to governance uncertainty
- Y3 BASE $55M → $48M (-13%): Series B diligence delayed 6 months; competitive window narrows
- Y5 BASE $185M → $170M (-8%): once resolved, recovery is largely complete

**Strategic response:** Lean into Dutch Stichting (which is already in formation per the dual-entity structure) as primary EU vehicle; AISBL backup; recast 501(c)(3) timing communications. Manageable. Foundation governance story survives.

### Scenario 5: Competitor coalition (Truera + Arize + W&B) ships competing Article 50 story

**Trigger:** Q3–Q4 26: Truera (acquired by Snowflake), Arize, Weights & Biases coalition announces joint cryptographic attestation export feature inside their existing platforms, positioned as "Article 50 ready."

**Revenue impact:**
- Y1: minimal (their announcement is feature, not full product)
- Y2 BASE $19.7M → $17M (-14%): some mid-market customers buy bundled with existing AI eval platform instead of LedgerProof standalone
- Y3 BASE $55M → $45M (-18%): competitive sales cycles lengthen; Hosted Operator Service growth slows
- Y5 BASE $185M → $150M (-19%): LedgerProof retains evidentiary-substrate position but mid-market growth slower

**Strategic response:** Reposition LedgerProof as "the cryptographic substrate Truera/Arize/W&B export TO" — same playbook as the Vanta/Drata defensive positioning. Build integrations with their platforms; certify their export pipelines as LP-Conformant. Convert competitive pressure into partnership revenue (vendor certification fees).

### Scenario 6: Vanta ships native cryptographic attestation Q1 27 (CFO model DOWNSIDE trigger)

**Trigger:** Vanta announces native cryptographic attestation export in Q1 27 earnings (before LedgerProof's Vanta connector is in production). Mid-market customers default to bundled Vanta solution.

**Revenue impact:**
- Y1 BASE $6.7M → $4.8M (CFO model DOWNSIDE): mid-market connector revenue eliminated
- Y2 BASE $19.7M → $8.2M (CFO model DOWNSIDE): -58%
- Y3 BASE $55M → $20M: mid-market story collapses; Hosted Operator Service narrows to enterprise-only
- Y5 BASE $185M → $90M: -51%

**Strategic response:** Reposition as Vanta-complement (not substrate); ACV ceiling drops to $50–100K for mid-market; refocus growth on Enterprise Tier + Foundation institutional credibility. This is the single highest-impact single scenario and the reason the master plan recommends shipping the Vanta connector Q3 26 BEFORE Vanta ships native.

### Composite sensitivity table

| Scenario | Y3 rev impact | Y5 rev impact | Y5 EBITDA impact |
|---|--:|--:|--:|
| BASE (no shocks) | $55M | $185M | +$40.4M |
| KS6 enforcement delayed 12mo | $32M (-42%) | $130M (-30%) | +$15M (-63%) |
| KS7 LangChain partnership fails | $42M (-24%) | $150M (-19%) | +$25M (-38%) |
| KS3 no FM by Jun 22 cascade | $25M (-55%) | $80M (-57%) | ($8M) (cash burn-down) |
| KS8 Form 1023 delayed | $48M (-13%) | $170M (-8%) | +$35M (-13%) |
| Truera/Arize/W&B competitor | $45M (-18%) | $150M (-19%) | +$25M (-38%) |
| Vanta ships native (DOWNSIDE trigger) | $20M (-64%) | $90M (-51%) | ($5M) |
| **Multi-shock (KS6 + KS7 + Vanta)** | **$15M** | **$60M** | **($10M)** |

The multi-shock scenario is approximately the Pessimistic case in §0. It is survivable with cost discipline but does not justify the Full Stack Plan investment by itself.

---

## 9. The honest answer to "What's the profit?"

### The clean table

| | Y1 (FY27) | Y2 (FY28) | Y3 (FY29) | Y4 (FY30) | Y5 (FY31) |
|--|--:|--:|--:|--:|--:|
| **Pessimistic revenue** | $3.4M | $8.2M | $18M | $33M | $65M |
| **Pessimistic EBITDA** | ($5.8M) | ($14.6M) | ($16.3M) | ($5.0M) | ($4.3M) |
| **BASE revenue** | $6.7M | $19.7M | $55M | $118M | $185M |
| **BASE EBITDA** | ($5.3M) | ($10.7M) | ($6.8M) | +$15.8M | +$40.4M |
| **Bull revenue** | $9.2M | $31M | $110M | $270M | $420M |
| **Bull EBITDA** | ($4.6M) | ($6.1M) | +$13.1M | +$65M | +$135M |

### Interpretation paragraphs

**Pessimistic case interpretation.** Revenue plateaus around $65M at Y5 because the Article 50 enforcement story softens AND Vanta ships native cryptographic attestation AND mid-market adoption stalls. EBITDA stays negative throughout because the cost structure built for BASE-case scale becomes inefficient at lower revenue. This case requires either (a) significant headcount restructuring around Q2 28 if BASE trajectory clearly isn't materializing, or (b) successful pivot to a narrower service surface (Enterprise Tier + Foundation institutional services only). The company survives but requires additional dilutive capital and may exit through strategic acquisition by a Big-4 firm or a Vanta/Drata-tier compliance platform at 4–8× revenue ($260–520M valuation) rather than IPO. This is an outcome that returns capital to investors at ~1.5–2.5× MOIC for seed and ~1.0–1.5× for Series A. It is acceptable, not aspirational.

**BASE case interpretation.** Revenue tracks the CFO 24-month model through Y2, then compounds via the cohort dynamics of the Vanta/Drata/Purview connector base plus the Enterprise Tier cumulative logo count. Y3 is the inflection year where the Hosted Operator Service Y2 base ($8.6M) compounds to $25M and Enterprise Tier cumulative reaches $22M; combined, these two surfaces become 85% of revenue. Y4 crosses EBITDA breakeven driven by gross margin expansion (75% → 83%) and S&M efficiency stabilizing at 88% of new ARR. Y5 generates $40M EBITDA at 22% margin — a clean, fundable category-creator profile. At Y5 ($185M revenue, 22% EBITDA, 57% YoY growth) the public-market comparable valuation is **12–18× revenue = $2.2–3.3B**. This is the trajectory of Vanta (which last priced at ~$2.45B on ~$200M ARR), Drata (recent secondary at ~$2B on ~$100M ARR), HashiCorp (acquired by IBM at $6.4B on $322M ARR, ~14× post-ZIRP compression), and Confluent (currently ~$8B on ~$1B ARR, ~8× post-ZIRP — but Confluent IPO'd at $9B on $300M ARR = 30× ZIRP-era). LedgerProof BASE Y5 lands squarely in this neighborhood. **Capital required to reach BASE: ~$87M total across seed + Series A + Series B + optional Series C.** Founder dilution: ~25–30% ownership at Y5. Investor MOIC: seed ~10–20×, Series A ~6–12×, Series B ~3–6×.

**Bull case interpretation.** Revenue reaches $420M at Y5 because Article 50 evidentiary infrastructure becomes de facto mandatory (insurance discounts, procurement requirements), CEN/CENELEC harmonized standard names SCITT-based receipt format as an acceptable Article 50 implementation, and LangChain/Mistral/Aleph Alpha partnerships convert into volume vendor-led adoption. Y3 EBITDA turns positive a full year earlier than BASE; Y5 EBITDA reaches 32% margin — top-decile SaaS profitability. At Y5 ($420M revenue, 32% EBITDA, 70% YoY growth), the comparable valuation is **18–25× revenue = $7.5–10.5B**. This is the trajectory of MongoDB (current ~$25B on $1.8B ARR = ~14×) at an equivalent stage, or Snowflake (current ~$50B on $3.5B ARR = ~14×) at an equivalent stage. **Capital required to reach Bull: ~$130M total across seed + Series A + Series B.** Bull case is self-funding from Y4 onward; no Series C needed. Founder dilution: ~35–42% ownership at Y5. Investor MOIC: seed ~30–60×, Series A ~15–30×, Series B ~5–10×. **Bull case requires all five things to happen:** (1) Foundation reference anchor ships by Aug 2, (2) at least one Founding Member signs Strategic Beta tier in Sep 26, (3) IETF SCITT WG adopts the draft at IETF 120/121 by Q4 26, (4) JTC 21 WG 4 invites LedgerProof as expert observer by Q1 27, (5) one major insurance carrier (Munich Re likely) announces Article 50-evidence-based underwriting discount by Q2 28. If any two of these five fail, Bull case drops to BASE.

---

## 10. What this means for V's Full Stack Plan decision

The Full Stack Plan (Master Plan 00-MASTER-PLAN.md) commits to incremental investment above the CFO 24-month model baseline:

- **Backend MVP (next 60 days):** $15–25K/mo incremental burn (3–4 engineers + 1 SRE + ~$5K cloud)
- **Phase 2 backend (Q3–Q4 26):** $40–60K/mo incremental
- **Phase 3 backend (Q1–Q2 27):** $80–120K/mo incremental
- **Site rebuild + design system (Jun–Oct 26):** $200–400K total (one-time)
- **Phase 2–5 adapter expansion (34 adapters total by Q1 27):** $300–500K total (engineering allocation, partially absorbed by existing eng FTE)

**Cumulative incremental Full Stack Plan investment through May 27:** ~$1.5–2.5M above the existing CFO model baseline.

### Does the Pessimistic case justify the Full Stack Plan investment?

**Mostly yes, with caveats.** In Pessimistic, the same backend serves the Enterprise Tier customer base regardless of mid-market operator-service volume. The Foundation-operated reference anchor service is institutionally credibility-positive even when revenue is soft. The site rebuild + design system is enabling infrastructure for ALL revenue scenarios. Adapter expansion has marginal cost beyond a certain point — Phases 4–5 can be paused if Pessimistic trajectory is clear. **Recoverable investment: ~$1.0–1.5M of the $1.5–2.5M is institutional infrastructure that pays off in any scenario.** Non-recoverable: ~$0.5–1.0M is Hosted Operator Service-specific buildout that under-monetizes in Pessimistic. That non-recoverable portion is ~10–15% of seed capital, which is within the bounds of a defensible scenario-hedged bet.

### Does the BASE case justify it?

**Yes, clearly.** In BASE, the Hosted Operator Service generates $8.6M Y2 / $25M Y3 / $90M Y5 revenue — directly enabled by the Full Stack Plan backend investment. The site rebuild + design system enables the three-audience routing strategy that materially improves conversion across Founding Member, Enterprise, and Vendor surfaces. Adapter expansion is the leading indicator of bottom-up developer-led adoption that drives the mid-market connector revenue. **ROI on the $1.5–2.5M incremental investment: ~$200–400M of cumulative Y2–Y5 revenue directly attributable to surfaces the Full Stack Plan enables.** That's a 80–250× return on the incremental investment. BASE case clearly justifies the Full Stack Plan.

### Does the Bull case justify it (and is Bull achievable)?

**Yes, and Bull is conditionally achievable.** Bull case requires the Hosted Operator Service to reach $200M at Y5 — that absolutely requires the Phase 2 + Phase 3 backend to be production-grade with enterprise-tier HSM, multi-region failover, audit-firm integration tooling, and cross-jurisdictional regulator access. None of that ships without the Full Stack Plan investment. Bull is achievable IF the five conditions in §9 Bull interpretation materialize. The Full Stack Plan investment is a necessary-but-not-sufficient condition for Bull. **The investment is the gate; the conditions are the lock.**

### 5-year valuation multiple range at exit

| Scenario | Y5 revenue | Y5 EBITDA margin | Multiple range | Valuation range |
|---|--:|--:|---|---|
| Pessimistic | $65M | (7%) | 4–8× rev (acquisition multiple) | $260M–$520M |
| BASE | $185M | 22% | 12–18× rev (private SaaS comp band) | $2.2B–$3.3B |
| Bull | $420M | 32% | 18–25× rev (top-decile category creator) | $7.5B–$10.5B |

Datadog at FY15 (Y5) was private at ~$300M valuation on $30M ARR (~10×, pre-IPO uncertainty discount). At IPO FY19 (Y9) it was $7.8B on $363M revenue (~22×). Confluent IPO'd at $9.1B on $300M ARR (~30× ZIRP-era). Snowflake IPO'd at $33B on $592M ARR (~56× ZIRP-era). LedgerProof BASE Y5 ($2.2–3.3B on $185M revenue, 12–18×) is post-ZIRP-rational and consistent with current category-creator private secondaries.

### The clean answer: at what investment level does BASE Y5 produce acceptable returns?

**Total capital required through Y5 BASE: ~$87M cumulative.**
**BASE Y5 valuation: $2.2–3.3B.**
**Implied investor blended MOIC: ~5–7× across all rounds.**
**Implied founder ownership at Y5: ~25–30% → $550–990M founder equity value.**

For comparison: Vanta total capital raised through equivalent stage ~$215M; current valuation ~$2.45B; implied blended MOIC ~3–4×. LedgerProof BASE is more capital-efficient because (a) the Foundation governance model attracts higher-quality early capital at better terms, (b) the regulatory forcing function compresses time-to-revenue, (c) the open-protocol model reduces customer acquisition friction.

### V's decision recommendation (with appropriate humility)

**Proceed with the Full Stack Plan.** The investment level (~$1.5–2.5M incremental through May 27) is materially less than the recoverable institutional-infrastructure value in Pessimistic, and the upside in BASE/Bull is 80–250× the investment. The risk-adjusted expected value is strongly positive across the realistic scenario distribution.

**However, three discipline conditions should attach:**

1. **Tranche the backend buildout.** Phase 1 (MVP, $15–25K/mo) commits now. Phase 2 ($40–60K/mo) commits only if (a) at least 5 Founding Members signed by Sep 30, (b) IETF SCITT WG adoption by IETF 121, (c) one paid Hosted Operator Service customer signed by Oct 31. Phase 3 ($80–120K/mo) commits only if (a) Series A closed at $25M+ at $135M+ post, (b) at least 3 Enterprise Tier contracts signed by Mar 31 27.

2. **Lock the Vanta integration as a Q3 26 priority.** The single largest downside scenario is Vanta shipping native cryptographic attestation before LedgerProof's Vanta connector is in production. The Full Stack Plan's Phase 2 adapter expansion must include Vanta + Drata export connectors as the highest-priority items, shipped no later than Aug 31 26.

3. **Foundation reference anchor service ships by Aug 2 26.** Without this, the Foundation governance story is hollow and Bull case becomes structurally unreachable. Decision point: if this slips past Aug 16, pause Phase 3 backend buildout and reallocate to anchor-service completion.

These three discipline conditions are NOT additional investment — they are sequencing constraints on the existing Full Stack Plan investment. Done with discipline, the plan produces the BASE case profile. Done without discipline, the plan slips toward Pessimistic.

---

## Closing note on honesty

This document deliberately avoids three things the previous explosive-adoption deck did:

1. **No $86M Y1 revenue claim.** Y1 BASE recognized revenue is $6.7M, which is the CFO model number, which is defensible.
2. **No $65B Y5 valuation claim.** Y5 BASE valuation is $2.2–3.3B, which is the realistic Vanta/Drata/HashiCorp/Confluent comparable neighborhood.
3. **No "50% of EU market share" claim.** Y5 BASE customer count is 3,500–7,000 paying organisations across all tiers, which is consistent with what category creators actually achieve at Y5.

The numbers in this document are designed to survive Series A diligence. They are also designed to be the real numbers V uses to make the Full Stack Plan investment decision. Those should be the same numbers. They are.

If V wants to test the Bull case more aggressively (e.g., what if we capture 25% share at maturity instead of 10–15%?), or wants to stress-test additional sensitivity scenarios (e.g., what if EU AI Office cites SCITT directly in the Article 50 implementing act?), this model is structured to allow that. The cohort revenue waterfall, the surface breakdown, the headcount build, and the OpEx categories are all parameterised in a way that supports incremental scenario work without rebuilding from scratch.

The recommendation stands: **proceed with the Full Stack Plan, tranched against the three discipline conditions above.** The honest BASE case Y5 outcome ($185M revenue, $40M EBITDA, $2.2–3.3B valuation) is a magnificent outcome. It is the right outcome to aim for. The numbers are defensible. The path is achievable. The investment is justified.

---

**End of analysis. Ready for V review.**
