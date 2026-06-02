# ledgerproof-haystack

**LedgerProof adapter for Haystack 2.x — side-channel cryptographic receipts for EU AI Act Article 50 transparency.**

[![Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)

`ledgerproof-haystack` is the official LedgerProof Foundation adapter for [Haystack 2.x](https://haystack.deepset.ai/) — the open-source LLM orchestration framework built by [deepset GmbH](https://www.deepset.ai/) (Berlin). It plugs LedgerProof receipt emission into any Haystack `Pipeline` as a side-channel observer node, so that every RAG run, every generation, and every editorial review step produces a tamper-evident cryptographic receipt suitable for EU AI Act Article 50 disclosure obligations.

---

## Strategic positioning: German enterprise RAG

Haystack is the de facto RAG orchestration layer in **German enterprise** (BMW, Siemens, Allianz, SAP-adjacent integrators) and across the broader **DACH** market. It is also the framework most frequently cited by **CEN-CENELEC JTC 21** working participants for AI Act-aligned reference architectures.

This adapter is built to slot directly into existing Haystack 2.x pipelines without rewriting orchestration code — and it produces receipts that align to the **rag_pipeline_session/v1** schema, the **generated_content/v1** schema (Article 50(2) AI-generated content), and the **editorial_pipeline_review/v1** schema (Article 50(4) public-interest text).

---

## Article 50 obligation coverage

| Obligation                                                  | LedgerProof schema                  | Haystack hook              |
|-------------------------------------------------------------|-------------------------------------|----------------------------|
| 50(1) — User-facing AI disclosure                           | `rag_pipeline_session/v1`           | Pipeline-level component   |
| 50(2) — AI-generated content marking                        | `generated_content/v1`              | Generator wrapper          |
| 50(4) — Editorial review for public-interest text           | `editorial_pipeline_review/v1`      | Editorial pipeline node    |
| Per-node trace (any component)                              | `haystack_node_receipt/v1`          | `@component` decorator     |

---

## Installation

```bash
pip install ledgerproof-haystack
```

Requires Python 3.10+, `haystack-ai>=2.0`, `cryptography>=41`, `cbor2>=5.0`, `pydantic>=2.0`.

---

## Quickstart

```python
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from ledgerproof_haystack import LedgerProofComponent, load_or_generate_signing_key

key = load_or_generate_signing_key()

pipeline = Pipeline()
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))
pipeline.add_component(
    "ledgerproof",
    LedgerProofComponent(
        signing_key=key,
        schema="generated_content/v1",
        deployer="acme-bank-de",
    ),
)
pipeline.connect("llm.replies", "ledgerproof.content")

result = pipeline.run({"llm": {"prompt": "Erklären Sie GDPR Artikel 7."}})
print(result["ledgerproof"]["receipt_id"])
```

The receipt is emitted as a **side channel** — the LLM reply itself is untouched. Verifiers download the public key from your Foundation-published location and validate the signature locally.

---

## Design constraints (Foundation-mandated)

This adapter is governed by the LedgerProof Foundation constraint matrix. The following constraints are enforced **in code**:

- **C1 — No regulator endorsement, no Article 40 presumption.** This software does not constitute legal advice, does not assert presumption of conformity under Article 40 of Regulation (EU) 2024/1689, and is not endorsed by the European Commission, the AI Office, ENISA, or any national competent authority.
- **C4 — Local verification only.** No verifier network calls. All cryptographic verification happens locally against the signing public key. No phone-home, no telemetry.
- **C6 — Stream-aware signing.** Streaming generators are supported via incremental hashing through `lpr_pipeline_callback`; receipts are emitted once the stream closes.
- **C7 — Side-channel emission.** Receipts are emitted to the side-channel sink (filesystem, S3, OTel, your own emitter). The user-facing model output is never modified.

---

## GDPR posture

The adapter does **not** transmit prompt content or generation output off-host by default. The default emitter writes a CBOR-encoded receipt to a configurable local path. The receipt contains a SHA-256 hash of the input/output, not the plaintext. If you choose to enable a payload-bearing schema field, the adapter runs Pydantic validators that refuse fields containing apparent PII (email, IBAN, BIC, German Steuer-ID, national ID patterns) unless `gdpr_lawful_basis` is explicitly set.

---

## Foundation governance

This adapter is published by the **LedgerProof Foundation** (Stichting LedgerProof, Amsterdam, NL) — an independent non-profit. It is not a product of any single AI vendor. Issues and PRs at the [Foundation repo](https://github.com/ledgerproof-foundation/ledgerproof-haystack).

---

## License

Apache License 2.0. See [LICENSE](./LICENSE).
