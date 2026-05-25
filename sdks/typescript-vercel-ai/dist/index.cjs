"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/index.ts
var index_exports = {};
__export(index_exports, {
  ledgerproof: () => ledgerproof
});
module.exports = __toCommonJS(index_exports);
var import_sdk = require("@ledgerproof/sdk");
function ledgerproof(options) {
  const lp = new import_sdk.LedgerProof({
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
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ledgerproof
});
