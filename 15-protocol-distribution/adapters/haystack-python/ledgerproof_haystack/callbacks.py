"""Streaming callback support — C6 stream-aware signing.

Haystack 2.x generators accept a `streaming_callback` of type
`Callable[[StreamingChunk], None]`. We provide a callback factory that
hashes chunks incrementally and emits a receipt when the stream closes.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from typing import Any, Callable, Optional

from .canonical import canonical_cbor
from .emitter import Emitter
from .schema import build_receipt
from .signer import SigningKey


class StreamingReceiptBuilder:
    """Incremental hasher + receipt assembler for streaming generators.

    Wire `builder.on_chunk` as the generator's `streaming_callback`.
    Call `builder.finalize()` after the stream completes to sign + emit.
    """

    def __init__(
        self,
        signing_key: SigningKey,
        emitter: Emitter,
        deployer: str,
        model_id: str,
        generator_class: str,
        gdpr_lawful_basis: Optional[str] = None,
    ):
        self.signing_key = signing_key
        self.emitter = emitter
        self.deployer = deployer
        self.model_id = model_id
        self.generator_class = generator_class
        self.gdpr_lawful_basis = gdpr_lawful_basis
        self._hasher = hashlib.sha256()
        self._length = 0
        self._started = time.time()
        self._finalized = False

    # -- streaming callback --------------------------------------------------

    def on_chunk(self, chunk: Any) -> None:
        """Haystack 2.x calls this for every StreamingChunk."""
        content = getattr(chunk, "content", None)
        if content is None and isinstance(chunk, str):
            content = chunk
        if content is None:
            return
        encoded = content.encode("utf-8") if isinstance(content, str) else bytes(content)
        self._hasher.update(encoded)
        self._length += len(encoded)

    # -- finalization --------------------------------------------------------

    def finalize(self) -> dict[str, Any]:
        if self._finalized:
            raise RuntimeError("StreamingReceiptBuilder.finalize() already called")
        self._finalized = True
        content_hash = self._hasher.hexdigest()
        receipt = build_receipt(
            "generated_content/v1",
            receipt_id=str(uuid.uuid4()),
            deployer=self.deployer,
            key_id=self.signing_key.key_id,
            gdpr_lawful_basis=self.gdpr_lawful_basis,
            content_type="text",
            content_hash=content_hash,
            content_length=self._length,
            model_id=self.model_id,
            generator_class=self.generator_class,
        )
        payload = receipt.model_dump()
        signature = self.signing_key.sign(canonical_cbor(payload))
        envelope = {
            "receipt": payload,
            "signature_alg": "ed25519",
            "signature_b64": _b64(signature),
            "public_key_b64": self.signing_key.public_key_b64(),
            "latency_ms_streaming": round((time.time() - self._started) * 1000, 3),
        }
        self.emitter.emit(envelope)
        return envelope


def lpr_pipeline_callback(
    signing_key: SigningKey,
    emitter: Emitter,
    deployer: str,
    model_id: str,
    generator_class: str = "Generator",
    gdpr_lawful_basis: Optional[str] = None,
) -> tuple[Callable[[Any], None], StreamingReceiptBuilder]:
    """Return `(callback, builder)`.

    Attach `callback` as `streaming_callback=` on a Haystack generator.
    After the pipeline run completes, call `builder.finalize()` to emit.
    """
    builder = StreamingReceiptBuilder(
        signing_key=signing_key,
        emitter=emitter,
        deployer=deployer,
        model_id=model_id,
        generator_class=generator_class,
        gdpr_lawful_basis=gdpr_lawful_basis,
    )
    return builder.on_chunk, builder


def _b64(data: bytes) -> str:
    import base64

    return base64.b64encode(data).decode("ascii")
