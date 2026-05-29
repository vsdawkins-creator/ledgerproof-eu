# Multi-Region Operator Design — EU Active, US Passive (Day 60) → Active-Active (Day 90)

**Purpose:** Stand up the US operator in active-passive with the EU operator by Day 60, then move to active-active by Day 90. The motivation is not US customer demand (the US enterprise motion is deferred to Series B); it is **resilience for EU customers** during the August enforcement window and beyond.

**Owner:** Founder → SRE hire by Day 90
**Target dates:** Day 60 (us-east-1 in passive); Day 90 (active-active)

---

## Why multi-region now

Three reasons, in order of importance:

1. **A single-region operator is a single point of failure.** A Fly.io Frankfurt regional outage during a regulator examination is a survivable embarrassment in week 1 of enforcement, an existential problem by week 4.
2. **The Series A diligence audience expects multi-region.** Asking for $30M to scale a single-region service is a credibility tax we do not need to pay.
3. **DORA Article 28 examiners ask about geographic redundancy.** Even though receipts anchor to Bitcoin (which is globally redundant by definition), the operator layer must demonstrate geographic resilience to pass FSI procurement.

---

## Topology

```
                        ┌─────────────────────────┐
                        │ Customer SDK            │
                        │ region="eu" | "us"      │
                        │ | "auto"                │
                        └────────────┬────────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
       ┌────────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
       │ EU Operator     │  │ US Operator     │  │ UK Operator     │
       │ Fly.io Frankfurt│  │ Fly.io iad      │  │ Fly.io lhr      │
       │ (active)        │  │ (passive D60 →  │  │ (provisioned    │
       │                 │  │  active D90)    │  │  D90)           │
       └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
                │                    │                    │
                └────────────────────┼────────────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │ Shared state layer  │
                          │ - Postgres primary  │
                          │ - Read replicas/region
                          │ - Object storage    │
                          │   (S3-compat via    │
                          │   Tigris)           │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │ Bitcoin mainnet     │
                          │ (single, global)    │
                          └─────────────────────┘
```

**Critical:** The legacy `iad` deployment from before-product-launch (the 3 anchors that must stay verifiable forever) is **NOT** the same as the new us-east-1 operator. Names are similar, intent is not. Provision the new US operator under a different Fly app name (`lpr-operator-us`) and document the distinction prominently. **DO NOT touch the legacy iad app.**

---

## State management

### What is global state
- Customer accounts, API keys, billing
- Receipt index (id → metadata)
- Bitcoin anchor commits
- Foundation Canonical Registry entries

### What is regional state
- Receipt payload caches (regional read optimization)
- Audit logs (per-region; replicated to global for compliance archival)
- Rate-limit counters (per-region; eventual consistency)

### Replication strategy

**Day 60 (active-passive):**
- Postgres primary in EU
- US runs read-only replica + queues writes for EU
- If EU goes down, US becomes new primary via manual failover (RTO ~10 minutes)
- Customer SDK retries against US automatically (region="auto")

**Day 90 (active-active):**
- Postgres primary still in EU; writes from US replicated via logical replication
- For latency-sensitive paths, regional writes accepted with operator-side conflict resolution (last-write-wins on disjoint keys; vector clock on overlapping ones)
- Receipt issuance is naturally disjoint (receipt IDs include region prefix), so active-active is conflict-free for the hot path

**Bitcoin anchor:** anchor commits remain single-source-of-truth — only one region commits a given Merkle root. Both regions feed receipts into the same global Merkle batching service, which runs in EU with a hot-standby in US.

---

## Customer SDK behavior

SDK 1.1 ships with `region` parameter (functional only on EU until Day 60); SDK 1.2 lights up US.

```python
client = ledgerproof.Client(
    api_key=...,
    region="auto",  # DNS-based selection, defaults to nearest
)
```

`region="auto"` resolves to the nearest healthy region. If a customer's preferred region returns >2 consecutive 5xx, the SDK falls over to the secondary region transparently (no exception raised) and emits a structured log.

**Receipt IDs include region prefix** so that a receipt issued in EU vs. US is distinguishable by inspection. The verifier portal handles both transparently.

---

## Failover scenarios

| Scenario | Detection | Action | RTO | Customer impact |
|---|---|---|---|---|
| EU pod outage (single instance) | Fly health check fails | Fly auto-restart or rotate | <60s | None (other instances absorb) |
| EU region outage | Multi-instance failure | Manual cutover to US primary | ~10 min Day 60; <60s Day 90 | None at Day 90; brief retry blip at Day 60 |
| US region outage | Same as EU | Same as EU | Same | Same |
| Both EU + US down simultaneously | Fly-wide outage | UK region (provisioned Day 90) absorbs | <2 min | Brief queue depth growth |
| Bitcoin RPC providers all down | Anchor lag alert | Failover to private node | <5 min for switchover | Anchor delay; receipts continue to issue |
| Database primary down | Postgres health check | Promote read replica | ~5 min | Brief 503s during promote |
| Foundation Canonical Registry unreachable | Synthetic check fail | Serve from regional cache | <30s | Read-only mode for registry |

Every scenario has a runbook entry by Day 60.

---

## Deployment process

| Step | Owner | Day |
|---|---|---|
| Provision Fly.io us-east-1 app (`lpr-operator-us`) | Founder | Day 35 |
| Deploy operator binary to us-east-1 in maintenance mode | Founder | Day 38 |
| Stand up Postgres read replica in us-east-1 | Founder | Day 40 |
| Configure logical replication | Founder | Day 42 |
| Pass operator self-tests in us-east-1 against staging customers | Founder | Day 45 |
| Configure SDK `region` resolution DNS | Founder | Day 48 |
| Move 5% of staging customer traffic to us-east-1 (passive read mode) | Founder | Day 50 |
| Failover drill: cut EU, validate US absorption | Founder | Day 55 |
| Promote us-east-1 to passive production (zero-customer-impact) | Founder | Day 60 |
| Active-active design review by SRE hire | SRE | Day 70 |
| Active-active deployment | SRE | Day 90 |
| Add UK region | SRE | Day 90 |
| Chaos test active-active under W3 load | SRE | Day 100 |

---

## Cost model

| Item | Day 30 | Day 60 | Day 90 |
|---|---|---|---|
| EU operator | $1,500/mo | $2,000/mo | $2,500/mo |
| US operator | — | $800/mo (passive) | $2,200/mo (active) |
| UK operator | — | — | $1,800/mo |
| Database (multi-region) | $400/mo | $900/mo | $1,400/mo |
| Object storage + CDN | $200/mo | $400/mo | $700/mo |
| Bitcoin RPC | $150/mo | $300/mo | $500/mo |
| Observability | $300/mo | $500/mo | $800/mo |
| **Total** | **~$2,550/mo** | **~$4,900/mo** | **~$9,900/mo** |

Day 90 monthly run-rate: ~$120K/year. Inside the budget envelope.

---

## Cross-cutting validations (must hold across regions)

1. **Receipt verifiability is region-independent.** A receipt issued in EU verifies identically in US and UK. CI runs cross-region verification on every operator release.
2. **Bitcoin anchor is single global source.** A receipt anchored at block N is the same anchor whether observed from EU or US.
3. **Soft-delete propagates within 60 seconds across regions.** A GDPR Article 17 erasure request honored in EU is honored in US and UK before customer notification.
4. **PII rejection happens at the SDK; operator validation is a defense-in-depth check.** Pentest tests operator rejection across all three regions.
5. **No customer data crosses regions unless customer explicitly opts in.** Default region selection keeps EU customers on EU operator. The SDK fallover behavior is opt-in via the SDK `region` parameter; default behavior at Day 60 is no fallover.

---

## Open questions

1. **GDPR cross-region data flows.** Replicating EU customer metadata to US for failover is itself a GDPR consideration. **Recommend: at Day 60, no metadata replicates to US; US operates on its own customer data only (currently empty). Active-active at Day 90 only for tenants who opt in.**
2. **UK region post-Brexit data residency.** UK customers may require UK-only data. **Recommend: UK operator at Day 90 is UK-data-only; same active-active model as EU/US, opt-in.**
3. **Bitcoin pool relay diversity per region.** Should each region use different pool relays? **Recommend yes — distinct relay sets reduce correlated failure risk.**
