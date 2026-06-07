# ledgerproof-ai21

LedgerProof adapter for the [AI21 Labs Python SDK](https://github.com/AI21Labs/ai21-python) (`ai21>=3.0`).

Emits **side-channel cryptographic transparency receipts** for AI-touched interactions, suitable as an evidence layer
for **EU AI Act Article 50** (transparency obligations for providers and deployers of AI systems).

This adapter works with anyone using the AI21 SDK directly:

- `ai21.AI21Client` — sync `chat.completions.create()` (streaming and non-streaming)
- `ai21.AsyncAI21Client` — async `chat.completions.create()` (streaming and non-streaming)
- Function / tool calls — recorded into the `tool_uses` block of the receipt
- **Long-context attestation** (`long_context_inference/v1`) — record declared and effective context-window utilization for Jamba's 256k window
- **Jamba hybrid attestation** (`jamba_hybrid_attribution/v1`) — record the Mamba/Transformer hybrid architectural family of the model used

## 5-minute quickstart

```bash
pip install ledgerproof-ai21
export AI21_API_KEY=...
```

```python
from ai21_ledgerproof import LedgerProofAI21, LogEmitter

client = LedgerProofAI21(
    deployer_id="acme-corp-eu",
    api_key="...",  # or read from AI21_API_KEY
    emitter=LogEmitter(),
)

response = client.chat.completions.create(
    model="jamba-1.5-large",
    messages=[{"role": "user", "content": "Hello"}],
)

print(response.choices[0].message.content)
# A signed receipt has already been emitted to the log emitter side-channel.
```

The AI21 `ChatCompletionResponse` is returned **unchanged**. The receipt is emitted to the side channel only (constraint **C7**).

## Three integration patterns

1. **Client wrapper** (recommended) — `LedgerProofAI21` wraps `ai21.AI21Client` and intercepts
   `chat.completions.create()` for both streaming and non-streaming. `LedgerProofAsyncAI21` does the same for `AsyncAI21Client`.
2. **Decorator** — `@lpr_track(deployer_id="...")` for user-defined functions that already wrap an AI21 call.
3. **Manual emission** — `emit_receipt(response, deployer_id, regulatory_context)` for full control.

See `examples/` for runnable code:

- `01_jamba_quickstart.py` — minimum viable wrap of `chat.completions.create()`
- `02_long_context.py` — `long_context_inference/v1` schema for Jamba's 256k window
- `03_streaming.py` — incremental-hash streaming with `jamba_hybrid_attribution/v1`

## Long-context attestation (Jamba 256k window)

Jamba 1.5 ships a 256k token context window — one of the largest in the open ecosystem.
Deployers exercising this surface (RAG over whole codebases, multi-document legal review,
long-form policy synthesis) can opt into the `long_context_inference/v1` schema:

```python
from ai21_ledgerproof import LedgerProofAI21, LongContextAttestation

client = LedgerProofAI21(
    deployer_id="acme-legaltech-eu",
    schema="long_context_inference/v1",
    long_context=LongContextAttestation(
        declared_context_window=262_144,
        effective_input_tokens=180_000,
        long_context_workload="multi-doc-legal-review",
        truncation_applied=False,
    ),
)
```

The attestation block is **descriptive metadata only** — see the scope disclaimer below.

## Jamba hybrid architecture attestation

Jamba's hybrid SSM (Mamba) + attention architecture has different latency, throughput,
and memory characteristics than pure-Transformer models. Deployers can record the
architectural family inline with the Article 50 receipt:

```python
from ai21_ledgerproof import JambaHybridAttestation, LedgerProofAI21

client = LedgerProofAI21(
    deployer_id="acme-corp-eu",
    schema="jamba_hybrid_attribution/v1",
    jamba_hybrid=JambaHybridAttestation(
        architecture_family="mamba-transformer-hybrid",
        model_variant="jamba-1.5-large",
        parameter_class="398B-MoE",
        attention_layer_ratio="1:7",
    ),
)
```

## Architectural discipline (C1, C4, C6, C7)

This adapter is implemented under the LedgerProof protocol's load-bearing constraints:

- **C1**: No claim of regulator endorsement. No claim of Article 40 presumption of conformity. **No AI21 Labs endorsement.**
- **C4**: Local verification only. The adapter does **not** phone home to LedgerProof servers during normal operation.
- **C6**: Stream-aware signing. Streaming responses are signed using an incremental SHA-256 over text deltas; the body is never buffered in full. This is critical for Jamba 256k-context streams where buffering is not viable.
- **C7**: Side-channel emission only. The adapter **cannot and does not modify** the AI21 response payload.

## GDPR data-minimisation

Receipts never carry raw prompt or response text. Content is referenced by SHA-256 hash + byte length only.
Identifier fields (`deployer_id`, `user_session_id`) reject email-shaped strings to prevent accidental
direct-identifier leakage (GDPR Art. 4(1) / Art. 5(1)(c) data minimisation).

## Scope disclaimer

LedgerProof provides an **evidence layer for Article 50 transparency obligations only**.

It does **not** cover:

- Article 9 (risk management system)
- Article 10 (data and data governance)
- Article 13 (transparency and information to deployers)
- Article 15 (accuracy, robustness, and cybersecurity)
- Article 72 (post-market monitoring)

LedgerProof does **not** confer presumption of conformity under Article 40. LedgerProof is not endorsed by the
European Commission, the AI Office, any national competent authority, or AI21 Labs Ltd.

**This adapter wraps the official AI21 Labs Python SDK; it is not affiliated with, endorsed by, or supported by AI21 Labs Ltd.**

The `LongContextAttestation` and `JambaHybridAttestation` blocks are deployer-asserted descriptive metadata.
They are **not** certifications of model architecture, context-window behaviour, performance, or any other
regulatory or technical property.

## License

Apache 2.0. Copyright 2026 LedgerProof Foundation (in formation: US 501(c)(3) Delaware + Dutch Stichting EU subsidiary).
