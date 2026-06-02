# ledgerproof-huggingface

LedgerProof adapter for the [Hugging Face Inference API](https://huggingface.co/docs/huggingface_hub/guides/inference)
(`huggingface_hub`) **and** local [Transformers](https://huggingface.co/docs/transformers) pipelines.
Emits signed EU AI Act **Article 50** transparency receipts as a side channel —
your Hugging Face response is returned unmodified.

```
pip install ledgerproof-huggingface
# add local-inference support:
pip install "ledgerproof-huggingface[transformers]"
```

## Why Hugging Face — EU AI sovereignty

Hugging Face is **EU-headquartered** (Paris / NYC), and its model hub is the
de-facto distribution point for open-weights models that EU deployers can
inspect, fine-tune, self-host, and audit. The `eu_open_model_hosted/v1`
schema in this adapter records that hosting attribution explicitly so the
resulting receipts carry the EU sovereignty signal end-to-end.

For deployers running models on-prem (banks, insurers, telcos, public sector),
`LedgerProofPipeline` wraps a local `transformers.Pipeline` and emits a
`local_inference/v1` receipt that captures the host environment — proof that
the inference ran inside the deployer's controlled perimeter.

## 5-minute quickstart (hosted Inference API)

```python
from ledgerproof_huggingface import LedgerProofInferenceClient

client = LedgerProofInferenceClient(
    deployer_id="urn:eu:deployer:acme-bank-de",
    regulatory_context={
        "schema": "eu_open_model_hosted/v1",
        "jurisdiction": "EU",
        "model_license": "llama-3.1-community-license",
        "open_weights": True,
    },
    model="meta-llama/Llama-3.1-70B-Instruct",
    token="hf_...",
)

resp = client.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
)
print(resp.choices[0].message.content)
# A signed receipt has been emitted to the configured emitter
# (stdout LogEmitter by default).
```

## 5-minute quickstart (local Transformers pipeline)

```python
from transformers import pipeline
from ledgerproof_huggingface import LedgerProofPipeline

pipe = pipeline("text-generation", model="meta-llama/Llama-3.1-8B-Instruct")

lp_pipe = LedgerProofPipeline(
    pipe,
    deployer_id="urn:eu:deployer:acme-bank-de",
    regulatory_context={"schema": "local_inference/v1", "jurisdiction": "EU"},
)

result = lp_pipe("Hello, world", max_new_tokens=20)
# signed local_inference/v1 receipt emitted as a side channel
```

## Four integration patterns

### 1. InferenceClient wrapper (hosted API)

```python
from ledgerproof_huggingface import (
    LedgerProofInferenceClient,
    LedgerProofAsyncInferenceClient,
)

client = LedgerProofInferenceClient(deployer_id="urn:eu:deployer:acme", model="...")
async_client = LedgerProofAsyncInferenceClient(deployer_id="urn:eu:deployer:acme", model="...")
```

Works with both `chat_completion()` and `text_generation()`, both
non-streaming (`stream=False`) and streaming (`stream=True`). Streaming uses
incremental SHA-256 over each chunk (constraint **C6**).

### 2. Pipeline wrapper (local Transformers)

```python
from transformers import pipeline
from ledgerproof_huggingface import LedgerProofPipeline

pipe = pipeline("text-generation", model="...")
lp = LedgerProofPipeline(pipe, deployer_id="urn:eu:deployer:acme")
out = lp("Hello")
```

### 3. Decorator

```python
from huggingface_hub import InferenceClient
from ledgerproof_huggingface import lpr_track

client = InferenceClient(model="meta-llama/Llama-3.1-70B-Instruct")

@lpr_track(deployer_id="urn:eu:deployer:acme")
def ask(question: str):
    return client.chat_completion(
        messages=[{"role": "user", "content": question}],
    )
```

### 4. Manual emission

```python
from huggingface_hub import InferenceClient
from ledgerproof_huggingface import emit_receipt

client = InferenceClient(model="meta-llama/Llama-3.1-70B-Instruct")
resp = client.chat_completion(messages=[...])
emit_receipt(resp, deployer_id="urn:eu:deployer:acme", messages=[...])
```

## Receipt schemas

| schema_id                   | Article 50 basis | Use when                                                      |
| --------------------------- | ---------------- | ------------------------------------------------------------- |
| `chatbot_session/v1`        | 50(1)            | A natural person is talking to an AI system                   |
| `generated_content/v1`      | 50(2)            | The output is synthetic media (text/image/audio/video)        |
| `eu_open_model_hosted/v1`   | 50(1)            | Hosted on Hugging Face Inference API (EU sovereignty signal)  |
| `local_inference/v1`        | 50(1)            | Self-hosted Transformers pipeline (on-prem perimeter)         |

## Custom emitters

```python
from ledgerproof_huggingface import (
    LedgerProofInferenceClient, WebhookEmitter, QueueEmitter,
)

client = LedgerProofInferenceClient(
    deployer_id="urn:eu:deployer:acme",
    emitter=WebhookEmitter(url="https://receipts.acme.example/ingest"),
    model="meta-llama/Llama-3.1-70B-Instruct",
)
```

## GDPR discipline

Receipts MUST NOT carry plaintext PII. The schema layer:

- Stores only SHA-256 hashes of `prompt_sha256` and `response_sha256` — never raw text.
- Rejects `user_pseudonym` values that look like raw email addresses
  (GDPR Art. 5(1)(c) — data minimization).
- Recommends URN-style `deployer_id` (e.g. `urn:eu:deployer:acme-bank-de`).

## Scope and discipline (C1–C8)

This adapter implements the LedgerProof protocol with the following discipline:

- **C1 — No regulator endorsement.** This package is **not endorsed by Hugging
  Face**, by the European Commission, the EU AI Office, or any national
  supervisory authority. It does **not** provide an Article 40 presumption of
  conformity. "Hugging Face" is a trademark of Hugging Face, Inc., used here
  nominatively to identify the wrapped SDK.
- **C4 — Offline verification.** Receipts are verifiable offline against the
  published protocol public key and Bitcoin OP_RETURN anchor. The adapter does
  not phone home.
- **C6 — Stream-aware signing.** Streaming completions are hashed
  incrementally so the receipt covers the full reconstructed text, not just
  the final chunk.
- **C7 — Side-channel only.** This adapter never modifies the Hugging Face
  response. Receipts emit through a separate emitter (log/webhook/queue).
  Receipt failures never propagate into the caller's request path.

### What this adapter does NOT do

- Does **not** address Article 9 (risk management), Article 10 (data
  governance), Article 13 (transparency to deployers), Article 15
  (accuracy/robustness/cybersecurity), or Article 72 (post-market monitoring).
- Does **not** claim Article 40 presumption of conformity.
- Does **not** claim endorsement by Hugging Face, Inc., the European
  Commission, the EU AI Office, or any national supervisory authority.
- Provides the **Article 50 evidence layer only** for users of the
  Hugging Face Hub and Transformers libraries.

## Roadmap

- v0.2: Coverage for HF `text-to-image`, `automatic-speech-recognition`, and
  `image-to-text` Inference API tasks — auto-binding to `generated_content/v1`.
- v0.2: Pluggable HSM-backed signer (AWS KMS, GCP KMS, Azure Key Vault, YubiHSM2).
- v0.3: Built-in Merkle batcher with periodic flush to anchoring service.

## License

Apache 2.0. See `LICENSE`.
