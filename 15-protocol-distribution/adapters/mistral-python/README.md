# ledgerproof-mistral

LedgerProof adapter for the [Mistral Python SDK](https://github.com/mistralai/client-python) (`mistralai>=1.0`).

Emits **side-channel cryptographic transparency receipts** for AI-touched interactions, suitable as an evidence layer
for **EU AI Act Article 50** (transparency obligations for providers and deployers of AI systems).

This adapter works with anyone using the Mistral SDK directly:

- `mistralai.Mistral` client — sync `chat.complete()` and `chat.stream()`
- Async — `chat.complete_async()` and `chat.stream_async()`
- Function / tool calls — recorded into the `tool_uses` block of the receipt
- **EU-sovereign AI attribution** (`eu_sovereign_ai_session/v1`) — record Mistral-as-EU-provider facts (region, residency, control plane) alongside Article 50 transparency evidence

## 5-minute quickstart

```bash
pip install ledgerproof-mistral
export MISTRAL_API_KEY=...
```

```python
from ledgerproof_mistral import LedgerProofMistral, LogEmitter

client = LedgerProofMistral(
    deployer_id="acme-corp-eu",
    api_key="...",  # or read from MISTRAL_API_KEY
    emitter=LogEmitter(),
)

response = client.chat.complete(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": "Hello"}],
)

print(response.choices[0].message.content)
# A signed receipt has already been emitted to the log emitter side-channel.
```

The Mistral `ChatCompletionResponse` is returned **unchanged**. The receipt is emitted to the side channel only.

## Three integration patterns

1. **Client wrapper** (recommended) — `LedgerProofMistral` wraps `mistralai.Mistral` and intercepts
   `chat.complete()` / `chat.stream()`. `LedgerProofAsyncMistral` does the same for `complete_async()` / `stream_async()`.
2. **Decorator** — `@lpr_track(deployer_id="...")` for user-defined functions that already wrap a Mistral call.
3. **Manual emission** — `emit_receipt(response, deployer_id, regulatory_context)` for full control.

See `examples/` for runnable code:

- `01_chat_quickstart.py` — minimum viable wrap of `chat.complete()`
- `02_streaming.py` — incremental-hash streaming
- `03_eu_sovereign_attribution.py` — `eu_sovereign_ai_session/v1` schema

## EU-sovereign AI attribution

Because Mistral is a French / EU-headquartered model provider, this adapter ships a third schema —
`eu_sovereign_ai_session/v1` — that lets deployers record EU residency / control facts inline with the
Article 50 receipt:

```python
from ledgerproof_mistral import EuSovereigntyAttestation, LedgerProofMistral

client = LedgerProofMistral(
    deployer_id="acme-bank-eu",
    schema="eu_sovereign_ai_session/v1",
    eu_sovereignty=EuSovereigntyAttestation(
        inference_region="eu-west-3",
        eu_data_residency=True,
        eu_operated_infrastructure=True,
        provider_eu_headquartered=True,
        provider_legal_entity="Mistral AI SAS (Paris)",
    ),
)
```

The attestation block is **descriptive metadata only** — see the scope disclaimer below.

## Architectural discipline (C1–C8)

This adapter is implemented under the LedgerProof protocol's load-bearing constraints:

- **C1**: No claim of regulator endorsement. No claim of Article 40 presumption of conformity.
- **C4**: Local verification only. The adapter does **not** phone home to LedgerProof servers during normal operation.
- **C6**: Stream-aware signing. Streaming responses are signed using an incremental SHA-256 over text deltas; the body is never buffered in full.
- **C7**: Side-channel emission only. The adapter **cannot and does not modify** the Mistral response payload.

## GDPR data-minimisation

Receipts never carry raw prompt or response text. Content is referenced by SHA-256 hash + byte length only.
Identifier fields (`deployer_id`, `user_session_id`) reject email-shaped strings to prevent accidental
direct-identifier leakage.

## Scope disclaimer

LedgerProof provides an **evidence layer for Article 50 transparency obligations only**.

It does **not** cover:

- Article 9 (risk management system)
- Article 10 (data and data governance)
- Article 13 (transparency and information to deployers)
- Article 15 (accuracy, robustness, and cybersecurity)
- Article 72 (post-market monitoring)

LedgerProof does **not** confer presumption of conformity under Article 40. LedgerProof is not endorsed by the
European Commission, the AI Office, any national competent authority, or Mistral AI SAS.

The `EuSovereigntyAttestation` block is deployer-asserted descriptive metadata. It is **not** a
certification of EU sovereignty, EUCS conformance, GDPR Schrems-II adequacy, or any similar regulatory finding.

This adapter wraps the official Mistral Python SDK; it is not affiliated with Mistral AI SAS.

## License

Apache 2.0. Copyright 2026 LedgerProof Foundation (in formation: US 501(c)(3) Delaware + Dutch Stichting EU subsidiary).
