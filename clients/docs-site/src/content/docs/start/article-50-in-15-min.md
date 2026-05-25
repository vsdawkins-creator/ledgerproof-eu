---
title: Article 50 compliance in 15 minutes
description: From an unmodified production app to full EU AI Act Article 50 compliance in 15 minutes.
---

Goal: take a production app that calls OpenAI (or Anthropic / Google / Mistral)
and make it Article 50 compliant without changing any business logic.

Estimated time: 15 minutes.

## Step 1 — Install (1 min)

```bash
pip install ledgerproof
# or: npm install @ledgerproof/sdk
```

## Step 2 — Get credentials (5 min)

Email [veronica@ledgerproofhq.io](mailto:veronica@ledgerproofhq.io) with:

- Your organization legal name
- Your Legal Entity Identifier (LEI) or VAT number
- The country code where you operate (ISO 3166-1 alpha-2)

You'll receive within one business day:

- `LEDGERPROOF_API_KEY` (a `lp_...` token)
- A confirmation of your `publisher_id`

Until then, run against the staging API with a test publisher: see the
[testing guide](/how-to/testing/).

## Step 3 — Attach to your existing AI client (3 min)

If you're using OpenAI directly:

```python
import openai, ledgerproof

client = openai.OpenAI()  # however you already initialize it
ledgerproof.attach(
    client,
    publisher_id="LEI:5493001KJTIIGC8Y1R12",  # the one you received
    deployer_country="DE",
    deployer_name="Acme Insurance AG",
)
```

If you're using LangChain:

```python
from langchain_ledgerproof import LedgerProofCallbackHandler

callback = LedgerProofCallbackHandler(
    publisher_id="LEI:5493001KJTIIGC8Y1R12",
    deployer_country="DE",
    deployer_name="Acme Insurance AG",
)
# Add `callback` to your chain's callbacks list.
```

If you're using the Vercel AI SDK:

```ts
import { ledgerproof } from "@ledgerproof/vercel-ai";

await streamText({
  model: openai("gpt-4o"),
  prompt: "...",
  experimental_telemetry: ledgerproof({
    publisherId: "LEI:5493001KJTIIGC8Y1R12",
    deployerCountry: "DE",
    deployerName: "Acme Insurance AG",
  }),
});
```

## Step 4 — Deploy (3 min)

Set environment variables in your hosting platform:

```
LEDGERPROOF_API_KEY=lp_xxx
LEDGERPROOF_PUBLISHER_ID=LEI:5493001KJTIIGC8Y1R12
```

Deploy. Verify the next AI call in your logs has a receipt attached.

## Step 5 — Add the disclosure UI (3 min)

For Article 50(2) deepfakes / synthetic media, the disclosure must be visible
to users. The receipt's `transparency_marker` field is the canonical text;
embed it in your UI:

```html
<div data-lpr-receipt="42">
  Your AI-generated content here.
  <small>AI-GENERATED · <a href="https://api-eu.ledgerproofhq.io/v1/verify/42">Verify</a></small>
</div>
```

The `data-lpr-receipt` attribute is picked up automatically by the
[LedgerProof browser extension](https://chrome.google.com/webstore/...) and
the Provenance Search tool — readers see a verification badge next to your
AI content.

## You are Article 50 compliant

What you have now:

- ✅ Machine-readable cryptographic receipt for every AI generation (Article 50(2))
- ✅ Anchored to Bitcoin within 24 hours
- ✅ GDPR-safe: no PII in any receipt
- ✅ Verifiable by regulators without contacting you
- ✅ Survives metadata stripping (the receipt is off-file)
- ✅ Complementary to C2PA / SynthID watermarking — defense in depth

## Next steps

- [Article 50(4) human review exemption](/how-to/human-review/) — chain a
  human-review receipt to invoke the 50(4) text exemption.
- [GDPR Article 17 erasure](/how-to/gdpr-erasure/) — handle data-subject
  erasure requests.
- [Become a Code of Practice signatory](/explain/code-of-practice/) — pursue
  the presumption of conformity.
