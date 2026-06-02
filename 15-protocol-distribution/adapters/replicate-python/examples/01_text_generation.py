"""
Example 01 — Text generation with a Replicate-hosted LLM (Llama 3).

Emits a chatbot_session/v1 receipt (Article 50(1)) bound to the model
coordinate and the SHA-256 of the prompt + completion.

Run:
    export REPLICATE_API_TOKEN=r8_...
    python examples/01_text_generation.py

NOTE: Not endorsed by Replicate. Not endorsed by any regulator. The receipt is
evidence-generation only; it does not create a presumption of conformity.
"""

from __future__ import annotations

import sys

from ledgerproof_replicate import (
    LedgerProofReplicateClient,
    StderrEmitter,
)


def main() -> int:
    client = LedgerProofReplicateClient(
        deployer_id="acme-eu",
        emitter=StderrEmitter(),  # receipts go to stderr; model output to stdout
    )

    output = client.run(
        "meta/meta-llama-3-70b-instruct",
        input={
            "prompt": "Explain Article 50 of the EU AI Act in one paragraph.",
            "max_tokens": 256,
        },
    )

    # The model output is returned UNCHANGED (constraint C7).
    if isinstance(output, list):
        text = "".join(str(t) for t in output)
    else:
        text = str(output)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
