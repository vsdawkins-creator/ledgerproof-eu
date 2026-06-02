"""
Manual receipt emission. Use for full control over when and how a receipt fires,
for example inside a custom orchestration layer, a Lambda handler, or a
non-standard Bedrock call shape.

Bedrock response shapes vary significantly per upstream provider; helpers here
cover the most common ones (Claude, Llama, Mistral, Titan, Cohere, AI21) plus
the unified Converse API.
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
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
    ToolUseRef,
    infer_provider,
    is_eu_region,
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
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    schema: SchemaName = "chatbot_session/v1",
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    user_message_text: str | None = None,
    streaming: bool = False,
    tool_uses: list[ToolUseRef] | None = None,
    residency: DataResidencyAttestation | dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build, sign, and emit a receipt for a Bedrock response.

    `response` may be:
      - the dict returned by boto3 client.invoke_model (already-decoded JSON body)
      - the dict returned by client.converse
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

    model_ref = build_model_ref(response, model_id_hint=model_id, region_hint=region)

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
# Bedrock-specific extraction helpers
# ---------------------------------------------------------------------------


def extract_assistant_text(response: Any) -> str | None:
    """
    Pull plain text out of a Bedrock response, across providers.

    Handles:
      - Converse API:    response["output"]["message"]["content"][i]["text"]
      - Claude-on-Bedrock: response["content"][i]["text"]  (invoke_model body)
      - Llama / Mistral:   response["generation"] or response["outputs"][i]["text"]
      - Titan:             response["results"][i]["outputText"]
      - Cohere:            response["generations"][i]["text"] or response["text"]
      - AI21:              response["completions"][i]["data"]["text"]
    """
    if response is None:
        return None
    if not isinstance(response, dict):
        # Tolerate Pydantic-like objects.
        try:
            return extract_assistant_text(dict(response))
        except Exception:
            return None

    # Converse API
    output = response.get("output")
    if isinstance(output, dict):
        msg = output.get("message")
        if isinstance(msg, dict):
            blocks = msg.get("content") or []
            chunks = [b.get("text", "") for b in blocks if isinstance(b, dict) and "text" in b]
            if chunks:
                return "".join(chunks)

    # Claude (invoke_model body)
    content = response.get("content")
    if isinstance(content, list):
        chunks = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        if chunks:
            return "".join(chunks)

    # Llama (single string)
    if isinstance(response.get("generation"), str):
        return response["generation"]

    # Mistral (outputs list)
    outs = response.get("outputs")
    if isinstance(outs, list):
        chunks = [o.get("text", "") for o in outs if isinstance(o, dict)]
        if chunks:
            return "".join(chunks)

    # Titan
    results = response.get("results")
    if isinstance(results, list):
        chunks = [r.get("outputText", "") for r in results if isinstance(r, dict)]
        if chunks:
            return "".join(chunks)

    # Cohere
    gens = response.get("generations")
    if isinstance(gens, list):
        chunks = [g.get("text", "") for g in gens if isinstance(g, dict)]
        if chunks:
            return "".join(chunks)
    if isinstance(response.get("text"), str):
        return response["text"]

    # AI21
    comps = response.get("completions")
    if isinstance(comps, list):
        chunks = []
        for c in comps:
            data = c.get("data") if isinstance(c, dict) else None
            if isinstance(data, dict) and isinstance(data.get("text"), str):
                chunks.append(data["text"])
        if chunks:
            return "".join(chunks)

    return None


def build_model_ref(
    response: Any,
    *,
    model_id_hint: str | None = None,
    region_hint: str | None = None,
) -> ModelRef:
    """Build a ModelRef from a Bedrock response, with optional hints."""
    response_id = "unknown"
    stop_reason = None
    input_tokens = None
    output_tokens = None
    model_id = model_id_hint or "unknown"

    if isinstance(response, dict):
        # Converse usage
        usage = response.get("usage")
        if isinstance(usage, dict):
            input_tokens = usage.get("inputTokens") or usage.get("input_tokens")
            output_tokens = usage.get("outputTokens") or usage.get("output_tokens")

        # Stop / finish reason
        stop_reason = (
            response.get("stopReason")
            or response.get("stop_reason")
            or response.get("finish_reason")
        )

        # Best-effort response ID surfaces
        response_id = (
            response.get("ResponseMetadata", {}).get("RequestId")
            if isinstance(response.get("ResponseMetadata"), dict)
            else None
        ) or response.get("id") or response.get("response_id") or "unknown"

        # If the response didn't carry an id but the model is embedded.
        if model_id_hint is None and isinstance(response.get("model"), str):
            model_id = response["model"]

    return ModelRef(
        provider="bedrock",
        upstream_provider=infer_provider(model_id),
        model_id=str(model_id)[:256],
        response_id=str(response_id)[:256],
        region=region_hint,
        stop_reason=str(stop_reason)[:64] if stop_reason else None,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def extract_tool_uses(response: Any) -> list[ToolUseRef]:
    """
    Pull Converse-style toolUse blocks out of a Bedrock response.

    Converse shape:
      response["output"]["message"]["content"][i] = {
        "toolUse": {"toolUseId": "...", "name": "...", "input": {...}}
      }
    """
    refs: list[ToolUseRef] = []
    if not isinstance(response, dict):
        return refs
    output = response.get("output")
    if not isinstance(output, dict):
        return refs
    msg = output.get("message")
    if not isinstance(msg, dict):
        return refs
    for block in msg.get("content") or []:
        if not isinstance(block, dict):
            continue
        tu = block.get("toolUse")
        if not isinstance(tu, dict):
            continue
        name = str(tu.get("name") or "unknown")[:128]
        tu_id = str(tu.get("toolUseId") or "unknown")[:256]
        raw_input = tu.get("input") or {}
        try:
            input_bytes = canonical_encode(raw_input) if isinstance(raw_input, dict) else str(raw_input).encode()
        except Exception:
            input_bytes = repr(raw_input).encode("utf-8")
        refs.append(
            ToolUseRef(
                tool_name=name,
                tool_use_id=tu_id,
                input_sha256_hex=hashlib.sha256(input_bytes).hexdigest(),
            )
        )
    return refs


def extract_user_message_text_from_converse(
    messages: list[dict[str, Any]] | None,
) -> str:
    """Best-effort concatenation of user-role text from a Converse messages list."""
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


def extract_user_message_text_from_invoke_body(body_json_str: str) -> str:
    """Best-effort user-text extraction from an invoke_model JSON body string."""
    if not body_json_str:
        return ""
    try:
        body = json.loads(body_json_str)
    except (TypeError, ValueError):
        return ""
    if not isinstance(body, dict):
        return ""

    # Claude messages
    msgs = body.get("messages")
    if isinstance(msgs, list):
        parts: list[str] = []
        for m in msgs:
            if not isinstance(m, dict) or m.get("role") != "user":
                continue
            content = m.get("content")
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        parts.append(str(block.get("text", "")))
        if parts:
            return "\n".join(parts)

    # Llama / generic prompt field
    for k in ("prompt", "inputText", "input_text"):
        if isinstance(body.get(k), str):
            return body[k]

    return ""


def make_eu_residency_attestation(
    region: str | None,
    *,
    sccs_in_place: bool | None = None,
    notes: str | None = None,
) -> DataResidencyAttestation:
    """Helper: build a residency attestation for an eu_aws_data_residency receipt."""
    region = (region or "unknown").lower()
    return DataResidencyAttestation(
        attested_region=region,
        eu_region=is_eu_region(region),
        cross_border_transfer=False,
        sccs_in_place=sccs_in_place,
        notes=notes,
    )
