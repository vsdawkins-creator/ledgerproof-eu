"""
Synchronous client wrapper around `together.Together`.

Intercepts `client.chat.completions.create(...)` (streaming and non-streaming)
and `client.images.generate(...)` to emit a receipt on the side channel
(constraint C7) after the response is materialised. The wrapped response is
returned unchanged.

Together SDK reference (together>=1.3) — OpenAI-compatible shape:

    from together import Together
    client = Together(api_key=...)
    resp  = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        messages=[...],
    )
    for chunk in client.chat.completions.create(..., stream=True):
        ...

Together also exposes:
    client.images.generate(model="black-forest-labs/FLUX.1-schnell-Free", prompt=...)
"""

from __future__ import annotations

import logging
from typing import Any, Iterable, Iterator

from .canonical import IncrementalTextHasher, hash_text
from .emitter import Emitter, LogEmitter
from .manual import _build_model_ref, _extract_assistant_text, extract_tool_uses
from .schema import (
    ContentRef,
    OpenModelAttribution,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
    infer_open_model_attribution,
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
    Extract incremental text delta from a Together streaming chunk.

    OpenAI-compatible shape (Together returns the same):
        chunk.choices[0].delta.content -> str | None
    """
    choices = getattr(chunk, "choices", None)
    if not choices and isinstance(chunk, dict):
        choices = chunk.get("choices")
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
    Wraps Together's streaming iterator. For each yielded chunk we update an
    incremental SHA-256 (C6) over the assistant text delta. After the iterator
    is exhausted (or closed), we emit a single receipt with the final hash.
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


class _CompletionsProxy:
    """Wraps `client.chat.completions` and intercepts `create(...)`."""

    def __init__(self, parent: "LedgerProofTogether", inner: Any):
        self._parent = parent
        self._inner = inner

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def create(self, *args: Any, **kwargs: Any) -> Any:
        stream = bool(kwargs.get("stream"))
        if stream:
            return self._create_stream(*args, **kwargs)
        return self._create_blocking(*args, **kwargs)

    def _create_blocking(self, *args: Any, **kwargs: Any) -> Any:
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

    def _create_stream(self, *args: Any, **kwargs: Any) -> Iterator[Any]:
        hasher = IncrementalTextHasher()
        user_text = _extract_user_message_text(kwargs.get("messages"))

        inner_iter = self._inner.create(*args, **kwargs)

        def _on_finish(last_chunk: Any, h: IncrementalTextHasher) -> None:
            self._parent._emit_for_stream(
                final_chunk=last_chunk,
                user_message_text=user_text,
                text_hasher=h,
            )

        return _StreamIterator(inner_iter, _on_finish, hasher)


class _ChatProxy:
    """Wraps `client.chat` and exposes `.completions` as our proxy."""

    def __init__(self, parent: "LedgerProofTogether"):
        self._parent = parent
        self._inner = parent._inner.chat

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    @property
    def completions(self) -> _CompletionsProxy:
        return _CompletionsProxy(self._parent, self._inner.completions)


class _ImagesProxy:
    """Wraps `client.images` and intercepts `.generate(...)`."""

    def __init__(self, parent: "LedgerProofTogether"):
        self._parent = parent
        self._inner = parent._inner.images

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def generate(self, *args: Any, **kwargs: Any) -> Any:
        response = self._inner.generate(*args, **kwargs)
        try:
            self._parent._emit_for_image(
                response=response,
                prompt_text=str(kwargs.get("prompt", "")),
                model_hint=str(kwargs.get("model", "")),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof image-receipt emission failed: %s", exc)
        return response


class LedgerProofTogether:
    """
    Drop-in wrapper for `together.Together`.

    Usage:
        from together_ledgerproof import LedgerProofTogether

        client = LedgerProofTogether(deployer_id="acme-eu", api_key="...")
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": "Hi"}],
        )
        print(response.choices[0].message.content)

    All other attributes/methods of the underlying Together client are forwarded.
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
        open_model: OpenModelAttribution | dict[str, Any] | None = None,
        user_session_id: str | None = None,
        **together_kwargs: Any,
    ):
        self.deployer_id = deployer_id
        self.user_session_id = user_session_id
        if client is None:
            from together import Together  # lazy import — keeps test mocking simple
            client = Together(**together_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()
        if isinstance(open_model, dict):
            open_model = OpenModelAttribution(**open_model)
        self._open_model: OpenModelAttribution | None = open_model

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------
    @property
    def chat(self) -> _ChatProxy:
        return _ChatProxy(self)

    @property
    def images(self) -> _ImagesProxy:
        return _ImagesProxy(self)

    def __getattr__(self, name: str) -> Any:
        # Forward any unknown attribute (embeddings, audio, files, fine-tuning,
        # rerank, ...) to the underlying Together client.
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # Internal: receipt construction
    # ------------------------------------------------------------------
    def _resolve_open_model(self, model_id: str) -> OpenModelAttribution | None:
        if self._open_model is not None:
            return self._open_model
        # For schemas that explicitly carry upstream-model attribution, attempt
        # a best-effort inference from the model_id. Deployers can always
        # override with explicit OpenModelAttribution.
        if self._schema in ("open_model_inference/v1", "image_generation/v1"):
            return infer_open_model_attribution(model_id)
        return None

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
        self._build_and_emit(
            response=final_chunk,
            content_refs=content_refs,
            tool_uses=[],
            streaming=True,
        )

    def _emit_for_image(
        self,
        response: Any,
        prompt_text: str,
        model_hint: str,
    ) -> None:
        """Emit an image_generation/v1 receipt for client.images.generate calls."""
        import hashlib

        content_refs: list[ContentRef] = [
            ContentRef(
                sha256_hex=hash_text(prompt_text).hex(),
                byte_length=len(prompt_text.encode("utf-8")),
                role="user",
            )
        ]
        # Together image response shape: response.data -> list of image entries
        # (each with `url`, `b64_json`, etc.). We can hash whatever bytes are
        # already inline; URLs are referenced by URL hash as a best-effort.
        data = getattr(response, "data", None)
        if data is None and isinstance(response, dict):
            data = response.get("data")
        if data:
            for item in data:
                b64 = getattr(item, "b64_json", None)
                url = getattr(item, "url", None)
                if b64 is None and isinstance(item, dict):
                    b64 = item.get("b64_json")
                    url = item.get("url")
                if isinstance(b64, str) and b64:
                    import base64 as _b64
                    try:
                        blob = _b64.b64decode(b64)
                        content_refs.append(
                            ContentRef(
                                sha256_hex=hashlib.sha256(blob).hexdigest(),
                                byte_length=len(blob),
                                role="image",
                            )
                        )
                        continue
                    except Exception:  # noqa: BLE001
                        pass
                if isinstance(url, str) and url:
                    # URL-hash fallback when bytes aren't inline.
                    content_refs.append(
                        ContentRef(
                            sha256_hex=hashlib.sha256(url.encode("utf-8")).hexdigest(),
                            byte_length=len(url.encode("utf-8")),
                            role="image",
                        )
                    )

        # Force image_generation/v1 schema for this code path, but keep deployer
        # attribution if they supplied one.
        prior_schema = self._schema
        try:
            self._schema = "image_generation/v1"  # type: ignore[assignment]
            self._build_and_emit(
                response=response,
                content_refs=content_refs,
                tool_uses=[],
                streaming=False,
                model_id_hint=model_hint,
            )
        finally:
            self._schema = prior_schema

    def _build_and_emit(
        self,
        response: Any,
        content_refs: list[ContentRef],
        tool_uses: list,
        streaming: bool,
        model_id_hint: str | None = None,
    ) -> None:
        import base64
        import uuid

        from .canonical import canonical_encode

        model_ref = _build_model_ref(response)
        if model_ref.model_id == "unknown" and model_id_hint:
            # For image responses, the SDK sometimes omits model on the response.
            model_ref = model_ref.model_copy(update={"model_id": model_id_hint or "unknown"})

        open_model = self._resolve_open_model(model_ref.model_id)

        receipt = ReceiptV1(
            schema=self._schema,
            receipt_id=str(uuid.uuid4()),
            deployer_id=self.deployer_id,
            user_session_id=self.user_session_id,
            model=model_ref,
            content_refs=content_refs,
            regulatory_context=self._reg_ctx,
            open_model=open_model,
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
