"""@lpr_track decorator for plain functions / kernel-functions.

The filters and chat-service wrapper handle the standard SK paths. Use
`@lpr_track` for ad-hoc Python functions (e.g. a `@kernel_function`-
decorated helper you also want to call directly from Python) — it emits an
`agent_function_invocation/v1` receipt around each call.

Both sync and async functions are supported. The decorator does NOT record
argument values; only argument *names*.
"""

from __future__ import annotations

import asyncio
import base64
import functools
import hashlib
import inspect
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, TypeVar

from .canonical import canonical_encode
from .emitter import BaseEmitter, LogEmitter
from .schema import get_schema
from .signer import BaseSigner, Ed25519Signer

F = TypeVar("F", bound=Callable[..., Any])


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )


def lpr_track(
    *,
    deployer_id: str,
    plugin_name: str = "user",
    emitter: Optional[BaseEmitter] = None,
    signer: Optional[BaseSigner] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """Decorator that emits a receipt around each call.

    The signer/emitter are resolved at decoration time and reused for every
    call. Argument values are not retained; only argument names.
    """
    _emitter: BaseEmitter = emitter or LogEmitter("./ledgerproof-receipts.jsonl")
    _signer: BaseSigner = signer or Ed25519Signer()
    _extra = dict(extra or {})

    def _emit(fn_name: str, arg_names: list[str], result_text: str) -> None:
        h = hashlib.sha256()
        h.update(b"lpr:v1:sk:fn\n")
        h.update(len(plugin_name).to_bytes(8, "big"))
        h.update(plugin_name.encode("utf-8"))
        h.update(len(fn_name).to_bytes(8, "big"))
        h.update(fn_name.encode("utf-8"))
        h.update(b"lpr:v1:sk:result\n")
        rb = result_text.encode("utf-8")
        h.update(len(rb).to_bytes(8, "big"))
        h.update(rb)

        fields: Dict[str, Any] = {
            "schema_id": "agent_function_invocation/v1",
            "run_id": str(uuid.uuid4()),
            "timestamp_utc": _utc_now(),
            "deployer_id": deployer_id,
            "transcript_sha256": h.hexdigest(),
            "plugin_name": plugin_name,
            "function_name": fn_name,
            "argument_names": arg_names,
            "is_auto_invoked": False,
        }
        fields.update(_extra)

        try:
            validated = get_schema("agent_function_invocation/v1")(
                **fields
            ).model_dump()
        except Exception:
            return
        body_bytes = canonical_encode(validated)
        body_digest = hashlib.sha256(body_bytes).digest()
        signature = _signer.sign(body_digest)
        envelope = {
            "body": validated,
            "body_sha256": body_digest.hex(),
            "signature_ed25519": base64.urlsafe_b64encode(signature)
            .rstrip(b"=")
            .decode("ascii"),
            "public_key_ed25519": _signer.public_key_b64(),
            "alg": "Ed25519",
        }
        try:
            _emitter.emit(envelope)
        except Exception:
            pass

    def decorate(func: F) -> F:
        sig = inspect.signature(func)
        fn_name = func.__name__

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def awrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    bound = sig.bind_partial(*args, **kwargs)
                    arg_names = list(bound.arguments.keys())
                except Exception:
                    arg_names = []
                result = await func(*args, **kwargs)
                _emit(fn_name, arg_names, str(result))
                return result

            return awrapper  # type: ignore[return-value]

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                bound = sig.bind_partial(*args, **kwargs)
                arg_names = list(bound.arguments.keys())
            except Exception:
                arg_names = []
            result = func(*args, **kwargs)
            _emit(fn_name, arg_names, str(result))
            return result

        return wrapper  # type: ignore[return-value]

    return decorate
