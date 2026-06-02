"""Example 02 — EU data residency receipt with europe-west4.

Demonstrates the strategic Vertex AI pattern for European regulated
industries: deploying inference in a specific EU region (here
``europe-west4`` = Eemshaven, Netherlands) and emitting an
``eu_data_residency/v1`` receipt that captures project + location +
region-of-inference attestation.

Disclaimer: the receipt attests the *deployer's configured region*. It
does NOT independently verify Google Cloud's physical region routing.
Pair with GCP audit logs for end-to-end evidence.

Run with:
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json \
    python examples/02_eu_residency.py
"""
from __future__ import annotations

import vertexai

from ledgerproof_vertexai import LedgerProofGenerativeModel, configure


def main() -> None:
    # europe-west4 → Eemshaven, Netherlands (region_of_inference: EU/NL).
    vertexai.init(project="acme-eu-prod", location="europe-west4")

    configure(
        deployer_id="urn:lpr:deployer:acme-bank-de",
        sink="./eu-receipts.jsonl",
    )

    model = LedgerProofGenerativeModel(
        "gemini-2.0-flash-001",
        lpr_schema="eu_data_residency/v1",
    )

    # German-language inference, EU region, EU receipt.
    resp = model.generate_content(
        "Erkläre in einem Satz, was DORA (EU 2022/2554) für Banken bedeutet."
    )
    print("Vertex AI (europe-west4):", resp.text)
    print("EU residency receipt appended to ./eu-receipts.jsonl")


if __name__ == "__main__":
    main()
