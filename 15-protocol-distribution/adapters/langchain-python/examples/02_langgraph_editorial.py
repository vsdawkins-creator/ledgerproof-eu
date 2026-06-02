"""LangGraph state machine with a human-review node decorated for receipts.

Demonstrates the Article 50(4) editorial-control exemption pattern: a
human reviewer approves AI-generated content, and the `@lpr_receipt_node`
decorator emits a signed `human_review/v1` receipt on the resume edge.

Run:
    pip install "ledgerproof-langchain[langgraph]"
    python examples/02_langgraph_editorial.py
"""

from __future__ import annotations

import hashlib
import json
import queue
from typing import TypedDict

from ledgerproof_langchain import QueueEmitter
from ledgerproof_langchain.langgraph_middleware import lpr_receipt_node


class EditorialState(TypedDict, total=False):
    draft: str
    transcript_sha256: str
    decision: str
    lpr: dict


def main() -> None:
    try:
        from langgraph.graph import END, StateGraph
    except ImportError:
        print(
            "This example requires langgraph. Install it with:\n"
            '    pip install "ledgerproof-langchain[langgraph]"\n'
        )
        return

    receipts: "queue.Queue[dict]" = queue.Queue()
    emitter = QueueEmitter(receipts)

    def generate(state: EditorialState) -> EditorialState:
        draft = "AI-generated press release: Q2 results were within guidance."
        return {
            "draft": draft,
            "transcript_sha256": hashlib.sha256(draft.encode("utf-8")).hexdigest(),
        }

    @lpr_receipt_node(
        deployer_id="acme-corp-eu",
        schema="human_review/v1",
        emitter=emitter,
    )
    def human_review(state: EditorialState) -> EditorialState:
        # In a real graph this would block on a human reviewer's input.
        return {
            "decision": "approved",
            "lpr": {
                "reviewer_id": "reviewer-7421",
                "reviewer_role": "editor",
                "review_outcome": "approved",
                "review_rationale": "Spot-checked figures; consistent with public guidance.",
                "transcript_sha256": state.get("transcript_sha256", "0" * 64),
            },
        }

    graph = StateGraph(EditorialState)
    graph.add_node("generate", generate)
    graph.add_node("human_review", human_review)
    graph.set_entry_point("generate")
    graph.add_edge("generate", "human_review")
    graph.add_edge("human_review", END)
    app = graph.compile()

    final = app.invoke({})
    print("Final state:")
    print(json.dumps({k: v for k, v in final.items() if k != "lpr"}, indent=2))
    print()
    print("Emitted human_review/v1 receipt:")
    print(json.dumps(receipts.get_nowait(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
