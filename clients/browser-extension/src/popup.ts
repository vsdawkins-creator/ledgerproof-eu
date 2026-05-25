/**
 * Extension popup script. Lets the user type a sequence and verify.
 */

const seqInput = document.getElementById("seq") as HTMLInputElement;
const verifyBtn = document.getElementById("verifyBtn") as HTMLButtonElement;
const resultDiv = document.getElementById("result") as HTMLDivElement;

verifyBtn.addEventListener("click", async () => {
  const value = seqInput.value.trim();
  if (!value) {
    resultDiv.textContent = "Enter a sequence number first.";
    return;
  }
  const sequence = parseInt(value, 10);
  if (!Number.isFinite(sequence) || sequence < 0) {
    resultDiv.textContent = "Invalid sequence.";
    return;
  }
  resultDiv.textContent = "Verifying…";
  const response: any = await chrome.runtime.sendMessage({
    type: "verify",
    sequence,
  });
  if (response?.ok && response.entry) {
    const e = response.entry;
    resultDiv.innerHTML = `
      <strong>${e.deleted_at ? "⊘ Erased" : "✓ Verified"}</strong>
      <br />sequence: ${e.sequence}
      <br />entry_hash: ${e.entry_hash.slice(0, 16)}…
      <br />content_type: ${e.content_type}
      <br />publisher_id: ${e.publisher_id}
      <br />issued: ${e.entry_timestamp}
      ${e.deleted_at ? `<br />erased: ${e.deleted_at}` : ""}
    `;
  } else {
    resultDiv.textContent = `Not found or error: ${response?.error ?? "unknown"}`;
  }
});

seqInput.addEventListener("keydown", (ev) => {
  if (ev.key === "Enter") verifyBtn.click();
});
