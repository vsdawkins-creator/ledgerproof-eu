"""
LedgerProofChatSession — wraps a `google.generativeai.ChatSession`.

Each `send_message()` call emits a chatbot_session/v1 receipt on the side
channel. Streaming chat is supported via the same incremental hashing pattern
used in the model wrapper (constraint C6).
"""

from __future__ import annotations

import logging
from typing import Any, Iterator, TYPE_CHECKING

from .canonical import IncrementalTextHasher

if TYPE_CHECKING:  # avoid circular import at runtime
    from .model_wrapper import LedgerProofGenerativeModel

logger = logging.getLogger(__name__)


class LedgerProofChatSession:
    """Side-channel wrapper around a Gemini ChatSession."""

    def __init__(
        self,
        inner_chat: Any,
        parent_model: "LedgerProofGenerativeModel",
    ):
        self._inner = inner_chat
        self._parent = parent_model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send_message(self, content: Any, *args: Any, **kwargs: Any) -> Any:
        from .model_wrapper import _coerce_prompt_to_text  # avoid circular

        stream = bool(kwargs.get("stream", False))
        prompt_text, modalities = _coerce_prompt_to_text(content)

        if stream:
            inner_iter = self._inner.send_message(content, *args, **kwargs)
            return _StreamingChatProxy(
                inner=inner_iter,
                parent_model=self._parent,
                user_message_text=prompt_text,
                modalities=modalities,
            )

        response = self._inner.send_message(content, *args, **kwargs)
        try:
            self._parent._emit_for_response(
                response=response,
                user_message_text=prompt_text,
                modalities=modalities,
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof chat receipt emission failed: %s", exc)
        return response

    @property
    def history(self) -> Any:
        return self._inner.history

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class _StreamingChatProxy:
    """Streaming chat response wrapper (mirrors model_wrapper._StreamingResponseProxy)."""

    def __init__(
        self,
        inner: Any,
        parent_model: "LedgerProofGenerativeModel",
        user_message_text: str,
        modalities: list[str],
    ):
        self._inner = inner
        self._parent = parent_model
        self._user_text = user_message_text
        self._modalities = modalities  # type: ignore[assignment]
        self._hasher = IncrementalTextHasher()
        self._last_chunk: Any = None
        self._closed = False

    def __iter__(self) -> Iterator[Any]:
        try:
            for chunk in self._inner:
                self._last_chunk = chunk
                text = getattr(chunk, "text", None)
                if isinstance(text, str):
                    self._hasher.update(text)
                yield chunk
        finally:
            self._finalize()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def resolve(self) -> Any:
        result = None
        if hasattr(self._inner, "resolve"):
            result = self._inner.resolve()
        self._finalize()
        return result

    def _finalize(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            digest_hex = self._hasher.digest().hex()
            self._parent._emit_for_response(
                response=self._last_chunk,
                user_message_text=self._user_text,
                modalities=self._modalities,  # type: ignore[arg-type]
                streaming=True,
                assistant_byte_len_override=self._hasher.byte_count,
                assistant_hash_override=digest_hex,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof streaming chat receipt failed: %s", exc)
