# ledgerproof-replicate

**LedgerProof adapter for the Replicate Python SDK.**
Side-channel cryptographic transparency receipts for EU AI Act Article 50.
Multi-modal coverage: text, image, audio, video.

---

## Disclosures (C1)

- **This adapter is not endorsed by Replicate.** "Replicate" is a trademark of
  Replicate, Inc. This is an independent, open-source integration. We are not
  affiliated with, sponsored by, or partnered with Replicate, Inc.
- **No regulator endorsement.** LedgerProof is an open cryptographic protocol
  stewarded (in formation) by an independent foundation. It has not been
  endorsed by the European Commission, the EU AI Office, any National
  Competent Authority, ENISA, or any other public body.
- **No Article 40 presumption of conformity.** Use of this adapter does not
  create, imply, or substitute for a presumption of conformity with the EU AI
  Act. It is an evidence-generation tool. Legal compliance with Article 50
  remains the responsibility of the deployer of the AI system.
- **No Replicate model endorsement.** Receipts attest *what* model coordinate
  was used and *what* output bytes were produced; they make no statement about
  fitness, safety, or compliance of the underlying third-party models hosted
  on Replicate.

---

## Why this matters for multi-modal generation

Replicate is the leading open runtime for non-OpenAI generative models in the
European market: **FLUX, Stable Diffusion, SDXL** (image), **Whisper, MusicGen,
Bark** (audio), **ZeroScope, AnimateDiff** (video), and a long tail of
**Llama**-family chat models.

EU AI Act **Article 50(2)** requires providers of generative AI systems to
ensure outputs are marked in a machine-readable format and detectable as
artificially generated. **Article 50(1)** requires disclosure when natural
persons interact with chatbots.

This adapter emits a cryptographically signed receipt every time you call
`replicate.run(...)`, binding together:

1. The **exact model coordinate** — `author/name:version`, where `version` is
   the immutable content-addressed hash of the model weights on Replicate.
2. The **SHA-256 of every input parameter** (prompt, seed, guidance scale, …).
3. The **SHA-256 of every generated artifact** (image, audio clip, video).

The deployer keeps the receipts. A competent authority — or any third party,
offline — can verify the signature and prove that a specific prompt produced a
specific output from a specific model version, without ever seeing the raw
prompt or output bytes.

---

## Install

```bash
pip install ledgerproof-replicate
```

Python 3.10+.

Runtime dependencies: `replicate>=1.0`, `cryptography>=41`, `cbor2>=5.0`,
`pydantic>=2.0`.

---

## Quick start — client wrapper

```python
from ledgerproof_replicate import LedgerProofReplicateClient

client = LedgerProofReplicateClient(
    deployer_id="acme-eu",
    api_token="r8_...",
)

# Text generation (Llama, Mixtral, etc.)
output = client.run(
    "meta/meta-llama-3-70b-instruct",
    input={"prompt": "Explain Article 50 in one paragraph."},
)
```

A `chatbot_session/v1` receipt is emitted on the side channel and signed with
Ed25519. The `output` is returned **unchanged** (C7).

## Image generation with content provenance

```python
output = client.run_image(
    "black-forest-labs/flux-schnell:bf2f2e683d03a9549f484a37a0df1c4c08e8e3fa3a18f3e1c1d4a4dba8c0bc0e",
    input={"prompt": "a serene mountain lake at dawn"},
)
# Returns the FLUX image URL(s); the receipt binds:
#   - model_id = "black-forest-labs/flux-schnell"
#   - model_version = "bf2f2e683d03a9..."  (immutable Replicate version hash)
#   - input_refs[0] = SHA-256("a serene mountain lake at dawn")
#   - output_artifacts[0] = SHA-256 of the output URL or downloaded bytes
```

Receipt schema: `synthetic_image/v1`.

## Audio synthesis (Whisper, MusicGen, Bark)

```python
output = client.run_audio(
    "meta/musicgen",
    input={"prompt": "ambient piano with rain", "duration": 30},
)
```

Receipt schema: `synthetic_audio/v1`.

## Video synthesis (ZeroScope, AnimateDiff)

```python
output = client.run_video(
    "anotherjesse/zeroscope-v2-xl",
    input={"prompt": "a fox jumping over a wall"},
)
```

Receipt schema: `synthetic_video/v1`.

## Strongest binding — `multimodel_attribution/v1`

When you want a receipt that **proves the exact model weights** used (because
Replicate version hashes are content-addressed), use `run_with_attribution`:

```python
output = client.run_with_attribution(
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    input={"prompt": "modernist EU parliament concept art"},
)
```

The receipt will fail to build unless `:version` is present.

---

## Streaming (LLM token output)

```python
for event in client.stream(
    "meta/meta-llama-3-70b-instruct",
    input={"prompt": "Summarise the AI Act in three bullets."},
):
    print(event, end="")
```

Tokens are hashed incrementally (C6). One receipt is emitted when the stream
ends, with `streaming=True` and the SHA-256 of the full concatenated output.

---

## Decorator pattern

```python
import replicate
from ledgerproof_replicate import lpr_track

@lpr_track(deployer_id="acme-eu")
def generate_marketing_image(ref: str, input: dict):
    return replicate.run(ref, input=input)

img = generate_marketing_image(
    ref="black-forest-labs/flux-schnell",
    input={"prompt": "cozy bookstore interior"},
)
```

---

## Manual emission — full control

For non-standard flows (batch, mixed modality, custom hashing of large
downloaded artifacts) call `emit_receipt` directly:

```python
from ledgerproof_replicate import (
    emit_receipt,
    build_model_ref_from_coordinate,
    hash_image_bytes,
)

ref = build_model_ref_from_coordinate(
    "black-forest-labs/flux-schnell:bf2f2e...",
    prediction_id="pred_abc123",
    status="succeeded",
)
artifact = hash_image_bytes(image_bytes, width_px=1024, height_px=1024)

emit_receipt(
    deployer_id="acme-eu",
    model_ref=ref,
    schema="synthetic_image/v1",
    prompt_text="a serene mountain lake",
    output_artifacts=[artifact],
)
```

---

## Schemas (v1)

| Schema | Article 50 | When to use |
| --- | --- | --- |
| `chatbot_session/v1` | 50(1) | Text chat with Llama-family or similar models |
| `generated_content/v1` | 50(2) | General-purpose synthetic content |
| `synthetic_image/v1` | 50(2) | FLUX, SDXL, Stable Diffusion |
| `synthetic_audio/v1` | 50(2) | Whisper TTS, MusicGen, Bark, RVC |
| `synthetic_video/v1` | 50(2) | ZeroScope, AnimateDiff |
| `multimodel_attribution/v1` | 50(2) | Strongest binding — requires `:version` |

All schemas share an envelope (`ReceiptV1`) carrying `model`, `input_refs`,
`output_artifacts`, `content_refs`, and `regulatory_context`.

---

## GDPR posture

- Receipts **never store** raw prompt text or output bytes.
- Content is referenced by **SHA-256** only.
- Free-text identifier fields are length-bounded by Pydantic validators.
- No end-user identifiers, IP addresses, or locale metadata are part of the
  schema.

---

## Emission targets

Default: `LogEmitter` writes JSON-encoded signed receipts to `stdout` logging.

Provided emitters:

- `LogEmitter`, `StderrEmitter` — structured logging
- `WebhookEmitter` — HTTPS POST to a deployer-controlled endpoint
- `QueueEmitter` — wrap any callable (SQS, Kafka, Redis)
- `MultiEmitter` — fan-out

Custom emitters: any object satisfying `Emitter.emit(signed_receipt: dict)`.

---

## Verifying a receipt (offline, C4)

```python
import base64
from ledgerproof_replicate import canonical_encode, verify

signed = {...}  # loaded from your sink
canonical = canonical_encode(signed["receipt"])
sig = base64.b64decode(signed["signature_b64"])
assert verify(public_key_bytes, canonical, sig)
```

No network call. No phone-home. The signature is verifiable against the
deployer-published public key alone.

---

## Constraints honoured

- **C1** — No regulator endorsement; no Article 40 presumption; no Replicate
  endorsement. Stated in every shipped artefact.
- **C4** — Verification is local-only. The adapter never opens a network
  connection it didn't have to.
- **C6** — Streaming text deltas are hashed incrementally via
  `IncrementalTextHasher`. Large binary outputs can be hashed via
  `IncrementalBytesHasher` or `hash_file_output(stream)`.
- **C7** — Receipts are emitted on a side channel only. The Replicate output
  object is returned untouched.

---

## License

Apache License 2.0. See `LICENSE`.

---

## Status

`0.1.0` — Phase 1 MVP. Schemas, signers, and emitters are stable for the v1
envelope but the protocol is pre-1.0 and may evolve before the EU AI Act
Article 50 enforcement date (2 August 2026).
