# Asia Region Provisioning Plan — Singapore First (Q1 2027)

**Purpose:** Engineering counterpart to the [Asia Expansion Brief](../../08-gtm/day-180/03-asia-expansion-brief.md). Stand up the Singapore operator region during Q1 2027 so it is production-ready when the Singapore non-profit twin of the Foundation begins commercial engagement.

**Owner:** SRE + Asia GM (hired Q2 2027 per GTM plan)
**Provisioning target:** Q1 2027 (operator live in passive mode)
**GA target:** Q2 2027 (operator active for Singapore customers)

---

## Where to provision

| Provider | Region | Reasoning |
|---|---|---|
| **Fly.io** | `sin` (Singapore) | Same provider as EU/US/UK; minimum operational divergence |
| **AWS** | `ap-southeast-1` (Singapore) | Alternative if Fly.io capacity becomes a constraint; available via marketplace listing alignment |
| **Google Cloud** | `asia-southeast1` (Singapore) | Vertex AI customers may prefer co-located operator |
| **GCP Sovereign Cloud via S3NS / T-Systems** | n/a in Asia | Not applicable; sovereignty handled via Singapore non-profit governance |

**Recommendation:** Fly.io Singapore as the production operator; AWS Singapore as a secondary deployment for marketplace customers requesting region co-location. GCP Singapore considered for Vertex AI-heavy customers but only after demonstrated demand.

---

## Topology delta from EU+US+UK

Prior topology: three active regions, EU-primary for metadata writes, Bitcoin anchor batcher in EU with US standby.

Adding Singapore:

```
                  Customer SDK (region="auto")
                          │
        ┌─────────────────┼─────────────────┐
        │      EU         │      US         │      UK
        │   Frankfurt     │   us-east-1     │   London
        │   (active)      │   (active)      │   (active)
        └────────┬────────┴────────┬────────┴────────┬────────┐
                 │                 │                 │        │
                 │                 │                 │   ┌────▼─────┐
                 │                 │                 │   │ SG        │
                 │                 │                 │   │ Singapore │
                 │                 │                 │   │ (Q1 2027  │
                 │                 │                 │   │  passive) │
                 │                 │                 │   │ (Q2 2027  │
                 │                 │                 │   │  active)  │
                 │                 │                 │   └────┬──────┘
                 │                 │                 │        │
                 └─────────────────┴─────────────────┴────────┘
                                   │
                          ┌────────▼────────┐
                          │ Shared state    │
                          │ (Postgres,      │
                          │  object         │
                          │  storage,       │
                          │  Bitcoin RPC)   │
                          └─────────────────┘
```

**Singapore-specific design choices:**

1. **Singapore is its own write quorum.** Singapore customers' metadata writes commit locally first, then replicate to EU. The metadata replication is async with a 60-second target lag — acceptable for the rare metadata operation (account changes, key rotations).

2. **Singapore operator is its own SLO scope.** A Fly.io Singapore regional outage does NOT page EU/US/UK on-call. Singapore has its own SRE coverage (initially: SRE + Asia GM coverage during Singapore business hours; full coverage by Q3 2027).

3. **Bitcoin anchor remains EU-primary, US-standby.** Singapore operator forwards receipt anchors to EU for batching. Anchor commit latency may be ~50ms higher than EU/US customers; acceptable.

4. **Singapore-only data residency option.** Customers may pin `region="sg-only"` for Singapore data residency. No metadata replicates outside Singapore for these customers. Recovery in case of Singapore-only regional outage is manual; documented in pilot SOW.

---

## Pre-provisioning gates (Q4 2026)

Before Singapore provisioning begins:

- [ ] Singapore non-profit Foundation twin registration filed
- [ ] Asia GM job posting live (target hire by Q2 2027)
- [ ] MAS informational briefing complete (Foundation-driven, no commercial outreach)
- [ ] Singapore tax and operating entity decisions documented (corporate counsel)
- [ ] Multi-region active-active runtime stable for ≥90 days (EU+US+UK)
- [ ] SRE bandwidth confirmed (not blocked on EU work)

---

## Provisioning sequence (Q1 2027)

| Week | Action | Owner |
|---|---|---|
| W1 | Fly.io Singapore app created (`lpr-operator-sg`); secrets provisioned; never touched by EU release pipeline | SRE |
| W2 | Operator binary deployed to Singapore in maintenance mode | SRE |
| W3 | Postgres logical replica in Singapore established; replication lag monitored | SRE |
| W4 | Operator self-tests pass in Singapore region | SRE |
| W5 | Synthetic traffic from a Singapore-based test harness validates end-to-end | SRE |
| W6 | First Foundation-internal receipts issued from Singapore (dogfood); verified end-to-end | Founder + SRE |
| W7 | Region resolution updated to include Singapore for `region="auto"` | SRE |
| W8 | Singapore region listed at status.ledgerproofhq.io | SRE |
| W9 | Failover drill: cut Singapore; validate EU absorbs Singapore-pinned customers | SRE |
| W10 | Region documentation published at docs.ledgerproofhq.io/regions/sg | DevRel |
| W11 | First Singapore design partner pilot SOW signed (commercial trigger) | BD + Founder |
| W12 | Singapore region GA announced | All |

---

## Customer-facing API changes

`region="auto"` adds Singapore to its resolution table for customers geolocated in Asia-Pacific.

New explicit region values:
- `region="sg"` — Singapore preferred; EU fallover
- `region="sg-only"` — Singapore only; no fallover; explicit data residency

SDK 1.2+ supports the new regions transparently. No SDK upgrade required for existing customers.

---

## Cost model

| Item | Q1 2027 | Q2 2027 (active) | Q4 2027 |
|---|---|---|---|
| Fly.io Singapore operator | $800/mo (passive) | $2,000/mo | $2,800/mo |
| Postgres Singapore replica | $400/mo | $700/mo | $900/mo |
| Object storage + CDN (Asia) | $200/mo | $400/mo | $700/mo |
| Bitcoin RPC (Asia-routed) | $100/mo | $200/mo | $300/mo |
| Observability (Asia) | $200/mo | $300/mo | $400/mo |
| **Singapore monthly cost** | **~$1,700** | **~$3,600** | **~$5,100** |

Asia ops budget is folded into the Series A use-of-funds (25% Asia expansion line). Singapore operator cost at full scale is ~$60K/year — modest fraction of expected Singapore ARR.

---

## SLO commitments for Singapore

Initial commitments (Q2 2027 GA):

| SLO | Target |
|---|---|
| Operator availability | 99.5% |
| Receipt issuance p99 | ≤200ms |
| Bitcoin anchor commit within 24h | ≥99% |

These are intentionally identical to EU/US/UK commitments. The Singapore operator should not have a degraded SLO; if it cannot meet commitments at GA, GA is postponed.

By Q4 2027, Singapore SLOs target the same 99.9% the other regions hold.

---

## Failure modes

| Scenario | Detection | Action | RTO |
|---|---|---|---|
| Fly.io Singapore regional outage | Multi-instance failure | Auto-fallover to EU for `region="auto"`; `region="sg-only"` customers see degraded mode | <60s for auto; documented degraded for sg-only |
| Postgres Singapore replica lag exceeds 5min | Replication monitoring | Alert; investigate root cause | n/a (writes still commit; reads served from cache) |
| Bitcoin RPC Asia-routed provider down | Synthetic check | Failover to EU-routed RPC | <2 min |
| Singapore on-call unavailable during incident | PagerDuty escalation | EU on-call (or US, time-of-day appropriate) absorbs | n/a |

---

## What does NOT happen at provisioning

- We do not migrate any existing EU/US/UK customers to Singapore
- We do not require any customer to use Singapore
- We do not change pricing for Singapore (same per-receipt economics)
- We do not create a separate spec for Singapore — the protocol is global
- We do not fork the protocol governance — Singapore non-profit Foundation twin is a coordination entity, not a protocol authority

---

## Q3 2027 evolution (out of scope for this document but on the horizon)

- Tokyo (`hnd` / `ap-northeast-1`) operator provisioning begins
- First Japan customer pilots
- Singapore SRE seat added (locally hired)
- Singapore Big-4 partnership LOI signed
- HKMA / APRA / FSC informational briefings begin

These evolve from the Asia Expansion Brief schedule; the engineering capacity to support them is planned but not committed at Day 180.

---

## Open questions

1. **Tigris object storage Asia availability.** Confirm Tigris has Singapore POP for cost-effective object storage. Fallback: AWS S3 Singapore.
2. **Bitcoin RPC providers in Asia.** Mempool.space has global reach; we need at least one Asia-headquartered provider for relay diversity. **Recommend BlockCypher Asia + Anthropic-friendly Bitcoin Core node hosted on AWS Singapore.**
3. **GDPR-vs-PDPA precedence.** Singapore data residency is governed by Singapore PDPA; our GDPR posture must not conflict. **Recommend Singapore counsel review at Q4 2026.**
4. **MAS Veritas mapping document.** Should LedgerProof publish a Veritas-specific mapping (analogous to ISO 42001, DORA mappings)? **Recommend yes by Q2 2027; co-produce with Singapore non-profit Foundation.**
