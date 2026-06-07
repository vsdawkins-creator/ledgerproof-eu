"""
LedgerProofGenerativeModel — drop-in wrapper around
`google.generativeai.GenerativeModel`.

Intercepts `generate_content()` (both streaming and non-streaming) and emits
a signed receipt on the side channel (constraint C7) after the response is
materialised. The wrapped response is returned unchanged.

Streaming (constraint C6): uses an incremental SHA-256 over each chunk's
`.text` delta as the user iterates the response. The receipt fires once the
iterator is exhausted; the response body is never buffered server-side.
"""

from __future__ import annotations

import base64
import logging
import uuid
from typing import Any, Iterable, Iterator

from .canonical import IncrementalTextHasher, canonical_encode, hash_text
from .emitter import Emitter, LogEmitter
from .manual import _build_model_ref, extract_function_calls
from .schema import (
    ContentRef,
    Modality,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
)
from .signer import Ed25519Signer, Signer
from .version import __version__

logger = logging.getLogger(__name__)


_VALID_MODALITIES: tuple[str, ...] = ("text", "image", "audio", "video", "file")


def _default_reg_ctx() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def _coerce_prompt_to_text(prompt: Any) -> tuple[str, list[Modality]]:
    """
    Best-effort text extraction + modality detection from a generate_content
    `contents` argument.

    Supports:
      - str
      - iterables containing strings, PIL Images, dict parts, etc.
    Returns: (joined_text, modalities_seen)
    """
    if prompt is None:
        return "", ["text"]
    if isinstance(prompt, str):
        return prompt, ["text"]
    if isinstance(prompt, (bytes, bytearray)):
        # Raw bytes are most often image/audio in Gemini calls.
        return "", ["file"]

    texts: list[str] = []
    modalities: list[Modality] = []
    seen: set[Modality] = set()

    def _add_mod(m: Modality) -> None:
        if m not in seen:
            seen.add(m)
            modalities.append(m)

    items: Iterable[Any]
    if isinstance(prompt, dict):
        items = [prompt]
    elif isinstance(prompt, (list, tuple)):
        items = prompt
    else:
        # Anything else single-element (e.g. a PIL.Image instance).
        items = [prompt]

    for item in items:
        if isinstance(item, str):
            texts.append(item)
            _add_mod("text")
        elif isinstance(item, (bytes, bytearray)):
            _add_mod("file")
        elif isinstance(item, dict):
            # google-generativeai dict-form parts: {"text": ...} / {"inline_data": ...} / {"file_data": ...}
            if "text" in item:
                texts.append(str(item["text"]))
                _add_mod("text")
            elif "inline_data" in item:
                mime = ""
                if isinstance(item["inline_data"], dict):
                    mime = str(item["inline_data"].get("mime_type", ""))
                _add_mod(_mod_from_mime(mime))
            elif "file_data" in item:
                mime = ""
                if isinstance(item["file_data"], dict):
                    mime = str(item["file_data"].get("mime_type", ""))
                _add_mod(_mod_from_mime(mime))
            else:
                _add_mod("file")
        else:
            # PIL Image, audio object, etc — detect via class name string.
            cls = item.__class__.__name__.lower()
            if "image" in cls:
                _add_mod("image")
            elif "audio" in cls:
                _add_mod("audio")
            elif "video" in cls:
                _add_mod("video")
            else:
                _add_mod("file")

    if not modalities:
        modalities = ["text"]
    return "\n".join(texts), modalities


def _mod_from_mime(mime: str) -> Modality:
    mime = (mime or "").lower()
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("audio/"):
        return "audio"
    if mime.startswith("video/"):
        return "video"
    if mime.startswith("text/"):
        return "text"
    return "file"


class LedgerProofGenerativeModel:
    """
    Drop-in wrapper for `google.generativeai.GenerativeModel`.

    Usage:
        model = LedgerProofGenerativeModel("gemini-2.0-flash",
                                          deployer_id="acme-eu-bank")
        response = model.generate_content("Hello.")

    All other attributes of the underlying model are forwarded via __getattr__.
    """

    def __init__(
        self,
        model_name_or_model: Any,
        *,
        deployer_id: str,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
        schema: SchemaName = "chatbot_session/v1",
        session_id: str | None = None,
        **genai_kwargs: Any,
    ):
        self.deployer_id = deployer_id
        self._session_id = session_id
        self._inner = _build_inner_model(model_name_or_model, **genai_kwargs)
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_content(self, contents: Any = None, *args: Any, **kwargs: Any) -> Any:
        stream = bool(kwargs.get("stream", False))
        prompt_text, modalities = _coerce_prompt_to_text(contents)

        if stream:
            inner_iter = self._inner.generate_content(contents, *args, **kwargs)
            return _StreamingResponseProxy(
                inner=inner_iter,
                parent=self,
                user_message_text=prompt_text,
                modalities=modalities,
            )

        response = self._inner.generate_content(contents, *args, **kwargs)
        try:
            self._emit_for_response(
                response=response,
                user_message_text=prompt_text,
                modalities=modalities,
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001 — C7: never break the caller
            logger.warning("LedgerProof receipt emission failed: %s", exc)
        return response

    def start_chat(self, *args: Any, **kwargs: Any) -> Any:
        """Wrap the inner chat session so each send_message emits a receipt."""
        from .chat_wrapper import LedgerProofChatSession  # avoid circular import

        inner_chat = self._inner.start_chat(*args, **kwargs)
        return LedgerProofChatSession(inner_chat=inner_chat, parent_model=self)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # Internal: build + emit
    # ------------------------------------------------------------------

    def _emit_for_response(
        self,
        response: Any,
        user_message_text: str,
        modalities: list[Modality],
        streaming: bool,
        assistant_text_override: str | None = None,
        assistant_byte_len_override: int | None = None,
        assistant_hash_override: str | None = None,
    ) -> None:
        from .manual import _extract_model_text

        content_refs: list[ContentRef] = []
        if user_message_text:
            content_refs.append(
                ContentRef(
                    sha256_hex=hash_text(user_message_text).hex(),
                    byte_length=len(user_message_text.encode("utf-8")),
                    role="user",
                    modality="text",
                )
            )

        if assistant_hash_override is not None:
            content_refs.append(
                ContentRef(
                    sha256_hex=assistant_hash_override,
                    byte_length=assistant_byte_len_override or 0,
                    role="model",
                    modality="text",
                )
            )
        else:
            text = assistant_text_override
            if text is None:
                text = _extract_model_text(response) or ""
            content_refs.append(
                ContentRef(
                    sha256_hex=hash_text(text).hex(),
                    byte_length=len(text.encode("utf-8")),
                    role="model",
                    modality="text",
                )
            )

        function_calls = extract_function_calls(response) if response is not None else []
        effective_schema: SchemaName = self._schema
        if function_calls and effective_schema == "chatbot_session/v1":
            effective_schema = "gemini_function_call/v1"
        if (
            effective_schema == "chatbot_session/v1"
            and any(m != "text" for m in modalities)
        ):
            effective_schema = "multimodal_generation/v1"

        model_ref = _build_model_ref(response)

        receipt = ReceiptV1(
            schema=effective_schema,
            receipt_id=str(uuid.uuid4()),
            deployer_id=self.deployer_id,
            session_id=self._session_id,
            model=model_ref,
            content_refs=content_refs,
            regulatory_context=self._reg_ctx,
            function_calls=function_calls,
            input_modalities=modalities or ["text"],
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


def _build_inner_model(model_name_or_model: Any, **genai_kwargs: Any) -> Any:
    """
    Accept either:
      - a model name string ("gemini-2.0-flash"), in which case we construct
        the inner google.generativeai.GenerativeModel ourselves;
      - an existing GenerativeModel instance (or any object with
        generate_content), which we wrap directly. Useful for dependency
        injection in tests.
    """
    if isinstance(model_name_or_model, str):
        try:
            import google.generativeai as genai  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "google-generativeai is required. "
                "Install with: pip install google-generativeai"
            ) from exc
        return genai.GenerativeModel(model_name_or_model, **genai_kwargs)
    # Otherwise treat as an already-constructed model-like object.
    return model_name_or_model


class _StreamingResponseProxy:
    """
    Iterates the upstream streaming response, taps each chunk for incremental
    hashing (constraint C6), and emits a receipt once the iterator is
    exhausted. NEVER buffers the response body.

    The proxy itself is iterable so user code patterns:

        for chunk in model.generate_content("hi", stream=True):
            ...

    keep working without any change beyond the wrap.
    """

    def __init__(
        self,
        inner: Any,
        parent: LedgerProofGenerativeModel,
        user_message_text: str,
        modalities: list[Modality],
    ):
        self._inner = inner
        self._parent = parent
        self._user_text = user_message_text
        self._modalities = modalities
        self._hasher = IncrementalTextHasher()
        self._last_chunk: Any = None
        self._closed = False

    def __iter__(self) -> Iterator[Any]:
        try:
            for chunk in self._inner:
                self._last_chunk = chunk
                text = getattr(chunk, "text", None)
                if isinstance(text, str):
                    self._hasher.update(text)
                yield chunk
        finally:
            self._finalize()

    def __getattr__(self, name: str) -> Any:
        # Forward unknown attrs (.resolve(), .prompt_feedback, etc.) to the
        # upstream iterator/object.
        return getattr(self._inner, name)

    def resolve(self) -> Any:
        """Forward + finalize. Returns the inner SDK's resolved response."""
        result = None
        if hasattr(self._inner, "resolve"):
            result = self._inner.resolve()
        self._finalize()
        return result

    def _finalize(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            digest_hex = self._hasher.digest().hex()
            self._parent._emit_for_response(
                response=self._last_chunk,
                user_message_text=self._user_text,
                modalities=self._modalities,
                streaming=True,
                assistant_byte_len_override=self._hasher.byte_count,
                assistant_hash_override=digest_hex,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof streaming receipt failed: %s", exc)
