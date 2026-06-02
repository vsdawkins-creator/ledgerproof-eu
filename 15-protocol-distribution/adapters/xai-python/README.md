# ledgerproof-xai

LedgerProof adapter for **xAI Grok**, which exposes an OpenAI-compatible REST API
at `https://api.x.ai/v1`. This package wraps the official
[`openai` Python SDK](https://github.com/openai/openai-python) configured for that
endpoint and emits signed EU AI Act **Article 50** transparency receipts as a
side channel — your xAI response is returned unmodified.

```
pip install ledgerproof-xai
```

## Why xAI Grok matters for Article 50

xAI Grok is deployed in real time on the X platform. That puts it directly inside
the surface area that Article 50(4) of the EU AI Act calls "text generated or
manipulated by an AI system" disseminated "for the purpose of informing the public
on matters of public interest." Social-media AI summarisation, real-time
news-grounded inference, and image-input ("see this photo") chat are exactly the
deployer use cases where a verifiable receipt — bound to the prompt, the
response, and (where applicable) the real-time data sources or input image — is
most valuable for proving compliance to a regulator or end user.

This adapter ships four schemas tuned to those Grok-specific scenarios:

| Schema                              | Article basis | Use when |
|-------------------------------------|---------------|----------|
| `chatbot_session/v1`                | Art. 50(1)    | Standard conversational Grok inference |
| `generated_content/v1`              | Art. 50(2)    | Synthetic content output (text/image/audio/video) |
| `realtime_data_inference/v1`        | Art. 50(1)/(4) | Grok used live web / X-platform grounding |
| `vision_inference/v1`               | Art. 50(2)    | `grok-2-vision` image-input inference |

## 5-minute quickstart

```python
from ledgerproof_xai import LedgerProofXAI

# Defaults: base_url=https://api.x.ai/v1, api_key=$XAI_API_KEY
client = LedgerProofXAI(
    deployer_id="urn:eu:deployer:acme-media-de",
    regulatory_context={"schema": "chatbot_session/v1", "jurisdiction": "EU"},
)

resp = client.chat.completions.create(
    model="grok-2-latest",
    messages=[{"role": "user", "content": "Hello"}],
)

print(resp.choices[0].message.content)
# A signed receipt has been emitted to the configured emitter
# (stdout LogEmitter by default).
```

## Three integration patterns

### 1. Client wrapper (recommended)

```python
from ledgerproof_xai import LedgerProofXAI, LedgerProofAsyncXAI

client = LedgerProofXAI(deployer_id="urn:eu:deployer:acme")
async_client = LedgerProofAsyncXAI(deployer_id="urn:eu:deployer:acme")
```

Works with both **non-streaming** (`stream=False`) and **streaming**
(`stream=True`) chat completions. Streaming uses incremental SHA-256
over each chunk (constraint **C6**).

### 2. Decorator

```python
import os
from openai import OpenAI
from ledgerproof_xai import lpr_track

client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
)

@lpr_track(deployer_id="urn:eu:deployer:acme")
def ask(question: str, *, messages):
    return client.chat.completions.create(model="grok-2-latest", messages=messages)
```

### 3. Manual emission

```python
import os
from openai import OpenAI
from ledgerproof_xai import emit_receipt

client = OpenAI(api_key=os.environ["XAI_API_KEY"], base_url="https://api.x.ai/v1")
resp = client.chat.completions.create(
    model="grok-2-latest",
    messages=[{"role": "user", "content": "hi"}],
)
emit_receipt(resp, deployer_id="urn:eu:deployer:acme")
```

## Real-time data attribution (Grok's distinctive surface)

When you rely on Grok's live X-platform / web grounding, switch schemas:

```python
import hashlib, json
from ledgerproof_xai import LedgerProofXAI

sources = [
    {"url": "https://x.com/example/status/1234", "captured_at": "2026-08-02T09:15:00Z"},
]
sources_hash = hashlib.sha256(
    json.dumps(sorted(sources, key=lambda s: s["url"]), sort_keys=True).encode()
).hexdigest()

client = LedgerProofXAI(
    deployer_id="urn:eu:deployer:acme-media-de",
    regulatory_context={
        "schema": "realtime_data_inference/v1",
        "realtime_data_used": True,
        "realtime_sources_sha256": sources_hash,
        "public_interest_text": True,
    },
)
```

The adapter does **not** fetch or verify the sources for you (constraint **C4**:
local verification only). It records the hash that you compute. Pick a canonical
representation, document it in your deployer policy, and an auditor will be able
to reproduce the binding from the materials you preserve.

## Vision inference (`grok-2-vision`)

```python
from ledgerproof_xai import LedgerProofXAI

client = LedgerProofXAI(
    deployer_id="urn:eu:deployer:acme",
    regulatory_context={"schema": "vision_inference/v1"},
)
resp = client.chat.completions.create(
    model="grok-2-vision",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What is in this image?"},
            {"type": "image_url", "image_url": {"url": "https://..."}},
        ],
    }],
)
```

The wrapper auto-detects OpenAI-style `image_url` content blocks and records
`image_count` + `content_modality="image"`. To bind the receipt cryptographically
to the exact image bytes/URL list, pre-compute `image_input_sha256` and pass it
via `regulatory_context`.

## Custom emitters

```python
from ledgerproof_xai import LedgerProofXAI, WebhookEmitter, QueueEmitter

client = LedgerProofXAI(
    deployer_id="urn:eu:deployer:acme",
    emitter=WebhookEmitter(url="https://receipts.acme.example/ingest"),
)
```

## Scope and discipline (C1–C8)

This adapter implements the LedgerProof protocol with the following discipline:

- **C1 — No regulator endorsement.** This package is not endorsed by the European
  Commission, EU AI Office, or any national supervisory authority. It does **not**
  provide an Article 40 presumption of conformity.
- **Not endorsed by xAI.** This is an independent adapter built on top of xAI's
  publicly documented OpenAI-compatible API. It is not affiliated with, sponsored
  by, or endorsed by xAI Corp. "Grok" and "xAI" are trademarks of their respective
  owner; used here for descriptive interoperability purposes only.
- **C4 — Offline verification.** Receipts are verifiable offline against the
  published protocol public key and Bitcoin OP_RETURN anchor. The adapter does
  not phone home. Real-time-data attribution hashes are computed locally from
  deployer-controlled inputs — the adapter does not fetch or validate sources.
- **C6 — Stream-aware signing.** Streaming completions are hashed incrementally
  so the receipt covers the full reconstructed text.
- **C7 — Side-channel only.** This adapter never modifies the xAI response.
  Receipts emit through a separate emitter (log/webhook/queue), and emitter
  failures never propagate into the caller path.

### What this adapter does NOT do

- Does **not** address Article 9 (risk management), Article 10 (data governance),
  Article 13 (transparency to deployers), Article 15 (accuracy/robustness/
  cybersecurity), or Article 72 (post-market monitoring).
- Does **not** claim Article 40 presumption of conformity.
- Does **not** claim xAI Corp. endorsement or affiliation.
- Does **not** validate, fetch, or audit real-time data sources used by Grok.
  The deployer must establish a canonical source-attribution policy and compute
  the source hash from that policy's outputs.
- Provides the **Article 50 evidence layer only** for users of xAI Grok via the
  OpenAI-compatible API.

## Known limitations (v0.1)

- Ephemeral in-process Ed25519 keys only. HSM-backed signing (AWS KMS, GCP KMS,
  Azure Key Vault, YubiHSM2) lands in v0.2.
- xAI may expose Grok-specific endpoints in the future (e.g. native real-time
  search APIs) that fall outside the OpenAI-compatible surface; those will be
  added in v0.2 once xAI documents stable contracts.
- Vision-input image hashing is deployer-computed: the adapter detects the
  presence of `image_url` blocks but does not download or hash remote images
  (C4 discipline — no network egress).

## Roadmap

- v0.2: Native xAI endpoint coverage (if/when xAI publishes Grok-specific APIs
  beyond the OpenAI-compatible surface).
- v0.2: Pluggable HSM-backed signer.
- v0.3: Built-in Merkle batcher with periodic flush to anchoring service.

## License

Apache 2.0. See `LICENSE`.
