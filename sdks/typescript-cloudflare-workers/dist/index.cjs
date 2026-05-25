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
  receiptFromText: () => receiptFromText,
  withReceipt: () => withReceipt
});
module.exports = __toCommonJS(index_exports);
var import_sdk = require("@ledgerproof/sdk");
async function receiptFromText(env, text, aiSystemId, options = {}) {
  if (!text) return null;
  try {
    const lp = new import_sdk.LedgerProof({
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
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  receiptFromText,
  withReceipt
});
