"""02_chat_engine.py — chat engine with per-turn Article 50(1) receipts.

Run:
    pip install "ledgerproof-llamaindex[examples]"
    pip install llama-index-llms-openai
    export OPENAI_API_KEY=...
    mkdir -p data && echo "Our SLA is 99.9% monthly uptime." > data/sla.txt
    python examples/02_chat_engine.py

Each user turn produces a signed receipt on the side channel. The chat
response itself is byte-for-byte unchanged — C7 holds.
"""

from __future__ import annotations

import logging
import queue
import sys

from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.core.callbacks import CallbackManager

from ledgerproof_llamaindex import (
    Ed25519Signer,
    LedgerProofCallbackHandler,
    QueueEmitter,
)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    receipt_queue: queue.Queue = queue.Queue()

    handler = LedgerProofCallbackHandler(
        deployer_id="example-corp-eu",
        signer=Ed25519Signer.ephemeral(),
        emitter=QueueEmitter(receipt_queue),
        article="50(1)",
        model_provider="openai",
        model_name="gpt-4",
    )
    Settings.callback_manager = CallbackManager([handler])

    try:
        docs = SimpleDirectoryReader("./data").load_data()
    except Exception as exc:
        print(f"Could not read ./data ({exc})")
        return 1

    index = VectorStoreIndex.from_documents(docs)
    chat_engine = index.as_chat_engine(chat_mode="condense_question")

    turns = [
        "What is our SLA?",
        "And does that cover scheduled maintenance windows?",
    ]
    for turn in turns:
        print(f"\nUSER:  {turn}")
        resp = chat_engine.chat(turn)
        print(f"BOT:   {resp}")

        # Drain receipts produced by this turn.
        emitted = []
        while not receipt_queue.empty():
            emitted.append(receipt_queue.get_nowait())
        print(f"       [{len(emitted)} LedgerProof receipt(s) emitted]")
        for env in emitted:
            print(
                f"         - schema={env['payload']['schema_id']:32s} "
                f"digest={env['digest'][:16]}..."
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
