"""
Quickstart: wrap a Mistral client, send a message, see a receipt on stderr.

Requires:
    pip install ledgerproof-mistral
    export MISTRAL_API_KEY=...

The Mistral ChatCompletionResponse is returned UNCHANGED. The receipt is emitted
on the side channel only (constraint C7).
"""

from __future__ import annotations

import os

from ledgerproof_mistral import (
    LedgerProofMistral,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    client = LedgerProofMistral(
        deployer_id="acme-corp-eu",
        api_key=os.environ["MISTRAL_API_KEY"],
        emitter=StderrEmitter(),
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="FR",
            end_user_disclosure_made=True,
            notes="Customer support chatbot. End-user disclosure shown in UI banner.",
        ),
    )

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {"role": "user", "content": "In one sentence: what is the EU AI Act?"},
        ],
    )

    # The response is the standard Mistral ChatCompletionResponse — unchanged (C7).
    print("---- Assistant reply ----")
    print(response.choices[0].message.content)
    print("---- (A signed receipt was emitted on stderr) ----")


if __name__ == "__main__":
    main()
