# ledgerproof-mistral-codestral

LedgerProof adapter for **Mistral Codestral**, Mistral AI's code-tuned model
(`mistralai>=1.0`, Codestral endpoint).

Emits **side-channel cryptographic transparency receipts** for AI-generated **code**,
suitable as an evidence layer for **EU AI Act Article 50** transparency obligations
applied to the specific case of code generation: license compliance, security review
attestation, editorial oversight for safety-critical code, and human-in-the-loop
review tracking.

This adapter works with anyone using the Mistral SDK against the Codestral endpoint:

- `mistralai.Mistral` client pointed at `https://codestral.mistral.ai` — sync chat (`chat.complete`) and FIM (`fim.complete`)
- Async — `chat.complete_async` and `fim.complete_async`
- Fill-in-the-middle (FIM) completions — the dominant Codestral usage pattern (IDE autocomplete, refactor)
- Safety-critical code review attestations — Article 50(4) editorial-control evidence when generated code passes human review before deployment

## Why a separate adapter for Codestral?

Codestral is a *code-specific* model. Article 50 has different implications when the
"output" is executable code rather than prose:

- **License compliance** — code generation can replicate training-set patterns; receipts let downstream consumers prove what model produced what code at what time, which is necessary input to any IP / OSS-license dispute.
- **Security review** — generated code may contain vulnerable patterns; receipts include a `has_security_pattern` flag asserted by the deployer's static-analysis pipeline.
- **Attribution** — when Codestral output is committed to a repo, a receipt anchored alongside the commit gives downstream maintainers a verifiable "AI-touched" marker.
- **Editorial oversight for safety-critical code** — Article 50(4) "editorial control" exemption: when generated code passes a documented human review *before deployment*, the deployer can attest to that step in a `safety_critical_code_review/v1` receipt.

## 5-minute quickstart

```bash
pip install ledgerproof-mistral-codestral
export MISTRAL_CODESTRAL_API_KEY=...
```

```python
from ledgerproof_mistral_codestral import LedgerProofCodestral, LogEmitter

client = LedgerProofCodestral(
    deployer_id="acme-corp-eu",
    api_key="...",  # or read from MISTRAL_CODESTRAL_API_KEY
    emitter=LogEmitter(),
)

# Chat-style code generation
response = client.chat.complete(
    model="codestral-latest",
    messages=[{"role": "user", "content": "Write a Python fib() with memoisation."}],
)
print(response.choices[0].message.content)
# A signed receipt has already been emitted on the side channel.

# Fill-in-the-middle (the dominant Codestral pattern)
fim = client.fim.complete(
    model="codestral-latest",
    prompt="def fib(n):\n    ",
    suffix="\n    return result",
)
print(fim.choices[0].message.content)
```

The Codestral response objects are returned **unchanged**. Receipts ride the side channel only.

## Schemas

Four receipt schemas ship with this adapter:

| Schema | Article 50 paragraph | Use |
|---|---|---|
| `chatbot_session/v1` | 50(1) | Code-chatbot interactions (IDE chat panel, web chat) |
| `generated_code/v1` | 50(2) | Synthetic code outputs — carries `language`, `line_count`, `has_security_pattern` |
| `fim_completion/v1` | 50(2) | Fill-in-the-middle completions (most Codestral IDE traffic) |
| `safety_critical_code_review/v1` | 50(4) | Human-review attestation before generated code is deployed |

## Three integration patterns

1. **Client wrapper** (recommended) — `LedgerProofCodestral` and `LedgerProofAsyncCodestral`.
2. **Decorator** — `@lpr_track(deployer_id="...")` for user-defined functions.
3. **Manual emission** — `emit_receipt(response, deployer_id, ...)` for full control, especially for `safety_critical_code_review/v1` which requires deployer-asserted review metadata.

See `examples/` for runnable code:

- `01_codestral_chat_quickstart.py` — chat-style code generation receipts
- `02_fim_completion.py` — fill-in-the-middle completions
- `03_safety_critical_review.py` — Article 50(4) editorial-control attestation

## Architectural discipline (C1, C4, C6, C7)

This adapter is implemented under the LedgerProof protocol's load-bearing constraints:

- **C1** — No claim of regulator endorsement. No claim of Article 40 presumption of conformity. **This adapter is not endorsed by Mistral AI SAS.** It is not endorsed by the European Commission, the AI Office, any national competent authority, or any standards body.
- **C4** — Local verification only. The adapter does **not** phone home to LedgerProof servers during normal operation.
- **C6** — Stream-aware signing. Streaming responses are signed using an incremental SHA-256 over text deltas; the body is never buffered in full.
- **C7** — Side-channel emission only. The adapter **cannot and does not modify** the Codestral response payload.

## GDPR data-minimisation

Receipts never carry raw prompt, suffix, or generated-code text. Content is referenced by
SHA-256 hash + byte length only. Identifier fields (`deployer_id`, `user_session_id`,
`reviewer_id`) reject email-shaped strings to prevent direct-identifier leakage
(GDPR Art. 4(1) / Art. 5(1)(c)).

The `has_security_pattern` flag is a single boolean — it does not carry CVE numbers,
vulnerable line numbers, or stack traces.

## Scope disclaimer

LedgerProof provides an **evidence layer for Article 50 transparency obligations only**.

It does **not** cover:

- Article 9 (risk management system)
- Article 10 (data and data governance)
- Article 13 (transparency and information to deployers)
- Article 15 (accuracy, robustness, cybersecurity)
- Article 72 (post-market monitoring)

LedgerProof does **not** confer presumption of conformity under Article 40. LedgerProof
is **not endorsed by Mistral AI SAS**, the European Commission, the AI Office, any
national competent authority, or any standards body.

The `safety_critical_code_review/v1` schema records deployer-asserted facts about a
human review step. It is **not** a certification that the reviewed code is safe, secure,
or fit for any particular purpose. Liability for deployed code remains with the deployer.

This adapter wraps the official Mistral Python SDK; it is not affiliated with Mistral AI SAS.

## License

Apache 2.0. Copyright 2026 LedgerProof Foundation (in formation: US 501(c)(3) Delaware
+ Dutch Stichting EU subsidiary).
