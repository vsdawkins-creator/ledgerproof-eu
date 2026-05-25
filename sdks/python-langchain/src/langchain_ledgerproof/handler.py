"""LedgerProofCallbackHandler — a LangChain BaseCallbackHandler.

Hooks into the LangChain callbacks system to issue an LPR receipt every
time an LLM completes. Works for ``ChatModel.invoke``, ``LLM.predict``,
streaming, and agentic chains (every LLM step gets its own receipt).
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any
from uuid import UUID

from langchain_core.callbacks.base import BaseCallbackHandler
from ledgerproof import LedgerProof
from ledgerproof.errors import LedgerProofError

if TYPE_CHECKING:
    from langchain_core.outputs import LLMResult

logger = logging.getLogger("langchain_ledgerproof")


class LedgerProofCallbackHandler(BaseCallbackHandler):
    """LangChain callback that issues an LPR Article 50 receipt on every LLM completion.

    Drop into any LangChain LLM or chain::

        llm = ChatAnthropic(callbacks=[LedgerProofCallbackHandler(...)])

    All receipts are issued asynchronously in a background thread. Your chain
    is not blocked. Failures fail open — a warning is logged, your chain
    continues normally.
    """

    def __init__(
        self,
        *,
        publisher_id: str,
        deployer_country: str,
        deployer_name: str,
        ai_system_id: str | None = None,
        api_key: str | None = None,
        api_base: str | None = None,
        is_public_interest: bool | None = None,
    ) -> None:
        """Initialize the callback.

        :param publisher_id: Your legal-entity identifier (LEI/EUID/VAT/DID).
        :param deployer_country: ISO 3166-1 alpha-2 country code.
        :param deployer_name: Human-readable organization name.
        :param ai_system_id: Override the AI system identifier in the receipt.
            Default derived from the LangChain LLM metadata.
        :param api_key: LedgerProof API key. Falls back to ``LEDGERPROOF_API_KEY``.
        :param api_base: LedgerProof endpoint. Defaults to api-eu.ledgerproofhq.io.
        :param is_public_interest: Tag every receipt with this assertion.
        """
        self._lp = LedgerProof(
            publisher_id=publisher_id,
            deployer_country=deployer_country,
            api_key=api_key,
            api_base=api_base,
        )
        self._deployer_name = deployer_name
        self._ai_system_id_override = ai_system_id
        self._is_public_interest = is_public_interest
        self._executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="ledgerproof-langchain"
        )
        # Map run_id → invocation context for picking up the right metadata at end.
        self._runs: dict[UUID, dict[str, Any]] = {}

    # ── LangChain callback hooks ────────────────────────────────────────

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        """Stash the LLM identity so we can use it at end-time."""
        model_name = (
            serialized.get("kwargs", {}).get("model")
            or serialized.get("kwargs", {}).get("model_name")
            or serialized.get("name")
            or "langchain/unknown"
        )
        # Infer provider from the serialized.id chain (e.g., ["langchain", "chat_models", "anthropic", "ChatAnthropic"]).
        ids = serialized.get("id", [])
        if isinstance(ids, list) and len(ids) >= 3:
            provider = ids[2]
        else:
            provider = "langchain"
        self._runs[run_id] = {
            "ai_system_id": self._ai_system_id_override or f"{provider}/{model_name}",
        }

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[Any]],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        """Chat models use this instead of on_llm_start."""
        self.on_llm_start(serialized, [], run_id=run_id, **kwargs)

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, **kwargs: Any) -> None:
        """Extract the generation text and issue a receipt."""
        context = self._runs.pop(run_id, {})
        ai_system_id = context.get("ai_system_id", "langchain/unknown")

        # Concatenate all generations' text. For chat models the text is in
        # ``generation.message.content``; for completion LLMs it's in
        # ``generation.text``.
        text = self._extract_text(response)
        if not text:
            return
        self._executor.submit(self._issue_safe, text, ai_system_id)

    def on_llm_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> None:
        """LLM failed — drop the context, no receipt to issue."""
        self._runs.pop(run_id, None)

    # ── Internals ───────────────────────────────────────────────────────

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Pull all generated text out of a LangChain LLMResult."""
        try:
            parts: list[str] = []
            for generation_list in response.generations:
                for gen in generation_list:
                    text = getattr(gen, "text", "")
                    if text:
                        parts.append(text)
                    else:
                        message = getattr(gen, "message", None)
                        if message is not None:
                            content = getattr(message, "content", "")
                            if isinstance(content, str):
                                parts.append(content)
            return "\n".join(parts)
        except (AttributeError, TypeError):
            return ""

    def _issue_safe(self, text: str, ai_system_id: str) -> Any:
        try:
            return self._lp.publish_ai_article_50(
                artifact=text,
                artifact_content_type="text/plain",
                ai_system_id=ai_system_id,
                deployer_name=self._deployer_name,
                content_category="SYNTHETIC_TEXT",
                generation_type="FULLY_GENERATED",
                is_public_interest=self._is_public_interest,
            )
        except LedgerProofError as exc:
            logger.warning("LedgerProof receipt issuance failed (fail-open): %s", exc)
            return None

    def __del__(self) -> None:
        try:
            self._executor.shutdown(wait=False)
        except Exception:
            pass


__all__ = ["LedgerProofCallbackHandler"]
