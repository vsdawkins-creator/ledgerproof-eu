"""
Synchronous client wrapper around DashScope's `Generation` interface.

Intercepts `Generation.call(...)` (both streaming=False and streaming=True) and
emits a receipt on the side channel (constraint C7) after the response is
materialised. The wrapped response is returned unchanged.

DashScope SDK reference (dashscope>=1.20):

    import dashscope
    from dashscope import Generation

    dashscope.api_key = "..."
    response = Generation.call(model="qwen-max", messages=[...])
    # response.output.text  or  response.output.choices[0].message.content

    # Streaming:
    for chunk in Generation.call(model="qwen-max", messages=[...], stream=True):
        ...

DashScope streaming nuance:
    By default DashScope streams CUMULATIVE text (each chunk repeats the full text
    so far). When the deployer passes `incremental_output=True` the chunks become
    pure deltas. The wrapper handles both shapes by tracking the longest-common-
    prefix against the previous chunk text and only feeding the delta bytes to
    the incremental SHA-256 (constraint C6).
"""

from __future__ import annotations

import logging
from typing import Any, Iterable, Iterator

from .canonical import IncrementalTextHasher, hash_text
from .emitter import Emitter, LogEmitter
from .manual import _build_model_ref, _extract_assistant_text, extract_tool_uses
from .schema import (
    ChineseInferenceAttestation,
    ContentRef,
    CrossJurisdictionalRoute,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
)
from .signer import Ed25519Signer, Signer
from .version import __version__

logger = logging.getLogger(__name__)


def _extract_user_message_text(messages: Iterable[Any] | None, prompt: str | None) -> str:
    """
    Best-effort extraction of user-role text.

    DashScope accepts EITHER:
      - messages=[{"role": "user", "content": "..."}, ...]
      - prompt="..."          (plain string)
    """
    if prompt and isinstance(prompt, str):
        return prompt
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
    Extract the cumulative-or-delta text from a DashScope stream chunk.

    Chunk shape (dashscope>=1.20):
        chunk.output.text                              -> str  (plain mode)
        chunk.output.choices[0].message.content        -> str  (chat mode)
    """
    output = getattr(chunk, "output", None)
    if output is None and isinstance(chunk, dict):
        output = chunk.get("output")
    if output is None:
        return ""

    text = getattr(output, "text", None)
    if text is None and isinstance(output, dict):
        text = output.get("text")
    if isinstance(text, str) and text:
        return text

    choices = getattr(output, "choices", None)
    if choices is None and isinstance(output, dict):
        choices = output.get("choices")
    if not choices:
        return ""
    first = choices[0]
    message = getattr(first, "message", None)
    if message is None and isinstance(first, dict):
        message = first.get("message")
    if message is None:
        return ""
    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            t = getattr(block, "text", None)
            if t is None and isinstance(block, dict):
                t = block.get("text")
            if isinstance(t, str):
                parts.append(t)
        return "".join(parts)
    return ""


class _StreamIterator:
    """
    Wraps DashScope's streaming iterator. Computes incremental SHA-256 (C6).

    Handles both cumulative-output and incremental-output stream modes by
    diffing against the previous chunk's text and only feeding new suffix
    bytes to the hasher.
    """

    def __init__(self, inner: Iterable[Any], on_finish, hasher: IncrementalTextHasher):
        self._inner = iter(inner)
        self._on_finish = on_finish
        self._hasher = hasher
        self._prev_cumulative = ""
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
        chunk_text = _stream_chunk_text(chunk)
        if chunk_text:
            # Cumulative mode: chunk text starts with the previous cumulative
            # text (with possibly equal length on a repeat-finish chunk). Pure
            # delta mode: it does not.
            if chunk_text == self._prev_cumulative:
                # Cumulative repeat (e.g. final finish-reason chunk). No new
                # content — skip.
                pass
            elif chunk_text.startswith(self._prev_cumulative):
                delta = chunk_text[len(self._prev_cumulative) :]
                self._hasher.update(delta)
                self._prev_cumulative = chunk_text
            elif self._prev_cumulative == "":
                self._hasher.update(chunk_text)
                self._prev_cumulative = chunk_text
            else:
                # Treat as delta (incremental_output=True path).
                self._hasher.update(chunk_text)
                self._prev_cumulative += chunk_text
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


class _GenerationProxy:
    """Wrapper around DashScope `Generation` that intercepts `call`."""

    def __init__(self, parent: "LedgerProofQwen", inner: Any):
        self._parent = parent
        self._inner = inner

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def call(self, *args: Any, **kwargs: Any) -> Any:
        # Pull the model id and message text BEFORE the call so we can record
        # it even when DashScope omits model from the response (it usually does).
        model_id: str | None = kwargs.get("model") or (args[0] if args else None)
        messages = kwargs.get("messages")
        prompt = kwargs.get("prompt")
        user_text = _extract_user_message_text(messages, prompt)
        streaming = bool(kwargs.get("stream"))

        result = self._inner.call(*args, **kwargs)

        if streaming:
            hasher = IncrementalTextHasher()

            def _on_finish(last_chunk: Any, h: IncrementalTextHasher) -> None:
                self._parent._emit_for_stream(
                    final_chunk=last_chunk,
                    user_message_text=user_text,
                    text_hasher=h,
                    model_id=model_id,
                )

            return _StreamIterator(result, _on_finish, hasher)

        try:
            self._parent._emit_for_response(
                response=result,
                user_message_text=user_text,
                streaming=False,
                model_id=model_id,
            )
        except Exception as exc:  # noqa: BLE001
            # C7: never break the calling code path.
            logger.warning("LedgerProof receipt emission failed: %s", exc)
        return result


class LedgerProofQwen:
    """
    Drop-in wrapper for `dashscope.Generation`.

    Usage:
        from qwen_ledgerproof import LedgerProofQwen

        client = LedgerProofQwen(deployer_id="acme-eu", api_key="...")
        response = client.generation.call(
            model="qwen-max",
            messages=[{"role": "user", "content": "Hi"}],
        )
        print(response.output.text)

    The DashScope `Generation` class is module-level (not an instance). The
    wrapper accepts an optional `generation` argument for dependency injection
    in tests; in production it imports the real `dashscope.Generation`.
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        generation: Any | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
        schema: SchemaName = "chatbot_session/v1",
        chinese_inference: ChineseInferenceAttestation | dict[str, Any] | None = None,
        cross_jurisdictional_route: CrossJurisdictionalRoute | dict[str, Any] | None = None,
        user_session_id: str | None = None,
    ):
        self.deployer_id = deployer_id
        self.user_session_id = user_session_id

        if generation is None:
            # Lazy import — keeps test mocking simple.
            import dashscope
            from dashscope import Generation as _Generation

            if api_key is not None:
                dashscope.api_key = api_key
            if base_url is not None:
                # Regional endpoint selection.
                dashscope.base_http_api_url = base_url
            generation = _Generation

        self._generation = generation
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()
        if isinstance(chinese_inference, dict):
            chinese_inference = ChineseInferenceAttestation(**chinese_inference)
        self._chinese: ChineseInferenceAttestation | None = chinese_inference
        if isinstance(cross_jurisdictional_route, dict):
            cross_jurisdictional_route = CrossJurisdictionalRoute(**cross_jurisdictional_route)
        self._cjr: CrossJurisdictionalRoute | None = cross_jurisdictional_route

    # ------------------------------------------------------------------
    # Public surface — namespaced under `.generation` to mirror dashscope.
    # ------------------------------------------------------------------
    @property
    def generation(self) -> _GenerationProxy:
        return _GenerationProxy(self, self._generation)

    # ------------------------------------------------------------------
    # Internal: receipt construction
    # ------------------------------------------------------------------
    def _emit_for_response(
        self,
        response: Any,
        user_message_text: str,
        streaming: bool,
        model_id: str | None,
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
            model_id=model_id,
        )

    def _emit_for_stream(
        self,
        final_chunk: Any,
        user_message_text: str,
        text_hasher: IncrementalTextHasher,
        model_id: str | None,
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
            model_id=model_id,
        )

    def _build_and_emit(
        self,
        response: Any,
        content_refs: list[ContentRef],
        tool_uses: list,
        streaming: bool,
        model_id: str | None,
    ) -> None:
        import base64
        import uuid

        from .canonical import canonical_encode

        model_ref = _build_model_ref(response, fallback_model_id=model_id)

        receipt = ReceiptV1(
            schema=self._schema,
            receipt_id=str(uuid.uuid4()),
            deployer_id=self.deployer_id,
            user_session_id=self.user_session_id,
            model=model_ref,
            content_refs=content_refs,
            regulatory_context=self._reg_ctx,
            chinese_inference=self._chinese,
            cross_jurisdictional_route=self._cjr,
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
