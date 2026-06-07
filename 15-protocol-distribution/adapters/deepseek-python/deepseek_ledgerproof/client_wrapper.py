"""Sync client wrapper for DeepSeek via the OpenAI-compatible API.

`LedgerProofDeepSeek` wraps `openai.OpenAI` (configured with DeepSeek's
`base_url`) and intercepts `chat.completions.create()` calls. For non-streaming
requests, the receipt is emitted once the full response is in hand. For
streaming requests, we wrap the returned iterator with a stream-aware SHA-256
(constraint **C6**) and emit the receipt when the stream is fully drained.

Constraint **C7**: the DeepSeek response object is returned unmodified.

DeepSeek exposes an OpenAI-compatible REST surface at `https://api.deepseek.com`.
This wrapper defaults to that base URL but accepts any standard `openai` client
kwargs (including `base_url` overrides for proxy / gateway setups).
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

DEEPSEEK_DEFAULT_BASE_URL = "https://api.deepseek.com"


def _hash_messages(messages: list[dict[str, Any]] | None) -> str:
    if not messages:
        return hashlib.sha256(b"").hexdigest()
    payload = json.dumps(messages, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _extract_response_text_and_reasoning(response: Any) -> tuple[str, str]:
    """Return (final_answer_text, reasoning_trace_text) concatenated across choices.

    DeepSeek-R1 exposes `reasoning_content` on the assistant message in
    addition to the standard `content`. For non-reasoner models the trace will
    be empty.
    """
    answer_parts: list[str] = []
    reasoning_parts: list[str] = []
    for choice in getattr(response, "choices", None) or []:
        msg = getattr(choice, "message", None)
        if msg is None:
            continue
        content = getattr(msg, "content", None)
        if content:
            answer_parts.append(content)
        reasoning = getattr(msg, "reasoning_content", None)
        if reasoning:
            reasoning_parts.append(reasoning)
    return "".join(answer_parts), "".join(reasoning_parts)


def _hash_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _extract_chunk_text(chunk: Any) -> tuple[str, str]:
    """Pull (content, reasoning_content) incrementally from a ChatCompletionChunk."""
    answer = ""
    reasoning = ""
    for choice in getattr(chunk, "choices", None) or []:
        delta = getattr(choice, "delta", None)
        if delta is None:
            continue
        content = getattr(delta, "content", None)
        if content:
            answer += content
        rc = getattr(delta, "reasoning_content", None)
        if rc:
            reasoning += rc
    return answer, reasoning


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
            session_id=self.regulatory_context.get("session_id"),
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
            "adapter": {"name": "ledgerproof-deepseek", "version": __version__},
        }
        try:
            self.emitter.emit(envelope)
        except Exception:  # noqa: BLE001
            # C7 — never let a misbehaving emitter break the caller path.
            pass
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
        # C6: incremental hashers — we never buffer the full body.
        self._answer_hasher = hashlib.sha256()
        self._reasoning_hasher = hashlib.sha256()
        self._reasoning_seen = False
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
        answer, reasoning = _extract_chunk_text(chunk)
        if answer:
            self._answer_hasher.update(answer.encode("utf-8"))
        if reasoning:
            self._reasoning_seen = True
            self._reasoning_hasher.update(reasoning.encode("utf-8"))

    def _flush(self) -> None:
        if self._emitted:
            return
        self._emitted = True
        schema = self._builder.regulatory_context.get("schema", "chatbot_session/v1")
        extra_fields: dict[str, Any] = {}
        if schema == "reasoning_trace/v1" and self._reasoning_seen:
            extra_fields["reasoning_sha256"] = self._reasoning_hasher.hexdigest()
            extra_fields["trace_surfaced_to_user"] = bool(
                self._builder.regulatory_context.get("trace_surfaced_to_user", False)
            )
        if schema == "code_generation/v1":
            lang = self._builder.regulatory_context.get("programming_language")
            if lang:
                extra_fields["programming_language"] = lang
        self._builder.emit(
            model_id=self._model_id,
            interaction_id=self._interaction_id or self._fallback_interaction_id,
            prompt_sha256=self._prompt_sha256,
            response_sha256=self._answer_hasher.hexdigest(),
            extra={"streaming": True, "provider": "deepseek"},
            extra_fields=extra_fields or None,
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
        extra: dict[str, Any] = {"provider": "deepseek"}

        answer_text, reasoning_text = _extract_response_text_and_reasoning(result)

        if schema == "reasoning_trace/v1":
            if reasoning_text:
                extra_fields["reasoning_sha256"] = _hash_str(reasoning_text)
                # Token count is best-effort — DeepSeek may surface it on
                # `usage.completion_tokens_details.reasoning_tokens` in future
                # API revisions; we record what we can read today.
                usage = getattr(result, "usage", None)
                details = getattr(usage, "completion_tokens_details", None) if usage else None
                rtokens = getattr(details, "reasoning_tokens", None) if details else None
                if isinstance(rtokens, int):
                    extra_fields["reasoning_token_count"] = rtokens
            extra_fields["trace_surfaced_to_user"] = bool(
                self._builder.regulatory_context.get("trace_surfaced_to_user", False)
            )

        if schema == "code_generation/v1":
            lang = self._builder.regulatory_context.get("programming_language")
            if lang:
                extra_fields["programming_language"] = lang

        self._builder.emit(
            model_id=getattr(result, "model", "unknown"),
            interaction_id=getattr(result, "id", None) or str(uuid.uuid4()),
            prompt_sha256=prompt_sha256,
            response_sha256=_hash_str(answer_text),
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


class LedgerProofDeepSeek:
    """Wraps `openai.OpenAI` configured for DeepSeek. Same call surface;
    emits receipts on the side.

    Parameters
    ----------
    deployer_id:
        URN identifying the deployer organisation, e.g. `urn:eu:deployer:acme`.
    regulatory_context:
        Optional dict carrying `schema`, `jurisdiction`, `user_pseudonym`,
        `session_id`, and DeepSeek-specific fields like `trace_surfaced_to_user`,
        `programming_language`.
    signer:
        Optional `Signer`. Defaults to an ephemeral `Ed25519Signer` (MVP only).
    emitter:
        Optional `Emitter`. Defaults to `LogEmitter()` (stdout).
    openai_client:
        Optional pre-built `openai.OpenAI` instance (already pointed at
        DeepSeek). If omitted, one is built with
        `api_key=os.environ["DEEPSEEK_API_KEY"]` and
        `base_url="https://api.deepseek.com"`. Pass any extra `openai_kwargs`
        to override.
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
            openai_kwargs.setdefault("base_url", DEEPSEEK_DEFAULT_BASE_URL)
            if "api_key" not in openai_kwargs:
                env_key = os.environ.get("DEEPSEEK_API_KEY")
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
