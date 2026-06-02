"""01_rag_quickstart.py — minimal RAG pipeline with LedgerProof receipts.

Run:
    pip install "ledgerproof-llamaindex[examples]"
    pip install llama-index-llms-openai           # or your LLM of choice
    export OPENAI_API_KEY=...
    mkdir -p data && echo "Refunds are processed within 30 days." > data/refunds.txt
    python examples/01_rag_quickstart.py

What you'll see:
    1. A normal LlamaIndex RAG query + response.
    2. A separate, side-channel log line per signed LedgerProof receipt.
       The response payload itself is UNCHANGED — that's the C7 invariant.
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

    # Side-channel sink. In production this would be a Kafka/SQS-backed queue
    # feeding the Foundation's Merkle batcher.
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
        print(f"Could not read ./data — create some .txt files first ({exc})")
        return 1

    index = VectorStoreIndex.from_documents(docs)
    query_engine = index.as_query_engine()

    response = query_engine.query("What is the refund policy?")
    print("\n=== LlamaIndex response (unchanged by LedgerProof) ===")
    print(response)

    print("\n=== LedgerProof receipts emitted side-channel ===")
    while not receipt_queue.empty():
        env = receipt_queue.get_nowait()
        print(
            f"schema={env['payload']['schema_id']:32s} "
            f"digest={env['digest'][:16]}... "
            f"key={env['signature']['key_id']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
