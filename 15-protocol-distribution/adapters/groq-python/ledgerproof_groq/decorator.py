"""@lpr_track decorator for arbitrary Groq-using functions.

C6: stream-aware — if the wrapped function returns a generator/iterator
(as in `stream=True`), the receipt is emitted after the stream is fully
consumed, over the concatenated output.
"""

from __future__ import annotations

import functools
import hashlib
import inspect
import time
from typing import Any, Callable, Iterable, Optional

from .emitter import AsyncEmitter, build_signed_receipt, default_sink_from_env
from .schema import ReceiptSchemaName, resolve_schema
from .signer import Ed25519Signer


def _sha256(data: str) -> str:
    return "sha256:" + hashlib.sha256(data.encode("utf-8")).hexdigest()


def lpr_track(
    *,
    signer: Ed25519Signer,
    deployer_id: str,
    schema: str | ReceiptSchemaName = ReceiptSchemaName.GENERATED_CONTENT_V1,
    model: Optional[str] = None,
    emitter: Optional[AsyncEmitter] = None,
    extra_fields: Optional[dict[str, Any]] = None,
):
    """Decorator factory.

    The wrapped function may return either a concrete value or an iterable
    (streaming case). The receipt is emitted after completion in both cases.
    """

    em = emitter or AsyncEmitter(default_sink_from_env())

    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        is_coro = inspect.iscoroutinefunction(fn)
        schema_cls = resolve_schema(schema)

        def _emit(result_text: str, latency_ms: float) -> None:
            fields = {
                "deployer_id": deployer_id,
                "model": model or "unknown",
                "timestamp_unix_ms": int(time.time() * 1000),
            }
            if schema_cls.__name__ == "GeneratedContentV1":
                fields["content_hash"] = _sha256(result_text)
            elif schema_cls.__name__ == "LowLatencyInferenceV1":
                fields["inference_latency_ms"] = latency_ms
                fields["completion_hash"] = _sha256(result_text)
            elif schema_cls.__name__ == "ChatbotSessionV1":
                fields["completion_hash"] = _sha256(result_text)
            elif schema_cls.__name__ == "AudioTranscriptionV1":
                fields["audio_hash"] = _sha256("audio-placeholder")
                fields["transcript_hash"] = _sha256(result_text)
            if extra_fields:
                fields.update(extra_fields)
            receipt = schema_cls(**fields)
            em.submit(build_signed_receipt(receipt, signer))

        if is_coro:
            @functools.wraps(fn)
            async def awrapper(*args, **kwargs):
                t0 = time.monotonic()
                result = await fn(*args, **kwargs)
                latency_ms = (time.monotonic() - t0) * 1000
                _emit(str(result), latency_ms)
                return result
            return awrapper

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            t0 = time.monotonic()
            result = fn(*args, **kwargs)
            if isinstance(result, Iterable) and not isinstance(result, (str, bytes, dict, list)):
                # Stream-aware path (C6).
                def gen():
                    chunks: list[str] = []
                    try:
                        for item in result:
                            chunks.append(str(item))
                            yield item
                    finally:
                        latency_ms = (time.monotonic() - t0) * 1000
                        _emit("".join(chunks), latency_ms)
                return gen()
            latency_ms = (time.monotonic() - t0) * 1000
            _emit(str(result), latency_ms)
            return result

        return wrapper

    return deco
