"""
Quickstart: wrap a Together client, call Llama 3.3 on Together, see a receipt on stderr.

Requires:
    pip install ledgerproof-together
    export TOGETHER_API_KEY=...

The Together ChatCompletionResponse is returned UNCHANGED. The receipt is emitted
on the side channel only (constraint C7).
"""

from __future__ import annotations

import os

from ledgerproof_together import (
    LedgerProofTogether,
    OpenModelAttribution,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    client = LedgerProofTogether(
        deployer_id="acme-corp-eu",
        api_key=os.environ.get("TOGETHER_API_KEY"),
        emitter=StderrEmitter(),
        schema="open_model_inference/v1",
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="Customer support chatbot. End-user disclosure shown in UI banner.",
        ),
        # Explicit open-model attribution — Together hosts, Meta builds the weights.
        open_model=OpenModelAttribution(
            underlying_model_family="llama",
            underlying_model_provider="meta",
            host_provider="together",
            model_license="llama-3.3-community",
            weights_origin="https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct",
        ),
    )

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[
            {"role": "user", "content": "In one sentence: what is the EU AI Act?"},
        ],
    )

    # The response is the standard Together ChatCompletionResponse — unchanged (C7).
    print("---- Assistant reply ----")
    print(response.choices[0].message.content)
    print("---- (A signed receipt was emitted on stderr) ----")


if __name__ == "__main__":
    main()
