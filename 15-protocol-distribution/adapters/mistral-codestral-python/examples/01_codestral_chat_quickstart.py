"""
Quickstart: chat-style code generation through Codestral, with a side-channel
generated_code/v1 receipt emitted on each call.

Requires:
    pip install ledgerproof-mistral-codestral
    export MISTRAL_CODESTRAL_API_KEY=...
"""

from __future__ import annotations

import os
import sys

from ledgerproof_mistral_codestral import (
    LedgerProofCodestral,
    StderrEmitter,
)


def main() -> int:
    api_key = os.environ.get("MISTRAL_CODESTRAL_API_KEY")
    if not api_key:
        print("Set MISTRAL_CODESTRAL_API_KEY first.", file=sys.stderr)
        return 1

    client = LedgerProofCodestral(
        deployer_id="acme-corp-eu",
        api_key=api_key,
        emitter=StderrEmitter(),  # signed receipt printed to stderr
        language="python",
    )

    response = client.chat.complete(
        model="codestral-latest",
        messages=[
            {
                "role": "user",
                "content": (
                    "Write a Python function `fib(n)` that returns the nth "
                    "Fibonacci number using memoisation. No prose, just code."
                ),
            }
        ],
    )

    print(response.choices[0].message.content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
