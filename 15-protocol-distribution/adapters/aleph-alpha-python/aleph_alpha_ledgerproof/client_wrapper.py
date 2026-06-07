"""Sync ``Client`` wrapper for the Aleph Alpha SDK.

Forwards every call to the upstream `aleph_alpha_client.Client` instance,
extracts the prompt and completion text, and emits a receipt over a
side-channel emitter (C7).

The returned `CompletionResponse` is **the exact upstream object** — no fields
are added, removed, or reordered.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from .emitter import Emitter, StdoutEmitter
from .manual import emit_receipt
from .signer import EphemeralEd25519Signer


def _prompt_text_of(request: Any) -> str:
    """Best-effort extraction of plain-text prompt content.

    Aleph Alpha's ``Prompt`` accepts a list of items (text, image, tokens).
    For receipt purposes we concatenate textual segments only — multimodal
    content is referenced by hash of its repr to avoid leaking bytes.
    """
    prompt = getattr(request, "prompt", None)
    if prompt is None:
        return ""
    items = getattr(prompt, "items", None)
    if items is None:
        return str(prompt)
    parts: list[str] = []
    for it in items:
        text = getattr(it, "text", None)
        if isinstance(text, str):
            parts.append(text)
        else:
            parts.append(repr(it))
    return "".join(parts)


def _completion_text_of(response: Any) -> str:
    completions = getattr(response, "completions", None)
    if not completions:
        return ""
    first = completions[0]
    return getattr(first, "completion", "") or ""


def _model_version_of(response: Any) -> Optional[str]:
    return getattr(response, "model_version", None)


class LedgerProofAlephAlpha:
    """Sync wrapper around ``aleph_alpha_client.Client``.

    Parameters
    ----------
    upstream
        The configured ``aleph_alpha_client.Client`` instance.
    article
        Default Article 50 sub-article for emitted receipts (``"50(1)"`` etc.).
    schema
        Default schema name. ``"generated_content/v1"`` is appropriate for
        completion endpoints.
    deployer_id
        Optional opaque identifier for the calling deployer organisation.
    extra
        Default extra fields to merge into every receipt (e.g. on-prem
        attestation metadata).
    emitter
        Where receipts are delivered. Defaults to ``StdoutEmitter()``.
    signer
        Custom signer. Defaults to an ephemeral Ed25519 key.
    """

    def __init__(
        self,
        upstream: Any,
        *,
        article: str = "50(2)",
        schema: str = "generated_content/v1",
        deployer_id: Optional[str] = None,
        extra: Optional[Mapping[str, Any]] = None,
        emitter: Optional[Emitter] = None,
        signer: Optional[EphemeralEd25519Signer] = None,
    ) -> None:
        self._upstream = upstream
        self._article = article
        self._schema = schema
        self._deployer_id = deployer_id
        self._extra = dict(extra or {})
        self._emitter = emitter if emitter is not None else StdoutEmitter()
        self._signer = signer if signer is not None else EphemeralEd25519Signer()

    # ------------------------------------------------------------------
    # Public API surface — mirrors aleph_alpha_client.Client
    # ------------------------------------------------------------------

    def complete(self, request: Any, model: str, **kwargs: Any) -> Any:
        """Forward to ``upstream.complete`` and emit a receipt.

        Response payload is returned **unmodified** (C7).
        """
        response = self._upstream.complete(request, model=model, **kwargs)
        self._emit_for(request, response, model)
        return response

    # Convenience delegation: anything we don't override falls through
    # transparently to the upstream client.
    def __getattr__(self, item: str) -> Any:
        return getattr(self._upstream, item)

    # ------------------------------------------------------------------

    def _emit_for(self, request: Any, response: Any, model: str) -> None:
        extra: dict[str, Any] = dict(self._extra)
        if self._deployer_id and "deployer_id" not in extra and self._schema in (
            "chatbot_session/v1",
            "generated_content/v1",
        ):
            extra["deployer_id"] = self._deployer_id
        emit_receipt(
            article=self._article,
            schema=self._schema,
            prompt_text=_prompt_text_of(request),
            completion_text=_completion_text_of(response),
            model=model,
            model_version=_model_version_of(response),
            extra=extra,
            signer=self._signer,
            emitter=self._emitter,
        )
