"""Example 01 — Vertex AI quickstart.

Run with:
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json \
    python examples/01_vertex_quickstart.py

A LedgerProof receipt is appended to ./receipts.jsonl for every call.
"""
from __future__ import annotations

import vertexai

from ledgerproof_vertexai import LedgerProofGenerativeModel, configure


def main() -> None:
    vertexai.init(project="my-gcp-project", location="us-central1")

    configure(
        deployer_id="urn:lpr:deployer:quickstart-tenant",
        sink="./receipts.jsonl",
    )

    model = LedgerProofGenerativeModel(
        "gemini-2.0-flash-001",
        lpr_schema="generated_content/v1",
    )

    resp = model.generate_content(
        "In one sentence, what is the EU AI Act?"
    )
    print("Vertex AI says:", resp.text)
    print("Receipt appended to ./receipts.jsonl")


if __name__ == "__main__":
    main()
