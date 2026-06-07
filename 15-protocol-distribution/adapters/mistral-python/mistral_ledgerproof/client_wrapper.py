"""
Synchronous client wrapper around `mistralai.Mistral`.

Intercepts `client.chat.complete(...)` and `client.chat.stream(...)` to emit a
receipt on the side channel (constraint C7) after the response is materialised.
The wrapped response object is returned unchanged.

Mistral SDK reference (mistralai>=1.0):
    from mistralai import Mistral
    client = Mistral(api_key=...)
    resp  = client.chat.complete(model="mistral-large-latest", messages=[...])
    for chunk in client.chat.stream(...):   # iterator of ChatCompletionStreamResponse
        ...
"""

from __future__ import annotations

import logging
from typing import Any, Iterable, Iterator

from .canonical import IncrementalTextHasher, hash_text
from .emitter import Emitter, LogEmitter
from .manual import _build_model_ref, _extract_assistant_text, extract_tool_uses
from .schema import (
    ContentRef,
    EuSovereigntyAttestation,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
)
from .signer import Ed25519Signer, Signer
from .version import __version__

logger = logging.getLogger(__name__)


def _extract_user_message_text(messages: Iterable[Any] | None) -> str:
    """Best-effort concatenation of user-role text from a messages list."""
    if not messages:
        return ""
    parts: list[str] = []
    for msg in messages:
        role = getattr(msg, "role", None)
        content = getattr(msg, "content", None)
        if role is None and isinstance(msg, dict):
            role = msg.get("role")
            content = msg.get("content")
        if role != "user":
            continue
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                text = getattr(block, "text", None)
                if text is None and isinstance(block, dict):
                    text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
    return "\n".join(parts)


def _default_reg_ctx() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def _stream_chunk_text(chunk: Any) -> str:
    """
    Extract the incremental text delta from a Mistral stream chunk.

    Chunk shape (mistralai>=1.0):
        chunk.data.choices[0].delta.content  -> str | None
    Some versions expose `chunk.choices[0].delta.content` directly.
    """
    container = getattr(chunk, "data", chunk)
    choices = getattr(container, "choices", None)
    if not choices and isinstance(container, dict):
        choices = container.get("choices")
    if not choices:
        return ""
    first = choices[0]
    delta = getattr(first, "delta", None)
    if delta is None and isinstance(first, dict):
        delta = first.get("delta")
    if delta is None:
        return ""
    content = getattr(delta, "content", None)
    if content is None and isinstance(delta, dict):
        content = delta.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out: list[str] = []
        for block in content:
            text = getattr(block, "text", None)
            if text is None and isinstance(block, dict):
                text = block.get("text")
            if isinstance(text, str):
                out.append(text)
        return "".join(out)
    return ""


class _StreamIterator:
    """
    Wraps Mistral's streaming iterator. For each yielded chunk we update an
    incremental SHA-256 (C6) over the assistant text delta. After the iterator
    is exhausted, we emit a single receipt with the final hash.
    """

    def __init__(self, inner: Iterable[Any], on_finish, hasher: IncrementalTextHasher):
        self._inner = iter(inner)
        self._on_finish = on_finish
        self._hasher = hasher
        self._last_chunk: Any = None
        self._finished = False

    def __iter__(self) -> "_StreamIterator":
        return self

    def __next__(self) -> Any:
        try:
            chunk = next(self._inner)
        except StopIteration:
            self._finalize()
            raise
        text = _stream_chunk_text(chunk)
        if text:
            self._hasher.update(text)
        self._last_chunk = chunk
        return chunk

    def _finalize(self) -> None:
        if self._finished:
            return
        self._finished = True
        try:
            self._on_finish(self._last_chunk, self._hasher)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof streaming receipt failed: %s", exc)

    def close(self) -> None:
        # Belt-and-suspenders: if the caller breaks early, still emit a receipt.
        self._finalize()
        closer = getattr(self._inner, "close", None)
        if callable(closer):
            try:
                closer()
            except Exception:  # noqa: BLE001
                pass


class _ChatProxy:
    """Wrapper around `client.chat` that intercepts complete/stream."""

    def __init__(self, parent: "LedgerProofMistral"):
        self._parent = parent
        self._inner = parent._inner.chat

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # Non-streaming
    # ------------------------------------------------------------------
    def complete(self, *args: Any, **kwargs: Any) -> Any:
        response = self._inner.complete(*args, **kwargs)
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
    def stream(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        hasher = IncrementalTextHasher()
        user_text = _extract_user_message_text(kwargs.get("messages"))

        inner_iter = self._inner.stream(*args, **kwargs)

        def _on_finish(last_chunk: Any, h: IncrementalTextHasher) -> None:
            self._parent._emit_for_stream(
                final_chunk=last_chunk,
                user_message_text=user_text,
                text_hasher=h,
            )

        return _StreamIterator(inner_iter, _on_finish, hasher)


class LedgerProofMistral:
    """
    Drop-in wrapper for `mistralai.Mistral`.

    Usage:
        from mistralai import Mistral
        from mistral_ledgerproof import LedgerProofMistral

        client = LedgerProofMistral(deployer_id="acme-eu", api_key="...")
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": "Hi"}],
        )
        print(response.choices[0].message.content)

    All other attributes/methods of the underlying Mistral client are forwarded.
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        client: Any | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
        schema: SchemaName = "chatbot_session/v1",
        eu_sovereignty: EuSovereigntyAttestation | dict[str, Any] | None = None,
        user_session_id: str | None = None,
        **mistral_kwargs: Any,
    ):
        self.deployer_id = deployer_id
        self.user_session_id = user_session_id
        if client is None:
            from mistralai import Mistral  # lazy import — keeps test mocking simple
            client = Mistral(**mistral_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()
        if isinstance(eu_sovereignty, dict):
            eu_sovereignty = EuSovereigntyAttestation(**eu_sovereignty)
        self._eu_sov: EuSovereigntyAttestation | None = eu_sovereignty

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------
    @property
    def chat(self) -> _ChatProxy:
        return _ChatProxy(self)

    def __getattr__(self, name: str) -> Any:
        # Forward any unknown attribute (embeddings, ocr, agents, ...) to the
        # underlying Mistral client so advanced features keep working unmodified.
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
        self._build_and_emit(
            response=response,
            content_refs=content_refs,
            tool_uses=tool_uses,
            streaming=streaming,
        )

    def _emit_for_stream(
        self,
        final_chunk: Any,
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
        # The final chunk often carries the final id/model/usage info.
        # If it does, _build_model_ref will pick it up via duck typing.
        pseudo_response = final_chunk
        # Stream chunks sometimes wrap a `.data` field — unwrap once for model_ref.
        if pseudo_response is not None:
            data = getattr(pseudo_response, "data", None)
            if data is not None:
                pseudo_response = data
        self._build_and_emit(
            response=pseudo_response,
            content_refs=content_refs,
            tool_uses=[],
            streaming=True,
        )

    def _build_and_emit(
        self,
        response: Any,
        content_refs: list[ContentRef],
        tool_uses: list,
        streaming: bool,
    ) -> None:
        import base64
        import uuid

        from .canonical import canonical_encode

        model_ref = _build_model_ref(response)

        receipt = ReceiptV1(
            schema=self._schema,
            receipt_id=str(uuid.uuid4()),
            deployer_id=self.deployer_id,
            user_session_id=self.user_session_id,
            model=model_ref,
            content_refs=content_refs,
            regulatory_context=self._reg_ctx,
            eu_sovereignty=self._eu_sov,
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
