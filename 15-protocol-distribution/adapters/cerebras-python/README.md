# ledgerproof-cerebras

LedgerProof adapter for the [Cerebras](https://cerebras.ai) Cloud Python SDK. Emits side-channel cryptographic transparency receipts for AI inference calls, intended to support deployers preparing for EU AI Act Article 50 obligations (applicable from 2 August 2026).

## Important disclaimers

- **C1 — No regulator endorsement.** LedgerProof is an open cryptographic protocol stewarded by the LedgerProof Foundation. It has not been endorsed by the European Commission, the EU AI Office, any national supervisory authority, or any standardisation body. It does not, on its own, satisfy Article 50 — that determination is made by deployers, their counsel, and ultimately by regulators.
- **C1 — No Article 40 presumption of conformity.** LedgerProof is not a harmonised standard and does not confer a presumption of conformity under Article 40 of the EU AI Act.
- **Not endorsed by Cerebras.** This adapter is an independent open-source project. It is not produced, sponsored, endorsed, or supported by Cerebras Systems, Inc. "Cerebras", "CS-3", and "Wafer-Scale Engine" are trademarks of Cerebras Systems, Inc., used here nominatively to describe interoperability.
- **C7 — Side-channel only.** Receipts are emitted asynchronously and never alter, delay, or proxy inference requests or responses returned by Cerebras. The ultra-low-latency profile of the wafer-scale CS-3 inference path is preserved.
- **C6 — Stream-aware signing.** For streamed completions, receipts are emitted once after the stream terminates, over the concatenated output.
- **C4 — Local verification only.** Receipts can be verified offline against the public key. No verification endpoint is operated by the Foundation in Phase 1.

## Installation

```bash
pip install ledgerproof-cerebras
```

## Quickstart

```python
from ledgerproof_cerebras import LedgerProofCerebras

client = LedgerProofCerebras(
    api_key="...",                  # Cerebras API key (or env CEREBRAS_API_KEY)
    lpr_signing_key_path="key.pem", # Ed25519 private key (PEM)
    lpr_deployer_id="deployer-123",
)

resp = client.chat.completions.create(
    model="llama3.1-70b",
    messages=[{"role": "user", "content": "Hello"}],
    lpr_schema="chatbot_session/v1",
    lpr_subject_id_hash="sha256:...",  # pseudonymous subject id
)

print(resp.choices[0].message.content)
# Receipt has been emitted via side-channel.
```

### Wafer-scale inference receipts (Cerebras-specific)

Cerebras's differentiator is ultra-low-latency inference on the wafer-scale CS-3
engine. The `wafer_scale_inference/v1` schema captures `inference_latency_ms`
and `tokens_per_second` so deployers can attest to performance characteristics
alongside Article 50 transparency.

```python
resp = client.chat.completions.create(
    model="llama3.1-70b",
    messages=[...],
    lpr_schema="wafer_scale_inference/v1",
)
```

### Reasoning-model receipts (`reasoning_distilled/v1`)

For distilled reasoning models such as `deepseek-r1-distill-llama-70b` and
`qwen3-32b-thinking`, the `reasoning_distilled/v1` schema captures reasoning-trace
token usage alongside the final completion. The receipt remains a 50(1)/50(2)
hybrid: callers should still surface the AI-interaction disclosure to the
natural person where applicable.

```python
resp = client.chat.completions.create(
    model="deepseek-r1-distill-llama-70b",
    messages=[...],
    lpr_schema="reasoning_distilled/v1",
)
```

## Supported receipt schemas

| Schema | Article 50 hook | Use case |
|---|---|---|
| `chatbot_session/v1` | 50(1) | Conversational chatbots |
| `generated_content/v1` | 50(2) | Generic text generation |
| `wafer_scale_inference/v1` | 50(1) variant | CS-3 performance attestation |
| `reasoning_distilled/v1` | 50(1) variant | r1-distill / qwen3-thinking reasoning models |

## GDPR notes

The adapter validates that fields commonly carrying personal data (prompts,
completions, subject identifiers) are either omitted, hashed, or pseudonymised
before being included in a receipt. Deployers remain controllers under GDPR.

## License

Apache 2.0. See [LICENSE](LICENSE).
