"""
Synchronous client wrapper around `mistralai.Mistral` pointed at the Codestral
endpoint (`https://codestral.mistral.ai`).

Intercepts:
  - `client.chat.complete(...)`   — code-chat style
  - `client.chat.stream(...)`     — streaming chat
  - `client.fim.complete(...)`    — fill-in-the-middle (the dominant Codestral pattern)
  - `client.fim.stream(...)`      — streaming FIM

Emits a side-channel receipt (constraint C7) after the response is materialised.
The wrapped response object is returned unchanged.

Mistral SDK reference (mistralai>=1.0, Codestral endpoint):
    from mistralai import Mistral
    client = Mistral(
        api_key=os.environ["MISTRAL_CODESTRAL_API_KEY"],
        server_url="https://codestral.mistral.ai",
    )
    chat = client.chat.complete(model="codestral-latest", messages=[...])
    fim  = client.fim.complete(model="codestral-latest", prompt="def fib(", suffix=":\\n    return")
"""

from __future__ import annotations

import logging
import os
from typing import Any, Iterable, Iterator

from .canonical import IncrementalTextHasher, hash_text
from .emitter import Emitter, LogEmitter
from .manual import _build_model_ref, _extract_assistant_text, extract_tool_uses
from .schema import (
    ContentRef,
    FimPositions,
    GeneratedCodeAttributes,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
)
from .signer import Ed25519Signer, Signer
from .version import __version__

logger = logging.getLogger(__name__)

DEFAULT_CODESTRAL_URL = "https://codestral.mistral.ai"


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


def _default_reg_ctx_chat() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def _default_reg_ctx_generated_code() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="2",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def _stream_chunk_text(chunk: Any) -> str:
    """
    Extract the incremental text delta from a Codestral stream chunk.

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
    Wraps Codestral's streaming iterator. For each yielded chunk we update an
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
            logger.warning("LedgerProof Codestral streaming receipt failed: %s", exc)

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

    def __init__(self, parent: "LedgerProofCodestral"):
        self._parent = parent
        self._inner = parent._inner.chat

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def complete(self, *args: Any, **kwargs: Any) -> Any:
        response = self._inner.complete(*args, **kwargs)
        try:
            self._parent._emit_for_chat_response(
                response=response,
                user_message_text=_extract_user_message_text(kwargs.get("messages")),
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof Codestral receipt emission failed: %s", exc)
        return response

    def stream(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        hasher = IncrementalTextHasher()
        user_text = _extract_user_message_text(kwargs.get("messages"))
        inner_iter = self._inner.stream(*args, **kwargs)

        def _on_finish(last_chunk: Any, h: IncrementalTextHasher) -> None:
            self._parent._emit_for_chat_stream(
                final_chunk=last_chunk,
                user_message_text=user_text,
                text_hasher=h,
            )

        return _StreamIterator(inner_iter, _on_finish, hasher)


class _FimProxy:
    """Wrapper around `client.fim` that intercepts fill-in-the-middle complete/stream."""

    def __init__(self, parent: "LedgerProofCodestral"):
        self._parent = parent
        self._inner = parent._inner.fim

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def complete(self, *args: Any, **kwargs: Any) -> Any:
        response = self._inner.complete(*args, **kwargs)
        try:
            self._parent._emit_for_fim_response(
                response=response,
                prompt=kwargs.get("prompt", "") or "",
                suffix=kwargs.get("suffix", "") or "",
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof Codestral FIM receipt emission failed: %s", exc)
        return response

    def stream(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        hasher = IncrementalTextHasher()
        prompt = kwargs.get("prompt", "") or ""
        suffix = kwargs.get("suffix", "") or ""
        inner_iter = self._inner.stream(*args, **kwargs)

        def _on_finish(last_chunk: Any, h: IncrementalTextHasher) -> None:
            self._parent._emit_for_fim_stream(
                final_chunk=last_chunk,
                prompt=prompt,
                suffix=suffix,
                text_hasher=h,
            )

        return _StreamIterator(inner_iter, _on_finish, hasher)


class LedgerProofCodestral:
    """
    Drop-in wrapper for `mistralai.Mistral` configured against the Codestral endpoint.

    Usage:
        from ledgerproof_mistral_codestral import LedgerProofCodestral

        client = LedgerProofCodestral(
            deployer_id="acme-eu",
            api_key="...",  # or MISTRAL_CODESTRAL_API_KEY env var
        )
        response = client.chat.complete(
            model="codestral-latest",
            messages=[{"role": "user", "content": "Write a Python fib()."}],
        )
        fim = client.fim.complete(
            model="codestral-latest",
            prompt="def fib(n):\\n    ",
            suffix="\\n    return result",
        )

    Defaults to schema='generated_code/v1' for chat, 'fim_completion/v1' for FIM,
    'chatbot_session/v1' when explicit chat_schema='chatbot_session/v1' is set.

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
        chat_schema: SchemaName = "generated_code/v1",
        fim_schema: SchemaName = "fim_completion/v1",
        language: str = "unknown",
        user_session_id: str | None = None,
        api_key: str | None = None,
        server_url: str = DEFAULT_CODESTRAL_URL,
        **mistral_kwargs: Any,
    ):
        self.deployer_id = deployer_id
        self.user_session_id = user_session_id
        self._language = (language or "unknown").lower()
        if client is None:
            from mistralai import Mistral  # lazy import — keeps test mocking simple
            api_key = api_key or os.environ.get("MISTRAL_CODESTRAL_API_KEY")
            client = Mistral(api_key=api_key, server_url=server_url, **mistral_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._chat_schema: SchemaName = chat_schema
        self._fim_schema: SchemaName = fim_schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        # If a single reg_ctx is provided, use it for both. Otherwise we pick the
        # schema-appropriate default at emit time.
        self._reg_ctx_override: RegulatoryContext | None = regulatory_context

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------
    @property
    def chat(self) -> _ChatProxy:
        return _ChatProxy(self)

    @property
    def fim(self) -> _FimProxy:
        return _FimProxy(self)

    def __getattr__(self, name: str) -> Any:
        # Forward any unknown attribute to the underlying Mistral client.
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # Internal: chat receipt construction
    # ------------------------------------------------------------------
    def _reg_ctx_for(self, schema: SchemaName) -> RegulatoryContext:
        if self._reg_ctx_override is not None:
            return self._reg_ctx_override
        if schema == "chatbot_session/v1":
            return _default_reg_ctx_chat()
        return _default_reg_ctx_generated_code()

    def _emit_for_chat_response(
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
        code_attrs = self._build_code_attributes(
            assistant_text=assistant_text, line_count=assistant_text.count("\n")
        )
        self._build_and_emit(
            response=response,
            schema=self._chat_schema,
            content_refs=content_refs,
            tool_uses=tool_uses,
            streaming=streaming,
            code_attributes=code_attrs,
            fim_positions=None,
        )

    def _emit_for_chat_stream(
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
        pseudo_response = final_chunk
        if pseudo_response is not None:
            data = getattr(pseudo_response, "data", None)
            if data is not None:
                pseudo_response = data
        code_attrs = self._build_code_attributes(
            assistant_text=None, line_count=text_hasher.line_count
        )
        self._build_and_emit(
            response=pseudo_response,
            schema=self._chat_schema,
            content_refs=content_refs,
            tool_uses=[],
            streaming=True,
            code_attributes=code_attrs,
            fim_positions=None,
        )

    # ------------------------------------------------------------------
    # Internal: FIM receipt construction
    # ------------------------------------------------------------------
    def _emit_for_fim_response(
        self,
        response: Any,
        prompt: str,
        suffix: str,
        streaming: bool,
    ) -> None:
        prefix_bytes = prompt.encode("utf-8")
        suffix_bytes = suffix.encode("utf-8")
        middle_text = _extract_assistant_text(response) or ""
        middle_bytes = middle_text.encode("utf-8")

        content_refs: list[ContentRef] = [
            ContentRef(
                sha256_hex=hash_text(prompt).hex(),
                byte_length=len(prefix_bytes),
                role="prefix",
            ),
            ContentRef(
                sha256_hex=hash_text(suffix).hex(),
                byte_length=len(suffix_bytes),
                role="suffix",
            ),
            ContentRef(
                sha256_hex=hash_text(middle_text).hex(),
                byte_length=len(middle_bytes),
                role="middle",
            ),
        ]
        fim_positions = FimPositions(
            prefix_byte_length=len(prefix_bytes),
            suffix_byte_length=len(suffix_bytes),
            middle_byte_length=len(middle_bytes),
        )
        code_attrs = self._build_code_attributes(
            assistant_text=middle_text, line_count=middle_text.count("\n")
        )
        self._build_and_emit(
            response=response,
            schema=self._fim_schema,
            content_refs=content_refs,
            tool_uses=[],
            streaming=streaming,
            code_attributes=code_attrs,
            fim_positions=fim_positions,
        )

    def _emit_for_fim_stream(
        self,
        final_chunk: Any,
        prompt: str,
        suffix: str,
        text_hasher: IncrementalTextHasher,
    ) -> None:
        prefix_bytes = prompt.encode("utf-8")
        suffix_bytes = suffix.encode("utf-8")
        content_refs: list[ContentRef] = [
            ContentRef(
                sha256_hex=hash_text(prompt).hex(),
                byte_length=len(prefix_bytes),
                role="prefix",
            ),
            ContentRef(
                sha256_hex=hash_text(suffix).hex(),
                byte_length=len(suffix_bytes),
                role="suffix",
            ),
            ContentRef(
                sha256_hex=text_hasher.digest().hex(),
                byte_length=text_hasher.byte_count,
                role="middle",
            ),
        ]
        fim_positions = FimPositions(
            prefix_byte_length=len(prefix_bytes),
            suffix_byte_length=len(suffix_bytes),
            middle_byte_length=text_hasher.byte_count,
        )
        pseudo_response = final_chunk
        if pseudo_response is not None:
            data = getattr(pseudo_response, "data", None)
            if data is not None:
                pseudo_response = data
        code_attrs = self._build_code_attributes(
            assistant_text=None, line_count=text_hasher.line_count
        )
        self._build_and_emit(
            response=pseudo_response,
            schema=self._fim_schema,
            content_refs=content_refs,
            tool_uses=[],
            streaming=True,
            code_attributes=code_attrs,
            fim_positions=fim_positions,
        )

    # ------------------------------------------------------------------
    # Shared
    # ------------------------------------------------------------------
    def _build_code_attributes(
        self,
        *,
        assistant_text: str | None,
        line_count: int,
    ) -> GeneratedCodeAttributes | None:
        # We only attach code_attributes for code-flavoured schemas.
        if self._chat_schema == "chatbot_session/v1" and assistant_text is None and line_count == 0:
            return None
        return GeneratedCodeAttributes(
            language=self._language,
            line_count=line_count,
            has_security_pattern=False,  # adapter is content-blind; deployer overrides via manual emit
        )

    def _build_and_emit(
        self,
        response: Any,
        schema: SchemaName,
        content_refs: list[ContentRef],
        tool_uses: list,
        streaming: bool,
        code_attributes: GeneratedCodeAttributes | None,
        fim_positions: FimPositions | None,
    ) -> None:
        import base64
        import uuid

        from .canonical import canonical_encode

        model_ref = _build_model_ref(response)

        receipt = ReceiptV1(
            schema=schema,
            receipt_id=str(uuid.uuid4()),
            deployer_id=self.deployer_id,
            user_session_id=self.user_session_id,
            model=model_ref,
            content_refs=content_refs,
            regulatory_context=self._reg_ctx_for(schema),
            code_attributes=code_attributes,
            fim_positions=fim_positions,
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
