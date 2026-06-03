# ledgerproof-qwen

LedgerProof adapter for the [Alibaba DashScope / Qwen Python SDK](https://help.aliyun.com/zh/dashscope/) (`dashscope>=1.20`).

Emits **side-channel cryptographic transparency receipts** for AI-touched interactions, suitable as an evidence layer
for **EU AI Act Article 50** (transparency obligations for providers and deployers of AI systems).

This adapter works with anyone using the DashScope SDK directly:

- `dashscope.Generation.call(...)` — sync, non-streaming and streaming
- `dashscope.AioGeneration.call(...)` — async
- `dashscope.MultiModalConversation` — vision/audio Qwen variants
- Function / tool calls — recorded into the `tool_uses` block of the receipt
- **Chinese-origin AI attribution** (`multilingual_chinese_inference/v1`) — record Chinese-language disclosure facts and regional-endpoint routing
- **Cross-jurisdictional routing** (`cross_jurisdictional_routing/v1`) — record Singapore / Hong Kong / international endpoint selection that avoids mainland-China data residency

## 5-minute quickstart

```bash
pip install ledgerproof-qwen
export DASHSCOPE_API_KEY=...
```

```python
from ledgerproof_qwen import LedgerProofQwen, LogEmitter

client = LedgerProofQwen(
    deployer_id="acme-corp-eu",
    api_key="...",  # or read from DASHSCOPE_API_KEY
    emitter=LogEmitter(),
)

response = client.generation.call(
    model="qwen-max",
    messages=[{"role": "user", "content": "Hello"}],
)

print(response.output.text)
# A signed receipt has already been emitted to the log emitter side-channel.
```

The DashScope `GenerationResponse` is returned **unchanged**. The receipt is emitted to the side channel only.

## Three integration patterns

1. **Client wrapper** (recommended) — `LedgerProofQwen` wraps the DashScope `Generation` interface and
   intercepts `call(...)` whether streaming or non-streaming. `LedgerProofAsyncQwen` wraps `AioGeneration`.
2. **Decorator** — `@lpr_track(deployer_id="...")` for user-defined functions that already wrap a DashScope call.
3. **Manual emission** — `emit_receipt(response, deployer_id, regulatory_context)` for full control.

See `examples/` for runnable code:

- `01_qwen_quickstart.py` — minimum viable wrap of `Generation.call()`
- `02_singapore_endpoint.py` — cross-jurisdictional routing receipt
- `03_multilingual_chinese.py` — Chinese-language disclosure receipt

## Chinese-origin AI: Article 50 implications

The EU AI Act's Article 50 transparency obligations apply to **deployers** of AI systems in the EU,
regardless of where the underlying model was trained or where the model provider is headquartered.
Deploying a Chinese-origin foundation model in the EU does not exempt the deployer from Article 50
disclosure obligations; in some sector overlays (FSI / DORA, MiFID II suitability, GDPR Schrems-II
analysis) it may add documentation requirements.

This adapter ships two Qwen-specific schemas to help deployers record those facts inline with the
Article 50 receipt:

```python
from ledgerproof_qwen import (
    ChineseInferenceAttestation,
    CrossJurisdictionalRoute,
    LedgerProofQwen,
)

client = LedgerProofQwen(
    deployer_id="acme-bank-eu",
    schema="multilingual_chinese_inference/v1",
    chinese_inference=ChineseInferenceAttestation(
        chinese_disclosure_shown=True,
        chinese_disclosure_text_hash_sha256_hex="...",  # hash of zh-CN UI disclosure
        endpoint_region="singapore",
        avoids_mainland_residency=True,
    ),
)
```

For the cross-jurisdictional schema:

```python
client = LedgerProofQwen(
    deployer_id="acme-bank-eu",
    schema="cross_jurisdictional_routing/v1",
    cross_jurisdictional_route=CrossJurisdictionalRoute(
        endpoint_region="singapore",
        endpoint_base_url="https://dashscope-intl.aliyuncs.com",
        avoids_mainland_residency=True,
        transfer_mechanism="SCCs-2021/914 + supplementary measures",
    ),
)
```

These attestation blocks are **descriptive metadata only** — see the scope disclaimer below.

## Regional endpoints

DashScope exposes regional endpoints. The mainland-China endpoint is the default; Singapore and
Hong Kong endpoints exist for international traffic and are commonly chosen by EU deployers to
manage GDPR Schrems-II / cross-border data-transfer exposure:

| Region        | Base URL (illustrative)                       | Typical use case                          |
|---------------|-----------------------------------------------|-------------------------------------------|
| Mainland CN   | `https://dashscope.aliyuncs.com`              | Domestic-China deployments                |
| Singapore     | `https://dashscope-intl.aliyuncs.com`         | International / EU-facing traffic         |
| Hong Kong     | (region-specific)                             | International / EU-facing traffic         |

LedgerProof records the deployer-asserted endpoint region in the receipt. LedgerProof does **not**
verify the endpoint URL out-of-band; the receipt is an attestation, not a network audit.

## Architectural discipline (C1, C4, C6, C7)

This adapter is implemented under the LedgerProof protocol's load-bearing constraints:

- **C1**: No claim of regulator endorsement. No claim of Article 40 presumption of conformity.
  LedgerProof is **not endorsed by Alibaba Cloud**, Alibaba Group, the European Commission, the
  AI Office, the Cyberspace Administration of China, or any national competent authority.
- **C4**: Local verification only. The adapter does **not** phone home to LedgerProof servers
  during normal operation.
- **C6**: Stream-aware signing. Streaming responses are signed using an incremental SHA-256 over
  text deltas; the body is never buffered in full.
- **C7**: Side-channel emission only. The adapter **cannot and does not modify** the DashScope
  response payload.

## GDPR data-minimisation

Receipts never carry raw prompt or response text. Content is referenced by SHA-256 hash + byte
length only. Identifier fields (`deployer_id`, `user_session_id`) reject email-shaped strings to
prevent accidental direct-identifier leakage.

## Scope disclaimer

LedgerProof provides an **evidence layer for Article 50 transparency obligations only**.

It does **not** cover:

- Article 9 (risk management system)
- Article 10 (data and data governance)
- Article 13 (transparency and information to deployers)
- Article 15 (accuracy, robustness, and cybersecurity)
- Article 72 (post-market monitoring)

LedgerProof does **not** confer presumption of conformity under Article 40. LedgerProof is **not
endorsed by Alibaba Cloud**, Alibaba Group, the European Commission, the AI Office, any national
competent authority, or any Chinese regulator (including the Cyberspace Administration of China).

The `ChineseInferenceAttestation` and `CrossJurisdictionalRoute` blocks are deployer-asserted
descriptive metadata. They are **not** certifications of GDPR Schrems-II adequacy, of compliance
with the Chinese Generative AI Measures, of compliance with the Personal Information Protection
Law (PIPL), or any other regulatory finding.

This adapter wraps the official Alibaba DashScope Python SDK; it is **not affiliated with Alibaba
Cloud, Alibaba Group, or any Alibaba subsidiary**.

## License

Apache 2.0. Copyright 2026 LedgerProof Foundation (in formation: US 501(c)(3) Delaware + Dutch
Stichting EU subsidiary).
