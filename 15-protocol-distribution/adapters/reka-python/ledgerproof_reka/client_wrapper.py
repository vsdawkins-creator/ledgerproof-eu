"""
Synchronous client wrapper around `reka.client.Reka`.

Intercepts `chat.create()` and `chat.create_stream()` to emit a receipt on the
side channel (constraint C7) after the response is materialised. The wrapped
response object is returned unchanged.

Reka is MULTIMODAL-NATIVE: a single inference may bind text, image, audio,
and/or video inputs. This wrapper sniffs the `messages` payload for non-text
modalities, hashes any embedded media bytes (base64 / data URIs) it can reach,
and binds them via `MediaRef` entries. URI-only references are hashed by URI
so the receipt still binds the *reference* without phoning home.
"""

from __future__ import annotations

import base64
import hashlib
import logging
from typing import Any, Iterable

from .canonical import IncrementalTextHasher, hash_bytes, hash_text
from .emitter import Emitter, LogEmitter
from .manual import _build_model_ref, _extract_assistant_text, extract_tool_uses
from .schema import (
    ContentRef,
    MediaRef,
    Modality,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
)
from .signer import Ed25519Signer, Signer
from .version import __version__

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Message inspection helpers (multimodal-native)
# ---------------------------------------------------------------------------


def _extract_user_message_text(messages: list[dict[str, Any]] | None) -> str:
    """Best-effort concatenation of user-role TEXT content from a messages list."""
    if not messages:
        return ""
    parts: list[str] = []
    for msg in messages:
        if _role_of(msg) != "user":
            continue
        content = _content_of(msg)
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                btype, text = _block_text(block)
                if btype == "text" and text:
                    parts.append(text)
    return "\n".join(parts)


def _extract_media_refs(messages: list[dict[str, Any]] | None) -> list[MediaRef]:
    """
    Walk the messages list for non-text modality blocks and emit MediaRef entries.

    Reka supports image / audio / video content blocks. Blocks may carry inline
    base64 data, a `url`/`data_uri`, or a structured `source` dict. We hash
    whatever bytes we can reach. URL-only blocks are hashed by URL so we still
    bind the reference (C4: never fetch the URL).
    """
    if not messages:
        return []
    refs: list[MediaRef] = []
    for msg in messages:
        if _role_of(msg) != "user":
            continue
        content = _content_of(msg)
        if not isinstance(content, list):
            continue
        for block in content:
            ref = _block_to_media_ref(block)
            if ref is not None:
                refs.append(ref)
    return refs


def _block_to_media_ref(block: Any) -> MediaRef | None:
    btype = _block_type(block)
    if btype not in {"image", "image_url", "audio", "video"}:
        return None

    modality: Modality
    if btype.startswith("image"):
        modality = "image"
    elif btype == "audio":
        modality = "audio"
    else:
        modality = "video"

    # Pull raw bytes if available; otherwise hash a URI reference.
    raw, mime, byte_length = _block_payload(block)
    if raw is not None:
        digest = hash_bytes(raw).hex()
        return MediaRef(
            sha256_hex=digest,
            byte_length=byte_length if byte_length is not None else len(raw),
            modality=modality,
            mime_type=mime or _default_mime(modality),
        )

    uri = _block_uri(block)
    if uri is not None:
        # Hash the URI string itself — we never dereference it (C4).
        uri_hash = hashlib.sha256(uri.encode("utf-8")).hexdigest()
        # Reka URL blocks commonly carry `media_type` at the block top level.
        block_mime = None
        if isinstance(block, dict):
            block_mime = (
                block.get("media_type")
                or block.get("mime_type")
                or block.get("mime")
            )
        else:
            block_mime = (
                getattr(block, "media_type", None)
                or getattr(block, "mime_type", None)
            )
        return MediaRef(
            sha256_hex=uri_hash,
            byte_length=len(uri.encode("utf-8")),
            modality=modality,
            mime_type=mime or block_mime or _default_mime(modality),
            source_uri_sha256_hex=uri_hash,
            descriptor="uri-only",
        )
    return None


def _default_mime(modality: Modality) -> str:
    return {
        "image": "image/octet-stream",
        "audio": "audio/octet-stream",
        "video": "video/octet-stream",
        "text": "text/plain",
    }[modality]


def _block_type(block: Any) -> str | None:
    if isinstance(block, dict):
        return block.get("type")
    return getattr(block, "type", None)


def _block_text(block: Any) -> tuple[str | None, str | None]:
    btype = _block_type(block)
    if isinstance(block, dict):
        return btype, block.get("text") if isinstance(block.get("text"), str) else None
    text = getattr(block, "text", None)
    return btype, text if isinstance(text, str) else None


def _block_payload(block: Any) -> tuple[bytes | None, str | None, int | None]:
    """Return (raw_bytes, mime_type, byte_length) for an inline media block."""
    # Look for several common shapes:
    #   {"type": "image", "image": {"data": "<b64>", "media_type": "image/png"}}
    #   {"type": "image", "source": {"data": "<b64>", "media_type": "image/png"}}
    #   {"type": "audio", "audio": {"data": "<b64>", "media_type": "audio/wav"}}
    #   {"type": "video", "video": {"data": "<b64>", "media_type": "video/mp4"}}
    payload = None
    mime = None
    if isinstance(block, dict):
        for key in ("image", "audio", "video", "source", "media"):
            v = block.get(key)
            if isinstance(v, dict):
                payload = v.get("data") or v.get("bytes_b64") or v.get("b64_json")
                mime = v.get("media_type") or v.get("mime_type") or v.get("mime")
                if payload is not None:
                    break
        if payload is None and isinstance(block.get("data"), str):
            payload = block["data"]
            mime = block.get("media_type") or block.get("mime_type")
    else:
        for key in ("image", "audio", "video", "source", "media"):
            v = getattr(block, key, None)
            if v is not None:
                payload = getattr(v, "data", None)
                mime = getattr(v, "media_type", None) or getattr(v, "mime_type", None)
                if payload is not None:
                    break

    if not isinstance(payload, str):
        return None, mime, None

    # Strip a `data:<mime>;base64,` prefix if present.
    if payload.startswith("data:"):
        head, _, b64 = payload.partition(",")
        # head looks like "data:image/png;base64"
        if ";base64" in head and not mime:
            mime = head[5 : head.index(";")]
        payload = b64

    try:
        raw = base64.b64decode(payload, validate=False)
    except Exception:
        return None, mime, None
    return raw, mime, len(raw)


def _block_uri(block: Any) -> str | None:
    if isinstance(block, dict):
        for key in ("url", "uri", "image_url", "audio_url", "video_url"):
            v = block.get(key)
            if isinstance(v, str):
                return v
            if isinstance(v, dict) and isinstance(v.get("url"), str):
                return v["url"]
        src = block.get("source")
        if isinstance(src, dict) and isinstance(src.get("url"), str):
            return src["url"]
    else:
        for key in ("url", "uri"):
            v = getattr(block, key, None)
            if isinstance(v, str):
                return v
    return None


def _role_of(msg: Any) -> str | None:
    if isinstance(msg, dict):
        return msg.get("role")
    return getattr(msg, "role", None)


def _content_of(msg: Any) -> Any:
    if isinstance(msg, dict):
        return msg.get("content")
    return getattr(msg, "content", None)


def _input_modalities(text_present: bool, media: list[MediaRef]) -> list[Modality]:
    mods: list[Modality] = []
    if text_present:
        mods.append("text")
    for m in media:
        if m.modality not in mods:
            mods.append(m.modality)
    return mods or ["text"]


def _default_reg_ctx() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


# ---------------------------------------------------------------------------
# Schema auto-selection
# ---------------------------------------------------------------------------


def _select_schema(
    base_schema: SchemaName,
    modalities: list[Modality],
    tool_uses: list,
) -> SchemaName:
    """
    Promote receipt schema based on input modalities present.

    Priority:
      - If video input present -> video_understanding/v1
      - Else if 2+ modalities present -> multimodal_native_inference/v1
      - Else -> caller's base_schema
    """
    if "video" in modalities:
        return "video_understanding/v1"
    if len(modalities) >= 2:
        return "multimodal_native_inference/v1"
    return base_schema


# ---------------------------------------------------------------------------
# Sync wrapper
# ---------------------------------------------------------------------------


class _ChatProxy:
    """Wrapper around `client.chat` that intercepts create/create_stream."""

    def __init__(self, parent: "LedgerProofReka"):
        self._parent = parent
        self._inner = parent._inner.chat

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # Non-streaming
    # ------------------------------------------------------------------
    def create(self, *args: Any, **kwargs: Any) -> Any:
        response = self._inner.create(*args, **kwargs)
        try:
            messages = kwargs.get("messages")
            self._parent._emit_for_response(
                response=response,
                user_message_text=_extract_user_message_text(messages),
                media_refs=_extract_media_refs(messages),
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            # C7: never break the calling code path.
            logger.warning("LedgerProof receipt emission failed: %s", exc)
        return response

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------
    def create_stream(self, *args: Any, **kwargs: Any) -> Iterable[Any]:
        """
        Wrap Reka's streaming generator with an incremental SHA-256 (C6).

        Reka's `chat.create_stream(...)` returns an iterable of stream events;
        we re-yield them unchanged while accumulating the assistant text hash.
        """
        return _SyncStreamIterator(
            inner=self._inner.create_stream(*args, **kwargs),
            parent=self._parent,
            messages=kwargs.get("messages"),
        )


class _SyncStreamIterator:
    """Iterable proxy that taps each chunk's text delta and emits a receipt on close."""

    def __init__(self, inner: Iterable[Any], parent: "LedgerProofReka", messages: Any):
        self._inner_iter = iter(inner)
        self._parent = parent
        self._messages = messages
        self._hasher = IncrementalTextHasher()
        self._last_chunk: Any = None
        self._finalized = False

    def __iter__(self):
        return self

    def __next__(self) -> Any:
        try:
            chunk = next(self._inner_iter)
        except StopIteration:
            self._finalize()
            raise
        delta = _extract_stream_delta(chunk)
        if delta:
            self._hasher.update(delta)
        self._last_chunk = chunk
        return chunk

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        # Exhausting the iterator triggers finalization; ensure idempotency.
        self._finalize()
        return False

    def _finalize(self) -> None:
        if self._finalized:
            return
        self._finalized = True
        try:
            self._parent._emit_for_stream(
                final_chunk=self._last_chunk,
                user_message_text=_extract_user_message_text(self._messages),
                media_refs=_extract_media_refs(self._messages),
                text_hasher=self._hasher,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof streaming receipt failed: %s", exc)


def _extract_stream_delta(chunk: Any) -> str | None:
    """
    Extract the assistant text delta from a Reka stream chunk.

    Reka exposes deltas under `responses[0].chunk.content` in v3.x; we also
    accept a few fallbacks for compatibility.
    """
    if chunk is None:
        return None
    responses = getattr(chunk, "responses", None)
    if responses:
        try:
            first = responses[0]
            delta_obj = (
                getattr(first, "chunk", None)
                or getattr(first, "delta", None)
                or getattr(first, "message", None)
            )
            if delta_obj is not None:
                content = getattr(delta_obj, "content", None)
                if isinstance(content, str):
                    return content
        except (IndexError, AttributeError):
            pass
    # Generic fallback shapes
    delta = getattr(chunk, "delta", None)
    if isinstance(delta, str):
        return delta
    text = getattr(chunk, "text", None)
    if isinstance(text, str):
        return text
    if isinstance(chunk, dict):
        for key in ("delta", "text", "content"):
            v = chunk.get(key)
            if isinstance(v, str):
                return v
    return None


class LedgerProofReka:
    """
    Drop-in wrapper for `reka.client.Reka`.

    Usage:
        client = LedgerProofReka(deployer_id="acme-eu", api_key="...")
        response = client.chat.create(
            model="reka-flash-3.1",
            messages=[{"role": "user", "content": "Hello"}],
        )

    All other attributes/methods of the underlying client are forwarded.
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
        **reka_kwargs: Any,
    ):
        self.deployer_id = deployer_id
        if client is None:
            # Defer import to avoid hard-failing if reka-api isn't installed at
            # construction time of subclasses/tests using a mocked client.
            from reka.client import Reka  # type: ignore

            client = Reka(**reka_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()

    # ------------------------------------------------------------------
    @property
    def chat(self) -> _ChatProxy:
        return _ChatProxy(self)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # Internal: receipt construction
    # ------------------------------------------------------------------
    def _emit_for_response(
        self,
        response: Any,
        user_message_text: str,
        media_refs: list[MediaRef],
        streaming: bool,
    ) -> None:
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
        assistant_text = _extract_assistant_text(response) or ""
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(assistant_text).hex(),
                byte_length=len(assistant_text.encode("utf-8")),
                role="assistant",
                modality="text",
            )
        )
        tool_uses = extract_tool_uses(response)
        modalities = _input_modalities(bool(user_message_text), media_refs)
        schema = _select_schema(self._schema, modalities, tool_uses)
        self._build_and_emit(
            response=response,
            content_refs=content_refs,
            media_refs=media_refs,
            tool_uses=tool_uses,
            modalities=modalities,
            streaming=streaming,
            schema_override=schema,
        )

    def _emit_for_stream(
        self,
        final_chunk: Any,
        user_message_text: str,
        media_refs: list[MediaRef],
        text_hasher: IncrementalTextHasher,
    ) -> None:
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
        content_refs.append(
            ContentRef(
                sha256_hex=text_hasher.digest().hex(),
                byte_length=text_hasher.byte_count,
                role="assistant",
                modality="text",
            )
        )
        tool_uses = extract_tool_uses(final_chunk) if final_chunk is not None else []
        modalities = _input_modalities(bool(user_message_text), media_refs)
        schema = _select_schema(self._schema, modalities, tool_uses)
        self._build_and_emit(
            response=final_chunk,
            content_refs=content_refs,
            media_refs=media_refs,
            tool_uses=tool_uses,
            modalities=modalities,
            streaming=True,
            schema_override=schema,
        )

    def _build_and_emit(
        self,
        response: Any,
        content_refs: list[ContentRef],
        media_refs: list[MediaRef],
        tool_uses: list,
        modalities: list[Modality],
        streaming: bool,
        schema_override: SchemaName,
    ) -> None:
        import uuid

        from .canonical import canonical_encode

        model_ref = (
            _build_model_ref(response) if response is not None else _unknown_model_ref()
        )

        receipt = ReceiptV1(
            schema=schema_override,
            receipt_id=str(uuid.uuid4()),
            deployer_id=self.deployer_id,
            model=model_ref,
            content_refs=content_refs,
            media_refs=media_refs,
            regulatory_context=self._reg_ctx,
            tool_uses=tool_uses,
            input_modalities=modalities,
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


def _unknown_model_ref():
    from .schema import ModelRef

    return ModelRef(model_id="unknown", response_id="unknown")
