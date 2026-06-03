"""Async Cerebras client wrapper with LedgerProof side-channel receipts."""

from __future__ import annotations

import os
import time
from typing import Any, AsyncIterable, Optional, Union

from cerebras.cloud.sdk import AsyncCerebras

from .client_wrapper import _pop_lpr, _sha256, _REASONING_MODEL_RE
from .emitter import AsyncEmitter, ReceiptSink, build_signed_receipt, default_sink_from_env
from .schema import (
    ChatbotSessionV1,
    GeneratedContentV1,
    ReasoningDistilledV1,
    ReceiptSchemaName,
    WaferScaleInferenceV1,
)
from .signer import Ed25519Signer, load_signer_from_pem


class _AsyncChatCompletionsProxy:
    def __init__(self, parent: "LedgerProofAsyncCerebras"):
        self._parent = parent
        self._inner = parent._inner.chat.completions

    async def create(self, *args: Any, **kwargs: Any) -> Any:
        lpr_opts = _pop_lpr(kwargs)
        if lpr_opts.get("skip"):
            return await self._inner.create(*args, **kwargs)

        is_stream = bool(kwargs.get("stream", False))
        model = kwargs.get("model", "unknown")
        prompt_text = ""
        if "messages" in kwargs:
            try:
                prompt_text = "".join(
                    (m.get("content") or "") for m in kwargs["messages"] if isinstance(m, dict)
                )
            except Exception:
                prompt_text = ""

        t0 = time.monotonic()
        result = await self._inner.create(*args, **kwargs)

        if is_stream:
            return self._wrap_async_stream(result, lpr_opts, model, prompt_text, t0)

        latency_ms = (time.monotonic() - t0) * 1000
        completion_text = ""
        try:
            completion_text = result.choices[0].message.content or ""
        except Exception:
            completion_text = ""
        usage = getattr(result, "usage", None)
        self._parent._emit_chat_receipt(
            lpr_opts, model, prompt_text, completion_text, latency_ms, usage
        )
        return result

    def _wrap_async_stream(self, stream: AsyncIterable[Any], lpr_opts: dict,
                            model: str, prompt_text: str, t0: float) -> AsyncIterable[Any]:
        parent = self._parent

        async def gen():
            chunks: list[str] = []
            last_usage = None
            try:
                async for ev in stream:
                    try:
                        delta = ev.choices[0].delta
                        c = getattr(delta, "content", None)
                        if c:
                            chunks.append(c)
                    except Exception:
                        pass
                    u = getattr(ev, "usage", None)
                    if u is not None:
                        last_usage = u
                    yield ev
            finally:
                latency_ms = (time.monotonic() - t0) * 1000
                parent._emit_chat_receipt(
                    lpr_opts, model, prompt_text, "".join(chunks), latency_ms, last_usage
                )

        return gen()


class _AsyncChatProxy:
    def __init__(self, parent: "LedgerProofAsyncCerebras"):
        self.completions = _AsyncChatCompletionsProxy(parent)


class LedgerProofAsyncCerebras:
    """Async drop-in wrapper around `cerebras.cloud.sdk.AsyncCerebras`."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        lpr_signing_key_path: Optional[Union[str, os.PathLike]] = None,
        lpr_signer: Optional[Ed25519Signer] = None,
        lpr_deployer_id: str,
        lpr_sink: Optional[ReceiptSink] = None,
        lpr_emitter: Optional[AsyncEmitter] = None,
        **cerebras_kwargs: Any,
    ):
        if lpr_signer is None and lpr_signing_key_path is None:
            lpr_signer = Ed25519Signer.generate()
        elif lpr_signer is None:
            lpr_signer = load_signer_from_pem(lpr_signing_key_path)  # type: ignore[arg-type]

        self._inner = AsyncCerebras(api_key=api_key, **cerebras_kwargs)
        self._signer = lpr_signer
        self._deployer_id = lpr_deployer_id
        self._emitter = lpr_emitter or AsyncEmitter(lpr_sink or default_sink_from_env())

        self.chat = _AsyncChatProxy(self)

    @property
    def raw(self) -> AsyncCerebras:
        return self._inner

    @property
    def signer(self) -> Ed25519Signer:
        return self._signer

    def flush(self, timeout: float = 5.0) -> None:
        self._emitter.flush(timeout)

    def close(self) -> None:
        self._emitter.close()

    def _emit_chat_receipt(self, lpr_opts: dict, model: str, prompt_text: str,
                            completion_text: str, latency_ms: float, usage: Any) -> None:
        schema_name = lpr_opts.get("schema")
        if schema_name is None:
            if _REASONING_MODEL_RE.search(str(model)):
                schema_name = ReceiptSchemaName.REASONING_DISTILLED_V1
            else:
                schema_name = ReceiptSchemaName.CHATBOT_SESSION_V1
        if isinstance(schema_name, str):
            schema_name = ReceiptSchemaName(schema_name)

        ts = int(time.time() * 1000)
        common = {"deployer_id": self._deployer_id, "model": model, "timestamp_unix_ms": ts}

        prompt_tokens = getattr(usage, "prompt_tokens", None) if usage else None
        completion_tokens = getattr(usage, "completion_tokens", None) if usage else None
        total_tokens = getattr(usage, "total_tokens", None) if usage else None
        reasoning_tokens = None
        if usage is not None:
            for attr in ("reasoning_tokens", "thinking_tokens",
                         "completion_tokens_reasoning"):
                v = getattr(usage, attr, None)
                if v is not None:
                    reasoning_tokens = v
                    break

        if schema_name == ReceiptSchemaName.CHATBOT_SESSION_V1:
            receipt = ChatbotSessionV1(
                **common,
                subject_id_hash=lpr_opts.get("subject_id_hash"),
                session_id_hash=lpr_opts.get("session_id_hash"),
                prompt_hash=lpr_opts.get("prompt_hash") or _sha256(prompt_text),
                completion_hash=_sha256(completion_text),
                disclosure_shown=bool(lpr_opts.get("disclosure_shown", False)),
            )
        elif schema_name == ReceiptSchemaName.WAFER_SCALE_INFERENCE_V1:
            tps = None
            if completion_tokens and latency_ms > 0:
                tps = completion_tokens / (latency_ms / 1000.0)
            receipt = WaferScaleInferenceV1(
                **common,
                inference_latency_ms=latency_ms,
                tokens_per_second=tps,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                hardware_class=lpr_opts.get("hardware_class") or "wafer-scale",
                prompt_hash=lpr_opts.get("prompt_hash") or _sha256(prompt_text),
                completion_hash=_sha256(completion_text),
            )
        elif schema_name == ReceiptSchemaName.REASONING_DISTILLED_V1:
            receipt = ReasoningDistilledV1(
                **common,
                reasoning_tokens=reasoning_tokens,
                completion_tokens=completion_tokens,
                prompt_tokens=prompt_tokens,
                total_tokens=total_tokens,
                inference_latency_ms=latency_ms,
                prompt_hash=lpr_opts.get("prompt_hash") or _sha256(prompt_text),
                completion_hash=_sha256(completion_text),
                disclosure_shown=bool(lpr_opts.get("disclosure_shown", False)),
            )
        else:
            receipt = GeneratedContentV1(
                **common,
                content_hash=_sha256(completion_text),
                marking_method=lpr_opts.get("marking_method"),
            )

        self._emitter.submit(build_signed_receipt(receipt, self._signer))
