import { Receipt } from '@ledgerproof/sdk';

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

interface LedgerProofTelemetryOptions {
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
declare function ledgerproof(options: LedgerProofTelemetryOptions): {
    isEnabled: boolean;
    recordSpan: boolean;
    metadata: {
        "ledgerproof.publisher_id": string;
        "ledgerproof.deployer_country": string;
    };
    onFinish: (event: {
        text?: string;
        model?: {
            modelId?: string;
        };
    }) => Promise<Receipt | null>;
};

export { type LedgerProofTelemetryOptions, ledgerproof };
