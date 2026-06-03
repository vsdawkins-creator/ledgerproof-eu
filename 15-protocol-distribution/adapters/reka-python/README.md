# ledgerproof-reka

LedgerProof adapter for the [Reka AI Python SDK](https://docs.reka.ai/).

Emits **side-channel cryptographic transparency receipts** for AI-touched interactions, suitable as an evidence layer
for **EU AI Act Article 50** (transparency obligations for providers and deployers of AI systems).

This adapter is purpose-built for Reka's **multimodal-native** inference surface. A single Reka inference may bind
text, image, audio, and/or video inputs simultaneously; the adapter records each input modality as a separate
hash reference in the receipt and auto-selects the appropriate schema variant.

## 5-minute quickstart

```bash
pip install ledgerproof-reka
export REKA_API_KEY=...
```

```python
from ledgerproof_reka import LedgerProofReka, LogEmitter

client = LedgerProofReka(
    deployer_id="acme-corp-eu",
    emitter=LogEmitter(),
)

response = client.chat.create(
    model="reka-flash-3.1",
    messages=[{"role": "user", "content": "Hello"}],
)

print(response.responses[0].message.content)
# Receipt has already been emitted to the log emitter side-channel.
```

The Reka response object is returned **unchanged**. The receipt is emitted to the side channel only.

## Multimodal-native receipts

Reka models accept text, images, audio, and video in the same `messages` payload. The adapter inspects each
user-role content block and emits a `MediaRef` per non-text modality, then auto-selects the receipt schema:

| Inputs                           | Receipt schema                       |
| -------------------------------- | ------------------------------------ |
| Text only                        | `chatbot_session/v1`                 |
| Text + image / Text + audio      | `multimodal_native_inference/v1`     |
| Video input (any combination)    | `video_understanding/v1`             |

The `video_understanding/v1` schema is a **strategic forward surface** for Article 50(4) public-interest video
labeling once the upstream inference is bound to a downstream provenance pipeline. **This receipt by itself does
not discharge Article 50(4) obligations.** It is an evidence-layer binding of the inference event, nothing more.

### Inline media vs URL refs (C4)

The adapter handles two media-block shapes:

- **Inline base64 data** (`{"type": "image", "image": {"data": "<b64>", "media_type": "image/png"}}`) — the bytes
  are decoded and SHA-256 hashed locally.
- **URL-only references** (`{"type": "video", "url": "https://..."}`) — the **URL string itself** is hashed.
  The adapter **NEVER dereferences the URL** (constraint C4: no phone-home).

`data:<mime>;base64,...` URIs are normalised before hashing.

## Three integration patterns

1. **Client wrapper** (recommended) — `LedgerProofReka` wraps `reka.client.Reka` and intercepts
   `chat.create()` / `chat.create_stream()`. Sync, async, streaming, multimodal — all supported.
2. **Decorator** — `@lpr_track(deployer_id="...")` for user-defined functions that wrap Reka calls.
3. **Manual emission** — `emit_receipt(response, deployer_id, regulatory_context, ...)` for full control.

See `examples/` for runnable code:

- `01_reka_text_quickstart.py`
- `02_image_video_multimodal.py`
- `03_streaming.py`

## Architectural discipline (C1–C8)

This adapter is implemented under the LedgerProof protocol's load-bearing constraints:

- **C1**: No claim of regulator endorsement. No claim of Article 40 presumption of conformity.
- **C4**: Local verification only. The adapter does **not** phone home to LedgerProof servers during normal
  operation. URL-referenced media is hashed by URI; the adapter does not fetch the URL.
- **C6**: Stream-aware signing. Streaming responses are signed using an incremental SHA-256 over text deltas.
- **C7**: Side-channel emission only. The adapter **cannot and does not modify** the Reka response payload.

## GDPR guardrails

- Receipts **never** contain raw prompt or response text. Content is referenced via SHA-256 only.
- Receipts **never** contain raw media bytes. Media is referenced via SHA-256 plus MIME type and byte length.
- Free-text fields (`notes`, `descriptor`, `media_descriptor`) are length-bounded.
- Identifier fields (`deployer_id`, `receipt_id`) use a strict character pattern that rejects free-form PII.
- URL refs are hashed by URI; the URL itself is **not** stored in the receipt.

## Scope disclaimer

LedgerProof provides an **evidence layer for Article 50 transparency obligations only**.

It does **not** cover:

- Article 9 (risk management system)
- Article 10 (data and data governance)
- Article 13 (transparency and information to deployers)
- Article 15 (accuracy, robustness, and cybersecurity)
- Article 72 (post-market monitoring)

LedgerProof does **not** confer presumption of conformity under Article 40. LedgerProof is not endorsed by the
European Commission, the AI Office, any national competent authority, or any AI provider.

**This adapter wraps the official Reka AI Python SDK; it is not affiliated with, sponsored by, or endorsed by
Reka AI.** All Reka product names, model identifiers, and trademarks are the property of their respective owners.

## License

Apache 2.0. Copyright 2026 LedgerProof Foundation (in formation: US 501(c)(3) Delaware + Dutch Stichting EU subsidiary).
