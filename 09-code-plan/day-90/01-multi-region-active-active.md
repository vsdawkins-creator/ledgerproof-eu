# Multi-Region Active-Active — Day 90 Cutover Plan

**Purpose:** Move from EU-active / US-passive (Day 60 state) to true active-active across EU + US + UK. The Day 90 cutover is the engineering milestone the Series A audience evaluates: it demonstrates the operator has graduated from "production single-region" to "production fault-tolerant."

**Owner:** SRE (hired Day 90)
**Cutover date:** Day 90 ± 7 (some flexibility; do not cut over during a regulator examination window)

---

## Pre-cutover state (Day 89)

- EU operator (Frankfurt): active, ~99.8% trailing 30-day
- US operator (us-east-1): passive read replica + write queue
- UK operator (lhr): provisioned, not yet receiving traffic
- Customer SDK 1.2 deployed by ~60% of pilots; 1.1 still in use by ~40%
- Conformance suite passing across both operators
- Chaos test report from Day 80 passing on all injected failures

## Post-cutover state (Day 90 + 7)

- EU, US, UK operators all active
- Receipt issuance routed by SDK to nearest region with healthy SLO
- Postgres logical replication active across all three regions
- Bitcoin anchor batching service in EU primary, US hot-standby (no UK anchor — anchor is single-source)
- Foundation Canonical Registry served from CDN with all three regional caches
- SDK 1.2 mandatory for new customers (1.1 deprecated for new signups; existing customers continue)

---

## Cutover sequence

| T-offset | Action | Rollback trigger |
|---|---|---|
| T-14 days | SRE confirms conformance suite passing on all three regions for 5 consecutive days | If any region fails: postpone cutover |
| T-7 days | Customers notified via email of upcoming cutover; opt-out window opens (no customer expected to opt out, but the option exists) | If >2 customers opt out: investigate why |
| T-3 days | Final chaos drill: simulate EU full outage during peak hours of synthetic load; validate US absorbs | Any SLO breach: postpone |
| T-1 day | Postgres replication lag confirmed <5s across regions | Lag >5s: postpone |
| T-0 hour 0 | UK region begins receiving 5% of EU-routed traffic | UK error rate >0.5%: rollback UK traffic |
| T-0 hour 4 | UK at 20% of EU traffic | Same |
| T-0 hour 12 | UK at 50% of EU traffic | Same |
| T-0 hour 24 | UK fully active | Same |
| T+1 day | US transitions from passive to active (writes accepted) | US write conflicts: roll back to passive |
| T+3 days | All three regions fully active; SDK region="auto" makes regional decisions | SDK routing bug: pin all SDKs to region="eu" |
| T+7 days | Cutover complete; postmortem written | n/a |

The 7-day cutover window is deliberately slow. Article 50 is enforcing; we do not move fast.

---

## Conflict resolution under active-active

### Receipt issuance (read: append-only)

Receipt IDs are content-addressed. Two regions cannot collide on receipt ID because the content includes the issuer's signature with a region-stamped timestamp. The Merkle batching service in EU is the single coordinator for anchor commits — both regional operators stream their receipts to it; it batches and commits.

**Failure mode:** EU Merkle batcher goes down. US hot-standby promotes within 60s. All receipts in flight are re-batched under the new coordinator. No receipt is lost; some may have a brief delay in anchor commit. The anchor SLO is wide enough (24h) that this is well within tolerance.

### Customer metadata (read-write)

Account changes, API keys, billing — these are rare but must be globally consistent. We use Postgres logical replication with EU as the primary writer for metadata. US and UK accept reads only on these tables. Cross-region writes for metadata are intentionally not supported in v1 active-active; this is a Day-120 evolution.

### Rate-limit counters

Per-region rate limiting. A customer with 100 req/s limit gets 100 req/s in each region. This is intentional over-provisioning at the customer level (a single-region customer cannot exceed 100; a customer spanning regions can effectively get 300 if they spread perfectly). Documented in the customer-facing rate limit policy.

---

## Capacity provisioning per region

| Region | Instances at Day 90 | Burst capacity (auto-scale) | Cost/month |
|---|---|---|---|
| EU (Frankfurt) | 6 × shared-cpu-4x | 12 × | $2,500 |
| US (us-east-1) | 4 × shared-cpu-4x | 12 × | $2,200 |
| UK (London) | 2 × shared-cpu-4x | 8 × | $1,800 |

Total Day 90 compute spend on operator: ~$6,500/month. Within budget envelope.

---

## SDK 1.2 region-selection behavior

```python
client = ledgerproof.Client(
    api_key=...,
    region="auto",
)
```

`region="auto"` resolution:
1. SDK queries `https://region.ledgerproofhq.io` (CDN-cached, <50ms)
2. Endpoint returns ranked list of healthy regions for the caller (GeoIP-based)
3. SDK pins to top region for the session; rotates if it returns 5xx more than 3 times in 60s
4. If all regions return 5xx, SDK falls into local queue (the SDK 1.1 fallback queue feature lights up here)

Explicit region pinning is available for customers with data-residency constraints:
- `region="eu"` — EU only; no automatic fallover to US
- `region="us"` — US only
- `region="uk"` — UK only
- `region="eu-with-uk-fallover"` — EU primary, UK fallover (UK-only data residency)

---

## What does not change at active-active

- Receipt format remains v1.1 + v1.2; no schema changes at cutover
- Verifier portal API surface unchanged
- Bitcoin anchor commit semantics unchanged
- Foundation Canonical Registry unchanged
- Self-hosted reference operator unaffected (it does not participate in cross-region active-active; self-hosters operate single-region by default and build their own multi-region story if needed)

---

## Customer communication plan

### T-30 days
Email to all customers: "Active-active is coming. Here is what changes for you (almost nothing) and here is what improves (latency for non-EU traffic, resilience for everyone)."

### T-7 days
Email + status page banner: "Cutover begins on [date]. Expect no customer-visible impact. If you see anything unusual, here is who to contact."

### T+0
Status page banner: "Active-active cutover in progress; expected impact: none. Latest status here."

### T+7
Email: "Cutover complete. Here are the metrics: trailing-7-day SLO, latency reduction observed for US/UK traffic, anchor commit latency unchanged."

### T+30
Public Foundation transparency report includes the cutover postmortem.

---

## Rollback plan

If a critical issue surfaces during cutover:

1. **First action: pin all customer traffic back to EU.** SDK 1.2 `region="auto"` resolution returns EU-only for 24h via the `region.ledgerproofhq.io` endpoint.
2. **Second action: drain US and UK traffic to idle.** No teardown; just routing decision.
3. **Third action: postmortem within 48h.** Decide whether to retry cutover in 14 days or re-architect.

The rollback does not affect receipts already issued in US or UK during the window. Those receipts remain valid and anchored.

---

## Open questions

1. **DNS-based region selection vs. anycast.** Anycast is more sophisticated but Fly.io's regional model is more naturally addressed via DNS. **Recommend DNS for v1; revisit at Day 180.**
2. **Customer-side region pinning for SOC 2 evidence.** Customers under SOC 2 may need documented region. **Recommend: explicit region pinning in client config, surfaced in customer-facing audit log.**
3. **Bitcoin anchor regional preference.** Should US receipts anchor via US-relayed Bitcoin RPCs? **Recommend yes for relay diversity but anchor is single global event regardless.**
