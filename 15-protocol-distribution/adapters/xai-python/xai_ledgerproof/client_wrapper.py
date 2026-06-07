"""Sync client wrapper for xAI Grok via the OpenAI-compatible API.

`LedgerProofXAI` wraps `openai.OpenAI` (configured with xAI's `base_url`) and
intercepts `chat.completions.create()` calls. For non-streaming requests, the
receipt is emitted once the full response is in hand. For streaming requests,
we wrap the returned iterator with a stream-aware SHA-256 (constraint **C6**)
and emit the receipt when the stream is fully drained.

Constraint **C7**: the xAI response object is returned unmodified.

xAI Grok exposes an OpenAI-compatible REST surface at `https://api.x.ai/v1`.
This wrapper defaults to that base URL but accepts any standard `openai`
client kwargs (including `base_url` overrides for proxy / gateway setups).
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from typing import Any, Iterator

from openai import OpenAI

from .canonical import canonical_encode
from .emitter import Emitter, LogEmitter
from .schema import build_receipt
from .signer import Ed25519Signer, Signer
from .version import __version__

XAI_DEFAULT_BASE_URL = "https://api.x.ai/v1"


def _hash_messages(messages: list[dict[str, Any]] | None) -> str:
    if not messages:
        return hashlib.sha256(b"").hexdigest()
    payload = json.dumps(messages, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hash_non_streaming_response(response: Any) -> str:
    parts: list[str] = []
    for choice in getattr(response, "choices", None) or []:
        msg = getattr(choice, "message", None)
        if msg and getattr(msg, "content", None):
            parts.append(msg.content)
    return hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()


def _extract_chunk_text(chunk: Any) -> str:
    """Pull incremental assistant text out of a ChatCompletionChunk."""
    text = ""
    for choice in getattr(chunk, "choices", None) or []:
        delta = getattr(choice, "delta", None)
        if delta is None:
            continue
        content = getattr(delta, "content", None)
        if content:
            text += content
    return text


def _messages_contain_images(messages: list[dict[str, Any]] | None) -> tuple[bool, int]:
    """Detect OpenAI-style vision content blocks (image_url) in messages.

    Returns (has_image, count). Grok-2-vision uses the same multimodal content
    structure as gpt-4o-vision.
    """
    if not messages:
        return False, 0
    count = 0
    for m in messages:
        content = m.get("content") if isinstance(m, dict) else None
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "image_url":
                    count += 1
    return count > 0, count


class _SignedReceiptBuilder:
    """Shared receipt-building helper used by sync + async wrappers."""

    def __init__(
        self,
        *,
        deployer_id: str,
        regulatory_context: dict[str, Any],
        signer: Signer,
        emitter: Emitter,
    ) -> None:
        self.deployer_id = deployer_id
        self.regulatory_context = regulatory_context
        self.signer = signer
        self.emitter = emitter

    def emit(
        self,
        *,
        model_id: str,
        interaction_id: str,
        prompt_sha256: str,
        response_sha256: str,
        extra: dict[str, Any] | None = None,
        extra_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        schema_id = self.regulatory_context.get("schema", "chatbot_session/v1")
        kwargs: dict[str, Any] = dict(
            deployer_id=self.deployer_id,
            model_id=model_id,
            interaction_id=interaction_id,
            prompt_sha256=prompt_sha256,
            response_sha256=response_sha256,
            user_pseudonym=self.regulatory_context.get("user_pseudonym"),
            jurisdiction=self.regulatory_context.get("jurisdiction", "EU"),
            extra=extra or {},
        )
        if extra_fields:
            kwargs.update(extra_fields)
        receipt = build_receipt(schema_id, **kwargs)
        receipt_dict = receipt.model_dump()
        signature = self.signer.sign(canonical_encode(receipt_dict))
        envelope = {
            "receipt": receipt_dict,
            "signature": signature.hex(),
            "signature_alg": "ed25519",
            "public_key": self.signer.public_key_bytes().hex(),
            "adapter": {"name": "ledgerproof-xai", "version": __version__},
        }
        self.emitter.emit(envelope)
        return envelope


class _StreamingProxy:
    """Wraps a streaming response iterator and emits a receipt on drain."""

    def __init__(
        self,
        stream: Iterator[Any],
        *,
        builder: _SignedReceiptBuilder,
        prompt_sha256: str,
        fallback_interaction_id: str,
    ) -> None:
        self._stream = stream
        self._builder = builder
        self._prompt_sha256 = prompt_sha256
        self._fallback_interaction_id = fallback_interaction_id
        self._hasher = hashlib.sha256()
        self._model_id = "unknown"
        self._interaction_id: str | None = None
        self._emitted = False

    def __iter__(self) -> "_StreamingProxy":
        return self

    def __next__(self) -> Any:
        try:
            chunk = next(self._stream)
        except StopIteration:
            self._flush()
            raise
        self._absorb(chunk)
        return chunk

    def __enter__(self) -> "_StreamingProxy":
        return self

    def __exit__(self, *exc: Any) -> None:
        self._flush()
        close = getattr(self._stream, "close", None)
        if callable(close):
            close()

    def _absorb(self, chunk: Any) -> None:
        if self._interaction_id is None:
            self._interaction_id = getattr(chunk, "id", None)
        model = getattr(chunk, "model", None)
        if model:
            self._model_id = model
        text = _extract_chunk_text(chunk)
        if text:
            self._hasher.update(text.encode("utf-8"))

    def _flush(self) -> None:
        if self._emitted:
            return
        self._emitted = True
        self._builder.emit(
            model_id=self._model_id,
            interaction_id=self._interaction_id or self._fallback_interaction_id,
            prompt_sha256=self._prompt_sha256,
            response_sha256=self._hasher.hexdigest(),
            extra={"streaming": True, "provider": "xai"},
        )


class _ChatCompletionsProxy:
    """Intercepts `client.chat.completions.create(...)`."""

    def __init__(self, inner: Any, builder: _SignedReceiptBuilder) -> None:
        self._inner = inner
        self._builder = builder

    def create(self, *args: Any, **kwargs: Any) -> Any:
        messages = kwargs.get("messages")
        prompt_sha256 = _hash_messages(messages)
        streaming = bool(kwargs.get("stream"))
        result = self._inner.create(*args, **kwargs)

        if streaming:
            return _StreamingProxy(
                result,
                builder=self._builder,
                prompt_sha256=prompt_sha256,
                fallback_interaction_id=str(uuid.uuid4()),
            )

        schema = self._builder.regulatory_context.get("schema", "chatbot_session/v1")
        extra_fields: dict[str, Any] = {}
        extra: dict[str, Any] = {"provider": "xai"}

        if schema == "vision_inference/v1":
            has_image, image_count = _messages_contain_images(messages)
            extra_fields["image_count"] = image_count
            extra_fields["content_modality"] = "image" if has_image else "text"
            # If deployer pre-computed the image hash, surface it from context
            img_hash = self._builder.regulatory_context.get("image_input_sha256")
            if img_hash:
                extra_fields["image_input_sha256"] = img_hash

        if schema == "realtime_data_inference/v1":
            extra_fields["realtime_data_used"] = bool(
                self._builder.regulatory_context.get("realtime_data_used", False)
            )
            extra_fields["public_interest_text"] = bool(
                self._builder.regulatory_context.get("public_interest_text", False)
            )
            rt_hash = self._builder.regulatory_context.get("realtime_sources_sha256")
            if rt_hash:
                extra_fields["realtime_sources_sha256"] = rt_hash

        self._builder.emit(
            model_id=getattr(result, "model", "unknown"),
            interaction_id=getattr(result, "id", None) or str(uuid.uuid4()),
            prompt_sha256=prompt_sha256,
            response_sha256=_hash_non_streaming_response(result),
            extra=extra,
            extra_fields=extra_fields or None,
        )
        return result

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class _ChatProxy:
    def __init__(self, inner: Any, builder: _SignedReceiptBuilder) -> None:
        self._inner = inner
        self._builder = builder
        self.completions = _ChatCompletionsProxy(inner.completions, builder)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class LedgerProofXAI:
    """Wraps `openai.OpenAI` configured for xAI Grok. Same call surface;
    emits receipts on the side.

    Parameters
    ----------
    deployer_id:
        URN identifying the deployer organisation, e.g. `urn:eu:deployer:acme`.
    regulatory_context:
        Optional dict carrying `schema`, `jurisdiction`, `user_pseudonym`, and
        Grok-specific fields like `realtime_data_used`, `public_interest_text`,
        `realtime_sources_sha256`, `image_input_sha256`.
    signer:
        Optional `Signer`. Defaults to an ephemeral `Ed25519Signer` (MVP only).
    emitter:
        Optional `Emitter`. Defaults to `LogEmitter()` (stdout).
    openai_client:
        Optional pre-built `openai.OpenAI` instance (already pointed at xAI).
        If omitted, one is built with `api_key=os.environ["XAI_API_KEY"]` and
        `base_url="https://api.x.ai/v1"`. Pass any extra `openai_kwargs` to
        override.
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        regulatory_context: dict[str, Any] | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        openai_client: OpenAI | None = None,
        **openai_kwargs: Any,
    ) -> None:
        if openai_client is None:
            openai_kwargs.setdefault("base_url", XAI_DEFAULT_BASE_URL)
            if "api_key" not in openai_kwargs:
                env_key = os.environ.get("XAI_API_KEY")
                if env_key:
                    openai_kwargs["api_key"] = env_key
            openai_client = OpenAI(**openai_kwargs)
        self._client = openai_client
        self._builder = _SignedReceiptBuilder(
            deployer_id=deployer_id,
            regulatory_context=regulatory_context or {},
            signer=signer or Ed25519Signer(),
            emitter=emitter or LogEmitter(),
        )
        self.chat = _ChatProxy(self._client.chat, self._builder)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
