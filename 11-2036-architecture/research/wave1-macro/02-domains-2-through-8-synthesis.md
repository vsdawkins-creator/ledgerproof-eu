# Wave 1 Research Synthesis — Domains 2 through 8

**LedgerProof Foundation — 2036 Architecture Research Dossier, Wave 1 (Consolidated)**
*Prepared: May 20, 2026. Sources verified via WebSearch on the date of preparation.*

---

## DOMAIN 2 — IETF SCITT Working Group + cryptographic provenance standards

The **Supply Chain Integrity, Transparency, and Trust (SCITT)** working group at IETF is the established home for cryptographic provenance standards in the supply-chain and authorship-attestation space. Key facts:

### Current draft state, May 2026

- **`draft-ietf-scitt-architecture-22`** (working-group draft, expires April 13, 2026 — needs renewal soon) defines the SCITT architecture: signed statements about supply-chain commodities, registered with a transparency service, anchored on a ledger, with append-only inclusion proofs.
- **`draft-kamimura-scitt-vcp-01`** (individual draft, expires June 26, 2026) — **SCITT Profile for Financial Trading Audit Trails: VeritasChain Protocol (VCP)**. *This is the critical finding.* VeritasChain has already published a SCITT profile draft. The IETF home for our LPR work is established, the profile-extension pattern is demonstrated, and the natural sibling to LPR is VCP. **Our IETF -00 submission should be filed as `draft-dawkins-scitt-lpr-00`** — a SCITT profile, not a standalone draft.

### Working group scope

SCITT explicitly reuses **COSE** (CBOR Object Signing and Encryption) and **RATS** (Remote Attestation Procedures) work, and coordinates with W3C, ISO, OpenSSF, and the Trusted Computing Group. The protocol's signed-statement model is closely aligned with our existing LPR receipt structure.

### Architectural implication

**The LPR specification should be repositioned as a SCITT profile for cryptographic document and AI-agent-action provenance** with Bitcoin anchoring as the named transparency-service substrate. This positions LedgerProof as a SCITT participant alongside VeritasChain, not in competition with it. The Foundation contributes the Bitcoin-anchor SCITT profile while VeritasChain's VCP handles financial-trading audit trails — composable, non-overlapping.

### Sources
- [draft-ietf-scitt-architecture (IETF datatracker)](https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/)
- [draft-kamimura-scitt-vcp-01 — SCITT Profile for Financial Trading Audit Trails: VCP](https://datatracker.ietf.org/doc/draft-kamimura-scitt-vcp/01/)
- [SCITT Working Group Charter](https://datatracker.ietf.org/group/scitt/about/)
- [SCITT GitHub Organization](https://github.com/ietf-scitt)

---

## DOMAIN 3 — AI agent economy growth forecasts 2026-2036

### Market sizing

- **AI agents market 2030 forecasts**: $50.31B (Grand View Research, 45.8% CAGR), $52.62B (MarketsandMarkets), $47.1B (LinkedIn estimate). Broader "agentic economy" forecasts reach $1.5T by 2030 including enterprise productivity, consumer service, and specialized professional agents.
- **McKinsey**: Generative AI (the substrate of agents) contributes **$2.6T–$4.4T in annual global value** at maturity; up to **$13T in additional global economic output by 2030**.
- **Gartner**: By 2028, **15% of work decisions** are made autonomously by agentic AI (vs. 0% in 2024). By 2030, **20% of monetary transactions** are programmable with terms-of-use machine-readable. By 2030, **50% of cross-functional supply-chain solutions** use intelligent agents to autonomously execute decisions.

### Agent-to-agent commerce

The agent-to-agent (A2A) commerce layer is in active formation:
- **Google Agent2Agent (A2A)** protocol — published April 2025.
- **Anthropic Model Context Protocol (MCP)** — universal agent-tool transport, growing rapidly.
- **ERC-8004 Trustless Agents** — Ethereum/EVM agent identity layer, live Jan 29, 2026.
- **OpenAI Operator** — agent-action interface, public early 2025.

**Volume forecast**: by 2030, agent-mediated transactions are projected to represent meaningful fractions of programmable commerce. Specific 2030 transaction-volume numbers vary, but the consensus direction is **trillions of agent-mediated micro-transactions per day** by mid-decade.

### Architectural implication

LedgerProof's MCP receipt layer is positioned squarely against the largest emerging transaction class of the next decade. The **per-action receipt economics at agent-volume scale require sub-cent marginal cost** (already true at Bitcoin's Merkle-batched anchoring tier) and **basis-points pricing on transaction value** for high-value agent commitments.

### Sources
- [Gartner: Guardian Agents to capture 10-15% of agentic AI market by 2030](https://www.gartner.com/en/newsroom/press-releases/2025-06-11-gartner-predicts-that-guardian-agents-will-capture-10-15-percent-of-the-agentic-ai-market-by-2030)
- [Gartner: 50% of supply chain solutions with agentic AI by 2030](https://www.gartner.com/en/newsroom/press-releases/2025-05-21-gartner-predicts-half-of-supply-chain-management-solutions-will-include-agentic-ai-capabilities-by-2030)
- [Grand View Research: AI Agents Market $50.31B by 2030, 45.8% CAGR](https://www.grandviewresearch.com/press-release/global-ai-agents-market-report)
- [MarketsandMarkets: AI Agents Market $52.62B by 2030](https://www.marketsandmarkets.com/PressReleases/ai-agents.asp)
- [Gartner Top Predictions for IT Organizations 2026 and Beyond](https://www.gartner.com/en/newsroom/press-releases/2025-10-21-gartner-unveils-top-predictions-for-it-organizations-and-users-in-2026-and-beyond)

---

## DOMAIN 4 — Real-world-asset tokenization + stablecoin infrastructure

### RWA forecasts 2030 (consulting consensus)

- **McKinsey** (base case, excluding cryptocurrencies and stablecoins): **$2.0T–$2.5T** by 2030, **$4T** bullish.
- **BCG/Ripple** (2025 update): **$9.4T** by 2030; **~$19T by 2033**.
- **Citi**: **$4T–$5T** digital securities + **$1T** blockchain trade finance by 2030 (total ~$5T–$6T).
- **Ark Invest**: **$11T** by 2030.
- **Deloitte**: **$1T** tokenized private real estate funds by 2035 (8.5% market penetration).

The wide range ($2T–$30T) reflects different definitions (asset value vs. business opportunity vs. demand; inclusion or exclusion of stablecoins/CBDCs).

### Most-momentum RWA categories

1. **Tokenized US Treasuries** — fastest production growth; primary issuers BlackRock (BUIDL), Franklin Templeton (FOBXX), Ondo Finance.
2. **Private credit and invoice finance** — Maple Finance, Centrifuge, Goldfinch.
3. **Real estate** (commercial and residential fractional) — Securitize, RealT, Lofty.
4. **Carbon credits** — Toucan, KlimaDAO, integrated with Verra, Gold Standard.
5. **IP and royalty streams** — Story Protocol, Sound.xyz.

### Stablecoin landscape

- **Tether (USDT)**: $100B+ market cap; primary float-yield issuer (~$5-7B annual interest income).
- **Circle (USDC)**: ~$60B; institutional preference; growing in EU.
- **PayPal USD (PYUSD)**: $1B+; payments-adjacent.
- **EURC** (Circle's EUR stablecoin): growing under EU MiCA framework.
- **CBDCs**: pilots active in China (digital yuan, ~$250B in transactions), EU (digital euro in design phase), Brazil (Drex), India (e-Rupee).

### Architectural implication

Every tokenized real-world asset requires **provable provenance for issuance** and **continuous provable custody**. LedgerProof's anchoring layer can capture **basis-points-on-value fees** on each RWA-issuance and custody event. At $9.4T (BCG/Ripple central case) with even 0.25 basis points combined issuance + annual custody, the addressable revenue is **$2.35B annually** by 2030 from RWA-anchoring alone.

### Sources
- [McKinsey: tokenization will be less than $2 trillion by 2030](https://www.ledgerinsights.com/mckinsey-estimates-tokenization-will-be-less-than-2-trillion-by-2030/)
- [BCG/Ripple: $9.4T tokenized RWA demand by 2030](https://blog.tokenizer.estate/rwa-tokenization-forecast)
- [Ark Invest: Tokenized assets could surpass $11 trillion by 2030 (The Block)](https://www.theblock.co/post/386588/tokenization-outlook-ark-invest)
- [Asset Tokenization Forecasts $2T to $30T by 2030 — comparative analysis](https://www.assettokenization.com/resources/asset-tokenization-forecasts-range-from-2t-to-30t-by-2030)

---

## DOMAIN 5 — Deepfake and synthetic media volume trajectory

### Fraud loss forecasts

- **Deloitte (US)**: deepfake/genAI fraud losses projected at **$40B by 2027** — 32% CAGR from $12.3B in 2023.
- **2024 reality**: average loss per deepfake incident **~$500,000**.
- **Q1 2025 reality (North America)**: **$200M+** in deepfake fraud losses in a single quarter.
- **Attack volume**: CEO-impersonation deepfake fraud targets **400+ companies per day** as of 2026.

### Synthetic media volume

- **Gartner**: by 2028, **1 in 4 job candidate profiles globally** will be fake.
- **GenAI content market**: 560% growth 2025-2031, reaching **$442B**.
- **Detection asymmetry**: synthetic media generation tools improve faster than detection tools. The structural condition favors the attacker.

### Specific incident classes driving regulatory action

- Real-time voice deepfakes used in CFO/CEO wire-fraud attacks (notable: Arup engineering $25M loss, 2024).
- Synthetic-identity loans and benefit applications (US Social Security Administration, multiple state benefits programs).
- Court-document and evidence forgery cases (multiple US federal cases, 2025-2026).
- Political deepfakes (multiple G20 election cycles, 2024-2026).

### Architectural implication

The deepfake problem is **fundamentally a provenance problem expressed in the negative**. LedgerProof's role is not to detect deepfakes but to **enable affirmative cryptographic attestation that a document/media/AI-output is what it claims to be**. The market is structurally aligned with our positioning. The customer is anyone who needs to defend the authenticity of their own work in a world where forgery is industrial-scale.

### Sources
- [Deloitte: $40B US deepfake fraud losses by 2027](https://www.aicerts.ai/news/deepfake-fraud-could-cost-u-s-40b-by-2027-deloitte-warns/)
- [Deloitte Insights: Deepfake banking and AI fraud risk](https://www.deloitte.com/us/en/insights/industry/financial-services/deepfake-banking-fraud-risk-on-the-rise.html)
- [UNESCO: Deepfakes and the crisis of knowing](https://www.unesco.org/en/articles/deepfakes-and-crisis-knowing)
- [Deepfake Statistics & Trends 2026 (Keepnet)](https://keepnetlabs.com/blog/deepfake-statistics-and-trends)

---

## DOMAIN 6 — Global digital sovereignty + AI regulation 2026-2036

### EU evolution

- **EU AI Act Article 50** enters force **August 2, 2026** (already-known; primary launch peg).
- **High-risk obligations** (biometrics, critical infrastructure, education, employment, migration, asylum, border control) apply from **December 2, 2027**.
- **EU AI Omnibus legislative proposal** adopted **November 19, 2025**; political agreement reached **May 7, 2026** — adjusting and clarifying the Act's implementation.

### US federal

- **Trump December 2025 Executive Order on AI** signals federal intent to **consolidate AI oversight** and **discourage state-level AI regulation**.
- The EO does not itself establish standards; further Congressional and agency action is needed.
- **Strategic Bitcoin Reserve** established by Biden March 2025; **US Digital Asset Stockpile** mandate — sovereign Bitcoin holdings now a US federal reality.

### US state-level AI regulation

- **Colorado AI Act** becomes enforceable **June 2026** — *before* EU AI Act Article 50. This is a critical near-term regulatory clock we hadn't tracked.
- California, Illinois, New York, Texas have AI-specific bills in active legislative session.

### Other major jurisdictions

- **UK**: NCSC PQC migration timeline (2028-2031-2035), no comprehensive AI act yet but sector-specific regulation tightening.
- **China**: Strict AI content marking requirements since 2023; aggressive in synthetic media regulation.
- **India / Japan / Korea / Singapore / UAE**: AI governance frameworks in various stages; no unified position yet.
- **UNCITRAL / UN**: no specific AI provenance instrument yet, but interest growing.

### Architectural implication

The regulatory landscape supports LedgerProof's positioning but adds the **Colorado AI Act (June 2026)** as a near-term US-side launch peg alongside EU Article 50. Marketing and sales should reference both. Federal US AI provenance mandate is *unlikely before late-2027* given the EO's consolidation posture — meaning US institutional adoption flows through state law (Colorado, NY, CA), Big 4 audit, and PCAOB rather than federal mandate during the launch window.

### Sources
- [EU Artificial Intelligence Act (official site)](https://artificialintelligenceact.eu/)
- [Recent AI Regulatory Developments in the United States (Wilson Sonsini)](https://www.wsgr.com/en/insights/recent-ai-regulatory-developments-in-the-united-states.html)
- [2026 AI Laws Update: Key Regulations and Practical Guidance (Lexology)](https://www.lexology.com/library/detail.aspx?g=82cda450-2005-4c33-a87f-d670efa9a736)
- [State AI Laws — Where Are They Now (Cooley)](https://www.cooley.com/news/insight/2026/2026-04-24-state-ai-laws-where-are-they-now)
- [Key AI Regulations to Watch in 2026 (Eliassen)](https://www.eliassen.com/blog/key-ai-regulations-to-watch-in-2026)

---

## DOMAIN 7 — Bitcoin institutional + sovereign adoption 2026-2036

### Sovereign holdings (verified 2026)

- **US Strategic Bitcoin Reserve** (established March 2025) — federal sovereign holding, exact size undisclosed but substantial.
- **El Salvador** — continuing sovereign Bitcoin reserve and use of Simple Proof for document timestamping.
- **Norway's sovereign wealth fund** — holds **7,161 BTC** (via equity exposure to MicroStrategy and direct holdings).
- **Abu Dhabi's Mubadala** — holds **$1B+** in Bitcoin ETFs.
- **Bhutan** — significant national Bitcoin holdings via state-owned investment vehicle.

### Bitcoin ETF flows (verified 2025-2026)

- US Bitcoin ETF market: **$103B AUM** end of 2025, grew 45% over the year.
- US spot Bitcoin ETFs: **~$123.5B total net assets** mid-2026.
- BlackRock IBIT alone: **$70.6B** (the dominant institutional vehicle).
- Fidelity FBTC: **$17.7B**, holding **203,000 BTC** in custody.

### THE CRITICAL FINDING: Bitcoin Core v30 (October 10, 2025)

**Bitcoin Core v30, released October 10, 2025, raised the OP_RETURN limit from 83 bytes to 100,000 bytes.** This is a fundamental change in the Bitcoin data-carrier landscape.

Implications for LedgerProof:

- The original LPR v1.0 spec assumed a small OP_RETURN (4-byte prefix + 32-byte Merkle root = 36 bytes total). This still works under v30.
- But the new 100KB ceiling means **larger anchor payloads are economically feasible**. We could optionally anchor multiple Merkle roots per transaction (e.g., separate roots per profile or per region) or include richer metadata.
- The change is controversial in the Bitcoin community — Bitcoin Knots (the alternative client) maintains the stricter limit and resists the v30 changes.
- LedgerProof should design for **compatibility with both clients**: the v1.0 LPR1 OP_RETURN remains under 83 bytes (36 bytes actual), ensuring acceptance by Knots-aligned mining pools and full nodes. Larger payloads, if used, are an opt-in profile that customers explicitly accept.

### Lightning Network maturity

Lightning Network throughput has grown significantly through 2025-2026, with multiple commercial Lightning service providers (Voltage, Lightspark, Lightning Labs, Strike) offering institutional-grade Lightning infrastructure. This matters for *real-time pre-commitment* of LPR receipts before the daily on-chain anchor — a future-profile capability.

### Architectural implication

**The Bitcoin substrate choice is more durable than ever**, with both sovereign and institutional adoption deepening through 2026. The Core v30 OP_RETURN expansion provides architectural flexibility for richer anchoring without breaking the existing minimal-payload design. We should maintain a 36-byte default for Knots compatibility while reserving an expanded-payload profile for use cases that benefit.

### Sources
- [Sovereign Bitcoin Reserves and the Emerging Institutional Paradigm](https://www.ainvest.com/news/sovereign-bitcoin-reserves-emerging-institutional-paradigm-2512/)
- [Institutional Cryptocurrency Adoption 2025: Bitcoin ETF Boom, Corporate Treasuries](https://powerdrill.ai/blog/institutional-cryptocurrency-adoption)
- [Bitcoin Core v30: OP_RETURN raised from 83 to 100,000 bytes (OAK Research, Oct 2025)](https://oakresearch.io/en/analyses/fundamentals/update-op-return-bitcoin-core-v30-core-knots-war)
- [Bitcoin OP_RETURN Limit Removed: What It Means (Rango)](https://rango.exchange/learn/market-trends/bitcoin-op-return-removal)
- [Bitcoin's Q2 2026 Resilience: Institutional Demand (Coinranking)](https://coinranking.com/blog/bitcoin-q2-2026-resilience-institutional-demand/)

---

## DOMAIN 8 — Verifiable AI provenance commercial landscape (updated, May 2026)

### Microsoft Agent Governance Toolkit (April 2, 2026)

- **Languages**: Python, TypeScript, Rust, Go, .NET.
- **Coverage**: All 10 OWASP Agentic Top 10 risks (the OWASP Top 10 for Agentic Applications was published December 2025 — the first formal taxonomy of agent-specific risks).
- **MIT license**.
- **Integrations**: Microsoft Agent Framework (deep integration with Azure Agent Framework), App Service, Foundry.
- **Adoption**: significant Microsoft-ecosystem traction; specific named non-Microsoft customer announcements are not visible in public sources as of May 2026.
- **Architectural gap (re-confirmed)**: no public-chain anchoring; trust root is customer / Microsoft DID infrastructure.

### VeritasChain Standards Organization

- **VCP profile for SCITT (`draft-kamimura-scitt-vcp-01`)** filed at IETF — confirmed engagement with the IETF standards process.
- Demo Day at IOSCO C8, Madrid, October 8, 2026 (per earlier session research).
- Specific production deployments still not publicly named in the May 2026 search results.

### ERC-8004 Trustless Agents

- Example repositories exist on GitHub (`vistara-apps/erc-8004-example`).
- Live on Ethereum mainnet since January 29, 2026.
- Specific named production deployments still limited to early-builder community.

### Simple Proof / OriginStamp / Woleet / OpenTimestamps

No major change since earlier session research. Document-only, Bitcoin-anchored, mature but narrow.

### C2PA Content Credentials

No major change since earlier session research. Now in Adobe Creative Cloud, Microsoft Bing/Designer, TikTok, Samsung Galaxy S25, Google Pixel 10, Sony PXW-Z300. 100% stripping rate on social platforms remains the structural failure mode.

### Sources
- [Microsoft Agent Governance Toolkit (April 2, 2026)](https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/)
- [Microsoft AGT Architecture Deep Dive](https://techcommunity.microsoft.com/blog/linuxandopensourceblog/agent-governance-toolkit-architecture-deep-dive-policy-engines-trust-and-sre-for/4510105)
- [Govern AI Agents on App Service with Microsoft AGT](https://techcommunity.microsoft.com/blog/appsonazureblog/govern-ai-agents-on-app-service-with-the-microsoft-agent-governance-toolkit/4510962)
- [OWASP Top 10 for Agentic Applications (Dec 2025)](https://owasp.org/) *(via Microsoft AGT references)*

---

## Wave 1 — Top-line takeaways for the 2036 architecture

1. **Quantum/PQC**: Ship hybrid Ed25519+ML-DSA-65 as an opt-in profile in LPR v1.0. The migration architecture is solved; the standardization is done; we just need to implement it. (See `01-quantum-pqc-trajectory.md`.)

2. **IETF SCITT**: Reframe LPR as a SCITT profile (`draft-dawkins-scitt-lpr-00`), composable with the VeritasChain VCP profile already filed. Standards path is clear and natural.

3. **AI agent economy**: $50B+ direct market by 2030; $1.5T+ broader economy. Per-action receipts at agent-volume scale require sub-cent marginal cost (we have this) and basis-points-on-value pricing for high-value commitments (we should add this to the pricing architecture).

4. **RWA tokenization**: $2T-$30T forecasts for 2030. Basis-points-on-issuance + annual custody fees represent a multi-billion-dollar addressable revenue line if LedgerProof becomes the provenance layer.

5. **Deepfake / synthetic media**: $40B US fraud losses by 2027; structural attacker advantage. Affirmative cryptographic attestation is the only durable defense, and the market is structurally aligned with our positioning.

6. **Regulation**: EU AI Act Article 50 (Aug 2, 2026) is the primary launch peg; Colorado AI Act (June 2026) is the secondary US peg. Federal US AI provenance mandate unlikely before late-2027.

7. **Bitcoin**: **Bitcoin Core v30 (Oct 10, 2025) expanded OP_RETURN to 100KB.** We maintain 36-byte LPR1 default for Knots compatibility, with an opt-in expanded-payload profile. Sovereign + institutional adoption deepening.

8. **Competitive landscape**: Microsoft AGT is now cross-language (Python/TS/Rust/Go/.NET) but still has no Bitcoin anchor and no MCP receipt support. VeritasChain has filed at IETF SCITT but no production. ERC-8004 has limited public-named adoption. Our window remains open at the Bitcoin-anchored + SCITT-conformant + MCP-receipt intersection.

— end of Wave 1 synthesis —
