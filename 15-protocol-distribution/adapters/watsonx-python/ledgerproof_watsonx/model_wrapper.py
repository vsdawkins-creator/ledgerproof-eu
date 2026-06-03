"""
Drop-in wrapper for `ibm_watsonx_ai.foundation_models.ModelInference`.

Intercepts `chat`, `chat_stream`, `generate_text`, and `generate_text_stream`,
emitting a signed receipt on the side channel (constraint C7). The wrapped
response is returned UNCHANGED — callers can use this wrapper as a drop-in
for the standard `ModelInference` constructor.

Usage:

    from ibm_watsonx_ai import Credentials
    from ledgerproof_watsonx import LedgerProofModelInference

    credentials = Credentials(
        url="https://eu-de.ml.cloud.ibm.com",
        api_key="...",
    )

    model = LedgerProofModelInference(
        deployer_id="acme-eu-bank",
        model_id="ibm/granite-3-8b-instruct",
        credentials=credentials,
        project_id="<project-uuid>",
    )

    response = model.chat(messages=[{"role": "user", "content": "Hallo"}])
"""

from __future__ import annotations

import base64
import logging
import uuid
from typing import Any, Iterator

from .canonical import IncrementalTextHasher, canonical_encode, hash_text
from .emitter import Emitter, LogEmitter
from .manual import (
    build_model_ref,
    extract_assistant_text,
    extract_tool_uses,
    extract_user_message_text,
    extract_user_prompt_from_generate,
    make_eu_residency_attestation,
    make_granite_attestation,
)
from .schema import (
    ContentRef,
    DataResidencyAttestation,
    OpenWeightsAttestation,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
    is_granite_open_model,
    region_from_watsonx_url,
)
from .signer import Ed25519Signer, Signer
from .version import __version__

logger = logging.getLogger(__name__)


def _default_reg_ctx() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


class LedgerProofModelInference:
    """
    Drop-in wrapper for `ibm_watsonx_ai.foundation_models.ModelInference`.

    Construction mirrors the upstream `ModelInference` signature. You can
    either:
      (a) pass a pre-built `ModelInference` via the `inner=` kwarg, or
      (b) pass watsonx constructor kwargs (`model_id`, `credentials`,
          `project_id`, etc.) and we'll construct one lazily.

    All non-intercepted attributes fall through to the underlying model.
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        model_id: str | None = None,
        credentials: Any | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        deployment_id: str | None = None,
        params: dict[str, Any] | None = None,
        inner: Any | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
        schema: SchemaName = "chatbot_session/v1",
        region_name: str | None = None,
        attest_residency: bool = False,
        attest_granite_open_weights: bool = False,
        sccs_in_place: bool | None = None,
        tenant_id: str | None = None,
        **watsonx_kwargs: Any,
    ):
        self.deployer_id = deployer_id
        if inner is None:
            if model_id is None:
                raise ValueError(
                    "Either inner=<ModelInference> or model_id=... must be provided"
                )
            try:
                from ibm_watsonx_ai.foundation_models import ModelInference  # lazy
            except ImportError as exc:  # pragma: no cover
                raise ImportError(
                    "ibm-watsonx-ai is required. Run `pip install ibm-watsonx-ai`."
                ) from exc
            inner = ModelInference(
                model_id=model_id,
                credentials=credentials,
                project_id=project_id,
                space_id=space_id,
                deployment_id=deployment_id,
                params=params,
                **watsonx_kwargs,
            )
        self._inner = inner
        self._model_id = model_id or getattr(inner, "model_id", None) or "unknown"
        self._project_id = project_id or getattr(inner, "project_id", None)
        self._space_id = space_id or getattr(inner, "space_id", None)
        self._deployment_id = deployment_id or getattr(inner, "deployment_id", None)

        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        self._attest_residency = attest_residency
        self._attest_granite = attest_granite_open_weights
        self._sccs_in_place = sccs_in_place
        self._tenant_id = tenant_id

        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()

        # Pull the region from the Credentials.url when available.
        url = None
        if credentials is not None:
            url = getattr(credentials, "url", None) or (
                credentials.get("url") if isinstance(credentials, dict) else None
            )
        if url is None:
            inner_creds = getattr(inner, "credentials", None)
            if inner_creds is not None:
                url = getattr(inner_creds, "url", None) or (
                    inner_creds.get("url") if isinstance(inner_creds, dict) else None
                )
        self._region: str | None = region_name or region_from_watsonx_url(url)

    # ------------------------------------------------------------------
    # Fall-through
    # ------------------------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # chat
    # ------------------------------------------------------------------
    def chat(self, *args: Any, **kwargs: Any) -> Any:
        messages = kwargs.get("messages") or (args[0] if args else None)
        response = self._inner.chat(*args, **kwargs)
        try:
            self._emit(
                response_for_extraction=response if isinstance(response, dict) else {},
                user_message_text=extract_user_message_text(messages),
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof chat receipt failed: %s", exc)
        return response

    # ------------------------------------------------------------------
    # chat_stream
    # ------------------------------------------------------------------
    def chat_stream(self, *args: Any, **kwargs: Any) -> Any:
        messages = kwargs.get("messages") or (args[0] if args else None)
        user_text = extract_user_message_text(messages)
        stream = self._inner.chat_stream(*args, **kwargs)
        return _ChatStreamWrapper(
            inner=stream,
            on_complete=lambda hasher, final_summary: self._emit_stream(
                user_message_text=user_text,
                hasher=hasher,
                final_summary=final_summary,
            ),
        )

    # ------------------------------------------------------------------
    # generate_text  (legacy)
    # ------------------------------------------------------------------
    def generate_text(self, *args: Any, **kwargs: Any) -> Any:
        prompt = kwargs.get("prompt") or (args[0] if args else None)
        response = self._inner.generate_text(*args, **kwargs)
        try:
            # generate_text may return a plain str. Normalize.
            response_for_extraction: Any
            if isinstance(response, str):
                response_for_extraction = {"generated_text": response}
            elif isinstance(response, dict):
                response_for_extraction = response
            else:
                response_for_extraction = {}
            self._emit(
                response_for_extraction=response_for_extraction,
                user_message_text=extract_user_prompt_from_generate(prompt),
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof generate_text receipt failed: %s", exc)
        return response

    # ------------------------------------------------------------------
    # generate_text_stream  (legacy)
    # ------------------------------------------------------------------
    def generate_text_stream(self, *args: Any, **kwargs: Any) -> Any:
        prompt = kwargs.get("prompt") or (args[0] if args else None)
        user_text = extract_user_prompt_from_generate(prompt)
        stream = self._inner.generate_text_stream(*args, **kwargs)
        return _GenerateStreamWrapper(
            inner=stream,
            on_complete=lambda hasher, final_summary: self._emit_stream(
                user_message_text=user_text,
                hasher=hasher,
                final_summary=final_summary,
            ),
        )

    # ------------------------------------------------------------------
    # Internal: receipt construction
    # ------------------------------------------------------------------
    def _emit(
        self,
        response_for_extraction: Any,
        user_message_text: str,
        streaming: bool,
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
        assistant_text = extract_assistant_text(response_for_extraction) or ""
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(assistant_text).hex(),
                byte_length=len(assistant_text.encode("utf-8")),
                role="assistant",
            )
        )
        model_ref = build_model_ref(
            response_for_extraction,
            model_id_hint=self._model_id,
            region_hint=self._region,
            project_id_hint=self._project_id,
            space_id_hint=self._space_id,
        )
        tool_uses = extract_tool_uses(response_for_extraction)

        schema, residency, open_weights = self._resolve_schema_residency_openweights()

        receipt = ReceiptV1(
            schema=schema,
            receipt_id=str(uuid.uuid4()),
            deployer_id=self.deployer_id,
            model=model_ref,
            content_refs=content_refs,
            regulatory_context=self._reg_ctx,
            tool_uses=tool_uses,
            streaming=streaming,
            residency=residency,
            open_weights=open_weights,
            adapter_version=__version__,
        )
        self._sign_and_emit(receipt)

    def _emit_stream(
        self,
        user_message_text: str,
        hasher: IncrementalTextHasher,
        final_summary: dict[str, Any] | None,
    ) -> None:
        try:
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
                    sha256_hex=hasher.digest().hex(),
                    byte_length=hasher.byte_count,
                    role="assistant",
                )
            )
            model_ref = build_model_ref(
                final_summary,
                model_id_hint=self._model_id,
                region_hint=self._region,
                project_id_hint=self._project_id,
                space_id_hint=self._space_id,
            )
            schema, residency, open_weights = self._resolve_schema_residency_openweights()
            receipt = ReceiptV1(
                schema=schema,
                receipt_id=str(uuid.uuid4()),
                deployer_id=self.deployer_id,
                model=model_ref,
                content_refs=content_refs,
                regulatory_context=self._reg_ctx,
                streaming=True,
                residency=residency,
                open_weights=open_weights,
                adapter_version=__version__,
            )
            self._sign_and_emit(receipt)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof stream receipt failed: %s", exc)

    def _sign_and_emit(self, receipt: ReceiptV1) -> None:
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

    def _resolve_schema_residency_openweights(
        self,
    ) -> tuple[
        SchemaName,
        DataResidencyAttestation | None,
        OpenWeightsAttestation | None,
    ]:
        residency: DataResidencyAttestation | None = None
        open_weights: OpenWeightsAttestation | None = None
        schema = self._schema

        if self._attest_residency:
            schema = "eu_data_residency/v1"
            residency = make_eu_residency_attestation(
                self._region,
                project_id=self._project_id,
                tenant_id=self._tenant_id,
                sccs_in_place=self._sccs_in_place,
            )

        if self._attest_granite and is_granite_open_model(self._model_id):
            # Granite attestation does NOT override residency schema — both
            # facts can coexist. Granite schema wins only if residency is off.
            if not self._attest_residency:
                schema = "granite_open_model/v1"
            open_weights = make_granite_attestation(model_id=self._model_id)

        return schema, residency, open_weights


# ---------------------------------------------------------------------------
# Stream wrappers
# ---------------------------------------------------------------------------


class _ChatStreamWrapper:
    """
    Wrap the iterator returned by `ModelInference.chat_stream(...)`.

    Each event is a dict shaped like:
      {"id": "...", "choices": [{"index": 0, "delta": {"content": "..."}}],
       "model": "ibm/granite-3-8b-instruct", "object": "chat.completion.chunk"}
    """

    def __init__(self, inner: Any, on_complete: Any):
        self._inner = inner
        self._hasher = IncrementalTextHasher()
        self._on_complete = on_complete
        self._final_summary: dict[str, Any] = {}
        self._completed = False

    def __iter__(self) -> Iterator[Any]:
        try:
            for event in self._inner:
                self._consume(event)
                yield event
        finally:
            if not self._completed:
                self._completed = True
                try:
                    self._on_complete(self._hasher, self._final_summary)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("chat_stream on_complete failed: %s", exc)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def _consume(self, event: Any) -> None:
        if isinstance(event, str):
            # Some watsonx stream variants yield bare strings.
            self._hasher.update(event)
            return
        if not isinstance(event, dict):
            return
        # Capture id / model / usage into final summary.
        for k in ("id", "model", "model_id", "usage"):
            if k in event and k not in self._final_summary:
                self._final_summary[k] = event[k]
        choices = event.get("choices")
        if isinstance(choices, list):
            for ch in choices:
                if not isinstance(ch, dict):
                    continue
                delta = ch.get("delta") or {}
                if isinstance(delta, dict):
                    text = delta.get("content")
                    if isinstance(text, str):
                        self._hasher.update(text)
                    elif isinstance(text, list):
                        for block in text:
                            if isinstance(block, dict) and isinstance(block.get("text"), str):
                                self._hasher.update(block["text"])
                fr = ch.get("finish_reason")
                if fr and "finish_reason" not in self._final_summary:
                    # Inject into a choices-shaped slot so build_model_ref picks it up.
                    self._final_summary.setdefault("choices", [{"finish_reason": fr}])


class _GenerateStreamWrapper:
    """
    Wrap the iterator returned by `ModelInference.generate_text_stream(...)`.

    Events may be:
      - plain strings (delta tokens), or
      - dicts shaped like {"results": [{"generated_text": "..."}]} for
        watsonx's chunked generate variant.
    """

    def __init__(self, inner: Any, on_complete: Any):
        self._inner = inner
        self._hasher = IncrementalTextHasher()
        self._on_complete = on_complete
        self._final_summary: dict[str, Any] = {}
        self._completed = False

    def __iter__(self) -> Iterator[Any]:
        try:
            for event in self._inner:
                self._consume(event)
                yield event
        finally:
            if not self._completed:
                self._completed = True
                try:
                    self._on_complete(self._hasher, self._final_summary)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("generate_text_stream on_complete failed: %s", exc)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def _consume(self, event: Any) -> None:
        if isinstance(event, str):
            self._hasher.update(event)
            return
        if not isinstance(event, dict):
            return
        for k in ("id", "model_id"):
            if k in event and k not in self._final_summary:
                self._final_summary[k] = event[k]
        results = event.get("results")
        if isinstance(results, list):
            for r in results:
                if isinstance(r, dict) and isinstance(r.get("generated_text"), str):
                    self._hasher.update(r["generated_text"])
                if isinstance(r, dict) and r.get("stop_reason"):
                    self._final_summary.setdefault("results", []).append(
                        {"stop_reason": r["stop_reason"]}
                    )
