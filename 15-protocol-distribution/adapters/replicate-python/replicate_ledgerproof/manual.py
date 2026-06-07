"""
Manual receipt emission for Replicate prediction-shaped objects.

Use when you call `replicate.run(...)` or `client.predictions.create(...)` and
want explicit control over receipt construction (e.g. mixed text/image outputs,
custom modality binding, batch hashing of multiple output files).
"""

from __future__ import annotations

import base64
import hashlib
import uuid
from typing import Any, BinaryIO, Iterable

from .canonical import canonical_encode, hash_bytes, hash_stream, hash_text
from .emitter import Emitter, LogEmitter
from .schema import (
    ContentRef,
    InputRef,
    ModelRef,
    OutputArtifactRef,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
)
from .signer import Ed25519Signer, Signer
from .version import __version__


def _default_regulatory_context() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="2",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def emit_receipt(
    *,
    deployer_id: str,
    model_ref: ModelRef | None = None,
    prediction: Any = None,
    schema: SchemaName = "generated_content/v1",
    regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    prompt_text: str | None = None,
    output_text: str | None = None,
    inputs: dict[str, Any] | None = None,
    output_artifacts: Iterable[OutputArtifactRef] | None = None,
    output_bytes: bytes | None = None,
    output_media_type: str | None = None,
    streaming: bool = False,
) -> dict[str, Any]:
    """
    Build, sign, and emit a receipt for a Replicate prediction.

    Returns the signed-receipt dict that was emitted (also returned for inspection
    by the caller — never injected into the Replicate response, per constraint C7).

    The caller may supply either:
      - `prediction` (a replicate.predictions object) — model + status inferred,
      - or `model_ref` (an explicit ModelRef) — for `replicate.run()` callers
        who only have the model coordinate string.
    """
    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    if regulatory_context is None:
        regulatory_context = _default_regulatory_context()
    elif isinstance(regulatory_context, dict):
        regulatory_context = RegulatoryContext(**regulatory_context)

    if model_ref is None:
        if prediction is None:
            raise ValueError("emit_receipt requires either model_ref or prediction")
        model_ref = build_model_ref_from_prediction(prediction)

    content_refs: list[ContentRef] = []
    if prompt_text is not None:
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(prompt_text).hex(),
                byte_length=len(prompt_text.encode("utf-8")),
                role="prompt",
            )
        )
    if output_text is not None:
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(output_text).hex(),
                byte_length=len(output_text.encode("utf-8")),
                role="output",
            )
        )

    input_refs = build_input_refs(inputs) if inputs else []

    artifacts: list[OutputArtifactRef] = list(output_artifacts or [])
    if output_bytes is not None:
        artifacts.append(
            OutputArtifactRef(
                sha256_hex=hash_bytes(output_bytes).hex(),
                byte_length=len(output_bytes),
                media_type=output_media_type,
            )
        )

    receipt = ReceiptV1(
        schema=schema,
        receipt_id=str(uuid.uuid4()),
        deployer_id=deployer_id,
        model=model_ref,
        content_refs=content_refs,
        input_refs=input_refs,
        output_artifacts=artifacts,
        regulatory_context=regulatory_context,
        streaming=streaming,
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
# Helpers — model reference construction
# ---------------------------------------------------------------------------


def parse_model_coordinate(coord: str) -> tuple[str, str | None]:
    """
    Split a Replicate model coordinate into (model_id, version) parts.

        "stability-ai/sdxl:39ed52f2..."  -> ("stability-ai/sdxl", "39ed52f2...")
        "black-forest-labs/flux-schnell" -> ("black-forest-labs/flux-schnell", None)
    """
    if ":" in coord:
        author_name, version = coord.split(":", 1)
        return author_name, version
    return coord, None


def build_model_ref_from_coordinate(
    coord: str,
    *,
    prediction_id: str | None = None,
    status: str | None = None,
    predict_time_seconds: float | None = None,
) -> ModelRef:
    """Build a ModelRef from a `replicate.run("author/name:version", ...)` string."""
    model_id, version = parse_model_coordinate(coord)
    return ModelRef(
        model_id=model_id,
        model_version=version,
        prediction_id=prediction_id or "unknown",
        status=status,
        predict_time_seconds=predict_time_seconds,
    )


def build_model_ref_from_prediction(prediction: Any) -> ModelRef:
    """
    Inspect a replicate.predictions object (or compatible duck) and pull out
    model identity, version, prediction id, and timing.
    """
    pred_id = (
        getattr(prediction, "id", None)
        or _dict_get(prediction, "id")
        or "unknown"
    )
    # The Replicate SDK exposes `.model` (author/name) and `.version` (hash).
    model_id_raw = (
        getattr(prediction, "model", None)
        or _dict_get(prediction, "model")
    )
    version = (
        getattr(prediction, "version", None)
        or _dict_get(prediction, "version")
    )
    status = (
        getattr(prediction, "status", None)
        or _dict_get(prediction, "status")
    )
    metrics = (
        getattr(prediction, "metrics", None)
        or _dict_get(prediction, "metrics")
    )
    predict_time = None
    if metrics is not None:
        predict_time = (
            getattr(metrics, "predict_time", None)
            or _dict_get(metrics, "predict_time")
        )
    # Some predictions return only "author/name:version" as a single string.
    if isinstance(model_id_raw, str) and ":" in model_id_raw and not version:
        model_id, parsed_version = parse_model_coordinate(model_id_raw)
        version = parsed_version
    else:
        model_id = str(model_id_raw) if model_id_raw else "unknown/unknown"
        # Pydantic will reject "unknown/unknown" without slash, so default ok.
    return ModelRef(
        model_id=str(model_id) if model_id else "unknown/unknown",
        model_version=str(version) if version else None,
        prediction_id=str(pred_id),
        status=str(status) if status else None,
        predict_time_seconds=float(predict_time) if predict_time is not None else None,
    )


def _dict_get(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(key)
    return None


# ---------------------------------------------------------------------------
# Helpers — input hashing
# ---------------------------------------------------------------------------


def build_input_refs(inputs: dict[str, Any]) -> list[InputRef]:
    """
    Hash each scalar/text input parameter individually. Binary file inputs
    (paths, URLs) are detected heuristically and tagged as such.

    GDPR: prompt text is NEVER stored — only its SHA-256.
    """
    refs: list[InputRef] = []
    for name, value in inputs.items():
        if value is None:
            continue
        encoded, input_type = _encode_input_value(value)
        refs.append(
            InputRef(
                name=str(name)[:128],
                sha256_hex=hashlib.sha256(encoded).hexdigest(),
                byte_length=len(encoded),
                input_type=input_type,
            )
        )
    return refs


def _encode_input_value(value: Any) -> tuple[bytes, str]:
    """Convert a Replicate input value to canonical bytes plus a type tag."""
    if isinstance(value, bool):
        return (b"true" if value else b"false"), "boolean"
    if isinstance(value, (int, float)):
        return repr(value).encode("utf-8"), "number"
    if isinstance(value, str):
        # Heuristic: a URL or filepath is a file-shaped input on Replicate.
        if value.startswith(("http://", "https://", "data:", "/", "file://")):
            return value.encode("utf-8"), "file"
        return value.encode("utf-8"), "text"
    if isinstance(value, (bytes, bytearray)):
        return bytes(value), "file"
    # Anything else: JSON-encode deterministically via canonical CBOR digest.
    try:
        return canonical_encode(value if isinstance(value, dict) else {"_v": value}), "json"
    except Exception:
        return repr(value).encode("utf-8"), "json"


# ---------------------------------------------------------------------------
# Helpers — output artifact hashing
# ---------------------------------------------------------------------------


def hash_image_bytes(
    image_bytes: bytes,
    *,
    media_type: str = "image/png",
    width_px: int | None = None,
    height_px: int | None = None,
    output_uri: str | None = None,
) -> OutputArtifactRef:
    """Build an OutputArtifactRef for an in-memory image."""
    return OutputArtifactRef(
        sha256_hex=hash_bytes(image_bytes).hex(),
        byte_length=len(image_bytes),
        media_type=media_type,
        width_px=width_px,
        height_px=height_px,
        output_uri=output_uri,
    )


def hash_audio_bytes(
    audio_bytes: bytes,
    *,
    media_type: str = "audio/wav",
    duration_seconds: float | None = None,
    sample_rate_hz: int | None = None,
    output_uri: str | None = None,
) -> OutputArtifactRef:
    """Build an OutputArtifactRef for an in-memory audio clip."""
    return OutputArtifactRef(
        sha256_hex=hash_bytes(audio_bytes).hex(),
        byte_length=len(audio_bytes),
        media_type=media_type,
        duration_seconds=duration_seconds,
        sample_rate_hz=sample_rate_hz,
        output_uri=output_uri,
    )


def hash_video_bytes(
    video_bytes: bytes,
    *,
    media_type: str = "video/mp4",
    duration_seconds: float | None = None,
    frame_count: int | None = None,
    frames_per_second: float | None = None,
    width_px: int | None = None,
    height_px: int | None = None,
    output_uri: str | None = None,
) -> OutputArtifactRef:
    """Build an OutputArtifactRef for an in-memory video clip."""
    return OutputArtifactRef(
        sha256_hex=hash_bytes(video_bytes).hex(),
        byte_length=len(video_bytes),
        media_type=media_type,
        duration_seconds=duration_seconds,
        frame_count=frame_count,
        frames_per_second=frames_per_second,
        width_px=width_px,
        height_px=height_px,
        output_uri=output_uri,
    )


def hash_file_output(
    stream: BinaryIO,
    *,
    media_type: str | None = None,
    output_uri: str | None = None,
    **modality_kwargs: Any,
) -> OutputArtifactRef:
    """
    Stream-hash a Replicate FileOutput (constraint C6) without loading the
    full artifact into memory. Useful for multi-minute MusicGen audio or
    multi-megabyte ZeroScope video.
    """
    digest, total = hash_stream(stream)
    return OutputArtifactRef(
        sha256_hex=digest.hex(),
        byte_length=total,
        media_type=media_type,
        output_uri=output_uri,
        **modality_kwargs,
    )
