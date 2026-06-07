"""LedgerProof callback handler for LlamaIndex.

Plugs into ``llama_index.core.callbacks.CallbackManager``. On ``on_event_start``
we capture context and commit a transcript hash (C6). On ``on_event_end`` we
finalize the receipt, sign it with Ed25519, wrap it in the canonical envelope,
and hand it to the configured emitter — side-channel only (C7).

We focus on the ``LLM`` and ``QUERY`` events because those are the surfaces
Article 50(1) applies to in a typical LlamaIndex RAG / agent pipeline:

- ``LLM``    → ``rag_chatbot_session/v1`` disclosure receipt per call
- ``QUERY``  → ``rag_synthesized_response/v1`` source-attributed receipt

Other event types (EMBEDDING, RETRIEVE, etc.) are observed but not signed —
they would generate evidence noise without Article 50 coverage.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from llama_index.core.callbacks.base_handler import BaseCallbackHandler
from llama_index.core.callbacks.schema import CBEventType, EventPayload


def _ep(name: str) -> Any:
    """Resolve an EventPayload member by name, tolerating LlamaIndex version skew.

    Falls back to the lowercase string key (which is what LlamaIndex itself
    uses to populate the dict — EventPayload members are str-valued enums).
    """
    member = getattr(EventPayload, name, None)
    if member is not None:
        return member
    return name.lower()

from .canonical import receipt_digest, transcript_hash
from .emitter import Emitter, LogEmitter
from .schema import (
    RagChatbotSessionReceipt,
    RagSynthesizedResponseReceipt,
    receipt_envelope,
)
from .signer import Ed25519Signer, Signer

logger = logging.getLogger("ledgerproof.llamaindex")


# ---------------------------------------------------------------------------
# Per-event state captured at on_event_start, finalized at on_event_end.
# ---------------------------------------------------------------------------


@dataclass
class _EventCtx:
    event_type: CBEventType
    event_id: str
    parent_id: Optional[str]
    transcript_hash: str
    start_payload: dict[str, Any] = field(default_factory=dict)
    session_id: str = ""


def _sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _make_receipt_id(event_id: str) -> str:
    """Build a receipt_id that always satisfies the schema's 8–128 char rule.

    LlamaIndex event_ids vary in length and format depending on caller. We
    pad short ids with the sha256-prefix of the event_id so we never violate
    the schema for users passing terse test fixtures.
    """
    base = f"r-{event_id}" if event_id else f"r-{uuid.uuid4().hex[:16]}"
    if len(base) >= 8:
        return base[:128]
    pad = hashlib.sha256(base.encode()).hexdigest()[: (8 - len(base))]
    return (base + pad)[:128]


def _stringify(value: Any) -> str:
    """Cheap, deterministic-ish stringification for hashing inputs."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (bytes, bytearray)):
        try:
            return value.decode("utf-8", errors="replace")
        except Exception:  # pragma: no cover - defensive
            return value.hex()
    return repr(value)


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------


class LedgerProofCallbackHandler(BaseCallbackHandler):
    """LlamaIndex callback handler that emits Article 50 receipts.

    Parameters
    ----------
    deployer_id
        Legal-entity identifier of the deploying organisation. Not a person.
    signer
        Anything implementing the ``Signer`` protocol. Defaults to an ephemeral
        Ed25519 keypair — replace in production.
    emitter
        Where the signed envelope goes. Defaults to ``LogEmitter()``.
    article
        Which Article 50 sub-paragraph this deployment is asserting. Defaults
        to ``"50(1)"`` — the standard chatbot disclosure case.
    model_provider, model_name
        Free-form labels, recorded on every receipt. Override per call if you
        run multiple models behind the same handler.
    event_types_to_ignore, event_starts_to_ignore, event_ends_to_ignore
        Standard LlamaIndex ``BaseCallbackHandler`` knobs.
    """

    # ------------------------------------------------------------------ init

    def __init__(
        self,
        deployer_id: str,
        signer: Optional[Signer] = None,
        emitter: Optional[Emitter] = None,
        article: str = "50(1)",
        model_provider: str = "unknown",
        model_name: str = "unknown",
        event_starts_to_ignore: Optional[list[CBEventType]] = None,
        event_ends_to_ignore: Optional[list[CBEventType]] = None,
    ):
        super().__init__(
            event_starts_to_ignore=event_starts_to_ignore or [],
            event_ends_to_ignore=event_ends_to_ignore or [],
        )
        self._deployer_id = deployer_id
        self._signer: Signer = signer or Ed25519Signer.ephemeral()
        self._emitter: Emitter = emitter or LogEmitter()
        self._article = article
        self._model_provider = model_provider
        self._model_name = model_name

        # event_id → captured context. Bounded only by the lifetime of a trace.
        self._open_events: dict[str, _EventCtx] = {}
        # Trace-id → session-id mapping (one session_id per trace).
        self._trace_sessions: dict[str, str] = {}
        self._lock = threading.Lock()
        self._current_trace_id: Optional[str] = None

    # --------------------------------------------------------- BaseCallback

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        tid = trace_id or str(uuid.uuid4())
        with self._lock:
            self._current_trace_id = tid
            self._trace_sessions.setdefault(tid, f"sess-{uuid.uuid4().hex[:16]}")

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[dict[str, list[str]]] = None,
    ) -> None:
        tid = trace_id or self._current_trace_id
        if tid is None:
            return
        with self._lock:
            self._trace_sessions.pop(tid, None)
            if self._current_trace_id == tid:
                self._current_trace_id = None

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        """Capture the input transcript hash — commits C6 before the body streams."""
        eid = event_id or str(uuid.uuid4())
        payload = payload or {}

        # Pull whatever inputs are visible at start. LlamaIndex passes different
        # keys per event type, so we sweep the well-known ones.
        parts: list[Any] = []
        for key in (
            _ep("MESSAGES"),
            _ep("PROMPT"),
            _ep("QUERY_STR"),
            _ep("SERIALIZED"),
            _ep("TEMPLATE"),
        ):
            if key in payload:
                parts.append({"k": str(key), "v": _stringify(payload[key])})

        th = transcript_hash(parts) if parts else _sha256_hex(b"")

        with self._lock:
            sid = self._trace_sessions.get(
                self._current_trace_id or "",
                f"sess-{uuid.uuid4().hex[:16]}",
            )
            self._open_events[eid] = _EventCtx(
                event_type=event_type,
                event_id=eid,
                parent_id=parent_id or None,
                transcript_hash=th,
                start_payload=dict(payload),
                session_id=sid,
            )
        return eid

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """Finalize, sign, emit. Must never raise into the caller (C7)."""
        try:
            self._on_event_end_inner(event_type, payload or {}, event_id)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("LedgerProof receipt emission failed: %s", exc)

    # ----------------------------------------------------------- internals

    def _on_event_end_inner(
        self,
        event_type: CBEventType,
        payload: dict[str, Any],
        event_id: str,
    ) -> None:
        with self._lock:
            ctx = self._open_events.pop(event_id, None)

        if ctx is None:
            # Stray end without a start — nothing to sign.
            return

        if event_type == CBEventType.LLM:
            receipt = self._build_llm_receipt(ctx, payload)
        elif event_type == CBEventType.QUERY:
            receipt = self._build_query_receipt(ctx, payload)
        else:
            # We observed it but the protocol scope doesn't cover this event.
            return

        digest = receipt_digest(receipt.model_dump(mode="json"))
        sig = self._signer.sign(bytes.fromhex(digest))
        envelope = receipt_envelope(
            receipt=receipt,
            signature_hex=sig.hex(),
            public_key_hex=self._signer.public_key_bytes.hex(),
            key_id=self._signer.key_id,
        )
        # Carry the digest alongside the envelope so verifiers don't have to
        # recompute it before checking the signature.
        envelope["digest"] = digest
        self._emitter.emit(envelope)

    def _build_llm_receipt(
        self,
        ctx: _EventCtx,
        end_payload: dict[str, Any],
    ) -> RagChatbotSessionReceipt:
        # Best-effort retrieval-context hash: if the start payload referenced
        # any retrieved chunks via SERIALIZED, hash that; otherwise zero-hash.
        ctx_hash = _sha256_hex(
            _stringify(ctx.start_payload.get(_ep("SERIALIZED"), ""))
        )
        return RagChatbotSessionReceipt(
            receipt_id=_make_receipt_id(ctx.event_id),
            deployer_id=self._deployer_id,
            article=self._article,
            session_id=ctx.session_id,
            model_provider=self._model_provider,
            model_name=self._model_name,
            retrieval_context_hash=ctx_hash,
            num_retrieved_chunks=0,
            transcript_hash=ctx.transcript_hash,
            disclosure_shown=True,
        )

    def _build_query_receipt(
        self,
        ctx: _EventCtx,
        end_payload: dict[str, Any],
    ) -> RagSynthesizedResponseReceipt:
        query_str = _stringify(ctx.start_payload.get(_ep("QUERY_STR"), ""))
        response = end_payload.get(_ep("RESPONSE")) or end_payload.get("response")
        response_text = _stringify(response)

        # If LlamaIndex attached source nodes on the response, hash each node's
        # text into source_document_hashes. Defensive: nothing on this path is
        # allowed to raise out of a callback.
        src_hashes: list[str] = []
        nodes = getattr(response, "source_nodes", None) if response is not None else None
        if nodes:
            for n in nodes:
                node_obj = getattr(n, "node", n)
                text = getattr(node_obj, "text", None) or getattr(node_obj, "get_content", lambda: "")()
                src_hashes.append(_sha256_hex(_stringify(text)))

        return RagSynthesizedResponseReceipt(
            receipt_id=_make_receipt_id(ctx.event_id),
            deployer_id=self._deployer_id,
            article=self._article,
            session_id=ctx.session_id,
            query_hash=_sha256_hex(query_str),
            response_hash=_sha256_hex(response_text),
            source_document_hashes=src_hashes[:1000],
            model_provider=self._model_provider,
            model_name=self._model_name,
        )
