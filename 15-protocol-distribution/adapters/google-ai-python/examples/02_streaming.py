"""
Streaming example: incremental SHA-256 (constraint C6).

The wrapped streaming iterator never buffers the full response body. The
receipt is emitted once the iterator is exhausted.
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
        print("Set GOOGLE_API_KEY before running this example.", file=sys.stderr)
        sys.exit(1)
    genai.configure(api_key=api_key)

    model = LedgerProofGenerativeModel(
        "gemini-2.0-flash",
        deployer_id="acme-eu-bank",
        emitter=StderrEmitter(),
    )

    stream = model.generate_content(
        "Explain transformer attention to a finance compliance officer.",
        stream=True,
    )
    for chunk in stream:
        print(chunk.text, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
