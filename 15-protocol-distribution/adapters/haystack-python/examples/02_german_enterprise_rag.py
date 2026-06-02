"""German enterprise RAG with LedgerProof disclosure receipts.

Scenario:
    Allianz / Munich Re / Deutsche Bank-style enterprise deploying
    Haystack 2.x as their internal RAG backbone for compliance
    advisors. Each query produces:
      1. A `rag_pipeline_session/v1` receipt (Art. 50(1))
      2. A `generated_content/v1` receipt (Art. 50(2))
    Receipts are persisted to a JSONL audit log.

Run:
    export OPENAI_API_KEY=sk-...
    python examples/02_german_enterprise_rag.py
"""

from __future__ import annotations

from haystack import Document, Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

from ledgerproof_haystack import (
    JSONLEmitter,
    LedgerProofComponent,
    LedgerProofGeneratorWrapper,
    load_or_generate_signing_key,
)


def main() -> None:
    key = load_or_generate_signing_key("./.lpr-de-enterprise.pem")
    audit_log = JSONLEmitter("./audit/lpr-receipts.jsonl")

    store = InMemoryDocumentStore()
    store.write_documents([
        Document(content="§ 25a KWG verlangt geeignete Geschäftsorganisation."),
        Document(content="DSGVO Artikel 6 regelt die Rechtmäßigkeit der Verarbeitung."),
        Document(content="EU AI Act Art. 50 erfordert Transparenz bei generativen Systemen."),
    ])

    template = (
        "Beantworte auf Deutsch.\n"
        "Quellen: {% for d in documents %}- {{ d.content }}\n{% endfor %}\n"
        "Frage: {{ frage }}\nAntwort:"
    )

    # Wrap the generator so each generation produces a generated_content/v1.
    inner_llm = OpenAIGenerator(model="gpt-4o-mini")
    wrapped_llm = LedgerProofGeneratorWrapper(
        inner=inner_llm,
        signing_key=key,
        deployer="allianz-compliance-de",
        emitter=audit_log,
        gdpr_lawful_basis="art-6-1-c-legal-obligation",
    )

    # Session-level receipt at the end of the pipeline.
    session_receipt = LedgerProofComponent(
        signing_key=key,
        schema="rag_pipeline_session/v1",
        deployer="allianz-compliance-de",
        emitter=audit_log,
        model_id="gpt-4o-mini",
        gdpr_lawful_basis="art-6-1-c-legal-obligation",
        extra_fields={
            "pipeline_name": "de-compliance-rag",
            "component_count": 4,
            "retrieved_doc_count": 3,
        },
    )

    pipeline = Pipeline()
    pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=store))
    pipeline.add_component("prompt", PromptBuilder(template=template))
    pipeline.add_component("llm", wrapped_llm)
    pipeline.add_component("ledgerproof_session", session_receipt)

    pipeline.connect("retriever.documents", "prompt.documents")
    pipeline.connect("prompt.prompt", "llm.prompt")
    pipeline.connect("llm.replies", "ledgerproof_session.content")

    frage = "Welche Transparenzpflichten gelten ab August 2026?"
    result = pipeline.run({
        "retriever": {"query": frage},
        "prompt": {"frage": frage},
        "ledgerproof_session": {"query": frage},
    })

    print("Antwort:", result["llm"]["replies"][0])
    print("Receipt id (session):", result["ledgerproof_session"]["receipt_id"])
    print("Audit log: ./audit/lpr-receipts.jsonl")


if __name__ == "__main__":
    main()
