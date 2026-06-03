"""Sync client wrapper for Perplexity AI via the OpenAI-compatible API.

`LedgerProofPerplexity` wraps `openai.OpenAI` (configured with Perplexity's
`base_url`) and intercepts `chat.completions.create()` calls. For
non-streaming requests, the receipt is emitted once the full response is in
hand. For streaming requests, we wrap the returned iterator with a
stream-aware SHA-256 (constraint **C6**) and emit the receipt when the
stream is fully drained.

Constraint **C7**: the Perplexity response object is returned unmodified.

Perplexity exposes an OpenAI-compatible REST surface at
`https://api.perplexity.ai`. This wrapper defaults to that base URL but
accepts any standard `openai` client kwargs (including `base_url`
overrides for proxy / gateway setups).

Perplexity's distinguishing feature is **live web search with citations**:
the Sonar family (`sonar`, `sonar-pro`, `sonar-reasoning`, `sonar-deep-research`)
returns a `citations` field on the response. This wrapper auto-extracts
citations for citation-aware schemas, computes a deterministic hash, and
binds them into the receipt — the binding that makes Article 50(4)
public-interest-text labeling actionable.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from typing import Any, Iterator

from openai import OpenAI

from .canonical import canonical_encode, citation_list_hash_hex
from .emitter import Emitter, LogEmitter
from .manual import extract_citations
from .schema import build_receipt
from .signer import Ed25519Signer, Signer
from .version import __version__

PERPLEXITY_DEFAULT_BASE_URL = "https://api.perplexity.ai"

# Schemas that auto-extract `response.citations`.
_CITATION_SCHEMAS = {"ai_search_with_citations/v1", "public_interest_text/v1"}


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


def _extract_chunk_citations(chunk: Any) -> list[str]:
    """Pull citations attached to a streaming chunk, if any.

    Perplexity may attach the final citation list to the *last* chunk of a
    stream, or echo a partial list on earlier chunks. We collect any
    URL-shaped citations we see; the streaming proxy de-duplicates and
    canonicalises at flush time.
    """
    cites = getattr(chunk, "citations", None)
    if not cites:
        extra = getattr(chunk, "model_extra", None)
        if isinstance(extra, dict):
            cites = extra.get("citations")
    if not cites and isinstance(chunk, dict):
        cites = chunk.get("citations")
    if not cites:
        return []
    return [str(c) for c in cites]


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
            "adapter": {"name": "ledgerproof-perplexity", "version": __version__},
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
        self._citations: set[str] = set()
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
        for url in _extract_chunk_citations(chunk):
            self._citations.add(url)

    def _flush(self) -> None:
        if self._emitted:
            return
        self._emitted = True
        schema = self._builder.regulatory_context.get("schema", "chatbot_session/v1")
        extra_fields: dict[str, Any] = {}
        if schema in _CITATION_SCHEMAS:
            cites = sorted(self._citations)
            extra_fields["citations_sha256"] = citation_list_hash_hex(cites)
            extra_fields["citations_count"] = len(cites)
        self._builder.emit(
            model_id=self._model_id,
            interaction_id=self._interaction_id or self._fallback_interaction_id,
            prompt_sha256=self._prompt_sha256,
            response_sha256=self._hasher.hexdigest(),
            extra={"streaming": True, "provider": "perplexity"},
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
        extra: dict[str, Any] = {"provider": "perplexity"}

        if schema in _CITATION_SCHEMAS:
            # Auto-extract citations from the response, unless the deployer
            # pre-computed them in regulatory_context.
            preset_hash = self._builder.regulatory_context.get("citations_sha256")
            preset_count = self._builder.regulatory_context.get("citations_count")
            if preset_hash:
                extra_fields["citations_sha256"] = preset_hash
                if preset_count is not None:
                    extra_fields["citations_count"] = int(preset_count)
            else:
                cites = extract_citations(result)
                extra_fields["citations_sha256"] = citation_list_hash_hex(cites)
                extra_fields["citations_count"] = len(cites)

        if schema == "public_interest_text/v1":
            for k in ("disclosure_label_shown", "editorial_review", "subject_category"):
                if k in self._builder.regulatory_context:
                    extra_fields[k] = self._builder.regulatory_context[k]

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


class LedgerProofPerplexity:
    """Wraps `openai.OpenAI` configured for Perplexity AI. Same call surface;
    emits receipts on the side.

    Parameters
    ----------
    deployer_id:
        URN identifying the deployer organisation, e.g. `urn:eu:deployer:acme`.
    regulatory_context:
        Optional dict carrying `schema`, `jurisdiction`, `user_pseudonym`, and
        Perplexity-specific fields like `citations_sha256`, `citations_count`,
        `disclosure_label_shown`, `editorial_review`, `subject_category`.
    signer:
        Optional `Signer`. Defaults to an ephemeral `Ed25519Signer` (MVP only).
    emitter:
        Optional `Emitter`. Defaults to `LogEmitter()` (stdout).
    openai_client:
        Optional pre-built `openai.OpenAI` instance (already pointed at
        Perplexity). If omitted, one is built with
        `api_key=os.environ["PPLX_API_KEY"]` and
        `base_url="https://api.perplexity.ai"`. Pass any extra `openai_kwargs`
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
            openai_kwargs.setdefault("base_url", PERPLEXITY_DEFAULT_BASE_URL)
            if "api_key" not in openai_kwargs:
                env_key = os.environ.get("PPLX_API_KEY") or os.environ.get(
                    "PERPLEXITY_API_KEY"
                )
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
