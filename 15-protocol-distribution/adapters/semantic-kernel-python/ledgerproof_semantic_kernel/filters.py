"""Semantic Kernel filters that emit LedgerProof transparency receipts.

Architectural invariants (do not violate):

  * Side-channel only (C7). The filters MUST NOT mutate function arguments
    or the function result. They observe, hash, and emit.
  * Stream-aware (C6). Where streaming is in play, the chat-service wrapper
    consumes tokens incrementally and hashes them as they pass; filters here
    digest the final FunctionResult.
  * Local verification only (C4). No regulator endpoint is contacted. The
    side channel is whatever BaseEmitter the deployer wires up.
  * Argument *values* are NEVER recorded. Only argument *names* are recorded
    in `agent_function_invocation/v1`. The transcript hash is the only place
    where argument content has any influence, and only as a one-way digest.

Two filters:

  * LedgerProofFunctionFilter        - implements FunctionInvocationFilter.
                                       Emits an `agent_function_invocation/v1`
                                       receipt for every kernel function call.
  * LedgerProofAutoFunctionFilter    - implements AutoFunctionInvocationFilter.
                                       Same receipt, with `is_auto_invoked=True`,
                                       for auto-function-calling agents.

Both filters degrade gracefully if Semantic Kernel is not installed, so the
package remains importable in environments that only need the manual or
schema helpers.
"""

from __future__ import annotations

import base64
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Optional

from .canonical import canonical_encode
from .emitter import BaseEmitter, LogEmitter
from .schema import get_schema
from .signer import BaseSigner, Ed25519Signer

# Semantic Kernel exposes filter base classes under
# `semantic_kernel.filters`. We import lazily and fall back to `object` so
# the module remains importable without SK installed (filters then raise
# clearly if they are actually used).
try:  # pragma: no cover - import shim
    from semantic_kernel.filters import (  # type: ignore[import-not-found]
        FunctionInvocationContext,
    )

    try:
        from semantic_kernel.filters import (  # type: ignore[import-not-found]
            AutoFunctionInvocationContext,
        )
    except ImportError:  # pragma: no cover
        AutoFunctionInvocationContext = Any  # type: ignore[misc,assignment]
    _SK_AVAILABLE = True
except ImportError:  # pragma: no cover
    FunctionInvocationContext = Any  # type: ignore[misc,assignment]
    AutoFunctionInvocationContext = Any  # type: ignore[misc,assignment]
    _SK_AVAILABLE = False


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )


def _result_text(result: Any) -> str:
    """Best-effort string projection of a Semantic Kernel FunctionResult."""
    if result is None:
        return ""
    # FunctionResult instances have `.value`; fall back to str().
    value = getattr(result, "value", result)
    if isinstance(value, (list, tuple)):
        return "".join(str(v) for v in value)
    return str(value)


def _safe_function_meta(context: Any) -> tuple[str, str, list[str]]:
    """Extract plugin, function, argument-name list from a filter context.

    Tolerant of minor SK API drift (function/function_metadata fields).
    Argument *values* are intentionally never read.
    """
    plugin = "unknown"
    function = "unknown"
    arg_names: list[str] = []

    fn = getattr(context, "function", None)
    meta = getattr(fn, "metadata", None) if fn is not None else None

    if meta is not None:
        plugin = getattr(meta, "plugin_name", None) or plugin
        function = getattr(meta, "name", None) or function
    elif fn is not None:
        plugin = getattr(fn, "plugin_name", None) or plugin
        function = getattr(fn, "name", None) or function

    args = getattr(context, "arguments", None)
    if args is not None:
        try:
            arg_names = list(args.keys())
        except Exception:
            arg_names = []

    return str(plugin), str(function), [str(n) for n in arg_names]


class _ReceiptCore:
    """Shared signing / emission logic for both filter classes."""

    def __init__(
        self,
        *,
        deployer_id: str,
        schema_id: str = "agent_function_invocation/v1",
        emitter: Optional[BaseEmitter] = None,
        signer: Optional[BaseSigner] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not _SK_AVAILABLE:
            raise ImportError(
                "semantic-kernel is not installed. "
                "Install with: pip install ledgerproof-semantic-kernel[sk]"
            )
        self.deployer_id = deployer_id
        self.schema_id = schema_id
        self.emitter: BaseEmitter = emitter or LogEmitter(
            "./ledgerproof-receipts.jsonl"
        )
        self.signer: BaseSigner = signer or Ed25519Signer()
        self.extra: Dict[str, Any] = dict(extra or {})

    def _build_and_emit(
        self,
        *,
        plugin: str,
        function: str,
        argument_names: list[str],
        result_text: str,
        is_auto_invoked: bool,
    ) -> None:
        # Stream-aware-style framing: domain-separator + length-prefixed chunks.
        h = hashlib.sha256()
        h.update(b"lpr:v1:sk:fn\n")
        h.update(len(plugin).to_bytes(8, "big"))
        h.update(plugin.encode("utf-8"))
        h.update(len(function).to_bytes(8, "big"))
        h.update(function.encode("utf-8"))
        h.update(b"lpr:v1:sk:result\n")
        rb = result_text.encode("utf-8")
        h.update(len(rb).to_bytes(8, "big"))
        h.update(rb)

        receipt_fields: Dict[str, Any] = {
            "schema_id": self.schema_id,
            "run_id": str(uuid.uuid4()),
            "timestamp_utc": _utc_now(),
            "deployer_id": self.deployer_id,
            "transcript_sha256": h.hexdigest(),
            "plugin_name": plugin,
            "function_name": function,
            "argument_names": argument_names,
            "is_auto_invoked": is_auto_invoked,
        }
        receipt_fields.update(self.extra)

        validated = get_schema(self.schema_id)(**receipt_fields).model_dump()
        body_bytes = canonical_encode(validated)
        body_digest = hashlib.sha256(body_bytes).digest()
        signature = self.signer.sign(body_digest)

        envelope: Dict[str, Any] = {
            "body": validated,
            "body_sha256": body_digest.hex(),
            "signature_ed25519": base64.urlsafe_b64encode(signature)
            .rstrip(b"=")
            .decode("ascii"),
            "public_key_ed25519": self.signer.public_key_b64(),
            "alg": "Ed25519",
        }
        self.emitter.emit(envelope)


class LedgerProofFunctionFilter(_ReceiptCore):
    """FunctionInvocationFilter: emit a receipt for each kernel function call.

    Wire into a Kernel via:

        kernel.add_filter("function_invocation", LedgerProofFunctionFilter(...))
    """

    async def on_function_invocation(
        self,
        context: "FunctionInvocationContext",
        next: Callable[["FunctionInvocationContext"], Awaitable[None]],
    ) -> None:
        await next(context)
        try:
            plugin, function, arg_names = _safe_function_meta(context)
            result_text = _result_text(getattr(context, "result", None))
            self._build_and_emit(
                plugin=plugin,
                function=function,
                argument_names=arg_names,
                result_text=result_text,
                is_auto_invoked=False,
            )
        except Exception:
            # Side-channel invariant: receipt failure must NEVER break the
            # function-invocation path. The deployer will see the function's
            # real result; receipt issues surface in the emitter's own
            # diagnostics.
            pass


class LedgerProofAutoFunctionFilter(_ReceiptCore):
    """AutoFunctionInvocationFilter: emit a receipt for each auto-invoked tool.

    Wire into a Kernel via:

        kernel.add_filter("auto_function_invocation",
                          LedgerProofAutoFunctionFilter(...))
    """

    async def on_auto_function_invocation(
        self,
        context: "AutoFunctionInvocationContext",
        next: Callable[["AutoFunctionInvocationContext"], Awaitable[None]],
    ) -> None:
        await next(context)
        try:
            plugin, function, arg_names = _safe_function_meta(context)
            result_text = _result_text(
                getattr(context, "function_result", None)
                or getattr(context, "result", None)
            )
            self._build_and_emit(
                plugin=plugin,
                function=function,
                argument_names=arg_names,
                result_text=result_text,
                is_auto_invoked=True,
            )
        except Exception:
            pass
