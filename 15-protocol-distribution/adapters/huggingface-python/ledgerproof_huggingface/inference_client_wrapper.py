"""Sync wrapper for `huggingface_hub.InferenceClient`.

`LedgerProofInferenceClient` wraps `InferenceClient` and intercepts
`chat_completion()` and `text_generation()` calls. For non-streaming requests,
the receipt is emitted once the full response is in hand. For streaming
requests, we wrap the returned iterator with a stream-aware SHA-256
(constraint **C6**) and emit the receipt when the stream is fully drained.

Constraint **C7**: the Hugging Face response object is returned unmodified.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any, Iterator


from .canonical import canonical_encode
from .emitter import Emitter, LogEmitter
from .schema import build_receipt
from .signer import Ed25519Signer, Signer
from .version import __version__


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------


def _hash_messages(messages: list[dict[str, Any]] | None) -> str:
    if not messages:
        return hashlib.sha256(b"").hexdigest()
    payload = json.dumps(messages, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hash_text_prompt(prompt: str | None) -> str:
    if prompt is None:
        return hashlib.sha256(b"").hexdigest()
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _extract_response_text(response: Any) -> str:
    """Pull assistant text out of a `ChatCompletionOutput`-like object."""
    # 1) duck-typed access (HF dataclass-like objects)
    parts: list[str] = []
    choices = getattr(response, "choices", None)
    if choices is None and isinstance(response, dict):
        choices = response.get("choices")
    if choices:
        for choice in choices:
            msg = getattr(choice, "message", None)
            if msg is None and isinstance(choice, dict):
                msg = choice.get("message")
            if msg is None:
                continue
            content = getattr(msg, "content", None)
            if content is None and isinstance(msg, dict):
                content = msg.get("content")
            if content:
                parts.append(content)
        return "".join(parts)
    # 2) text_generation returns a plain string
    if isinstance(response, str):
        return response
    # 3) text_generation can return an object with .generated_text
    gen = getattr(response, "generated_text", None)
    if gen:
        return gen
    return ""


def _hash_non_streaming_response(response: Any) -> str:
    return hashlib.sha256(_extract_response_text(response).encode("utf-8")).hexdigest()


def _extract_chunk_text(chunk: Any) -> str:
    """Pull incremental assistant text out of a chat-completion stream chunk
    (`ChatCompletionStreamOutput`) or a text-generation stream chunk
    (`TextGenerationStreamOutput`).
    """
    # chat_completion stream: choices[0].delta.content
    choices = getattr(chunk, "choices", None)
    if choices is None and isinstance(chunk, dict):
        choices = chunk.get("choices")
    if choices:
        text = ""
        for choice in choices:
            delta = getattr(choice, "delta", None)
            if delta is None and isinstance(choice, dict):
                delta = choice.get("delta")
            if delta is None:
                continue
            content = getattr(delta, "content", None)
            if content is None and isinstance(delta, dict):
                content = delta.get("content")
            if content:
                text += content
        return text
    # text_generation stream: token.text or .token.text or .generated_text
    token = getattr(chunk, "token", None)
    if token is not None:
        t_text = getattr(token, "text", None)
        if t_text is None and isinstance(token, dict):
            t_text = token.get("text")
        if t_text:
            return t_text
    if isinstance(chunk, str):
        return chunk
    return ""


def _extract_model_id(obj: Any, fallback: str) -> str:
    """Best-effort `model_id` extraction from a response or chunk."""
    model = getattr(obj, "model", None)
    if model is None and isinstance(obj, dict):
        model = obj.get("model")
    return model or fallback


def _extract_interaction_id(obj: Any) -> str | None:
    """Best-effort `id` extraction."""
    rid = getattr(obj, "id", None)
    if rid is None and isinstance(obj, dict):
        rid = obj.get("id")
    return rid


# ---------------------------------------------------------------------------
# Receipt builder
# ---------------------------------------------------------------------------


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
        schema_overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        schema_id = self.regulatory_context.get("schema", "chatbot_session/v1")
        fields: dict[str, Any] = dict(
            deployer_id=self.deployer_id,
            model_id=model_id,
            interaction_id=interaction_id,
            prompt_sha256=prompt_sha256,
            response_sha256=response_sha256,
            user_pseudonym=self.regulatory_context.get("user_pseudonym"),
            jurisdiction=self.regulatory_context.get("jurisdiction", "EU"),
            extra=extra or {},
        )
        if schema_overrides:
            fields.update(schema_overrides)
        # Allow regulatory_context to feed schema-specific defaults
        for k in (
            "hosting_provider_hq",
            "model_license",
            "open_weights",
            "host_environment",
            "device",
            "task",
            "content_modality",
            "machine_readable_marker",
            "disclosure_shown",
        ):
            if k in self.regulatory_context and k not in fields:
                fields[k] = self.regulatory_context[k]

        receipt = build_receipt(schema_id, **fields)
        receipt_dict = receipt.model_dump()
        signature = self.signer.sign(canonical_encode(receipt_dict))
        envelope = {
            "receipt": receipt_dict,
            "signature": signature.hex(),
            "signature_alg": "ed25519",
            "public_key": self.signer.public_key_bytes().hex(),
            "adapter": {"name": "ledgerproof-huggingface", "version": __version__},
        }
        self.emitter.emit(envelope)
        return envelope


# ---------------------------------------------------------------------------
# Streaming proxy
# ---------------------------------------------------------------------------


class _StreamingProxy:
    """Wraps a streaming response iterator and emits a receipt on drain."""

    def __init__(
        self,
        stream: Iterator[Any],
        *,
        builder: _SignedReceiptBuilder,
        prompt_sha256: str,
        fallback_interaction_id: str,
        fallback_model_id: str,
    ) -> None:
        self._stream = iter(stream)
        self._builder = builder
        self._prompt_sha256 = prompt_sha256
        self._fallback_interaction_id = fallback_interaction_id
        self._hasher = hashlib.sha256()
        self._model_id = fallback_model_id
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
            try:
                close()
            except Exception:  # noqa: BLE001
                pass

    def _absorb(self, chunk: Any) -> None:
        if self._interaction_id is None:
            self._interaction_id = _extract_interaction_id(chunk)
        self._model_id = _extract_model_id(chunk, self._model_id)
        text = _extract_chunk_text(chunk)
        if text:
            self._hasher.update(text.encode("utf-8"))

    def _flush(self) -> None:
        if self._emitted:
            return
        self._emitted = True
        try:
            self._builder.emit(
                model_id=self._model_id,
                interaction_id=self._interaction_id or self._fallback_interaction_id,
                prompt_sha256=self._prompt_sha256,
                response_sha256=self._hasher.hexdigest(),
                extra={"streaming": True},
            )
        except Exception:  # noqa: BLE001
            # C7: receipt failure must never propagate into caller path
            pass


# ---------------------------------------------------------------------------
# Wrapper
# ---------------------------------------------------------------------------


class LedgerProofInferenceClient:
    """Wraps `huggingface_hub.InferenceClient`. Same call surface; emits
    receipts on the side.

    Parameters
    ----------
    deployer_id:
        URN identifying the deployer organisation, e.g. `urn:eu:deployer:acme`.
    regulatory_context:
        Optional dict carrying `schema`, `jurisdiction`, `user_pseudonym`,
        and schema-specific defaults (e.g. `model_license`, `open_weights`).
    signer:
        Optional `Signer`. Defaults to an ephemeral `Ed25519Signer` (MVP only).
    emitter:
        Optional `Emitter`. Defaults to `LogEmitter()` (stdout).
    inference_client:
        Optional pre-built `huggingface_hub.InferenceClient`. If omitted, one
        is built with the remaining `**hf_kwargs` (e.g. `model=...`, `token=...`).
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        regulatory_context: dict[str, Any] | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        inference_client: Any | None = None,
        **hf_kwargs: Any,
    ) -> None:
        if inference_client is None:
            from huggingface_hub import InferenceClient  # local import to keep import light
            inference_client = InferenceClient(**hf_kwargs)
        self._client = inference_client
        self._default_model = hf_kwargs.get("model") or getattr(inference_client, "model", None) or "unknown"
        self._builder = _SignedReceiptBuilder(
            deployer_id=deployer_id,
            regulatory_context=regulatory_context or {},
            signer=signer or Ed25519Signer(),
            emitter=emitter or LogEmitter(),
        )

    # ------------------------------------------------------------------ chat
    def chat_completion(self, *args: Any, **kwargs: Any) -> Any:
        messages = kwargs.get("messages")
        if messages is None and args:
            # huggingface_hub signature: chat_completion(messages, ...)
            messages = args[0] if isinstance(args[0], list) else None
        prompt_sha256 = _hash_messages(messages)
        streaming = bool(kwargs.get("stream"))
        model_hint = kwargs.get("model") or self._default_model
        result = self._client.chat_completion(*args, **kwargs)

        if streaming:
            return _StreamingProxy(
                result,
                builder=self._builder,
                prompt_sha256=prompt_sha256,
                fallback_interaction_id=str(uuid.uuid4()),
                fallback_model_id=model_hint,
            )

        try:
            self._builder.emit(
                model_id=_extract_model_id(result, model_hint),
                interaction_id=_extract_interaction_id(result) or str(uuid.uuid4()),
                prompt_sha256=prompt_sha256,
                response_sha256=_hash_non_streaming_response(result),
            )
        except Exception:  # noqa: BLE001
            # C7
            pass
        return result

    # --------------------------------------------------------- text generation
    def text_generation(self, prompt: str, *args: Any, **kwargs: Any) -> Any:
        prompt_sha256 = _hash_text_prompt(prompt)
        streaming = bool(kwargs.get("stream"))
        model_hint = kwargs.get("model") or self._default_model
        result = self._client.text_generation(prompt, *args, **kwargs)

        if streaming:
            return _StreamingProxy(
                result,
                builder=self._builder,
                prompt_sha256=prompt_sha256,
                fallback_interaction_id=str(uuid.uuid4()),
                fallback_model_id=model_hint,
            )

        try:
            self._builder.emit(
                model_id=_extract_model_id(result, model_hint),
                interaction_id=_extract_interaction_id(result) or str(uuid.uuid4()),
                prompt_sha256=prompt_sha256,
                response_sha256=_hash_non_streaming_response(result),
            )
        except Exception:  # noqa: BLE001
            pass
        return result

    # -------------------------------------------------- attribute passthrough
    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
