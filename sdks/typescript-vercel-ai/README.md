# @ledgerproof/vercel-ai

Vercel AI SDK plug-in. Three lines, every AI generation issues an LPR receipt.

```bash
npm install @ledgerproof/sdk @ledgerproof/vercel-ai
```

```ts
import { streamText } from "ai";
import { openai } from "@ai-sdk/openai";
import { ledgerproof } from "@ledgerproof/vercel-ai";

const result = await streamText({
  model: openai("gpt-4o"),
  prompt: "Write a haiku about Bitcoin.",
  experimental_telemetry: ledgerproof({
    publisherId: "LEI:5493001KJTIIGC8Y1R12",
    deployerCountry: "DE",
    deployerName: "Acme Corp",
  }),
});

// Compliant. Receipt issued in the background.
```

Apache-2.0.
