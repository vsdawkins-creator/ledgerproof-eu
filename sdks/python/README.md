# ledgerproof

**EU AI Act Article 50 compliance in three lines of Python.**

LedgerProof is the open-protocol cryptographic transparency layer for AI-generated content.
This package gives you a one-line install and a three-line integration that issues a
machine-readable, Bitcoin-anchored, GDPR-safe receipt for every AI completion your code
produces. No backend changes. No new endpoints. No vendor lock-in.

## Why this exists

The EU AI Act's Article 50 takes effect August 2, 2026. Penalties reach €15M or 3% of
worldwide revenue. Compliance requires machine-readable disclosure of AI-generated
content. This package is the path of least resistance: install it, attach it, you're
compliant.

## Install

```bash
pip install ledgerproof
```

## Three-line compliance

```python
import openai
import ledgerproof

client = openai.OpenAI()
ledgerproof.attach(
    client,
    publisher_id="LEI:5493001KJTIIGC8Y1R12",   # your legal-entity identifier
    deployer_country="DE",                      # ISO 3166-1 alpha-2
    deployer_name="Acme Corp",
)

# Every chat completion below auto-issues an LPR receipt anchored to Bitcoin.
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku."}],
)
print(response.choices[0].message.content)
```

You get back the exact same `response` object. The LPR receipt is issued in the
background. If you want the receipt synchronously, await the attached future:

```python
receipt = response._ledgerproof_future.result(timeout=10)
print(receipt.verify_url)
# https://api-eu.ledgerproofhq.io/v1/verify/42
```

## Direct usage (no monkey-patching)

```python
from ledgerproof import LedgerProof

lp = LedgerProof(
    publisher_id="LEI:5493001KJTIIGC8Y1R12",
    deployer_country="DE",
    # api_key reads from LEDGERPROOF_API_KEY env var if not passed
)

receipt = lp.publish_ai_article_50(
    artifact="The generated article text here...",
    artifact_content_type="text/plain",
    ai_system_id="openai/gpt-4o/2024-11-20",
    deployer_name="Acme Insurance AG",
    content_category="SYNTHETIC_TEXT",
    generation_type="FULLY_GENERATED",
    is_public_interest=False,
)

print(receipt.sequence, receipt.entry_hash, receipt.verify_url)
```

The artifact (your text/image/audio/video bytes) is hashed locally — it never leaves
your machine. Only the SHA-256 hash is transmitted to LedgerProof.

## Article 50(4) human editorial review exemption

If your content went through human editorial review, you can chain a review receipt
to invoke the Article 50(4) exemption:

```python
review_receipt = lp.publish_human_review(
    original_entry_hash=receipt.entry_hash,
    original_sequence=receipt.sequence,
    reviewed_artifact=edited_text,
    reviewer_role="senior-editor",        # role, NOT a name
    reviewer_country="DE",
    review_type="SUBSTANTIAL_EDIT",
    is_public_interest=True,
    review_rationale="Reviewed for factual accuracy and source attribution.",
)
```

## Async support

```python
from ledgerproof import AsyncLedgerProof

async with AsyncLedgerProof(
    publisher_id="LEI:5493001KJTIIGC8Y1R12",
    deployer_country="DE",
) as lp:
    receipt = await lp.publish_ai_article_50(
        artifact=text,
        artifact_content_type="text/plain",
        ai_system_id="openai/gpt-4o/2024-11-20",
        deployer_name="Acme Corp",
        content_category="SYNTHETIC_TEXT",
    )
```

## Verification

Anyone can verify a receipt without authentication or being a customer:

```python
entry = lp.verify(sequence=42)
print(entry.entry_hash, entry.signature, entry.content)
```

Or look up by content hash — for journalists, regulators, courts:

```python
matches = lp.lookup_by_content_hash("a1b2c3d4...")
for m in matches:
    print(m.sequence, m.publisher_id, m.entry_hash)
```

## Configuration

The SDK reads from these environment variables (kwargs always win):

| Variable | Purpose |
|---|---|
| `LEDGERPROOF_API_KEY` | Your publisher API key (provisioned by your LedgerProof operator) |
| `LEDGERPROOF_API_BASE` | API endpoint (default: `https://api-eu.ledgerproofhq.io`) |
| `LEDGERPROOF_SIGNING_KEY_HEX` | 64-char hex private signing key (overrides file store) |
| `LEDGERPROOF_KEY_ID` | Logical name for the signing key (default: `"default"`) |
| `LEDGERPROOF_KEY_PATH` | Override the file-store key location |

The signing key is auto-generated on first use and saved to
`~/.config/ledgerproof/signing_key.bin` with `0600` permissions.
**Back it up.** It cannot be recovered if lost.

## GDPR by construction

The SDK refuses to transmit anything that looks like personal data. The architecture
forbids the failures:

- `publisher_id` must be a legal-entity identifier (LEI/EUID/VAT/DID). Emails are rejected.
- `reviewer_role` must be a role identifier ("senior-editor"), never a person's name.
- The artifact (your content) is hashed locally; only the hash leaves your machine.
- GDPR Article 17 erasure is supported via soft-delete on the server side.

See the [LedgerProof GDPR Architecture](https://github.com/vsdawkins-creator/ledgerproof-eu/blob/main/12-eu-compliance/03-GDPR-ARCHITECTURE-AND-DPA.md).

## Provider support

| Provider | Status |
|---|---|
| OpenAI | ✅ `ledgerproof.attach(openai_client, ...)` |
| Anthropic | ⏳ Coming in `1.1.0` |
| Google Gemini | ⏳ Coming in `1.1.0` |
| Mistral | ⏳ Coming in `1.1.0` |
| Hugging Face | ⏳ Coming in `1.2.0` (sidecar) |
| LangChain | ⏳ Coming in `1.1.0` (`langchain-ledgerproof` package) |
| Vercel AI SDK | TypeScript only — see [`@ledgerproof/vercel-ai`](https://www.npmjs.com/package/@ledgerproof/vercel-ai) |

For any provider not yet adapted, use `LedgerProof.publish_ai_article_50()` directly.

## Testing your integration

```bash
pytest -m live   # only runs if LEDGERPROOF_LIVE_API_KEY is set
```

## Links

- [Documentation](https://docs.ledgerproofhq.io/sdks/python)
- [LPR v1.1 Specification](https://github.com/vsdawkins-creator/ledgerproof-eu/blob/main/04-lpr-spec/LPR-1.1-SPECIFICATION.md)
- [IETF Draft](https://github.com/vsdawkins-creator/ledgerproof-eu/blob/main/04-lpr-spec/IETF-DRAFT-DAWKINS-SCITT-AI-ARTICLE50-00.txt)
- [EU AI Act Article 50](https://artificialintelligenceact.eu/article/50/)
- [Issues](https://github.com/vsdawkins-creator/ledgerproof-python/issues)

## License

Apache-2.0. See [LICENSE](LICENSE).
