/**
 * Provenance Search — public LPR receipt lookup tool.
 *
 * Uses the @ledgerproof/sdk verifier module. No publishing, no auth, no
 * keys. Pure read-only public verifier surface.
 */

import { verifyReceipt, lookupByContentHash, hashArtifact } from "@ledgerproof/sdk/verifier";
import type { EntryResponse } from "@ledgerproof/sdk";

const seqInput = document.getElementById("seq") as HTMLInputElement;
const hashInput = document.getElementById("hash") as HTMLInputElement;
const fileInput = document.getElementById("file") as HTMLInputElement;
const verifySeqBtn = document.getElementById("verifySeqBtn") as HTMLButtonElement;
const lookupHashBtn = document.getElementById("lookupHashBtn") as HTMLButtonElement;
const hashFileBtn = document.getElementById("hashFileBtn") as HTMLButtonElement;
const resultDiv = document.getElementById("result") as HTMLDivElement;

// Tab switching ──────────────────────────────────────────────────────────────
const tabs = document.querySelectorAll<HTMLButtonElement>(".tab");
const panels = document.querySelectorAll<HTMLDivElement>(".panel");
tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    panels.forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    const target = tab.dataset.tab;
    document.querySelector(`[data-panel="${target}"]`)?.classList.add("active");
    resultDiv.style.display = "none";
  });
});

// Result rendering ───────────────────────────────────────────────────────────
function renderResult(html: string): void {
  resultDiv.innerHTML = html;
  resultDiv.style.display = "block";
}

function renderEntry(e: EntryResponse): string {
  const status = e.deleted_at
    ? '<span class="badge erased">⊘ Erased (GDPR Art. 17)</span>'
    : '<span class="badge ok">✓ Verified</span>';
  return `
    ${status}
    <br /><strong>sequence:</strong> ${e.sequence}
    <br /><strong>publisher_id:</strong> ${escapeHtml(e.publisher_id)}
    <br /><strong>content_type:</strong> ${escapeHtml(e.content_type)}
    <br /><strong>entry_hash:</strong> ${escapeHtml(e.entry_hash)}
    <br /><strong>content_hash:</strong> ${escapeHtml(e.content_hash)}
    <br /><strong>issued:</strong> ${escapeHtml(e.entry_timestamp)}
    ${e.deleted_at ? `<br /><strong>erased:</strong> ${escapeHtml(e.deleted_at)}` : ""}
    <br /><br />
    <a href="https://api-eu.ledgerproofhq.io/v1/verify/${e.sequence}" target="_blank" rel="noopener">
      → View raw receipt JSON
    </a>
  `;
}

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[ch]!);
}

// Handlers ───────────────────────────────────────────────────────────────────
verifySeqBtn.addEventListener("click", async () => {
  const value = seqInput.value.trim();
  if (!value) return renderResult("Enter a sequence first.");
  const sequence = parseInt(value, 10);
  if (!Number.isFinite(sequence) || sequence < 0) return renderResult("Invalid sequence.");
  renderResult("Verifying…");
  try {
    const entry = await verifyReceipt(sequence);
    if (entry === null) {
      renderResult('<span class="badge none">Not found</span> No receipt at this sequence.');
    } else {
      renderResult(renderEntry(entry));
    }
  } catch (exc) {
    renderResult(`Error: ${(exc as Error).message}`);
  }
});

lookupHashBtn.addEventListener("click", async () => {
  const hash = hashInput.value.trim().toLowerCase();
  if (!/^[0-9a-f]{64}$/.test(hash)) {
    return renderResult("Hash must be exactly 64 lowercase hex characters.");
  }
  renderResult("Looking up…");
  try {
    const matches = await lookupByContentHash(hash);
    if (matches.length === 0) {
      renderResult('<span class="badge none">No matches</span> No receipt issued for this content hash.');
    } else {
      renderResult(matches.map(renderEntry).join('<hr style="margin:16px 0;" />'));
    }
  } catch (exc) {
    renderResult(`Error: ${(exc as Error).message}`);
  }
});

hashFileBtn.addEventListener("click", async () => {
  const file = fileInput.files?.[0];
  if (!file) return renderResult("Select a file first.");
  renderResult("Hashing locally…");
  try {
    const hash = await hashArtifact(file);
    renderResult(`<strong>SHA-256:</strong> ${hash}<br /><br />Looking up…`);
    const matches = await lookupByContentHash(hash);
    if (matches.length === 0) {
      renderResult(`
        <strong>SHA-256:</strong> ${hash}
        <br /><br /><span class="badge none">No matches</span>
        No receipt has been issued for this file's content.
      `);
    } else {
      renderResult(
        `<strong>SHA-256:</strong> ${hash}<br /><br />` +
        matches.map(renderEntry).join('<hr style="margin:16px 0;" />')
      );
    }
  } catch (exc) {
    renderResult(`Error: ${(exc as Error).message}`);
  }
});
