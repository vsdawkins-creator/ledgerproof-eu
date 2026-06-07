# ledgerproof-anthropic

LedgerProof adapter for the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python).

Emits **side-channel cryptographic transparency receipts** for AI-touched interactions, suitable as an evidence layer
for **EU AI Act Article 50** (transparency obligations for providers and deployers of AI systems).

This adapter works with anyone using the Anthropic SDK directly, including users of:

- `anthropic.Anthropic` / `anthropic.AsyncAnthropic` clients
- Claude Code (which uses the Anthropic SDK under the hood)
- The Claude Agent SDK (tool-use receipts via `agent_action/v1`)

## 5-minute quickstart

```bash
pip install ledgerproof-anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

```python
from anthropic_ledgerproof import LedgerProofAnthropic, LogEmitter

client = LedgerProofAnthropic(
    deployer_id="acme-corp-eu",
    emitter=LogEmitter(),
)

response = client.messages.create(
    model="claude-opus-4-1",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello"}],
)

print(response.content[0].text)
# Receipt has already been emitted to the log emitter side-channel.
```

The Anthropic response object is returned **unchanged**. The receipt is emitted to the side channel only.

## Three integration patterns

1. **Client wrapper** (recommended) — `LedgerProofAnthropic` wraps `anthropic.Anthropic` and intercepts
   `messages.create()`. Sync, async, streaming and non-streaming all supported.
2. **Decorator** — `@lpr_track(deployer_id="...")` for user-defined functions that wrap Anthropic calls.
3. **Manual emission** — `emit_receipt(response, deployer_id, regulatory_context)` for full control.

See `examples/` for runnable code.

## Architectural discipline (C1–C8)

This adapter is implemented under the LedgerProof protocol's load-bearing constraints:

- **C1**: No claim of regulator endorsement. No claim of Article 40 presumption of conformity.
- **C4**: Local verification only. The adapter does **not** phone home to LedgerProof servers during normal operation.
- **C6**: Stream-aware signing. Streaming messages are signed using an incremental SHA-256 over text deltas.
- **C7**: Side-channel emission only. The adapter **cannot and does not modify** the Anthropic response payload.

## Scope disclaimer

LedgerProof provides an **evidence layer for Article 50 transparency obligations only**.

It does **not** cover:

- Article 9 (risk management system)
- Article 10 (data and data governance)
- Article 13 (transparency and information to deployers)
- Article 15 (accuracy, robustness, and cybersecurity)
- Article 72 (post-market monitoring)

LedgerProof does **not** confer presumption of conformity under Article 40. LedgerProof is not endorsed by the
European Commission, the AI Office, any national competent authority, or Anthropic, PBC.

This adapter wraps the official Anthropic Python SDK; it is not affiliated with Anthropic.

## License

Apache 2.0. Copyright 2026 LedgerProof Foundation (in formation: US 501(c)(3) Delaware + Dutch Stichting EU subsidiary).
