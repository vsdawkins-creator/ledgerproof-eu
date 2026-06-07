"""
Synchronous client wrapper around `anthropic.Anthropic`.

Intercepts `messages.create()` and `messages.stream()` to emit a receipt on the
side channel (constraint C7) after the response is materialised. The wrapped
response object is returned unchanged.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator

from anthropic import Anthropic

from .canonical import IncrementalTextHasher, hash_text
from .emitter import Emitter, LogEmitter
from .manual import _build_model_ref, _extract_assistant_text, extract_tool_uses
from .schema import (
    ContentRef,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
)
from .signer import Ed25519Signer, Signer
from .version import __version__

logger = logging.getLogger(__name__)


def _extract_user_message_text(messages: list[dict[str, Any]] | None) -> str:
    """Best-effort concatenation of user-role text from a messages list."""
    if not messages:
        return ""
    parts: list[str] = []
    for msg in messages:
        if msg.get("role") != "user":
            continue
        content = msg.get("content")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
    return "\n".join(parts)


def _default_reg_ctx() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


class _MessagesProxy:
    """Wrapper around `client.messages` that intercepts create/stream."""

    def __init__(self, parent: "LedgerProofAnthropic"):
        self._parent = parent
        self._inner = parent._inner.messages

    def __getattr__(self, name: str) -> Any:
        # Anything not explicitly overridden falls through to the upstream SDK.
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # Non-streaming
    # ------------------------------------------------------------------
    def create(self, *args: Any, **kwargs: Any) -> Any:
        response = self._inner.create(*args, **kwargs)
        try:
            self._parent._emit_for_response(
                response=response,
                user_message_text=_extract_user_message_text(kwargs.get("messages")),
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            # C7: never break the calling code path.
            logger.warning("LedgerProof receipt emission failed: %s", exc)
        return response

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------
    @contextmanager
    def stream(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        hasher = IncrementalTextHasher()
        user_text = _extract_user_message_text(kwargs.get("messages"))

        with self._inner.stream(*args, **kwargs) as inner_stream:
            wrapped = _StreamWrapper(inner_stream, hasher)
            try:
                yield wrapped
            finally:
                try:
                    final_message = wrapped.get_final_message_safe()
                    self._parent._emit_for_stream(
                        final_message=final_message,
                        user_message_text=user_text,
                        text_hasher=hasher,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("LedgerProof streaming receipt failed: %s", exc)


class _StreamWrapper:
    """
    Proxy that forwards attribute access to the upstream Anthropic MessageStream,
    while tapping `text_stream` to update an incremental SHA-256 (constraint C6).
    """

    def __init__(self, inner: Any, hasher: IncrementalTextHasher):
        self._inner = inner
        self._hasher = hasher

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    @property
    def text_stream(self) -> Iterator[str]:
        for delta in self._inner.text_stream:
            self._hasher.update(delta)
            yield delta

    def get_final_message_safe(self) -> Any:
        # Anthropic SDK exposes get_final_message(); if the user already consumed
        # it, calling again may raise. Guard defensively.
        try:
            return self._inner.get_final_message()
        except Exception:
            return None


class LedgerProofAnthropic:
    """
    Drop-in wrapper for `anthropic.Anthropic`.

    Usage:
        client = LedgerProofAnthropic(deployer_id="acme-eu")
        response = client.messages.create(model="claude-opus-4-1", ...)

    All other attributes/methods of the underlying client are forwarded.
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        client: Anthropic | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
        schema: SchemaName = "chatbot_session/v1",
        **anthropic_kwargs: Any,
    ):
        self.deployer_id = deployer_id
        self._inner: Anthropic = client or Anthropic(**anthropic_kwargs)
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------
    @property
    def messages(self) -> _MessagesProxy:
        return _MessagesProxy(self)

    def __getattr__(self, name: str) -> Any:
        # Forward any unknown attribute to the underlying Anthropic client so that
        # advanced features (e.g. files, beta endpoints) keep working unmodified.
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # Internal: receipt construction
    # ------------------------------------------------------------------
    def _emit_for_response(
        self,
        response: Any,
        user_message_text: str,
        streaming: bool,
    ) -> None:
        content_refs: list[ContentRef] = []
        if user_message_text:
            content_refs.append(
                ContentRef(
                    sha256_hex=hash_text(user_message_text).hex(),
                    byte_length=len(user_message_text.encode("utf-8")),
                    role="user",
                )
            )
        assistant_text = _extract_assistant_text(response) or ""
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(assistant_text).hex(),
                byte_length=len(assistant_text.encode("utf-8")),
                role="assistant",
            )
        )
        tool_uses = extract_tool_uses(response)
        schema = "agent_action/v1" if tool_uses else self._schema
        self._build_and_emit(
            response=response,
            content_refs=content_refs,
            tool_uses=tool_uses,
            streaming=streaming,
            schema_override=schema,
        )

    def _emit_for_stream(
        self,
        final_message: Any,
        user_message_text: str,
        text_hasher: IncrementalTextHasher,
    ) -> None:
        content_refs: list[ContentRef] = []
        if user_message_text:
            content_refs.append(
                ContentRef(
                    sha256_hex=hash_text(user_message_text).hex(),
                    byte_length=len(user_message_text.encode("utf-8")),
                    role="user",
                )
            )
        content_refs.append(
            ContentRef(
                sha256_hex=text_hasher.digest().hex(),
                byte_length=text_hasher.byte_count,
                role="assistant",
            )
        )
        tool_uses = extract_tool_uses(final_message) if final_message is not None else []
        schema = "agent_action/v1" if tool_uses else self._schema
        self._build_and_emit(
            response=final_message,
            content_refs=content_refs,
            tool_uses=tool_uses,
            streaming=True,
            schema_override=schema,
        )

    def _build_and_emit(
        self,
        response: Any,
        content_refs: list[ContentRef],
        tool_uses: list,
        streaming: bool,
        schema_override: SchemaName,
    ) -> None:
        import base64
        import uuid

        from .canonical import canonical_encode

        model_ref = _build_model_ref(response) if response is not None else _unknown_model_ref()

        receipt = ReceiptV1(
            schema=schema_override,
            receipt_id=str(uuid.uuid4()),
            deployer_id=self.deployer_id,
            model=model_ref,
            content_refs=content_refs,
            regulatory_context=self._reg_ctx,
            tool_uses=tool_uses,
            streaming=streaming,
            adapter_version=__version__,
        )
        payload = receipt.to_payload()
        canonical_bytes = canonical_encode(payload)
        signature = self._signer.sign(canonical_bytes)
        signed = {
            "receipt": payload,
            "signature_alg": "ed25519",
            "signature_b64": base64.b64encode(signature).decode("ascii"),
            "signer_key_id": self._signer.key_id,
            "canonical_encoding": "cbor-rfc8949-deterministic",
        }
        self._emitter.emit(signed)


def _unknown_model_ref():
    from .schema import ModelRef

    return ModelRef(model_id="unknown", response_id="unknown")
