"""Sonar Deep Research with a custom emitter.

Perplexity's `sonar-deep-research` model performs multi-step web research
and tends to return a long answer with a large citation set. Deep-research
outputs are exactly the kind of artefact that Article 50(4) reaches when
the result is published to a public audience.

This example also demonstrates a custom emitter — replacing the default
stdout `LogEmitter` with a `QueueEmitter` so the caller can inspect /
forward the envelope (e.g. to a Merkle batcher).

Requires `PPLX_API_KEY`.

    pip install ledgerproof-perplexity
    export PPLX_API_KEY=pplx-...
    python examples/03_deep_research.py
"""

from __future__ import annotations

import json
import queue

from ledgerproof_perplexity import LedgerProofPerplexity, QueueEmitter


def main() -> None:
    receipt_q: queue.Queue = queue.Queue()

    client = LedgerProofPerplexity(
        deployer_id="urn:eu:deployer:acme-research",
        regulatory_context={
            "schema": "ai_search_with_citations/v1",
            "jurisdiction": "EU",
        },
        emitter=QueueEmitter(receipt_q),
    )

    resp = client.chat.completions.create(
        model="sonar-deep-research",
        messages=[
            {
                "role": "user",
                "content": (
                    "Survey the current academic literature on differential "
                    "privacy applied to large language model training corpora "
                    "from 2023 through today. Provide a structured comparison "
                    "of the main approaches with citations."
                ),
            },
        ],
    )

    print("--- deep-research answer ---")
    print(resp.choices[0].message.content)

    cites = getattr(resp, "citations", None) or []
    print(f"\n--- {len(cites)} citations grounded the answer ---")

    # Pull the signed envelope out of our QueueEmitter and pretty-print it.
    envelope = receipt_q.get_nowait()
    print("\n--- signed receipt envelope ---")
    print(json.dumps(envelope, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
