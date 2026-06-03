"""
Fill-in-the-middle (FIM) completion — the dominant Codestral usage pattern in
IDEs. The adapter emits a fim_completion/v1 receipt with separate prefix/suffix/
middle hashes plus byte-length positions, so a downstream verifier can audit
how much of the final file was AI-generated without seeing the source.

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
        emitter=StderrEmitter(),
        language="python",
    )

    prompt = "def fib(n):\n    memo = {}\n    "
    suffix = "\n    return memo[n]\n"

    response = client.fim.complete(
        model="codestral-latest",
        prompt=prompt,
        suffix=suffix,
    )

    print(prompt + response.choices[0].message.content + suffix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
