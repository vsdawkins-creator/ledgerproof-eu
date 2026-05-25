/**
 * @ledgerproof/vercel-ai — Vercel AI SDK plug-in.
 *
 * Usage with Vercel AI SDK 3+::
 *
 *   import { streamText } from "ai";
 *   import { openai } from "@ai-sdk/openai";
 *   import { ledgerproof } from "@ledgerproof/vercel-ai";
 *
 *   const result = await streamText({
 *     model: openai("gpt-4o"),
 *     prompt: "Write a haiku.",
 *     experimental_telemetry: ledgerproof({
 *       publisherId: "LEI:5493001KJTIIGC8Y1R12",
 *       deployerCountry: "DE",
 *       deployerName: "Acme Corp",
 *     }),
 *   });
 */

import { LedgerProof } from "@ledgerproof/sdk";
import type { Receipt } from "@ledgerproof/sdk";

export interface LedgerProofTelemetryOptions {
  publisherId: string;
  deployerCountry: string;
  deployerName: string;
  aiSystemId?: string;
  apiKey?: string;
  apiBase?: string;
  isPublicInterest?: boolean;
}

/**
 * Build a Vercel AI SDK `experimental_telemetry` recorder.
 *
 * Receipts are issued asynchronously after each generation completes.
 * Your `streamText` / `generateText` call returns immediately as usual.
 */
export function ledgerproof(options: LedgerProofTelemetryOptions) {
  const lp = new LedgerProof({
    publisherId: options.publisherId,
    deployerCountry: options.deployerCountry,
    apiKey: options.apiKey,
    apiBase: options.apiBase,
  });

  return {
    isEnabled: true,
    recordSpan: false,
    metadata: {
      // Vercel AI SDK exposes these as known metadata fields.
      "ledgerproof.publisher_id": options.publisherId,
      "ledgerproof.deployer_country": options.deployerCountry,
    },
    // Custom finalize callback — invoked by Vercel AI SDK when a span ends.
    // The exact hook depends on SDK version; we expose the recorder shape
    // they support and the consumer wires it.
    onFinish: async (event: {
      text?: string;
      model?: { modelId?: string };
    }): Promise<Receipt | null> => {
      const text = event?.text ?? "";
      if (!text) return null;
      try {
        const modelId = event?.model?.modelId ?? "vercel-ai/unknown";
        const aiSystemId = options.aiSystemId ?? modelId;
        return await lp.publishAiArticle50({
          artifact: text,
          artifactContentType: "text/plain",
          aiSystemId,
          deployerName: options.deployerName,
          contentCategory: "SYNTHETIC_TEXT",
          generationType: "FULLY_GENERATED",
          ...(options.isPublicInterest !== undefined && {
            isPublicInterest: options.isPublicInterest,
          }),
        });
      } catch {
        return null;
      }
    },
  };
}
