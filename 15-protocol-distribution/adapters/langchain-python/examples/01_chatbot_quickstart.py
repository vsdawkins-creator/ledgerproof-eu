"""Minimal LedgerProof callback handler example.

Run:
    pip install ledgerproof-langchain langchain-openai
    export OPENAI_API_KEY=sk-...
    python examples/01_chatbot_quickstart.py

The LLM response prints to stdout. The signed transparency receipt prints
on its own line, demonstrating that the receipt is a side channel and does
not modify the model output.
"""

from __future__ import annotations

import json
import queue

from ledgerproof_langchain import LedgerProofCallbackHandler, QueueEmitter


def main() -> None:
    receipt_queue: "queue.Queue[dict]" = queue.Queue()
    emitter = QueueEmitter(receipt_queue)

    handler = LedgerProofCallbackHandler(
        deployer_id="acme-corp-eu",
        schema="chatbot_session/v1",
        emitter=emitter,
    )

    # Lazy import so the example file is importable without optional deps.
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        print(
            "This example requires langchain-openai. Install it with:\n"
            "    pip install langchain-openai\n"
        )
        return

    llm = ChatOpenAI(model="gpt-4o-mini", callbacks=[handler])
    response = llm.invoke("In one sentence: what is the EU AI Act?")
    print("LLM response:")
    print(response.content)
    print()

    print("LedgerProof receipt (side channel):")
    envelope = receipt_queue.get_nowait()
    print(json.dumps(envelope, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
