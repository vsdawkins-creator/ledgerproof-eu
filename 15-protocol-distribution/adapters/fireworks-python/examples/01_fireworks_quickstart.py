"""
Quickstart: wrap a Fireworks client, call Llama 3.1 on Fireworks, see a receipt on stderr.

Requires:
    pip install ledgerproof-fireworks
    export FIREWORKS_API_KEY=...

The Fireworks ChatCompletion is returned UNCHANGED. The receipt is emitted
on the side channel only (constraint C7).
"""

from __future__ import annotations

import os

from ledgerproof_fireworks import (
    LedgerProofFireworks,
    OpenModelAttribution,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    client = LedgerProofFireworks(
        deployer_id="acme-corp-eu",
        api_key=os.environ.get("FIREWORKS_API_KEY"),
        emitter=StderrEmitter(),
        schema="open_model_hosted/v1",
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="Customer support chatbot. End-user disclosure shown in UI banner.",
        ),
        # Explicit open-model attribution — Fireworks hosts, Meta builds the weights.
        open_model=OpenModelAttribution(
            underlying_model_family="llama",
            underlying_model_provider="meta",
            host_provider="fireworks",
            model_license="llama-3.1-community",
            weights_origin="https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct",
        ),
    )

    response = client.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-70b-instruct",
        messages=[
            {"role": "user", "content": "In one sentence: what is the EU AI Act?"},
        ],
    )

    # The response is the standard Fireworks ChatCompletion — unchanged (C7).
    print("---- Assistant reply ----")
    print(response.choices[0].message.content)
    print("---- (A signed receipt was emitted on stderr) ----")


if __name__ == "__main__":
    main()
