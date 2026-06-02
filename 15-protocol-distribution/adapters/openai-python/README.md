# ledgerproof-openai

LedgerProof adapter for the official [OpenAI Python SDK](https://github.com/openai/openai-python).
Emits signed EU AI Act **Article 50** transparency receipts as a side channel — your
OpenAI response is returned unmodified.

```
pip install ledgerproof-openai
```

## 5-minute quickstart

```python
from ledgerproof_openai import LedgerProofOpenAI

client = LedgerProofOpenAI(
    deployer_id="urn:eu:deployer:acme-bank-de",
    regulatory_context={"schema": "chatbot_session/v1", "jurisdiction": "EU"},
)

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)

print(resp.choices[0].message.content)
# A signed receipt has been emitted to the configured emitter
# (stdout LogEmitter by default).
```

## Three integration patterns

### 1. Client wrapper (recommended)

```python
from ledgerproof_openai import LedgerProofOpenAI, LedgerProofAsyncOpenAI

client = LedgerProofOpenAI(deployer_id="urn:eu:deployer:acme")
async_client = LedgerProofAsyncOpenAI(deployer_id="urn:eu:deployer:acme")
```

Works with both **non-streaming** (`stream=False`) and **streaming**
(`stream=True`) chat completions. Streaming uses incremental SHA-256
over each chunk (constraint **C6**).

### 2. Decorator

```python
from openai import OpenAI
from ledgerproof_openai import lpr_track

client = OpenAI()

@lpr_track(deployer_id="urn:eu:deployer:acme")
def ask(question: str):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": question}],
    )
```

### 3. Manual emission

```python
from openai import OpenAI
from ledgerproof_openai import emit_receipt

client = OpenAI()
resp = client.chat.completions.create(...)
emit_receipt(resp, deployer_id="urn:eu:deployer:acme")
```

## Custom emitters

```python
from ledgerproof_openai import LedgerProofOpenAI, WebhookEmitter, QueueEmitter

client = LedgerProofOpenAI(
    deployer_id="urn:eu:deployer:acme",
    emitter=WebhookEmitter(url="https://receipts.acme.example/ingest"),
)
```

## Scope and discipline (C1–C8)

This adapter implements the LedgerProof protocol with the following discipline:

- **C1 — No regulator endorsement.** This package is not endorsed by the European
  Commission, EU AI Office, or any national supervisory authority. It does **not**
  provide an Article 40 presumption of conformity.
- **C4 — Offline verification.** Receipts are verifiable offline against the published
  protocol public key and Bitcoin OP_RETURN anchor. The adapter does not phone home.
- **C6 — Stream-aware signing.** Streaming completions are hashed incrementally so the
  receipt covers the full reconstructed text.
- **C7 — Side-channel only.** This adapter never modifies the OpenAI response. Receipts
  emit through a separate emitter (log/webhook/queue).

### What this adapter does NOT do

- Does **not** address Article 9 (risk management), Article 10 (data governance),
  Article 13 (transparency to deployers), Article 15 (accuracy/robustness/cybersecurity),
  or Article 72 (post-market monitoring).
- Does **not** claim Article 40 presumption of conformity.
- Does **not** claim OpenAI Inc. endorsement.
- Provides the **Article 50 evidence layer only** for users of the direct OpenAI SDK.

## Roadmap

- v0.2: OpenAI Assistants API (`client.beta.threads.runs`) coverage via
  `assistant_response/v1` schema.
- v0.2: Pluggable HSM-backed signer (AWS KMS, GCP KMS, Azure Key Vault, YubiHSM2).
- v0.3: Built-in Merkle batcher with periodic flush to anchoring service.

## License

Apache 2.0. See `LICENSE`.
