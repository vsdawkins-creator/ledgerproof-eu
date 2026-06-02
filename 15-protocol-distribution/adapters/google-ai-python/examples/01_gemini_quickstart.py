"""
Quickstart: drop-in LedgerProof wrapper around the Gemini Python SDK.

This produces a signed receipt on the side channel (LogEmitter by default,
which writes JSON to the `ledgerproof.receipt` logger).
"""

from __future__ import annotations

import os
import sys

import google.generativeai as genai

from ledgerproof_google_ai import (
    LedgerProofGenerativeModel,
    StderrEmitter,
)


def main() -> None:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(
            "Set GOOGLE_API_KEY before running this example.",
            file=sys.stderr,
        )
        sys.exit(1)
    genai.configure(api_key=api_key)

    model = LedgerProofGenerativeModel(
        "gemini-2.0-flash",
        deployer_id="acme-eu-bank",
        emitter=StderrEmitter(),
    )

    response = model.generate_content(
        "Summarize Article 50 of the EU AI Act in three sentences."
    )
    print(response.text)


if __name__ == "__main__":
    main()
