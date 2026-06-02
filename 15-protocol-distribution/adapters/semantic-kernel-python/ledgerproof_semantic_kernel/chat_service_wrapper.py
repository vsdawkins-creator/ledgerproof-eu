"""Wrap a Semantic Kernel chat completion service to emit chatbot receipts.

Why a wrapper instead of just a filter? SK filters intercept *kernel function*
invocations. Direct chat-service calls (`service.get_chat_message_content()`
or `get_streaming_chat_message_content()`) don't pass through function
filters. The wrapper hooks the chat-service surface directly so we still
emit Article 50(1) chatbot receipts for direct-chat usage patterns.

Use with `OpenAIChatCompletion`, `AzureChatCompletion`, or any SK
`ChatCompletionClientBase` subclass.
"""

from __future__ import annotations

import base64
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, Optional

from .canonical import canonical_encode
from .emitter import BaseEmitter, LogEmitter
from .schema import get_schema
from .signer import BaseSigner, Ed25519Signer


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )


def _message_text(msg: Any) -> str:
    """Best-effort text projection of a Semantic Kernel ChatMessageContent."""
    if msg is None:
        return ""
    content = getattr(msg, "content", None)
    if content is not None:
        return str(content)
    return str(msg)


def _history_text(history: Any) -> list[str]:
    """Return per-message text from a ChatHistory-like object."""
    if history is None:
        return []
    messages = getattr(history, "messages", history)
    out: list[str] = []
    try:
        for m in messages:
            out.append(_message_text(m))
    except TypeError:
        pass
    return out


class LedgerProofChatService:
    """Wraps an SK chat-completion service, emitting a signed receipt per call.

    Parameters
    ----------
    inner:
        The wrapped service (e.g. `OpenAIChatCompletion`, `AzureChatCompletion`).
    deployer_id:
        Pseudonymous deployer identifier. MUST NOT be an email.
    schema:
        One of: 'chatbot_session/v1' (default), 'generated_content/v1',
        'azure_enterprise_session/v1'.
    emitter:
        BaseEmitter implementation. Defaults to LogEmitter.
    signer:
        BaseSigner implementation. Defaults to ephemeral Ed25519Signer.
    extra:
        Dict of additional schema fields (e.g. `tenant_id`, `subscription_scope`
        for `azure_enterprise_session/v1`).
    """

    def __init__(
        self,
        inner: Any,
        *,
        deployer_id: str,
        schema: str = "chatbot_session/v1",
        emitter: Optional[BaseEmitter] = None,
        signer: Optional[BaseSigner] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._inner = inner
        self.deployer_id = deployer_id
        self.schema_id = schema
        self.emitter: BaseEmitter = emitter or LogEmitter(
            "./ledgerproof-receipts.jsonl"
        )
        self.signer: BaseSigner = signer or Ed25519Signer()
        self.extra: Dict[str, Any] = dict(extra or {})

    def __getattr__(self, name: str) -> Any:
        # Transparent delegation for everything we don't override.
        return getattr(self._inner, name)

    # ------------------------------------------------------------ helpers
    def _model_id(self) -> str:
        for attr in ("ai_model_id", "model_id", "model", "deployment_name"):
            v = getattr(self._inner, attr, None)
            if v:
                return str(v)
        return "unknown"

    def _emit(self, transcript_sha256: str) -> None:
        fields: Dict[str, Any] = {
            "schema_id": self.schema_id,
            "run_id": str(uuid.uuid4()),
            "timestamp_utc": _utc_now(),
            "deployer_id": self.deployer_id,
            "transcript_sha256": transcript_sha256,
        }
        if self.schema_id in (
            "chatbot_session/v1",
            "generated_content/v1",
            "azure_enterprise_session/v1",
        ):
            fields.setdefault("model_identifier", self._model_id())
        if self.schema_id == "generated_content/v1":
            fields.setdefault("content_type", "text/plain")
        fields.update(self.extra)

        try:
            validated = get_schema(self.schema_id)(**fields).model_dump()
        except Exception:
            return  # side-channel invariant: receipt failure must not raise

        body_bytes = canonical_encode(validated)
        body_digest = hashlib.sha256(body_bytes).digest()
        signature = self.signer.sign(body_digest)
        envelope: Dict[str, Any] = {
            "body": validated,
            "body_sha256": body_digest.hex(),
            "signature_ed25519": base64.urlsafe_b64encode(signature)
            .rstrip(b"=")
            .decode("ascii"),
            "public_key_ed25519": self.signer.public_key_b64(),
            "alg": "Ed25519",
        }
        try:
            self.emitter.emit(envelope)
        except Exception:
            pass

    def _hash_prompt(self, chat_history: Any) -> "hashlib._Hash":
        h = hashlib.sha256()
        h.update(b"lpr:v1:prompts\n")
        for text in _history_text(chat_history):
            b = text.encode("utf-8")
            h.update(len(b).to_bytes(8, "big"))
            h.update(b)
        h.update(b"lpr:v1:tokens\n")
        return h

    # --------------------------------------------------- non-streaming path
    async def get_chat_message_content(
        self, chat_history: Any, settings: Any = None, **kwargs: Any
    ) -> Any:
        """Non-streaming chat completion; emits a single receipt after."""
        result = await self._inner.get_chat_message_content(
            chat_history=chat_history, settings=settings, **kwargs
        )
        h = self._hash_prompt(chat_history)
        text = _message_text(result).encode("utf-8")
        h.update(len(text).to_bytes(8, "big"))
        h.update(text)
        self._emit(h.hexdigest())
        return result

    async def get_chat_message_contents(
        self, chat_history: Any, settings: Any = None, **kwargs: Any
    ) -> Any:
        """Plural-returning variant. One receipt per response message."""
        results = await self._inner.get_chat_message_contents(
            chat_history=chat_history, settings=settings, **kwargs
        )
        for r in results or []:
            h = self._hash_prompt(chat_history)
            text = _message_text(r).encode("utf-8")
            h.update(len(text).to_bytes(8, "big"))
            h.update(text)
            self._emit(h.hexdigest())
        return results

    # --------------------------------------------------------- streaming
    async def get_streaming_chat_message_content(
        self, chat_history: Any, settings: Any = None, **kwargs: Any
    ) -> AsyncGenerator[Any, None]:
        """Stream-aware (C6): hash tokens as they pass, emit at stream end.

        Does NOT buffer the full response; only the running digest is kept.
        """
        h = self._hash_prompt(chat_history)
        async for chunk in self._inner.get_streaming_chat_message_content(
            chat_history=chat_history, settings=settings, **kwargs
        ):
            text = _message_text(chunk).encode("utf-8")
            if text:
                h.update(len(text).to_bytes(8, "big"))
                h.update(text)
            yield chunk
        self._emit(h.hexdigest())

    async def get_streaming_chat_message_contents(
        self, chat_history: Any, settings: Any = None, **kwargs: Any
    ) -> AsyncGenerator[Any, None]:
        """Plural streaming variant; same stream-aware semantics."""
        h = self._hash_prompt(chat_history)
        async for chunk_list in self._inner.get_streaming_chat_message_contents(
            chat_history=chat_history, settings=settings, **kwargs
        ):
            try:
                iterable = list(chunk_list)
            except TypeError:
                iterable = [chunk_list]
            for chunk in iterable:
                text = _message_text(chunk).encode("utf-8")
                if text:
                    h.update(len(text).to_bytes(8, "big"))
                    h.update(text)
            yield chunk_list
        self._emit(h.hexdigest())
