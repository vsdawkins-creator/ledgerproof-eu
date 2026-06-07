# ledgerproof-vertexai

LedgerProof adapter for the Google Cloud **Vertex AI** Python SDK
(`google-cloud-aiplatform` / `vertexai`).

Emits side-channel cryptographic transparency receipts suitable for
EU AI Act **Article 50** compliance evidence, with first-class capture
of Vertex AI's `location` parameter for **EU data residency attestation**.

---

## Important disclaimers

- **C1 — No regulator endorsement.** LedgerProof is an open cryptographic
  protocol stewarded by the LedgerProof Foundation (Stichting, in formation).
  It is **not endorsed by, certified by, or affiliated with** the European
  Commission, the EU AI Office, any National Competent Authority, ENISA, or
  any other regulator. The protocol does **not** confer an Article 40
  presumption of conformity.
- **Not endorsed by Google Cloud.** This adapter is an independent open-source
  project. It is **not endorsed by, certified by, or affiliated with** Google
  LLC, Google Cloud, the Vertex AI team, or any Alphabet subsidiary. "Vertex
  AI", "Gemini", and "Google Cloud" are trademarks of Google LLC, used here
  nominatively to describe interoperability only.
- **C7 — Side-channel only.** This adapter **never** modifies the response
  payload returned by Vertex AI. Receipts are emitted out-of-band.
- **C6 — Stream-aware.** Streaming responses are signed after the final chunk
  has been observed; intermediate chunks are never modified.
- **C4 — Local verification only.** All receipts are verifiable locally with
  the LedgerProof verifier CLI. No phone-home is performed.

---

## Why Vertex AI specifically

Vertex AI is the dominant enterprise-grade Gemini deployment surface for
European banks, insurers, and regulated industries that need **regional
data residency**. The `location` parameter (e.g. `europe-west4` = Eemshaven,
Netherlands; `europe-west9` = Paris; `europe-west3` = Frankfurt) determines
which physical region processes the inference.

This adapter captures `project`, `location`, and a derived
`region_of_inference_attestation` field into a purpose-built
`eu_data_residency/v1` receipt schema, which is strategically aligned with
GDPR Chapter V (international transfers) and the EU AI Act Article 50
audit trail requirements.

> Receipts assert *what was configured by the deployer*. They do not
> independently verify Google Cloud's physical region routing.

---

## Install

```bash
pip install ledgerproof-vertexai
```

## Quickstart

```python
import vertexai
from vertexai_ledgerproof import LedgerProofGenerativeModel, configure

vertexai.init(project="my-project", location="europe-west4")

configure(deployer_id="urn:lpr:deployer:my-bank-eu",
          sink="./receipts.jsonl")

model = LedgerProofGenerativeModel(
    "gemini-2.0-flash-001",
    lpr_schema="generated_content/v1",
)

resp = model.generate_content("Summarize MiFID II in two sentences.")
print(resp.text)
# A side-channel receipt is emitted to ./receipts.jsonl
```

## EU data residency example

```python
import vertexai
from vertexai_ledgerproof import LedgerProofGenerativeModel, configure

# europe-west4 = Eemshaven, Netherlands
vertexai.init(project="acme-eu", location="europe-west4")

configure(deployer_id="urn:lpr:deployer:acme-bank-de",
          sink="./eu-receipts.jsonl")

model = LedgerProofGenerativeModel(
    "gemini-2.0-flash-001",
    lpr_schema="eu_data_residency/v1",
)

resp = model.generate_content("Was ist DORA?")
```

The receipt will contain a `region_of_inference_attestation` field
asserting `europe-west4` as the configured inference region.

---

## Schemas

| Schema | Article 50 mapping | Use case |
| --- | --- | --- |
| `chatbot_session/v1` | 50(1) | Multi-turn chat / `ChatSession` |
| `generated_content/v1` | 50(2) | One-shot generated text/code/image |
| `eu_data_residency/v1` | 50(1) variant | Captures project + location + region attestation |
| `gemini_function_call/v1` | (internal audit) | Tool / function-call invocations |

---

## License

Apache 2.0. See [LICENSE](LICENSE).
