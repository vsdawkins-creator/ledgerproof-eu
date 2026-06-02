"""Wrapper for `transformers.Pipeline` — local model inference.

Use `LedgerProofPipeline` when you're running a model locally (self-hosted,
on-prem, air-gapped) using the `transformers` library directly. The receipt
captures `local_inference/v1` by default — it records the host environment
so on-prem deployers can demonstrate the inference ran inside their
controlled perimeter.

Constraint **C7**: the pipeline output is returned unmodified.
"""

from __future__ import annotations

import hashlib
import json
import platform
import socket
import uuid
from typing import Any

from .emitter import Emitter, LogEmitter
from .inference_client_wrapper import _SignedReceiptBuilder
from .signer import Ed25519Signer, Signer


def _default_host_environment() -> dict[str, Any]:
    """Best-effort host fingerprint for on-prem audit trails.

    Pure stdlib — no `torch`/`psutil` dependency. Production deployers may
    enrich this via `regulatory_context["host_environment"]`.
    """
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
    }


def _hash_prompt(prompt: Any) -> str:
    """Hash the prompt argument passed to a transformers pipeline call.

    The pipeline call accepts a `str`, a `list[str]`, or for chat models a
    list of message dicts. We canonicalize via JSON for compound inputs.
    """
    if isinstance(prompt, str):
        payload = prompt.encode("utf-8")
    else:
        payload = json.dumps(prompt, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hash_pipeline_output(result: Any) -> str:
    """Extract and hash the generated text from a transformers pipeline output.

    `text-generation` returns a list of dicts with `generated_text`.
    `text2text-generation` returns a list of dicts with `generated_text`.
    `conversational` returns Conversation objects (older versions).
    For unknown shapes we fall back to canonical JSON.
    """
    parts: list[str] = []
    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict):
                t = item.get("generated_text")
                if isinstance(t, str):
                    parts.append(t)
                elif isinstance(t, list):
                    # chat-format output is a list of message dicts
                    for msg in t:
                        if isinstance(msg, dict):
                            c = msg.get("content")
                            if isinstance(c, str):
                                parts.append(c)
                else:
                    s = item.get("summary_text") or item.get("translation_text")
                    if isinstance(s, str):
                        parts.append(s)
            elif isinstance(item, str):
                parts.append(item)
    elif isinstance(result, dict):
        t = result.get("generated_text")
        if isinstance(t, str):
            parts.append(t)
    elif isinstance(result, str):
        parts.append(result)

    if not parts:
        # Last resort: canonical JSON of whatever shape we got
        payload = json.dumps(result, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()
    return hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()


class LedgerProofPipeline:
    """Wraps a `transformers.Pipeline` instance.

    Same call surface — `lp_pipe(prompt, ...)` — but emits a signed
    `local_inference/v1` receipt as a side channel each time the pipeline
    is invoked.

    Parameters
    ----------
    pipeline:
        A `transformers.Pipeline` (typically returned by
        `transformers.pipeline("text-generation", model=...)`).
    deployer_id:
        URN identifying the deployer organisation.
    regulatory_context:
        Optional dict. Defaults to `{"schema": "local_inference/v1"}`. You
        may override the schema (e.g. `"chatbot_session/v1"`), or supply
        `host_environment`, `device`, `task` to augment the receipt.
    signer / emitter:
        Optional plug-ins. Defaults match the InferenceClient wrapper.
    """

    def __init__(
        self,
        pipeline: Any,
        deployer_id: str,
        *,
        regulatory_context: dict[str, Any] | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
    ) -> None:
        self._pipeline = pipeline
        ctx: dict[str, Any] = dict(regulatory_context or {})
        ctx.setdefault("schema", "local_inference/v1")
        # Pre-fill schema-specific defaults from the pipeline itself
        if "host_environment" not in ctx:
            ctx["host_environment"] = _default_host_environment()
        if "task" not in ctx:
            ctx["task"] = getattr(pipeline, "task", None)
        if "device" not in ctx:
            device = getattr(pipeline, "device", None)
            ctx["device"] = str(device) if device is not None else None
        self._builder = _SignedReceiptBuilder(
            deployer_id=deployer_id,
            regulatory_context=ctx,
            signer=signer or Ed25519Signer(),
            emitter=emitter or LogEmitter(),
        )

    # ------------------------------------------------------------------ call
    def __call__(self, prompt: Any, *args: Any, **kwargs: Any) -> Any:
        result = self._pipeline(prompt, *args, **kwargs)
        try:
            model_id = (
                getattr(getattr(self._pipeline, "model", None), "name_or_path", None)
                or getattr(self._pipeline, "model_name", None)
                or "unknown"
            )
            self._builder.emit(
                model_id=str(model_id),
                interaction_id=str(uuid.uuid4()),
                prompt_sha256=_hash_prompt(prompt),
                response_sha256=_hash_pipeline_output(result),
            )
        except Exception:  # noqa: BLE001
            # C7
            pass
        return result

    # ----------------------------------------------------- attribute passthrough
    def __getattr__(self, name: str) -> Any:
        return getattr(self._pipeline, name)
