"""LangChain × LedgerProof — auto-issue Article 50 receipts for every LLM call.

Usage::

    from langchain_anthropic import ChatAnthropic
    from langchain_ledgerproof import LedgerProofCallbackHandler

    callback = LedgerProofCallbackHandler(
        publisher_id="LEI:5493001KJTIIGC8Y1R12",
        deployer_country="DE",
        deployer_name="Acme Corp",
    )

    llm = ChatAnthropic(model="claude-sonnet-4-6", callbacks=[callback])
    response = llm.invoke("Write a haiku.")
    # The callback issued an LPR receipt for the completion automatically.

Works with any LangChain LLM that emits ``on_llm_end`` events.
"""

from __future__ import annotations

from ._version import __version__
from .handler import LedgerProofCallbackHandler

__all__ = ["LedgerProofCallbackHandler", "__version__"]
