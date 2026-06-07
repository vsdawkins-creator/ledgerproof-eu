"""
Synchronous client wrapper around `replicate.Client`.

Intercepts `run()` and `stream()` to emit a receipt on the side channel
(constraint C7) after the prediction completes. The wrapped response is returned
unchanged.

Receipt schema is selected heuristically based on the model coordinate and the
output type:
  - text output (string, list of strings) -> chatbot_session/v1 OR generated_content/v1
  - FileOutput / URL output with image MIME -> synthetic_image/v1
  - FileOutput / URL output with audio MIME -> synthetic_audio/v1
  - FileOutput / URL output with video MIME -> synthetic_video/v1
The caller may force a specific schema via the `schema` constructor kwarg, or by
calling the modality-specific helpers (`run_image`, `run_audio`, `run_video`).
"""

from __future__ import annotations

import base64
import logging
import uuid
from typing import Any, Iterator

from .canonical import IncrementalTextHasher, canonical_encode, hash_bytes, hash_text
from .emitter import Emitter, LogEmitter
from .manual import (
    build_input_refs,
    build_model_ref_from_coordinate,
    build_model_ref_from_prediction,
)
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

logger = logging.getLogger(__name__)


_IMAGE_MIME_PREFIXES = ("image/",)
_AUDIO_MIME_PREFIXES = ("audio/",)
_VIDEO_MIME_PREFIXES = ("video/",)


def _default_reg_ctx() -> RegulatoryContext:
    return RegulatoryContext(
        article_50_paragraph="2",
        deployer_jurisdiction="EU",
        end_user_disclosure_made=True,
    )


def _guess_media_type_from_url(url: str) -> str | None:
    """Best-effort MIME inference from a Replicate output URL extension."""
    lower = url.lower().split("?", 1)[0]
    if lower.endswith((".png",)):
        return "image/png"
    if lower.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if lower.endswith((".webp",)):
        return "image/webp"
    if lower.endswith((".gif",)):
        return "image/gif"
    if lower.endswith((".mp3",)):
        return "audio/mpeg"
    if lower.endswith((".wav",)):
        return "audio/wav"
    if lower.endswith((".flac",)):
        return "audio/flac"
    if lower.endswith((".ogg", ".opus")):
        return "audio/ogg"
    if lower.endswith((".mp4",)):
        return "video/mp4"
    if lower.endswith((".webm",)):
        return "video/webm"
    if lower.endswith((".mov",)):
        return "video/quicktime"
    return None


def _schema_for_media_type(media_type: str | None) -> SchemaName | None:
    if media_type is None:
        return None
    if media_type.startswith(_IMAGE_MIME_PREFIXES):
        return "synthetic_image/v1"
    if media_type.startswith(_AUDIO_MIME_PREFIXES):
        return "synthetic_audio/v1"
    if media_type.startswith(_VIDEO_MIME_PREFIXES):
        return "synthetic_video/v1"
    return None


def _coerce_url(item: Any) -> str | None:
    """Replicate FileOutput exposes .url; some outputs are bare strings."""
    if isinstance(item, str) and item.startswith(("http://", "https://", "data:")):
        return item
    url = getattr(item, "url", None)
    if isinstance(url, str):
        return url
    # Some clients expose __str__ -> URL.
    try:
        s = str(item)
        if s.startswith(("http://", "https://", "data:")):
            return s
    except Exception:
        pass
    return None


class LedgerProofReplicateClient:
    """
    Drop-in wrapper for `replicate.Client`.

    Usage:
        import replicate
        from replicate_ledgerproof import LedgerProofReplicateClient

        client = LedgerProofReplicateClient(
            deployer_id="acme-eu",
            api_token="r8_...",
        )
        output = client.run(
            "black-forest-labs/flux-schnell",
            input={"prompt": "a serene mountain lake"},
        )

    All other attributes of the underlying replicate.Client are forwarded
    (`predictions`, `models`, `trainings`, etc.).
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        client: Any | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        regulatory_context: RegulatoryContext | dict[str, Any] | None = None,
        schema: SchemaName | None = None,
        api_token: str | None = None,
        **replicate_kwargs: Any,
    ):
        self.deployer_id = deployer_id
        if client is None:
            import replicate
            client = replicate.Client(api_token=api_token, **replicate_kwargs)
        self._inner = client
        self._signer: Signer = signer or Ed25519Signer()
        self._emitter: Emitter = emitter or LogEmitter()
        self._default_schema: SchemaName | None = schema
        if isinstance(regulatory_context, dict):
            regulatory_context = RegulatoryContext(**regulatory_context)
        self._reg_ctx: RegulatoryContext = regulatory_context or _default_reg_ctx()

    # ------------------------------------------------------------------
    # Pass-through to the underlying replicate.Client for any non-intercepted
    # attribute (predictions, models, trainings, hardware, deployments, ...).
    # ------------------------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    # ------------------------------------------------------------------
    # run() — synchronous, returns the model output
    # ------------------------------------------------------------------
    def run(
        self,
        ref: str,
        *,
        input: dict[str, Any] | None = None,
        schema_override: SchemaName | None = None,
        prompt_text_kwarg: str | None = "prompt",
        **kwargs: Any,
    ) -> Any:
        """
        Wrap `replicate.Client.run()`. Returns the model output unchanged.

        After the run completes, a receipt is built that binds:
          - model coordinate + version hash (from `ref`),
          - SHA-256 of each input parameter (from `input`),
          - SHA-256 of each output artifact when the output is a FileOutput / URL.
        """
        output = self._inner.run(ref, input=input, **kwargs)
        try:
            self._emit_for_run(
                ref=ref,
                input_dict=input or {},
                output=output,
                schema_override=schema_override,
                prompt_text_kwarg=prompt_text_kwarg,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("LedgerProof receipt emission failed: %s", exc)
        return output

    # ------------------------------------------------------------------
    # stream() — token-streaming for LLMs
    # ------------------------------------------------------------------
    def stream(
        self,
        ref: str,
        *,
        input: dict[str, Any] | None = None,
        schema_override: SchemaName | None = None,
        prompt_text_kwarg: str | None = "prompt",
        **kwargs: Any,
    ) -> Iterator[Any]:
        """
        Wrap `replicate.Client.stream()`. Yields stream events unchanged
        (constraint C7). After the stream completes, a receipt is emitted on
        the side channel using the incremental hash of `.data` text deltas
        (constraint C6).

        Replicate stream events have a `.event` attribute ("output", "done",
        "logs") and a `.data` attribute carrying the text increment.
        """
        hasher = IncrementalTextHasher()
        try:
            for event in self._inner.stream(ref, input=input, **kwargs):
                delta = _extract_stream_delta(event)
                if delta:
                    hasher.update(delta)
                yield event
        finally:
            try:
                self._emit_for_stream(
                    ref=ref,
                    input_dict=input or {},
                    text_hasher=hasher,
                    schema_override=schema_override,
                    prompt_text_kwarg=prompt_text_kwarg,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("LedgerProof streaming receipt failed: %s", exc)

    # ------------------------------------------------------------------
    # Modality-specific helpers — force a schema regardless of inference
    # ------------------------------------------------------------------
    def run_image(self, ref: str, *, input: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """Force synthetic_image/v1 receipt schema."""
        return self.run(ref, input=input, schema_override="synthetic_image/v1", **kwargs)

    def run_audio(self, ref: str, *, input: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """Force synthetic_audio/v1 receipt schema."""
        return self.run(ref, input=input, schema_override="synthetic_audio/v1", **kwargs)

    def run_video(self, ref: str, *, input: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """Force synthetic_video/v1 receipt schema."""
        return self.run(ref, input=input, schema_override="synthetic_video/v1", **kwargs)

    def run_with_attribution(
        self,
        ref: str,
        *,
        input: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Force multimodel_attribution/v1 — requires `ref` to include `:version`.
        Strongest binding: content-addressed model identity.
        """
        _, version = _split_ref(ref)
        if not version:
            raise ValueError(
                "run_with_attribution() requires a versioned model reference "
                "(e.g. 'author/name:abc123...'); got: " + ref
            )
        return self.run(ref, input=input, schema_override="multimodel_attribution/v1", **kwargs)

    # ------------------------------------------------------------------
    # Internal: receipt construction
    # ------------------------------------------------------------------
    def _emit_for_run(
        self,
        ref: str,
        input_dict: dict[str, Any],
        output: Any,
        schema_override: SchemaName | None,
        prompt_text_kwarg: str | None,
    ) -> None:
        model_ref = build_model_ref_from_coordinate(
            ref,
            prediction_id=f"run-{uuid.uuid4().hex[:16]}",
            status="succeeded",
        )
        content_refs, artifacts, inferred_schema = _classify_output(
            output, prompt_text=input_dict.get(prompt_text_kwarg) if prompt_text_kwarg else None
        )
        input_refs = build_input_refs(input_dict)
        schema = schema_override or self._default_schema or inferred_schema or "generated_content/v1"
        self._build_and_emit(
            schema=schema,
            model_ref=model_ref,
            content_refs=content_refs,
            input_refs=input_refs,
            output_artifacts=artifacts,
            streaming=False,
        )

    def _emit_for_stream(
        self,
        ref: str,
        input_dict: dict[str, Any],
        text_hasher: IncrementalTextHasher,
        schema_override: SchemaName | None,
        prompt_text_kwarg: str | None,
    ) -> None:
        model_ref = build_model_ref_from_coordinate(
            ref,
            prediction_id=f"stream-{uuid.uuid4().hex[:16]}",
            status="succeeded",
        )
        content_refs: list[ContentRef] = []
        prompt_text = input_dict.get(prompt_text_kwarg) if prompt_text_kwarg else None
        if isinstance(prompt_text, str):
            content_refs.append(
                ContentRef(
                    sha256_hex=hash_text(prompt_text).hex(),
                    byte_length=len(prompt_text.encode("utf-8")),
                    role="prompt",
                )
            )
        content_refs.append(
            ContentRef(
                sha256_hex=text_hasher.digest().hex(),
                byte_length=text_hasher.byte_count,
                role="output",
            )
        )
        input_refs = build_input_refs(input_dict)
        schema = schema_override or self._default_schema or "chatbot_session/v1"
        self._build_and_emit(
            schema=schema,
            model_ref=model_ref,
            content_refs=content_refs,
            input_refs=input_refs,
            output_artifacts=[],
            streaming=True,
        )

    def _build_and_emit(
        self,
        schema: SchemaName,
        model_ref: ModelRef,
        content_refs: list[ContentRef],
        input_refs: list[InputRef],
        output_artifacts: list[OutputArtifactRef],
        streaming: bool,
    ) -> None:
        receipt = ReceiptV1(
            schema=schema,
            receipt_id=str(uuid.uuid4()),
            deployer_id=self.deployer_id,
            model=model_ref,
            content_refs=content_refs,
            input_refs=input_refs,
            output_artifacts=output_artifacts,
            regulatory_context=self._reg_ctx,
            streaming=streaming,
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


# ---------------------------------------------------------------------------
# Output classification
# ---------------------------------------------------------------------------


def _classify_output(
    output: Any, prompt_text: Any = None
) -> tuple[list[ContentRef], list[OutputArtifactRef], SchemaName | None]:
    """
    Heuristically classify a Replicate output into ContentRefs + OutputArtifacts
    and propose an inferred schema based on the dominant modality.

    Returns (content_refs, output_artifacts, inferred_schema).
    """
    content_refs: list[ContentRef] = []
    artifacts: list[OutputArtifactRef] = []

    if isinstance(prompt_text, str):
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(prompt_text).hex(),
                byte_length=len(prompt_text.encode("utf-8")),
                role="prompt",
            )
        )

    # Normalise to list for uniform processing.
    items: list[Any]
    if isinstance(output, list):
        items = list(output)
    elif isinstance(output, (str, bytes)):
        items = [output]
    elif output is None:
        items = []
    else:
        items = [output]

    inferred: SchemaName | None = None

    # If everything is a string of natural-language text (not a URL), treat as
    # generated text output.
    if items and all(isinstance(i, str) and not i.startswith(("http://", "https://", "data:")) for i in items):
        joined = "".join(items)
        content_refs.append(
            ContentRef(
                sha256_hex=hash_text(joined).hex(),
                byte_length=len(joined.encode("utf-8")),
                role="output",
            )
        )
        inferred = "chatbot_session/v1"
        return content_refs, artifacts, inferred

    # Mixed / file outputs: hash each individually.
    image_count = audio_count = video_count = 0
    for item in items:
        url = _coerce_url(item)
        if url is not None:
            media_type = _guess_media_type_from_url(url)
            # We cannot fetch the URL here (C4: no phone-home for verification,
            # but adapter shouldn't fetch either — we record what the deployer
            # gave us). The deployer is expected to hash the downloaded bytes
            # themselves via emit_receipt() if they want full coverage.
            artifacts.append(
                OutputArtifactRef(
                    sha256_hex=hash_text(url).hex(),  # hash of the URL string as a proxy
                    byte_length=len(url.encode("utf-8")),
                    media_type=media_type,
                    output_uri=url[:512],
                )
            )
            if media_type and media_type.startswith(_IMAGE_MIME_PREFIXES):
                image_count += 1
            elif media_type and media_type.startswith(_AUDIO_MIME_PREFIXES):
                audio_count += 1
            elif media_type and media_type.startswith(_VIDEO_MIME_PREFIXES):
                video_count += 1
        elif isinstance(item, (bytes, bytearray)):
            artifacts.append(
                OutputArtifactRef(
                    sha256_hex=hash_bytes(bytes(item)).hex(),
                    byte_length=len(item),
                )
            )
        elif isinstance(item, str):
            content_refs.append(
                ContentRef(
                    sha256_hex=hash_text(item).hex(),
                    byte_length=len(item.encode("utf-8")),
                    role="output",
                )
            )

    if video_count and video_count >= max(image_count, audio_count):
        inferred = "synthetic_video/v1"
    elif audio_count and audio_count >= max(image_count, video_count):
        inferred = "synthetic_audio/v1"
    elif image_count:
        inferred = "synthetic_image/v1"
    elif artifacts:
        inferred = "generated_content/v1"

    return content_refs, artifacts, inferred


# ---------------------------------------------------------------------------
# Stream-event helpers
# ---------------------------------------------------------------------------


def _extract_stream_delta(event: Any) -> str | None:
    """
    Pull the text delta from a Replicate stream event. Replicate events look like:
        ServerSentEvent(event="output", data="token")
    We probe defensively across attribute and dict access.
    """
    etype = getattr(event, "event", None)
    if isinstance(event, dict):
        etype = etype or event.get("event")
    if etype is not None and str(etype) not in ("output", "data", None):
        return None

    data = getattr(event, "data", None)
    if data is None and isinstance(event, dict):
        data = event.get("data")
    if isinstance(data, str):
        return data
    if isinstance(data, bytes):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return None
    return None


def _split_ref(ref: str) -> tuple[str, str | None]:
    if ":" in ref:
        a, b = ref.split(":", 1)
        return a, b
    return ref, None
