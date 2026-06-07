"""
Manual receipt emission. Use for full control over when and how a receipt
fires — for example inside a custom orchestration layer, a serverless function,
or a non-standard watsonx call shape.

watsonx.ai response shapes follow an OpenAI-compatible chat-completion
structure, with `choices[i].message.content` for non-streaming and
`choices[i].delta.content` for streaming. Helpers here cover both, plus
the `generate_text(...)` legacy shape.
"""

from __future__ import annotations

import base64
import hashlib
import json
import uuid
from typing import Any

from .canonical import canonical_encode, hash_text
from .emitter import Emitter, LogEmitter
from .schema import (
    ContentRef,
    DataResidencyAttestation,
    ModelRef,
    OpenWeightsAttestation,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
    ToolUseRef,
    infer_provider,
    is_eu_region,
    is_granite_open_model,
)
from .signer import Ed25519Signer, Signer
from .version import __version__


def _default_regulatory_context() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="1",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def emit_receipt(
    response: Any,
    deployer_id: str,
    *,
    model_id: str | None = None,
    region: str | None = None,
    project_id: str | None = None,
    space_id: str | None = None,
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    schema: SchemaName = "chatbot_session/v1",
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    user_message_text: str | None = None,
    streaming: bool = False,
    tool_uses: list[ToolUseRef] | None = None,
    residency: DataResidencyAttestation | dict[str, Any] | None = None,
    open_weights: OpenWeightsAttestation | dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build, sign, and emit a receipt for a watsonx.ai response.

    `response` may be:
      - the dict returned by `ModelInference.chat(messages=...)`
      - the dict returned by `ModelInference.generate_text(prompt=...)`
      - any custom shape — pass model_id and region explicitly to override.

    Returns the signed-receipt dict that was emitted (never injected into
    `response`, per constraint C7).
    """
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    if regulatory_context is None:
        regulatory_context = _default_regulatory_context()
    elif isinstance(regulatory_context, dict):
        regulatory_context = RegulatoryContext(**regulatory_context)

    if isinstance(residency, dict):
        residency = DataResidencyAttestation(**residency)
    if isinstance(open_weights, dict):
        open_weights = OpenWeightsAttestation(**open_weights)

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

    model_ref = build_model_ref(
        response,
        model_id_hint=model_id,
        region_hint=region,
        project_id_hint=project_id,
        space_id_hint=space_id,
    )

    # If the caller didn't pass an open_weights attestation but the model is
    # a Granite open-weights model AND the schema is granite_open_model, fill
    # in a default attestation so the receipt is self-consistent.
    if (
        open_weights is None
        and schema == "granite_open_model/v1"
        and is_granite_open_model(model_ref.model_id)
    ):
        open_weights = OpenWeightsAttestation(
            model_family="ibm-granite",
            license_spdx="Apache-2.0",
            weights_url=None,
            reproducible=True,
        )

    receipt = ReceiptV1(
        schema=schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        model=model_ref,
        content_refs=content_refs,
        regulatory_context=regulatory_context,
        tool_uses=tool_uses or [],
        streaming=streaming,
        residency=residency,
        open_weights=open_weights,
        adapter_version=__version__,
    )

    payload = receipt.to_payload()
    canonical_bytes = canonical_encode(payload)
    signature = signer.sign(canonical_bytes)

    signed = {
        "receipt": payload,
        "signature_alg": "ed25519",
        "signature_b64": base64.b64encode(signature).decode("ascii"),
        "signer_key_id": signer.key_id,
        "canonical_encoding": "cbor-rfc8949-deterministic",
    }
    emitter.emit(signed)
    return signed


# ---------------------------------------------------------------------------
# watsonx-specific extraction helpers
# ---------------------------------------------------------------------------


def extract_assistant_text(response: Any) -> str | None:
    """
    Pull plain text out of a watsonx.ai response.

    Handles:
      - chat (OpenAI-compatible):   response["choices"][i]["message"]["content"]
      - chat (content blocks list): response["choices"][i]["message"]["content"]
                                    where content is a list of {"type":"text","text":"..."} dicts
      - generate_text:              response["results"][i]["generated_text"]
      - generate_text (single):     response["generated_text"]
    """
    if response is None:
        return None
    if not isinstance(response, dict):
        try:
            return extract_assistant_text(dict(response))
        except Exception:
            return None

    # Chat-completions shape
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        chunks: list[str] = []
        for ch in choices:
            if not isinstance(ch, dict):
                continue
            msg = ch.get("message") or ch.get("delta") or {}
            if not isinstance(msg, dict):
                continue
            content = msg.get("content")
            if isinstance(content, str):
                chunks.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and isinstance(block.get("text"), str):
                        chunks.append(block["text"])
        if chunks:
            return "".join(chunks)

    # generate_text (multi)
    results = response.get("results")
    if isinstance(results, list):
        chunks = [
            r.get("generated_text", "")
            for r in results
            if isinstance(r, dict) and isinstance(r.get("generated_text"), str)
        ]
        if chunks:
            return "".join(chunks)

    # generate_text (single)
    if isinstance(response.get("generated_text"), str):
        return response["generated_text"]

    return None


def build_model_ref(
    response: Any,
    *,
    model_id_hint: str | None = None,
    region_hint: str | None = None,
    project_id_hint: str | None = None,
    space_id_hint: str | None = None,
) -> ModelRef:
    """Build a ModelRef from a watsonx.ai response, with optional hints."""
    response_id = "unknown"
    stop_reason = None
    input_tokens = None
    output_tokens = None
    model_id = model_id_hint or "unknown"

    if isinstance(response, dict):
        # OpenAI-style usage
        usage = response.get("usage")
        if isinstance(usage, dict):
            input_tokens = (
                usage.get("prompt_tokens")
                or usage.get("input_tokens")
                or usage.get("inputTokens")
            )
            output_tokens = (
                usage.get("completion_tokens")
                or usage.get("output_tokens")
                or usage.get("generated_token_count")
            )

        # Stop / finish reason
        choices = response.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                stop_reason = (
                    first.get("finish_reason")
                    or first.get("stop_reason")
                )
        # generate_text shape
        if stop_reason is None:
            results = response.get("results")
            if isinstance(results, list) and results and isinstance(results[0], dict):
                stop_reason = results[0].get("stop_reason")

        response_id = (
            response.get("id")
            or response.get("response_id")
            or response.get("trace_id")
            or "unknown"
        )

        if model_id_hint is None and isinstance(response.get("model_id"), str):
            model_id = response["model_id"]
        elif model_id_hint is None and isinstance(response.get("model"), str):
            model_id = response["model"]

    return ModelRef(
        provider="watsonx",
        upstream_provider=infer_provider(model_id),
        model_id=str(model_id)[:256],
        response_id=str(response_id)[:256],
        region=region_hint,
        project_id=project_id_hint,
        space_id=space_id_hint,
        stop_reason=str(stop_reason)[:64] if stop_reason else None,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        is_open_weights=is_granite_open_model(model_id),
    )


def extract_tool_uses(response: Any) -> list[ToolUseRef]:
    """
    Pull tool-call blocks out of a watsonx.ai chat response.

    OpenAI-compatible shape:
      response["choices"][i]["message"]["tool_calls"] = [
        {"id": "...", "type": "function",
         "function": {"name": "...", "arguments": "<json string>"}},
        ...
      ]
    """
    refs: list[ToolUseRef] = []
    if not isinstance(response, dict):
        return refs
    choices = response.get("choices")
    if not isinstance(choices, list):
        return refs
    for choice in choices:
        if not isinstance(choice, dict):
            continue
        msg = choice.get("message") or {}
        if not isinstance(msg, dict):
            continue
        for tc in msg.get("tool_calls") or []:
            if not isinstance(tc, dict):
                continue
            fn = tc.get("function") or {}
            name = str(fn.get("name") or "unknown")[:128]
            tu_id = str(tc.get("id") or "unknown")[:256]
            raw_args = fn.get("arguments")
            if isinstance(raw_args, str):
                input_bytes = raw_args.encode("utf-8")
            else:
                try:
                    input_bytes = canonical_encode(raw_args) if isinstance(raw_args, dict) else repr(raw_args).encode("utf-8")
                except Exception:
                    input_bytes = repr(raw_args).encode("utf-8")
            refs.append(
                ToolUseRef(
                    tool_name=name,
                    tool_use_id=tu_id,
                    input_sha256_hex=hashlib.sha256(input_bytes).hexdigest(),
                )
            )
    return refs


def extract_user_message_text(messages: list[dict[str, Any]] | None) -> str:
    """Best-effort concatenation of user-role text from a chat messages list."""
    if not messages:
        return ""
    parts: list[str] = []
    for msg in messages:
        if msg.get("role") != "user":
            continue
        content = msg.get("content")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    parts.append(block["text"])
    return "\n".join(parts)


def extract_user_prompt_from_generate(prompt: Any) -> str:
    """Best-effort: pull user text out of a generate_text prompt argument."""
    if isinstance(prompt, str):
        return prompt
    if isinstance(prompt, list):
        return "\n".join(p for p in prompt if isinstance(p, str))
    return ""


def make_eu_residency_attestation(
    region: str | None,
    *,
    project_id: str | None = None,
    tenant_id: str | None = None,
    sccs_in_place: bool | None = None,
    notes: str | None = None,
) -> DataResidencyAttestation:
    """Build a residency attestation for an eu_data_residency receipt."""
    region = (region or "unknown").lower()
    return DataResidencyAttestation(
        attested_region=region,
        eu_region=is_eu_region(region),
        cross_border_transfer=False,
        sccs_in_place=sccs_in_place,
        tenant_id=tenant_id,
        notes=notes,
    )


def make_granite_attestation(
    *,
    model_id: str | None = None,
    weights_url: str | None = None,
    notes: str | None = None,
) -> OpenWeightsAttestation:
    """
    Build an open-weights attestation for an IBM Granite invocation.

    Default `weights_url` points to the Hugging Face org for Granite when
    `model_id` matches a known Granite ID.
    """
    if weights_url is None and model_id and is_granite_open_model(model_id):
        # Best-effort guess at the HF URL. Deployer may override.
        weights_url = f"https://huggingface.co/{model_id.replace('ibm/', 'ibm-granite/')}"
    return OpenWeightsAttestation(
        model_family="ibm-granite",
        license_spdx="Apache-2.0",
        weights_url=weights_url,
        reproducible=True,
        notes=notes,
    )
