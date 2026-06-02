"""Quickstart: drop LedgerProofComponent into a Haystack 2.x RAG pipeline.

Run:
    pip install ledgerproof-haystack haystack-ai
    export OPENAI_API_KEY=sk-...
    python examples/01_rag_pipeline_quickstart.py

This example builds a minimal RAG pipeline (in-memory retriever + LLM)
and attaches a LedgerProof side-channel receipt component at the LLM node.

C7: receipts are emitted to the side-channel (MemoryEmitter here, swap
for FileEmitter / JSONLEmitter / your own CallableEmitter in prod).
C1: this code makes no Article 40 presumption claim. It produces
cryptographic transparency receipts under Article 50.
"""

from __future__ import annotations

from haystack import Document, Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

from ledgerproof_haystack import (
    LedgerProofComponent,
    MemoryEmitter,
    load_or_generate_signing_key,
)


def main() -> None:
    # 1. LedgerProof signing key (persist to disk in production).
    key = load_or_generate_signing_key("./.lpr-signing-key.pem")

    # 2. Side-channel emitter — receipts go HERE, not into user output.
    receipts = MemoryEmitter()

    # 3. Build a Haystack pipeline.
    store = InMemoryDocumentStore()
    store.write_documents([
        Document(content="The EU AI Act enters force Aug 2, 2026 for Article 50."),
        Document(content="LedgerProof is a Foundation-stewarded open protocol."),
    ])

    template = (
        "Answer using the documents.\n"
        "Documents: {% for d in documents %}{{ d.content }}\n{% endfor %}\n"
        "Question: {{ question }}\nAnswer:"
    )

    pipeline = Pipeline()
    pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=store))
    pipeline.add_component("prompt", PromptBuilder(template=template))
    pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))
    pipeline.add_component(
        "ledgerproof",
        LedgerProofComponent(
            signing_key=key,
            schema="rag_pipeline_session/v1",
            deployer="acme-bank-de",
            emitter=receipts,
            model_id="gpt-4o-mini",
            extra_fields={
                "pipeline_name": "rag-quickstart",
                "component_count": 4,
                "retrieved_doc_count": 2,
            },
        ),
    )

    pipeline.connect("retriever.documents", "prompt.documents")
    pipeline.connect("prompt.prompt", "llm.prompt")
    pipeline.connect("llm.replies", "ledgerproof.content")

    question = "When does Article 50 take effect?"
    result = pipeline.run({
        "retriever": {"query": question},
        "prompt": {"question": question},
        "ledgerproof": {"query": question},
    })

    print("LLM reply :", result["llm"]["replies"][0])
    print("Receipt id:", result["ledgerproof"]["receipt_id"])
    print("Sidechannel receipts captured:", len(receipts))


if __name__ == "__main__":
    main()
