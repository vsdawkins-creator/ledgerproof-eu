/**
 * Service worker: handles verifier API calls and message-passing with the content script.
 *
 * Manifest V3 service workers are killed when idle; we do not rely on
 * module-level state surviving restarts. State lives in chrome.storage.
 */

import { verifyReceipt, lookupByContentHash, hashArtifact } from "@ledgerproof/sdk/verifier";

interface VerifyMessage {
  type: "verify";
  sequence: number;
}

interface LookupMessage {
  type: "lookup";
  contentHash: string;
}

interface HashMessage {
  type: "hash";
  text: string;
}

type IncomingMessage = VerifyMessage | LookupMessage | HashMessage;

chrome.runtime.onMessage.addListener((msg: IncomingMessage, _sender, sendResponse) => {
  (async () => {
    try {
      switch (msg.type) {
        case "verify": {
          const entry = await verifyReceipt(msg.sequence);
          sendResponse({ ok: true, entry });
          return;
        }
        case "lookup": {
          const matches = await lookupByContentHash(msg.contentHash);
          sendResponse({ ok: true, matches });
          return;
        }
        case "hash": {
          const h = await hashArtifact(msg.text);
          sendResponse({ ok: true, hash: h });
          return;
        }
        default:
          sendResponse({ ok: false, error: "unknown message type" });
      }
    } catch (exc) {
      sendResponse({ ok: false, error: (exc as Error).message });
    }
  })();
  return true; // keep channel open for async sendResponse
});

chrome.runtime.onInstalled.addListener(() => {
  console.log("LedgerProof Verifier installed.");
});
