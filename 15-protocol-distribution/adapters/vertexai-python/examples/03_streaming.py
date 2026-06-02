"""Example 03 — streaming with stream-aware receipt emission (C6).

Streaming chunks are yielded to the caller immediately and unmodified
(C7). The LedgerProof receipt is emitted side-channel after the final
chunk arrives, with the concatenated output digest.

Run with:
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json \
    python examples/03_streaming.py
"""
from __future__ import annotations

import vertexai

from ledgerproof_vertexai import LedgerProofGenerativeModel, configure


def main() -> None:
    vertexai.init(project="acme-eu-prod", location="europe-west4")
    configure(
        deployer_id="urn:lpr:deployer:streaming-demo",
        sink="./stream-receipts.jsonl",
    )

    model = LedgerProofGenerativeModel(
        "gemini-2.0-flash-001",
        lpr_schema="generated_content/v1",
    )

    print("Streamed response:")
    for chunk in model.generate_content(
        "Write a short haiku about regulatory transparency.",
        stream=True,
    ):
        # Chunks reach the caller exactly as Vertex AI produced them.
        text = getattr(chunk, "text", "")
        if text:
            print(text, end="", flush=True)
    print("\n\nReceipt appended to ./stream-receipts.jsonl after final chunk.")


if __name__ == "__main__":
    main()
