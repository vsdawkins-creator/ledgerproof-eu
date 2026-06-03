"""
Quickstart: wrap DashScope's Generation, send a message, see a receipt on stderr.

Requires:
    pip install ledgerproof-qwen
    export DASHSCOPE_API_KEY=...

The DashScope GenerationResponse is returned UNCHANGED. The receipt is emitted
on the side channel only (constraint C7).
"""

from __future__ import annotations

import os

from ledgerproof_qwen import (
    LedgerProofQwen,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    client = LedgerProofQwen(
        deployer_id="acme-corp-eu",
        api_key=os.environ["DASHSCOPE_API_KEY"],
        emitter=StderrEmitter(),
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="Customer support chatbot. End-user disclosure shown in UI banner.",
        ),
    )

    response = client.generation.call(
        model="qwen-max",
        messages=[
            {"role": "user", "content": "In one sentence: what is the EU AI Act?"},
        ],
    )

    # The response is the standard DashScope GenerationResponse — unchanged (C7).
    print("---- Assistant reply ----")
    if response.output.choices:
        print(response.output.choices[0].message.content)
    else:
        print(response.output.text)
    print("---- (A signed receipt was emitted on stderr) ----")


if __name__ == "__main__":
    main()
