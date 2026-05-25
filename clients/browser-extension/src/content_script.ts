/**
 * Content script: scans the active tab for elements tagged with
 * `data-lpr-receipt="{sequence}"` and decorates them with a verification badge.
 *
 * Privacy posture:
 * - Only runs on document_idle, only on the user's active tab (via activeTab).
 * - Sends no telemetry. No analytics. No history.
 * - All network goes through the service worker, which only talks to api-eu.
 */

(async function () {
  const elements = Array.from(
    document.querySelectorAll<HTMLElement>("[data-lpr-receipt]")
  );
  if (elements.length === 0) return;

  for (const element of elements) {
    const seq = element.getAttribute("data-lpr-receipt");
    if (!seq || !/^\d+$/.test(seq)) {
      decorateBadge(element, "invalid");
      continue;
    }
    const response: any = await chrome.runtime.sendMessage({
      type: "verify",
      sequence: parseInt(seq, 10),
    });
    if (response?.ok && response.entry) {
      const entry = response.entry;
      if (entry.deleted_at) {
        decorateBadge(element, "erased", entry);
      } else {
        decorateBadge(element, "verified", entry);
      }
    } else {
      decorateBadge(element, "unknown");
    }
  }
})();

function decorateBadge(
  element: HTMLElement,
  status: "verified" | "erased" | "invalid" | "unknown",
  entry?: any
): void {
  const badge = document.createElement("span");
  badge.style.cssText = `
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-left: 6px;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 11px;
    font-family: ui-sans-serif, system-ui, sans-serif;
    font-weight: 500;
    vertical-align: middle;
    cursor: pointer;
  `;

  const labels: Record<typeof status, { text: string; bg: string; fg: string }> = {
    verified: { text: "✓ LedgerProof", bg: "#dcfce7", fg: "#166534" },
    erased: { text: "⊘ LedgerProof (erased)", bg: "#fef3c7", fg: "#854d0e" },
    invalid: { text: "✗ LedgerProof", bg: "#fee2e2", fg: "#991b1b" },
    unknown: { text: "? LedgerProof", bg: "#e5e7eb", fg: "#4b5563" },
  };
  const { text, bg, fg } = labels[status];
  badge.textContent = text;
  badge.style.backgroundColor = bg;
  badge.style.color = fg;
  badge.title =
    entry && entry.entry_hash
      ? `LPR receipt sequence ${entry.sequence}, hash ${entry.entry_hash.slice(0, 16)}…`
      : `Status: ${status}`;
  badge.addEventListener("click", (ev) => {
    ev.preventDefault();
    if (entry?.sequence !== undefined) {
      window.open(
        `https://api-eu.ledgerproofhq.io/v1/verify/${entry.sequence}`,
        "_blank",
        "noopener,noreferrer"
      );
    }
  });
  element.appendChild(badge);
}
