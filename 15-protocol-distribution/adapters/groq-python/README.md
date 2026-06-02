# ledgerproof-groq

LedgerProof adapter for the [Groq](https://groq.com) Python SDK. Emits side-channel cryptographic transparency receipts for AI inference calls, intended to support deployers preparing for EU AI Act Article 50 obligations (applicable from 2 August 2026).

## Important disclaimers

- **C1 — No regulator endorsement.** LedgerProof is an open cryptographic protocol stewarded by the LedgerProof Foundation. It has not been endorsed by the European Commission, the EU AI Office, any national supervisory authority, or any standardisation body. It does not, on its own, satisfy Article 50 — that determination is made by deployers, their counsel, and ultimately by regulators.
- **C1 — No Article 40 presumption of conformity.** LedgerProof is not a harmonised standard and does not confer a presumption of conformity under Article 40 of the EU AI Act.
- **Not endorsed by Groq.** This adapter is an independent open-source project. It is not produced, sponsored, endorsed, or supported by Groq, Inc. "Groq" is a trademark of Groq, Inc., used here nominatively to describe interoperability.
- **C7 — Side-channel only.** Receipts are emitted asynchronously and never alter, delay, or proxy inference requests or responses returned by Groq. Groq's LPU-driven low-latency profile is preserved.
- **C6 — Stream-aware signing.** For streamed completions, receipts are emitted once after the stream terminates, over the concatenated output.
- **C4 — Local verification only.** Receipts can be verified offline against the public key. No verification endpoint is operated by the Foundation in Phase 1.

## Installation

```bash
pip install ledgerproof-groq
```

## Quickstart

```python
from ledgerproof_groq import LedgerProofGroq

client = LedgerProofGroq(
    api_key="...",                  # Groq API key (or env GROQ_API_KEY)
    lpr_signing_key_path="key.pem", # Ed25519 private key (PEM)
    lpr_deployer_id="deployer-123",
)

resp = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello"}],
    lpr_schema="chatbot_session/v1",
    lpr_subject_id_hash="sha256:...",  # pseudonymous subject id
)

print(resp.choices[0].message.content)
# Receipt has been emitted via side-channel.
```

### Low-latency inference receipts (Groq-specific)

Groq's differentiator is sub-second LPU inference. The `low_latency_inference/v1`
schema captures `inference_latency_ms` and `tokens_per_second` so deployers can
attest to performance characteristics alongside Article 50 transparency.

```python
resp = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...],
    lpr_schema="low_latency_inference/v1",
)
```

### Whisper audio transcription receipts (Article 50(2))

Groq hosts Whisper at high throughput. The `audio_transcription/v1` schema is
designed for deployers who use Groq to transcribe audio that they later mark or
publish as AI-generated under Article 50(2).

```python
with open("clip.wav", "rb") as f:
    transcript = client.audio.transcriptions.create(
        file=f, model="whisper-large-v3",
        lpr_schema="audio_transcription/v1",
    )
```

## Supported receipt schemas

| Schema | Article 50 hook | Use case |
|---|---|---|
| `chatbot_session/v1` | 50(1) | Conversational chatbots |
| `generated_content/v1` | 50(2) | Generic text generation |
| `low_latency_inference/v1` | 50(1) variant | LPU performance attestation |
| `audio_transcription/v1` | 50(2) variant | Whisper transcription |

## GDPR notes

The adapter validates that fields commonly carrying personal data (prompts,
completions, subject identifiers) are either omitted, hashed, or pseudonymised
before being included in a receipt. Deployers remain controllers under GDPR.

## License

Apache 2.0. See [LICENSE](LICENSE).
