"""Showcase the `reasoning_trace/v1` receipt for DeepSeek-R1.

`deepseek-reasoner` returns two fields on the assistant message:
- `content`            — the final answer text
- `reasoning_content`  — the chain-of-thought trace

Both are AI-generated text. When the trace is surfaced to the user OR used in
downstream decision-making, the Article 50(1) transparency surface gains a new
requirement: a regulator or end-user asking "what reasoning produced this
answer?" must get a verifiable answer.

This receipt schema binds three things together:
- the prompt hash
- the final answer hash
- the chain-of-thought trace hash (optional — populated if the trace is present)

The deployer does NOT have to disclose the raw trace text to an auditor — the
hash is sufficient to prove the binding once the deployer surfaces the trace
under their normal retention policy.

    pip install ledgerproof-deepseek
    export DEEPSEEK_API_KEY=sk-...
    python examples/02_reasoner_with_trace.py
"""

from __future__ import annotations

from ledgerproof_deepseek import LedgerProofDeepSeek


def main() -> None:
    client = LedgerProofDeepSeek(
        deployer_id="urn:eu:deployer:acme-bank-de",
        regulatory_context={
            "schema": "reasoning_trace/v1",
            "jurisdiction": "EU",
            "trace_surfaced_to_user": True,
        },
    )

    resp = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {
                "role": "user",
                "content": "Prove that the square root of 2 is irrational.",
            }
        ],
    )

    msg = resp.choices[0].message
    reasoning = getattr(msg, "reasoning_content", None) or ""

    print("--- reasoning trace ---")
    print(reasoning[:400] + ("..." if len(reasoning) > 400 else ""))
    print("--- final answer ---")
    print(msg.content)
    print(
        "--- reasoning_trace/v1 receipt was emitted to stdout above, binding "
        "the prompt to BOTH the answer hash and the trace hash."
    )


if __name__ == "__main__":
    main()
