# LPR-FEE-001 — Anchor Fee Policy v1.0

| Field | Value |
|---|---|
| Policy ID | LPR-FEE-001 |
| Status | Active |
| Effective | 2026-07-06 (public launch) |
| Author | LedgerProof Foundation |
| Permanent URL | `spec.ledgerproofhq.io/fee-policy-v1` |
| Supersedes | None — first published fee policy |
| Reviewed by | Technical Steering Committee (TSC) on ratification, Day 90 |

## Purpose

Document the Foundation's commitment on how LedgerProof operators anchor receipts to Bitcoin under variable mempool fee conditions, what SLO customers can rely on, and what degraded-mode operation looks like when network conditions exceed the policy's economic bounds.

This document is published BEFORE a customer or regulator asks "what happens when Bitcoin fees spike?" — it is the answer they get when they ask.

## SLO commitments

Operators conforming to LPR v1.1 + this fee policy commit to:

| Tier | Receipt commitment lag | Bitcoin confirmation lag | Per-receipt anchor cost |
|---|---|---|---|
| **Soft SLO** | ≤ 1 hour | ≤ 6 confirmations within 24 hours | ≤ $0.001 (target; subsidized below this in batching) |
| **Hard SLO** | ≤ 24 hours | ≤ 6 confirmations within 72 hours | ≤ $0.01 (degraded mode) |

A receipt is "committed" when the operator has signed the receipt and the receipt's Merkle root is queued for anchor. A receipt is "confirmed" when the Bitcoin transaction containing its OP_RETURN payload has at least 6 confirmations.

Operators publish their measured soft-SLO and hard-SLO compliance in `lpr-status.json`, anchored weekly.

## Anchoring mechanism

All LPR v1.1+ receipts are anchored via a single Merkle-batched OP_RETURN per anchor cycle. The OP_RETURN payload is 36 bytes:

```
"LPR1" || merkle_root_32
```

Per the receipt format spec; this never changes within a major protocol version.

**Anchor cadence:** the operator's anchor worker collects committed receipts every 5 minutes (configurable, minimum 60 seconds) and emits one OP_RETURN transaction containing the Merkle root of all receipts committed since the last anchor.

**Fee strategy in order of preference:**

1. **Normal mode** (mempool 1-hour estimate ≤ 50 sat/vB): pay the 1-hour fee estimate from mempool.space (primary) or blockstream.info (fallback).
2. **Elevated mode** (mempool 1-hour estimate 50–150 sat/vB): pay the 6-hour fee estimate; soft SLO holds; communicate to customer dashboards.
3. **Spike mode** (mempool 1-hour estimate > 150 sat/vB sustained > 30 minutes): pay the 24-hour fee estimate; reduce anchor cadence to 60 minutes; soft SLO at risk, hard SLO holds.
4. **Degraded mode** (mempool 1-hour estimate > 300 sat/vB sustained > 60 minutes OR primary + fallback fee oracles both unavailable): activate OpenTimestamps escalation path; commit to Bitcoin within 24h via OTS calendar servers and the OPENTS aggregation; hard SLO holds.
5. **Hard fail mode** (Bitcoin mainnet unreachable for > 4 hours): receipts continue to be committed and signed by the operator; anchor queue grows; customers are notified; once mainnet returns, anchor backlog is drained in chronological order; hard SLO may be temporarily violated and the violation is disclosed in `lpr-status.json` and the customer dashboard.

## Replace-by-Fee (RBF) behavior

All anchor transactions are signaled BIP-125 RBF-enabled. The operator monitors the mempool for the anchor transaction:

- If unconfirmed after 60 minutes AND the current 1-hour mempool fee estimate exceeds the original fee by > 50%: rebroadcast with an RBF fee bump to the current 1-hour fee estimate.
- If unconfirmed after 6 hours regardless of fee market: rebroadcast with a Child-Pays-For-Parent (CPFP) transaction from a pre-funded UTXO.
- Maximum total fee per anchor (including all RBF / CPFP bumps): $50 USD equivalent. Any anchor that would exceed this is escalated to OpenTimestamps and Bitcoin-anchored on the next available cycle when the fee returns under the cap.

## Per-receipt cost economics

Under Merkle batching, the marginal Bitcoin fee per receipt is `(anchor_tx_fee_usd / receipts_in_batch)`. At the soft-SLO target of $0.001 per receipt under normal mempool conditions:

- Anchor cadence: 5 minutes → 288 anchor txs per day.
- Average receipts per batch needed to meet target: at 10 sat/vB and a 200 vB anchor tx, fee ≈ $0.0014 at current BTC price; batches of ≥ 14 receipts hit the target. At 1 sat/vB, batches of ≥ 2 hit the target.
- Per-customer cost passthrough: included in subscription tiers (Pilot $25K / Production $120K / $360K / Enterprise custom) up to the published volume thresholds. Overage pricing per receipt is documented in `LPR-MEMBERSHIP-001`.

In degraded mode (OpenTimestamps escalation), the per-receipt anchor cost approaches zero, but the latency target shifts from sub-hour to sub-day. OpenTimestamps escalations are flagged in the receipt's anchor metadata and visible to verifiers.

## OpenTimestamps escalation path

When Bitcoin mainnet fees exceed the policy's economic bounds (degraded mode 4 above), the operator submits the Merkle root to two OpenTimestamps calendar servers (`alice.btc.calendar.opentimestamps.org` and `bob.btc.calendar.opentimestamps.org`) and stores the resulting `.ots` proofs alongside the receipt.

OTS calendar servers aggregate proofs and anchor to Bitcoin mainnet within 24 hours (their own SLO). The receipt's `anchor_status` field reflects this — `pending-ots`, `confirmed-via-ots`, or `confirmed-direct` — so verifiers can show the regulator exactly how the receipt reached Bitcoin.

The Foundation maintains its own OpenTimestamps calendar server as a backstop, funded by Foundation membership fees. Calendar server URL: `calendar.ledgerproofhq.io` (Day 120 deliverable).

## Operator obligations

Any operator claiming LPR v1.1+ conformance MUST:

1. Anchor at least one OP_RETURN per `anchor_cadence_max` (default 5 minutes) when there are committed receipts pending.
2. Publish `lpr-status.json` containing measured `anchor_commit_p95_seconds`, `anchor_commit_p99_seconds`, and the fee policy state (`normal`/`elevated`/`spike`/`degraded`/`hard-fail`).
3. Disclose any hard-SLO violation within 24 hours of detection at `status.<operator-domain>` and in the customer dashboard.
4. Maintain a CPFP-fundable UTXO pool of at least 10× the maximum anchor fee cap.
5. Subscribe to both mempool.space and blockstream.info fee oracle feeds; use median when both are available; use single source when only one is available; fail to "elevated mode" presumption when neither is available.

## Fee policy version migration

The fee policy version is independent of the protocol version. A new fee policy version may be published when:

- The fee strategy materially changes (e.g., a new escalation tier is added)
- The cost economics shift (e.g., a sustained Bitcoin price move > 3x changes the per-receipt cost target)
- A new degraded-mode mechanism is introduced (e.g., Lightning anchoring becomes operationally viable)

New fee policies are ratified by the Foundation TSC, published as `LPR-FEE-NNN` with sequential numbering, and effective 30 days after publication unless emergency conditions justify a shorter window. Existing receipts remain bound to the fee policy version active at their issuance.

## Cost transparency for customers

Every operator publishes the following weekly in `lpr-status.json`:
- `anchor_txs_count_7d`: number of anchor transactions in the last 7 days
- `anchor_total_fee_usd_7d`: total fees paid
- `receipts_anchored_7d`: receipts committed in that window
- `effective_cost_per_receipt_usd_7d`: total / receipts
- `fee_policy_mode_distribution_7d`: histogram of normal/elevated/spike/degraded time

These figures are anchored as receipts. Customers and regulators can verify them independently.

## Operator failure path

If an operator violates this fee policy materially (e.g., consistently misses hard SLO; fails to publish required transparency data; uses a non-conforming anchor mechanism), the Foundation TSC may:

1. Issue a public deviation notice naming the operator and the violation
2. Suspend the operator's LP-Conformant certification mark
3. Recommend customers migrate to a conforming operator (the Foundation operates the conformance-spec test suite; customers can migrate without re-issuing receipts because receipts are operator-portable)

LedgerProof Inc. is subject to this enforcement on the same terms as any other operator.

---

**This fee policy is the Foundation's commitment to customers, regulators, and other operators about the economic discipline under which LPR receipts are anchored. It is published before contracts are signed so that no procurement conversation needs to ask "what happens at $X BTC price?" — the answer is here.**

Issued June 1, 2026 by the LedgerProof Foundation
Ratified by the Foundation Technical Steering Committee (target: Day 90)
