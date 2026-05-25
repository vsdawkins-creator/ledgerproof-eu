// src/index.ts
import { LedgerProof } from "@ledgerproof/sdk";
async function receiptFromText(env, text, aiSystemId, options = {}) {
  if (!text) return null;
  try {
    const lp = new LedgerProof({
      publisherId: env.LEDGERPROOF_PUBLISHER_ID,
      deployerCountry: env.LEDGERPROOF_DEPLOYER_COUNTRY,
      apiKey: env.LEDGERPROOF_API_KEY,
      apiBase: env.LEDGERPROOF_API_BASE
    });
    return await lp.publishAiArticle50({
      artifact: text,
      artifactContentType: "text/plain",
      aiSystemId,
      deployerName: env.LEDGERPROOF_DEPLOYER_NAME,
      contentCategory: options.contentCategory ?? "SYNTHETIC_TEXT",
      generationType: "FULLY_GENERATED",
      ...options.isPublicInterest !== void 0 && { isPublicInterest: options.isPublicInterest }
    });
  } catch {
    return null;
  }
}
async function withReceipt(env, ctx, aiSystemId, inference) {
  const result = await inference();
  if (typeof result?.response === "string" && result.response) {
    ctx.waitUntil(receiptFromText(env, result.response, aiSystemId));
  }
  return result;
}
export {
  receiptFromText,
  withReceipt
};
