// src/index.ts
import { LedgerProof } from "@ledgerproof/sdk";
function ledgerproof(options) {
  const lp = new LedgerProof({
    publisherId: options.publisherId,
    deployerCountry: options.deployerCountry,
    apiKey: options.apiKey,
    apiBase: options.apiBase
  });
  return {
    isEnabled: true,
    recordSpan: false,
    metadata: {
      // Vercel AI SDK exposes these as known metadata fields.
      "ledgerproof.publisher_id": options.publisherId,
      "ledgerproof.deployer_country": options.deployerCountry
    },
    // Custom finalize callback — invoked by Vercel AI SDK when a span ends.
    // The exact hook depends on SDK version; we expose the recorder shape
    // they support and the consumer wires it.
    onFinish: async (event) => {
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
          ...options.isPublicInterest !== void 0 && {
            isPublicInterest: options.isPublicInterest
          }
        });
      } catch {
        return null;
      }
    }
  };
}
export {
  ledgerproof
};
