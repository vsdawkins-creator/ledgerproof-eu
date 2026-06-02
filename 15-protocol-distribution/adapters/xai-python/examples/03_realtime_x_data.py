"""Showcase the `realtime_data_inference/v1` receipt.

Grok is distinctive among major LLMs because it can ground answers in
real-time X-platform / web data. When a deployer relies on that grounding,
the Article 50(1) transparency surface gains a new requirement: a regulator
or end-user asking "what sources did the model see?" must get a verifiable
answer.

This receipt schema binds three things together:
- the prompt hash
- the response hash
- a hash over the canonical, deployer-defined source-attribution surface

The adapter does **not** fetch or verify sources itself (C4 — local
verification only). It records the hash you compute. Deployers control the
canonical representation: e.g. JSON-sorted list of (url, capture_timestamp)
pairs, hashed with SHA-256.

If the output qualifies as Article 50(4) "public-interest text" (informing
the public on matters of public interest), set `public_interest_text=True`
so downstream tooling can route those receipts to a stricter labelling /
review queue.

    pip install ledgerproof-xai
    export XAI_API_KEY=xai-...
    python examples/03_realtime_x_data.py
"""

from __future__ import annotations

import hashlib
import json

from ledgerproof_xai import LedgerProofXAI


def canonical_sources_hash(sources: list[dict[str, str]]) -> str:
    """Deployer-defined canonicalization for source-attribution hash.

    Sort the source list by URL, sort each entry's keys, JSON-dump with
    `sort_keys=True`, then SHA-256. Any deterministic scheme works — pick
    one and stick with it across the deployment so receipts are reproducible
    by an auditor.
    """
    normalised = sorted(sources, key=lambda s: s.get("url", ""))
    payload = json.dumps(normalised, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    sources = [
        {"url": "https://x.com/example/status/1234", "captured_at": "2026-08-02T09:15:00Z"},
        {"url": "https://x.com/example/status/5678", "captured_at": "2026-08-02T09:15:10Z"},
    ]
    sources_hash = canonical_sources_hash(sources)

    client = LedgerProofXAI(
        deployer_id="urn:eu:deployer:acme-media-de",
        regulatory_context={
            "schema": "realtime_data_inference/v1",
            "jurisdiction": "EU",
            "realtime_data_used": True,
            "realtime_sources_sha256": sources_hash,
            "public_interest_text": True,
        },
    )

    resp = client.chat.completions.create(
        model="grok-2-latest",
        messages=[
            {
                "role": "user",
                "content": (
                    "Summarise the public-interest discussion happening on X "
                    "right now about EU AI Act enforcement."
                ),
            }
        ],
    )

    print("--- assistant response ---")
    print(resp.choices[0].message.content)
    print("--- realtime_data_inference/v1 receipt emitted with sources hash:")
    print(sources_hash)


if __name__ == "__main__":
    main()
