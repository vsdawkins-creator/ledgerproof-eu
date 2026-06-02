# Kong Plugin Specification v0.1 — `kong-plugin-ledgerproof`

**Target:** Kong Gateway 3.4 LTS, 3.5, 3.6, 3.7 (OSS and Enterprise)
**License:** Apache License 2.0
**Target ship date:** 2026-08-02 (KS5 deadline — EU AI Act Article 50 enforcement day)
**Status:** Draft v0.1 — engineering blueprint, not yet implemented. Third revision of the spec. Supersedes the two preceding drafts which conflated outbound publication with inbound third-party data inspection (C2 violation) and proposed a `body_filter`-phase implementation (C6 violation).
**Owner of record:** Senior Protocol Engineer (offer 2026-06-22; start 2026-07-13). Veronica S. Dawkins (Founder) holds the spec until handoff at start date.
**Maintainer of record:** LedgerProof Inc. — transferable to LedgerProof Foundation upon IRS §501(c)(3) determination and Dutch Stichting registration.
**Distribution:** LuaRocks (`kong-plugin-ledgerproof`) + GitHub Releases at `github.com/ledgerproof/kong-plugin-ledgerproof`
**References:**
- LPR 1.1 Specification (`/04-lpr-spec/LPR-1.1-SPECIFICATION.md`) — receipt format, canonicalization, signing model
- LPR 1.2 Canonicality Annex (`/04-lpr-spec/LPR-1.2-CANONICALITY-ANNEX.md`) — lineage chain encoding
- LPR-ERRATA-001 — Entry #0 RCA, applies only to legacy iad deployment, not to plugin
- Threat Model Briefing (`/14-seed-close-pack/02-threat-model-briefing.md`) — system architecture overview
- Master Code Plan v2 (`/09-code-plan/00-MASTER-CODE-PLAN-V2.md`)
- Atomic Explosion Master Plan (`/14-seed-close-pack/04-atomic-explosion-master-plan.md`) — KS5 ship deadline, C1–C8 corrections

---

## 1 · Scope

`kong-plugin-ledgerproof` is a Kong Gateway plugin that emits LedgerProof Protocol (LPR 1.1) receipts for AI inference traffic that an enterprise publishes through Kong to its own downstream customers. The plugin is installed and configured by the enterprise operating the Kong instance. It runs in-process inside Kong's `nginx` worker, observes the request and response lifecycle, captures the deterministic bytes required to construct an LPR entry, batches those entries into a Merkle tree, signs the Merkle root once per batch via an HSM, and emits per-request receipts to a configured side channel. The receipts can then be consumed by the enterprise's own SIEM (Splunk, Datadog, ServiceNow, Vanta, Drata) and by the public verifier at `/v/{slug}` on `verify.ledgerproofhq.io`.

The plugin's surface is the **outbound API publication boundary**: traffic that the enterprise originates from its own model-serving infrastructure (model gateway, model registry endpoint, customer-facing inference API) and exposes to its downstream consumers. The plugin is **not** an inbound third-party data inspection surface; that surface lives in the Snowflake UDF, Databricks notebook, Airflow operator, and Prefect task adapters which are specified separately (see `inbound-snowflake-spec.md`, planned for v0.2). This boundary is load-bearing for both threat-model reasons (C2) and for the EU AI Act Article 50 deployer-obligation chain (the enterprise publishing an AI service is the deployer; the receipt evidence is attached at that surface).

### 1.1 In-scope / out-of-scope table

| Surface | In scope for v0.1 | Notes |
|---|---|---|
| Outbound AI inference API published via Kong | YES | Primary target. Both unary and streaming (SSE / chunked HTTP). |
| Outbound non-AI traffic | NO | Plugin is a no-op when not enabled on a route. |
| Inbound third-party data fetch | NO | Lives in Snowflake / Databricks / Airflow / Prefect adapters (C2). |
| Receipt verification | NO | Verification is LOCAL via SDK (C4). Plugin emits only. |
| LedgerProof verification node coordination | NO | Plugin does NOT phone home (C4). Receipts are independently verifiable offline. |
| Response payload modification | NO | Receipts emit to a side channel, never appended to response (C6). |
| `body_filter` phase usage | NO | Prohibited — breaks streaming AI (C6). |
| Inline (per-request) HSM signature | NO | Prohibited — latency-prohibitive at AI request rates. Merkle-batch only (C6). |
| Snowflake / Databricks / Airflow / Prefect | NO | Separate adapters. |
| Kong Konnect (managed) compatibility | YES | Plugin is OSS-compatible; runs identically in Konnect via custom plugin upload. |
| Apache APISIX | NO | Out of scope for v0.1; planned for v0.2 if pulled by demand. |

---

## 2 · Architecture overview

```
                       Kong Gateway worker (nginx + OpenResty + LuaJIT)
   ┌───────────────────────────────────────────────────────────────────────────┐
   │                                                                           │
   │     ACCESS PHASE              UPSTREAM             HEADER_FILTER /        │
   │   (capture req hash,       (model inference        LOG PHASE              │
   │    deployer_id,            backend; the            (capture resp hash,    │
   │    model_id,               enterprise's            timing, status,        │
   │    context)                own service)            finalize entry)       │
   │   ──────────────►   ──────────────────────►   ──────────────────────►     │
   │           │                                              │                │
   │           ▼                                              ▼                │
   │   ┌─────────────────────┐                    ┌─────────────────────┐     │
   │   │ Pending entry table │                    │ Finalized entry     │     │
   │   │ keyed by request_id │   stream-end       │ enqueued to         │     │
   │   │ (in-worker SHM)     │ ───────────────►   │ batch accumulator   │     │
   │   └─────────────────────┘                    └──────────┬──────────┘     │
   │                                                          │                │
   │                                            window: 1s OR 1000 entries    │
   │                                                          │                │
   │                                                          ▼                │
   │                                          ┌────────────────────────────┐  │
   │                                          │  Merkle tree builder       │  │
   │                                          │  root = Merkle(entries)    │  │
   │                                          └─────────────┬──────────────┘  │
   │                                                        │                  │
   │                                                        ▼                  │
   │                                          ┌────────────────────────────┐  │
   │                                          │  HSM signer (out-of-band   │  │
   │                                          │  via PKCS#11 / KMIP /      │  │
   │                                          │  cloud KMS REST)           │  │
   │                                          │  sig = Ed25519(root)       │  │
   │                                          └─────────────┬──────────────┘  │
   │                                                        │                  │
   │                                                        ▼                  │
   │                                          ┌────────────────────────────┐  │
   │                                          │  Receipt emitter           │  │
   │                                          │  for each entry e_i:       │  │
   │                                          │    receipt = {             │  │
   │                                          │      entry: e_i,           │  │
   │                                          │      inclusion_proof: π_i, │  │
   │                                          │      root: r,              │  │
   │                                          │      root_sig: sig,        │  │
   │                                          │      anchor_ref: pending   │  │
   │                                          │    }                       │  │
   │                                          │  → side channel            │  │
   │                                          └─────────────┬──────────────┘  │
   │                                                        │                  │
   └────────────────────────────────────────────────────────┼──────────────────┘
                                                            │
                              ┌─────────────────────────────┴─────────────────┐
                              │                                                │
                              ▼                                                ▼
                      Enterprise SIEM                            LedgerProof Anchor Worker
                  (Splunk / Datadog /                            (out-of-band; receives
                   ServiceNow / Vanta /                          root + sig, batches into
                   Drata) — customer's                           Bitcoin OP_RETURN anchor)
                   compliance dashboard
                   per C5
```

Three properties of this architecture are load-bearing:

1. **Receipts emit to a side channel, never to the response body.** The response stream to the API consumer is untouched. There is no body buffering. SSE and chunked HTTP responses flow through Kong with zero added latency on the response path.
2. **The HSM signs once per batch, not once per request.** A 5–50 ms HSM round trip per request would cap the plugin at 20–200 req/s. Signing the Merkle root of a 1000-entry batch amortizes to under 50 µs per receipt.
3. **The anchor pipeline is asynchronous.** The plugin emits receipts immediately upon batch sign. The Bitcoin OP_RETURN anchor is added by the LedgerProof anchor worker on its own schedule (typically 10 minutes to 1 block). The receipt's `anchor_ref` field is `pending` at emit time and is updated by the SIEM-side consumer when the anchor lands. This is consistent with LPR 1.1 §6.

---

## 3 · Technical interface

### 3.1 Kong phases used

| Phase | Used | Purpose |
|---|---|---|
| `certificate` | No | — |
| `rewrite` | No | — |
| `access` | **Yes** | Capture request hash, deployer_id, model_id, route metadata, request_id; insert pending entry into per-worker SHM table. |
| `header_filter` | **Yes** | Capture response status, response headers required for the entry, response start timestamp. |
| `body_filter` | **NO — prohibited** | Would force full-body buffering, breaking SSE and chunked HTTP. C6. |
| `log` | **Yes** | Capture response end timestamp, response size, response hash (streamed via incremental SHA-256 in `header_filter` start + per-chunk in a custom stream observer that does **not** buffer the body), finalize the entry, enqueue into the batch accumulator. |

The plugin computes the response hash incrementally as bytes pass through the worker. Each chunk is fed to an incremental SHA-256 context held in the request context. The body is **not buffered**; only the rolling hash state (32 bytes) is held. At `log` phase the final digest is read out.

### 3.2 Plugin configuration schema

The Kong plugin schema lives in `schema.lua`. Example fields:

```lua
return {
  name = "ledgerproof",
  fields = {
    { config = {
        type = "record",
        fields = {
          { deployer_id      = { type = "string", required = true,
                                 match = "^[a-z0-9._-]{3,128}$" } },          -- C5: no PII, no emails
          { model_id         = { type = "string", required = true } },        -- e.g. "internal-llm-v3.2"
          { profile          = { type = "string", default = "EU-AI-ACT-50-v1.1",
                                 one_of = { "EU-AI-ACT-50-v1.1" } } },
          { batch_window_ms  = { type = "integer", default = 1000,
                                 between = { 100, 30000 } } },
          { batch_max_entries = { type = "integer", default = 1000,
                                  between = { 16, 10000 } } },
          { hsm = {
              type = "record",
              required = true,
              fields = {
                { provider = { type = "string", required = true,
                               one_of = { "thales-luna", "aws-cloudhsm",
                                          "azure-dedicated-hsm", "yubihsm2",
                                          "aws-kms", "gcp-kms", "azure-key-vault" } } },
                { key_label = { type = "string", required = true } },
                { endpoint  = { type = "string" } },
                { timeout_ms = { type = "integer", default = 5000 } },
              }
            } },
          { side_channel = {
              type = "record",
              required = true,
              fields = {
                { kind = { type = "string", required = true,
                           one_of = { "webhook", "kafka", "redis-stream",
                                      "syslog", "file", "stdout" } } },
                { endpoint = { type = "string" } },
                { auth_header = { type = "string" } },     -- bearer-only; no plaintext secrets in config
                { fanout = { type = "array", elements = { type = "string" }, default = {} } },
              }
            } },
          { fail_mode = { type = "string", default = "fail-open",
                          one_of = { "fail-open", "fail-closed" } } },
          { observability = {
              type = "record",
              fields = {
                { prometheus = { type = "boolean", default = true } },
                { trace_sample_rate = { type = "number", default = 0.0,
                                        between = { 0.0, 1.0 } } },
              }
            } },
        }
    } }
  }
}
```

`deployer_id` is enforced by regex against email shape. The plugin refuses to load any configuration whose `deployer_id` contains `@`. This is a GDPR Schema rejection consistent with LPR 1.1 §11.2.

### 3.3 Required dependencies

| Dependency | Version | Source | Notes |
|---|---|---|---|
| `kong` | ≥ 3.4.0 | Kong release | Tested matrix: 3.4, 3.5, 3.6, 3.7 |
| `lua-resty-openssl` | ≥ 1.0 | bundled with Kong | SHA-256 incremental hashing |
| `lua-cjson` | bundled | Kong | JSON encoding for side channel |
| `lua-resty-http` | ≥ 0.17 | bundled | Webhook side channel |
| `lua-protobuf` | ≥ 0.5 | LuaRocks | Optional, for protobuf side channel |
| `kong-plugin-ledgerproof-canonicalizer` | 0.1 | LuaRocks | Vendored Rust canonicalizer (LPR §5) compiled to a Lua FFI shim. Same canonical bytes as `lpr-rust`. |
| HSM client | provider-specific | vendor | Out-of-band sidecar (see §5.4) — NOT linked into Kong. |
| LedgerProof Python or TypeScript SDK | ≥ 1.1.0 | PyPI / npm | Optional, recommended for the side-channel consumer to verify receipts locally per C4. |

The plugin links **no** HTTP client to LedgerProof verification nodes. Verification is local (C4). The plugin links a sidecar HSM signer over loopback Unix domain socket; the HSM client library itself runs in a separate process to keep its dependency footprint out of the Kong worker.

---

## 4 · Stream-aware signing pipeline

### 4.1 Stream-start (access phase)

When the request enters Kong:

1. Allocate a `request_id` (UUID v7).
2. Compute `request_hash = SHA-256(canonical(request_envelope))` where `request_envelope` is the canonical CBOR encoding (LPR 1.1 §5) of `{ method, route_path, query, content_type, content_length, request_body_hash, ts_start }`.
3. The `request_body_hash` is computed incrementally as request chunks arrive (no buffering). For unary requests, the hash is final at the end of `access`. For SSE-uplink or streamed-request bodies, the hash is finalized in the request observer.
4. Build the pending entry skeleton:
   ```
   { request_id, ts_start, route, deployer_id, model_id,
     request_hash, profile, status: "pending" }
   ```
5. Insert into per-worker SHM hash table keyed by `request_id`. Eviction policy: TTL of `2 * batch_window_ms + 30s`, LRU under memory pressure.

### 4.2 Stream-end (log phase)

When Kong's `log` phase fires:

1. Compute `response_hash` from the incremental SHA-256 state captured during the response stream.
2. Finalize the entry:
   ```
   { request_id, deployer_id, model_id, profile,
     ts_start, ts_end, duration_ms,
     request_hash, response_hash,
     http_status, response_size_bytes,
     route_path, upstream_id,
     extensions: { ... profile-specific } }
   ```
3. Canonicalize the entry via the vendored Rust canonicalizer; compute `entry_hash = SHA-256(canonical_bytes)`.
4. Push `entry_hash` into the batch accumulator.

### 4.3 Batch accumulation

The batch accumulator is a per-worker (or per-Kong-node, configurable) ring buffer. A timer fires every `batch_window_ms`. Whichever of these conditions first becomes true closes the batch:

- The accumulator holds `batch_max_entries` (default 1000).
- The accumulator's oldest entry is older than `batch_window_ms` (default 1000 ms).

### 4.4 Merkle-batch sign

When the batch closes:

1. Build a binary Merkle tree of leaf hashes per LPR 1.1 §7. Padding rule: duplicate-last-leaf to even up an odd layer.
2. Send the Merkle root to the HSM sidecar via Unix domain socket. The HSM signs `"LPR1" || root` (4-byte tag prepended) using Ed25519 with the key labeled in config.
3. Receive `root_sig` (64 bytes).
4. For each entry `i` in the batch, compute the inclusion proof `π_i` (log₂(N) sibling hashes from leaf to root).

### 4.5 Receipt emission

For each entry in the batch the plugin builds:

```json
{
  "lpr_version": "1.1",
  "profile": "EU-AI-ACT-50-v1.1",
  "entry": { ... },
  "entry_hash": "...",
  "merkle_root": "...",
  "merkle_root_sig": "...",
  "signing_pubkey_id": "lpr-deployer-2026-q3",
  "inclusion_proof": [ ... ],
  "anchor_ref": { "status": "pending" }
}
```

It is emitted to the configured side channel. The plugin does **not** wait for the side channel to acknowledge before returning the response to the user — the response was already returned at `header_filter` time. The side channel emit is best-effort with bounded retry (3 attempts, exponential backoff, then drop to dead-letter queue).

The receipt is independently verifiable offline using the LedgerProof SDK:

```
verify_merkle_proof(entry_hash, inclusion_proof, merkle_root)
   && verify_ed25519(merkle_root, merkle_root_sig, pubkey)
   && (anchor_ref.status == "pending" OR verify_btc_anchor(merkle_root, anchor_ref))
```

This is the C4 boundary. There is no LedgerProof node call in the verification path.

---

## 5 · Configuration example

Full Kong declarative configuration. Sane defaults. Reference deployment.

```yaml
_format_version: "3.0"
plugins:
  - name: ledgerproof
    route: customer-inference-api          # route ID or name
    enabled: true
    config:
      deployer_id: acme-bank-eu-retail-llm    # no email, no PII (C5/GDPR)
      model_id: acme-internal-llm-v3.2
      profile: EU-AI-ACT-50-v1.1
      batch_window_ms: 1000
      batch_max_entries: 1000
      hsm:
        provider: aws-cloudhsm
        key_label: lpr-deployer-2026-q3
        endpoint: unix:/var/run/lpr-hsm-sidecar.sock
        timeout_ms: 5000
      side_channel:
        kind: kafka
        endpoint: kafka://siem-ingest.internal:9092/lpr-receipts
        auth_header: ${{ vault://hcv-1/kafka-bearer }}
        fanout:
          - https://lpr-emitter.internal/v1/forward          # to public /v/{slug} portal
      fail_mode: fail-open
      observability:
        prometheus: true
        trace_sample_rate: 0.01
```

`fail-open` is the default and is recommended for v0.1. The plugin must never block live AI traffic on its own failure path. Customers who require `fail-closed` (e.g., for ISMS-attested high-risk systems) can opt in. `fail-closed` returns HTTP 503 if the plugin cannot enqueue an entry, and is documented as causing availability loss if the HSM sidecar is unhealthy.

---

## 6 · Security model

### 6.1 Threat model summary

| Threat | Mitigation |
|---|---|
| **Replay** — attacker resubmits a captured request to inflate receipt count or grief the operator. | `request_id` is a UUID v7 with millisecond timestamp; deduplicated within the batch window. Receipts include `ts_start` which is signed into the entry. Replays produce a new receipt with a new timestamp; downstream consumers detect via `(deployer_id, request_hash)` dedup window. |
| **Mid-batch HSM key compromise.** | Receipts are scoped to a `signing_pubkey_id`. Key rotation (§6.3) invalidates all subsequent receipts under the old key. Past receipts remain verifiable as long as the public key is published on the registry. Key compromise notice is published as an LPR registry advisory and recorded as an anchored receipt of class `KEY_REVOCATION`. |
| **Batch-root revocation.** | A revoked root is recorded as an anchored `BATCH_REVOCATION` receipt naming the root and the reason. Verifiers consult the registry's revocation list at verify time. |
| **Partial-batch failure** — HSM signs but emit fails for some entries. | The batch root and signature are durable (written to local WAL before emit begins). Receipts for un-emitted entries can be regenerated from the WAL within the WAL retention window (default 24 h). |
| **Batch-window timing attack** — adversary times requests against batch close to predict root composition. | The composition of a batch (which requests are siblings) is not security-sensitive. The Merkle inclusion proof reveals only that the entry was part of the batch; it does not reveal other entries' contents. |
| **Side-channel exfiltration.** | The receipt body is the canonical LPR entry plus inclusion proof. By GDPR schema constraint, the entry contains no PII (deployer_id is a non-personal identifier, model_id is an internal identifier, no email/name/IP). |
| **HSM sidecar impersonation.** | Unix domain socket is permission-locked to the Kong user. PKCS#11 / KMIP credentials live in the sidecar, never in Kong config. |
| **Configuration tampering at the Kong admin API.** | Out of scope for the plugin. Kong RBAC and admin API protection are the operator's responsibility. The plugin emits a `CONFIG_CHANGE` receipt on every configuration reload (deployer_id, route, config_hash, ts) so configuration history is anchorable. |

### 6.2 HSM integration boundaries

The HSM client library runs in a sidecar process. The plugin speaks to it over a Unix domain socket with a small, schema-pinned RPC:

- `sign(key_label, message) → sig` — single Ed25519 signature
- `pubkey(key_label) → pubkey` — fetch the public key
- `health() → ok` — health check (used by `fail-closed`)

The sidecar is shipped as a separate package (`lpr-hsm-sidecar`). It handles PKCS#11 (Thales Luna), KMIP, AWS CloudHSM client, Azure Dedicated HSM client, YubiHSM2 connector, and the cloud KMS REST APIs. Each provider is a feature flag; the operator installs only what they use. No HSM provider libraries are statically linked into the Kong worker.

### 6.3 Key rotation

Key rotation is an operator-driven action. Recommended cadence is quarterly. The operator:

1. Generates a new key in the HSM under a new `key_label` (e.g., `lpr-deployer-2026-q4`).
2. Publishes the new public key to the LedgerProof registry.
3. Updates the Kong plugin config to reference the new label.
4. Issues a `KEY_ROTATION` receipt under the old key referencing the new key's public-key fingerprint.

The old key remains in the HSM but is no longer used to sign new batches. Receipts already in the field continue to verify against the old key's published public key.

### 6.4 Logging and observability without PII

The plugin emits Prometheus metrics: receipt rate, batch close rate, batch-size histogram, HSM signing latency histogram, side-channel emit success rate, side-channel dead-letter queue depth, in-memory pending-entry table size. No metric tags include request content, response content, request URL beyond the route ID, or any header value beyond the response status code class.

Tracing is sampled (default 1% via the `trace_sample_rate` knob), follows W3C trace context. Spans include phase boundaries and HSM round-trip latency. Spans do **not** include request/response bodies.

Per C5, the customer-facing compliance dashboard for this data is the customer's SIEM (Splunk / Datadog / ServiceNow / Vanta / Drata). The plugin's job ends at emission to that side channel. `/v/{slug}` is the public LedgerProof portal and is fed by the optional fanout to the LedgerProof emitter; it is not the enterprise's compliance UI.

---

## 7 · Operational boundaries (what this plugin does NOT do)

1. **Does NOT inspect inbound third-party data.** A request to retrieve training data from an external vendor, a Snowflake query against a third-party dataset, an Airflow operator that fetches from Hugging Face — none of these are this plugin's job. Inbound data attestation is provided by the Snowflake UDF / Databricks notebook / Airflow operator / Prefect task adapters, specified in `inbound-snowflake-spec.md` (planned v0.2).
2. **Does NOT modify response payloads.** No header is added to the response. No trailer. No body modification. Customers receive byte-identical responses with or without the plugin enabled.
3. **Does NOT phone home to LedgerProof verification nodes.** Verification nodes are an optional convenience for SaaS consumers who do not want to run the SDK themselves (C4). The plugin emits to a side channel and stops. Whether the customer's SIEM forwards anything to LedgerProof is the customer's decision.
4. **Does NOT use Kong's `body_filter` phase.** `body_filter` requires the gateway to buffer the response body across the phase boundary, which breaks streaming AI workloads (SSE, chunked HTTP, gRPC server-streaming) and imposes a 50–200 ms p99 latency penalty even on unary responses at moderate body sizes. The plugin computes response hashes incrementally without buffering.
5. **Does NOT sign per-request via HSM.** Per-request HSM signing would cap the plugin at the HSM's raw signature rate (5–50 ms / sig). Merkle-batch reduces this to 1 HSM call per `batch_window_ms` regardless of request rate.
6. **Does NOT enforce policy.** The plugin observes and emits. It does not block requests on policy violations. Policy enforcement is the deployer's responsibility and is layered separately (typically via the customer's existing Kong rate-limiting / acl / oauth2 plugins).

---

## 8 · Performance benchmarks (targets — to be validated)

All targets are end-to-end including plugin overhead, on a Kong 3.6 node with 8 vCPU, 32 GiB RAM, attached to an AWS CloudHSM cluster (3 partitions) and a Kafka side channel. Single AZ. Reference workload: unary 4 KB request / 8 KB response, no upstream-induced latency.

| Throughput | p50 added latency | p95 added latency | p99 added latency |
|---|---|---|---|
| 100 req/s | < 0.5 ms | < 1.0 ms | < 2.0 ms |
| 1000 req/s | < 0.6 ms | < 1.5 ms | < 3.0 ms |
| 10000 req/s | < 1.0 ms | < 3.0 ms | < 8.0 ms |

**HSM signing rate ceiling:** ~10 signatures per second per HSM partition for Thales Luna 7; ~50 sig/s for AWS CloudHSM. At `batch_window_ms = 1000`, that translates to an effective receipt rate of 50,000 receipts/s per CloudHSM partition. This is well above the AI-inference request rates seen at Tier-1 EU enterprises.

**Memory footprint:** Pending-entry table holds up to `(batch_window_ms / 1000) * peak_rps` entries. At 10000 req/s and 1 s window that's 10000 entries × ~512 B per pending entry = ~5 MiB per worker. Batch accumulator is bounded by `batch_max_entries × ~64 B per leaf` = ~64 KiB.

**Failure modes:**

- **HSM unavailable.** `fail-open` mode: pending batches accumulate; when HSM recovers, signing resumes. WAL preserves entries up to 24 h. `fail-closed` mode: plugin returns 503 for new requests until HSM recovers.
- **Batch overflow.** If `batch_max_entries` is hit faster than `batch_window_ms`, an extra batch closes early. There is no overflow loss.
- **Downstream side-channel failure.** Receipts queue to the dead-letter queue. Operators monitor DLQ depth via Prometheus and replay when the side channel recovers.

These targets are stated for the validation engineer (Senior Protocol Engineer, post-Jul 13 start). Benchmark suite under `tests/bench/` to be implemented in week 4 (§9.4).

---

## 9 · Implementation plan (4-week sprint)

Engineering owner: Senior Protocol Engineer (start Jul 13 2026). The plan assumes 4 weeks of focused work between Jul 13 and Aug 10, with a code-freeze on Aug 2 (KS5 ship) and a 1-week stabilization on the live plugin between Aug 3 and Aug 10.

### Week 1 (Jul 13 – Jul 19) — skeleton

- `kong-plugin-ledgerproof` repo scaffolded with `kong-pongo` test rig.
- `schema.lua` finalized against this spec.
- `access` and `log` handlers stubbed; pending-entry SHM table working end-to-end.
- Vendored Rust canonicalizer compiled to `.so` and FFI-bound. Differential test against `lpr-rust` on 10k sample entries — byte-identical canonical output required.

### Week 2 (Jul 20 – Jul 26) — batch + HSM

- Batch accumulator with timer-driven and size-driven close.
- Merkle tree builder; inclusion proof generator. Differential test against `lpr-rust` Merkle.
- HSM sidecar process; UDS RPC; AWS KMS and YubiHSM2 providers (the two we can stand up by Jul 20 in our own infra).
- WAL for in-flight batches; recovery test.

### Week 3 (Jul 27 – Aug 2) — side channels + observability

- Kafka, webhook, syslog, file, stdout side channels.
- Prometheus metrics endpoint.
- W3C trace context propagation.
- Configuration reload safety (no in-flight batches lost on reload).
- `fail-open` / `fail-closed` semantics verified.
- KS5 ship: tagged v0.1.0 published to LuaRocks and GitHub Releases at 14:00 CET on Aug 2.

### Week 4 (Aug 3 – Aug 10) — stabilization

- Benchmark suite executed; published numbers vs §8 targets.
- Documentation: install guide, configuration reference, operations runbook, threat-model document.
- Security review hand-off to NCC Group (continuation of the LPR 1.1 protocol audit).
- v0.1.1 patch release if benchmarks expose any path that misses §8 targets by more than 25%.

---

## 10 · Release timeline + KS5

| Date | Milestone |
|---|---|
| 2026-06-22 | Senior Protocol Engineer offer signed. |
| 2026-07-13 | Senior Protocol Engineer start; spec handed off; week 1 begins. |
| 2026-07-19 | Skeleton complete. |
| 2026-07-26 | Batch + HSM complete. |
| 2026-08-02 | **KS5 — v0.1.0 ships.** EU AI Act Article 50 enforcement day. Published to LuaRocks (`kong-plugin-ledgerproof-0.1.0-1`) and GitHub Releases. Blog post on `engineering.ledgerproofhq.io`. Konnect custom-plugin upload tested against a customer staging Konnect tenant. |
| 2026-08-10 | v0.1.1 stabilization release if needed. |
| 2026-09 | v0.2 planning kickoff; APISIX assessment; inbound adapter spec scoping. |

The KS5 ship is binding. If week 3 falls behind by more than 2 days, the scope contraction protocol is: drop `azure-key-vault`, `gcp-kms`, and `syslog` from v0.1.0 (defer to v0.1.1). HSM coverage at ship is `aws-cloudhsm`, `aws-kms`, `yubihsm2`. Side channels at ship are `kafka`, `webhook`, `file`, `stdout`. Everything else slips to v0.1.1 the following week.

---

## 11 · Out of scope (deferred to v0.2+)

- **Inbound surface adapters** (Snowflake UDF, Databricks notebook, Airflow operator, Prefect task). Separate spec `inbound-snowflake-spec.md` planned for v0.2.
- **Envoy filter.** Envoy is the analog of Kong for service-mesh-published APIs; a separate `envoy-filter-ledgerproof` spec covers it. Planned v0.2.
- **Apache APISIX plugin.** Subject to demand. Planned v0.2.
- **gRPC streaming methods.** Unary gRPC works in v0.1 via Kong's gRPC proxy. Server-streaming and bidi-streaming gRPC have additional hash-state-machine requirements deferred to v0.2.
- **In-Kong verification.** Verification stays local-only per C4. If, post-v0.1, an enterprise wants the plugin to additionally verify upstream-provided receipts (e.g., the inference backend itself emits LPR receipts and Kong wants to validate them before relaying), that becomes a `kong-plugin-ledgerproof-verify` companion plugin — separate code, separate release.
- **Policy enforcement.** As stated in §7.6.
- **LangGraph node middleware.** A LangGraph-side middleware (C7) is tracked separately; it is not a Kong concern.
- **Receipt redaction.** GDPR Article 17 erasure flows are handled at the Foundation registry level, not at the plugin.

---

## 12 · Open questions for review

1. **`batch_window_ms` default.** 1000 ms minimizes anchor latency. Some enterprises with extremely steady traffic could go to 5000 ms to reduce HSM call rate further. Should we expose a recommended-defaults table per request-rate band?
2. **Per-route vs per-worker batch.** v0.1 batches per worker. For very-high-cardinality multi-deployer-on-one-Kong-node deployments, a per-route batch may be preferable to keep `deployer_id` separation cryptographically clean. Decision: defer to v0.2 unless a Founding Member surfaces the requirement in pilot.
3. **Side-channel acknowledgment durability.** v0.1 fire-and-forget with DLQ. A `wait_for_ack` mode (block log phase until ack) would catch more failures but at the cost of log-phase latency. Default stays fire-and-forget; opt-in `wait_for_ack` planned for v0.1.1.
4. **`signing_pubkey_id` discovery.** The verifier needs the public key. v0.1 publishes pubkeys to the LedgerProof registry. Should we also support a JWKS endpoint operated by the deployer for air-gapped consumers? Likely yes; defer mechanism to v0.2.
5. **Kong Enterprise vs OSS feature parity.** v0.1 uses no Kong Enterprise-only primitives. Confirmed against the 3.7 Enterprise-only feature list. Should we offer Vault integration for `auth_header` secret loading? Decision: yes, but as an optional config form, not a hard requirement.
6. **C2PA assertion emission.** Inference outputs that are themselves media (image, audio, video) could be C2PA-signed with the receipt embedded as an assertion. Out of scope for v0.1 Kong plugin; lives in the SDK. Confirm at week-3 review.
7. **Konnect distribution channel.** Kong's Konnect plugin marketplace approval cycle is 4–8 weeks. We will not block KS5 on marketplace approval. Direct LuaRocks install via Konnect custom plugin is supported on day 1.
8. **C8 counterweight.** This plugin ships in the same window as the C8 counterweight anchor decision. If a US/EU counterweight anchor is named publicly in this window, the v0.1.0 blog post should reference it; if not, the post stands on EU-Article-50 readiness alone. Decision belongs to the Founder, not engineering.

— end of spec —
