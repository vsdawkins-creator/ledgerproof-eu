"""
Synchronous wrapper around a boto3 'bedrock-runtime' client for the legacy
`invoke_model` and `invoke_model_with_response_stream` APIs.

Intercepts both calls, decodes the JSON response body (best-effort), and emits
a signed receipt on the side channel (constraint C7). The wrapped response is
returned UNCHANGED — callers can use this wrapper as a drop-in for
`boto3.client("bedrock-runtime")`.

A separate wrapper handles the newer Converse API (see converse_wrapper.py).
This file deliberately does not import that one — they share `LedgerProofBedrockClient`
via composition in `__init__.py`.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import uuid
from typing import Any, Iterator

from .canonical import IncrementalTextHasher, canonical_encode, hash_text
from .emitter import Emitter, LogEmitter
from .manual import (
    build_model_ref,
    extract_assistant_text,
    extract_user_message_text_from_invoke_body,
    make_eu_residency_attestation,
)
from .schema import (
    ContentRef,
    DataResidencyAttestation,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
    is_eu_region,
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


def _decode_body(body: Any) -> dict[str, Any] | None:
    """
    boto3 returns invoke_model body as a StreamingBody. Read + parse JSON.

    NOTE: this consumes the body. We re-wrap the bytes into a fresh BytesIO so
    the caller still gets a `.read()`-able object — this is the standard
    pattern boto3 users expect after intercepting invoke_model.
    """
    if body is None:
        return None
    try:
        raw = body.read() if hasattr(body, "read") else body
    except Exception:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def _rewrap_body(raw_bytes: bytes) -> io.BytesIO:
    """Return a fresh stream-like object that mimics StreamingBody for the caller."""
    return io.BytesIO(raw_bytes)


class LedgerProofBedrockClient:
    """
    Drop-in wrapper for `boto3.client("bedrock-runtime")`.

    Usage:
        import boto3
        raw = boto3.client("bedrock-runtime", region_name="eu-west-1")
        client = LedgerProofBedrockClient(deployer_id="acme-eu", client=raw)
        response = client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=json.dumps({"messages": [...], "anthropic_version": "..."}),
        )

    Any attribute not explicitly intercepted falls through to the underlying
    boto3 client (so `client.list_foundation_models()` etc. keep working).
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
        region_name: str | None = None,
        attest_residency: bool = False,
        sccs_in_place: bool | None = None,
        **boto3_kwargs: Any,
    ):
        self.deployer_id = deployer_id
        if client is None:
            import boto3  # lazy

            client = boto3.client(
                "bedrock-runtime",
                region_name=region_name,
                **boto3_kwargs,
            )
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._schema: SchemaName = schema
        self._attest_residency = attest_residency
        self._sccs_in_place = sccs_in_place
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()

        # Pull the region from the underlying client config when available.
        self._region: str | None = (
            getattr(getattr(self._inner, "meta", None), "region_name", None)
            or region_name
        )

    # ------------------------------------------------------------------
    # Fall-through
    # ------------------------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # invoke_model
    # ------------------------------------------------------------------
    def invoke_model(self, *args: Any, **kwargs: Any) -> Any:
        body_kwarg = kwargs.get("body")
        model_id = kwargs.get("modelId") or (args[0] if args else None)
        response = self._inner.invoke_model(*args, **kwargs)

        try:
            # Read the body, parse JSON, rewrap so the caller can still .read().
            sb = response.get("body") if isinstance(response, dict) else None
            raw_bytes = sb.read() if sb is not None and hasattr(sb, "read") else b""
            decoded = None
            try:
                decoded = json.loads(raw_bytes) if raw_bytes else None
            except (TypeError, ValueError):
                decoded = None

            # Replace body so the caller is unaffected (C7 + non-invasive).
            if isinstance(response, dict):
                response["body"] = _rewrap_body(raw_bytes)

            user_text = ""
            if isinstance(body_kwarg, (bytes, bytearray)):
                user_text = extract_user_message_text_from_invoke_body(
                    body_kwarg.decode("utf-8", errors="replace")
                )
            elif isinstance(body_kwarg, str):
                user_text = extract_user_message_text_from_invoke_body(body_kwarg)

            self._emit(
                response_for_extraction=decoded,
                user_message_text=user_text,
                model_id=str(model_id) if model_id else "unknown",
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof invoke_model receipt failed: %s", exc)
        return response

    # ------------------------------------------------------------------
    # invoke_model_with_response_stream
    # ------------------------------------------------------------------
    def invoke_model_with_response_stream(self, *args: Any, **kwargs: Any) -> Any:
        body_kwarg = kwargs.get("body")
        model_id = kwargs.get("modelId") or (args[0] if args else None)
        response = self._inner.invoke_model_with_response_stream(*args, **kwargs)

        user_text = ""
        if isinstance(body_kwarg, (bytes, bytearray)):
            user_text = extract_user_message_text_from_invoke_body(
                body_kwarg.decode("utf-8", errors="replace")
            )
        elif isinstance(body_kwarg, str):
            user_text = extract_user_message_text_from_invoke_body(body_kwarg)

        # Wrap the EventStream iterator with one that hashes incrementally (C6).
        stream = response.get("body") if isinstance(response, dict) else None
        if stream is not None:
            wrapper = _StreamEventWrapper(
                inner=stream,
                on_complete=lambda hasher, final_summary: self._emit_stream(
                    user_message_text=user_text,
                    hasher=hasher,
                    final_summary=final_summary,
                    model_id=str(model_id) if model_id else "unknown",
                ),
            )
            response["body"] = wrapper
        return response

    # ------------------------------------------------------------------
    # Internal: receipt construction
    # ------------------------------------------------------------------
    def _emit(
        self,
        response_for_extraction: Any,
        user_message_text: str,
        model_id: str,
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
            model_id_hint=model_id,
            region_hint=self._region,
        )

        schema, residency = self._resolve_schema_and_residency()

        receipt = ReceiptV1(
            schema=schema,
            receipt_id=str(uuid.uuid4()),
            deployer_id=self.deployer_id,
            model=model_ref,
            content_refs=content_refs,
            regulatory_context=self._reg_ctx,
            streaming=streaming,
            residency=residency,
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

    def _emit_stream(
        self,
        user_message_text: str,
        hasher: IncrementalTextHasher,
        final_summary: dict[str, Any] | None,
        model_id: str,
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
                model_id_hint=model_id,
                region_hint=self._region,
            )

            schema, residency = self._resolve_schema_and_residency()

            receipt = ReceiptV1(
                schema=schema,
                receipt_id=str(uuid.uuid4()),
                deployer_id=self.deployer_id,
                model=model_ref,
                content_refs=content_refs,
                regulatory_context=self._reg_ctx,
                streaming=True,
                residency=residency,
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
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof stream receipt failed: %s", exc)

    def _resolve_schema_and_residency(
        self,
    ) -> tuple[SchemaName, DataResidencyAttestation | None]:
        if self._attest_residency:
            return (
                "eu_aws_data_residency/v1",
                make_eu_residency_attestation(
                    self._region, sccs_in_place=self._sccs_in_place
                ),
            )
        # If region is EU but residency not explicitly attested, still record
        # provider attribution via the cross-provider schema by default.
        if self._schema == "chatbot_session/v1":
            return self._schema, None
        return self._schema, None


class _StreamEventWrapper:
    """
    Wrap a Bedrock EventStream iterator (the body of
    `invoke_model_with_response_stream`).

    Each event is a dict like `{"chunk": {"bytes": b"..."}}` where bytes decodes
    to a JSON object with a provider-specific delta shape. We hash the JSON
    bytes (stable across providers) AND best-effort decode known text fields.
    """

    def __init__(
        self,
        inner: Any,
        on_complete: Any,
    ):
        self._inner = inner
        self._hasher = IncrementalTextHasher()
        self._on_complete = on_complete
        self._final_summary: dict[str, Any] | None = None
        self._completed = False

    def __iter__(self) -> Iterator[Any]:
        try:
            for event in self._inner:
                self._consume_event(event)
                yield event
        finally:
            if not self._completed:
                self._completed = True
                try:
                    self._on_complete(self._hasher, self._final_summary)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("stream on_complete failed: %s", exc)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def _consume_event(self, event: Any) -> None:
        if not isinstance(event, dict):
            return
        chunk = event.get("chunk")
        if not isinstance(chunk, dict):
            return
        data = chunk.get("bytes")
        if not isinstance(data, (bytes, bytearray)):
            return
        # Always hash raw bytes — provider-agnostic deterministic content ref.
        self._hasher.update_bytes(bytes(data))
        # Best-effort text extraction for known providers.
        try:
            payload = json.loads(data)
        except (TypeError, ValueError):
            return
        if not isinstance(payload, dict):
            return
        # Capture metadata-ish events for the final summary.
        if payload.get("type") in ("message_stop", "message_delta") or "amazon-bedrock-invocationMetrics" in payload:
            self._final_summary = payload
