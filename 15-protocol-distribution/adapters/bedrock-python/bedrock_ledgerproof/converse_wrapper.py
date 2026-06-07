"""
Wrapper for the Bedrock Converse API (`client.converse`, `client.converse_stream`).

The Converse API is the newer, unified, provider-agnostic interface to Bedrock.
It carries a much cleaner response shape, so the receipt extraction is simpler
than the per-provider invoke_model path.

We layer this on top of the same `LedgerProofBedrockClient` from
`client_wrapper.py` by patching the two methods after construction. Users get
one drop-in client that handles all four entrypoints.
"""

from __future__ import annotations

import base64
import logging
import uuid
from typing import Any, Iterator

from .canonical import IncrementalTextHasher, canonical_encode, hash_text
from .client_wrapper import LedgerProofBedrockClient
from .manual import (
    build_model_ref,
    extract_assistant_text,
    extract_tool_uses,
    extract_user_message_text_from_converse,
)
from .schema import ContentRef, ReceiptV1
from .version import __version__

logger = logging.getLogger(__name__)


def _emit_for_converse_response(
    parent: LedgerProofBedrockClient,
    response: dict[str, Any],
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
    assistant_text = extract_assistant_text(response) or ""
    content_refs.append(
        ContentRef(
            sha256_hex=hash_text(assistant_text).hex(),
            byte_length=len(assistant_text.encode("utf-8")),
            role="assistant",
        )
    )
    tool_uses = extract_tool_uses(response)
    model_ref = build_model_ref(
        response,
        model_id_hint=model_id,
        region_hint=parent._region,
    )

    schema, residency = parent._resolve_schema_and_residency()
    # Bedrock cross-provider receipts make sense for Converse since the API is
    # explicitly multi-provider. Promote chatbot_session/v1 → bedrock_cross_provider/v1
    # when tool_uses are present OR when the caller hasn't overridden the schema.
    if tool_uses and schema == "chatbot_session/v1":
        schema = "bedrock_cross_provider/v1"

    receipt = ReceiptV1(
        schema=schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=parent.deployer_id,
        model=model_ref,
        content_refs=content_refs,
        regulatory_context=parent._reg_ctx,
        tool_uses=tool_uses,
        streaming=streaming,
        residency=residency,
        adapter_version=__version__,
    )
    payload = receipt.to_payload()
    canonical_bytes = canonical_encode(payload)
    signature = parent._signer.sign(canonical_bytes)
    signed = {
        "receipt": payload,
        "signature_alg": "ed25519",
        "signature_b64": base64.b64encode(signature).decode("ascii"),
        "signer_key_id": parent._signer.key_id,
        "canonical_encoding": "cbor-rfc8949-deterministic",
    }
    parent._emitter.emit(signed)


class _ConverseStreamWrapper:
    """Wrap the EventStream iterator returned by `converse_stream`."""

    def __init__(self, inner: Any, on_complete: Any):
        self._inner = inner
        self._hasher = IncrementalTextHasher()
        self._on_complete = on_complete
        self._final_summary: dict[str, Any] = {"output": {"message": {"content": []}}}
        self._tool_use_blocks: list[dict[str, Any]] = []
        self._completed = False

    def __iter__(self) -> Iterator[Any]:
        try:
            for event in self._inner:
                self._consume(event)
                yield event
        finally:
            if not self._completed:
                self._completed = True
                # Synthesize a minimal Converse-shaped summary so downstream
                # extraction helpers still work.
                blocks: list[dict[str, Any]] = self._tool_use_blocks
                self._final_summary["output"]["message"]["content"] = blocks
                try:
                    self._on_complete(self._hasher, self._final_summary)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("converse stream on_complete failed: %s", exc)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def _consume(self, event: Any) -> None:
        if not isinstance(event, dict):
            return
        # Converse stream event shapes (most common):
        #   {"contentBlockDelta": {"delta": {"text": "..."}, "contentBlockIndex": 0}}
        #   {"contentBlockStart": {"start": {"toolUse": {"toolUseId": "...", "name": "..."}}, ...}}
        #   {"messageStop": {"stopReason": "end_turn"}}
        #   {"metadata": {"usage": {...}}}
        cbd = event.get("contentBlockDelta")
        if isinstance(cbd, dict):
            delta = cbd.get("delta") or {}
            text = delta.get("text") if isinstance(delta, dict) else None
            if isinstance(text, str):
                self._hasher.update(text)

        cbs = event.get("contentBlockStart")
        if isinstance(cbs, dict):
            start = cbs.get("start") or {}
            tu = start.get("toolUse") if isinstance(start, dict) else None
            if isinstance(tu, dict):
                self._tool_use_blocks.append({"toolUse": tu})

        meta = event.get("metadata")
        if isinstance(meta, dict):
            usage = meta.get("usage")
            if isinstance(usage, dict):
                self._final_summary["usage"] = usage

        ms = event.get("messageStop")
        if isinstance(ms, dict):
            self._final_summary["stopReason"] = ms.get("stopReason")


def install_converse_methods(client: LedgerProofBedrockClient) -> None:
    """Monkey-patch a LedgerProofBedrockClient with converse + converse_stream."""

    inner = client._inner

    def converse(*args: Any, **kwargs: Any) -> Any:
        messages = kwargs.get("messages")
        model_id = kwargs.get("modelId") or (args[0] if args else None)
        response = inner.converse(*args, **kwargs)
        try:
            _emit_for_converse_response(
                parent=client,
                response=response if isinstance(response, dict) else {},
                user_message_text=extract_user_message_text_from_converse(messages),
                model_id=str(model_id) if model_id else "unknown",
                streaming=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof converse receipt failed: %s", exc)
        return response

    def converse_stream(*args: Any, **kwargs: Any) -> Any:
        messages = kwargs.get("messages")
        model_id = kwargs.get("modelId") or (args[0] if args else None)
        user_text = extract_user_message_text_from_converse(messages)
        response = inner.converse_stream(*args, **kwargs)

        stream = response.get("stream") if isinstance(response, dict) else None
        if stream is None:
            return response

        def _on_complete(hasher: IncrementalTextHasher, final_summary: dict[str, Any]) -> None:
            try:
                content_refs: list[ContentRef] = []
                if user_text:
                    content_refs.append(
                        ContentRef(
                            sha256_hex=hash_text(user_text).hex(),
                            byte_length=len(user_text.encode("utf-8")),
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
                tool_uses = extract_tool_uses(final_summary)
                model_ref = build_model_ref(
                    final_summary,
                    model_id_hint=str(model_id) if model_id else "unknown",
                    region_hint=client._region,
                )
                schema, residency = client._resolve_schema_and_residency()
                if tool_uses and schema == "chatbot_session/v1":
                    schema = "bedrock_cross_provider/v1"
                receipt = ReceiptV1(
                    schema=schema,
                    receipt_id=str(uuid.uuid4()),
                    deployer_id=client.deployer_id,
                    model=model_ref,
                    content_refs=content_refs,
                    regulatory_context=client._reg_ctx,
                    tool_uses=tool_uses,
                    streaming=True,
                    residency=residency,
                    adapter_version=__version__,
                )
                payload = receipt.to_payload()
                canonical_bytes = canonical_encode(payload)
                signature = client._signer.sign(canonical_bytes)
                signed = {
                    "receipt": payload,
                    "signature_alg": "ed25519",
                    "signature_b64": base64.b64encode(signature).decode("ascii"),
                    "signer_key_id": client._signer.key_id,
                    "canonical_encoding": "cbor-rfc8949-deterministic",
                }
                client._emitter.emit(signed)
            except Exception as exc:  # noqa: BLE001
                logger.warning("converse_stream emit failed: %s", exc)

        response["stream"] = _ConverseStreamWrapper(stream, _on_complete)
        return response

    # Bind to the wrapper instance (not the class).
    object.__setattr__(client, "converse", converse)
    object.__setattr__(client, "converse_stream", converse_stream)
