"""01 — Completion quickstart.

Minimal example using the sync wrapper around `aleph_alpha_client.Client`.

Set `AA_TOKEN` in your environment before running.
"""

from __future__ import annotations

import os

from aleph_alpha_client import Client, CompletionRequest, Prompt

from ledgerproof_aleph_alpha import (
    InMemoryEmitter,
    LedgerProofAlephAlpha,
    verify_receipt,
)


def main() -> None:
    token = os.environ.get("AA_TOKEN")
    if not token:
        raise SystemExit("Set AA_TOKEN to run this example.")

    upstream = Client(token=token, host="https://api.aleph-alpha.com")

    sink = InMemoryEmitter()
    client = LedgerProofAlephAlpha(
        upstream,
        article="50(2)",
        schema="generated_content/v1",
        deployer_id="example-deployer",
        emitter=sink,
    )

    req = CompletionRequest(
        prompt=Prompt.from_text(
            "In one sentence: what does EU AI Act Article 50 require?"
        ),
        maximum_tokens=64,
    )
    resp = client.complete(req, model="luminous-base")

    print("Completion:", resp.completions[0].completion)
    print("Receipts:", len(sink))
    assert verify_receipt(sink.receipts[0])
    print("Receipt verified locally (C4).")


if __name__ == "__main__":
    main()
