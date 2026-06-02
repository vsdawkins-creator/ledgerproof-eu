"""LedgerProofGeneratorWrapper — wrap any Haystack 2.x Generator.

The wrapper preserves the wrapped generator's input/output socket shape
and adds a side-channel signed receipt on every `run()` call.
"""

from __future__ import annotations

import base64
import time
import uuid
from typing import Any, Optional

from .canonical import canonical_cbor, sha256_hex
from .emitter import Emitter, MemoryEmitter
from .schema import build_receipt
from .signer import SigningKey

try:
    from haystack import component  # type: ignore[import-not-found]

    _HAYSTACK_AVAILABLE = True
except Exception:  # pragma: no cover
    _HAYSTACK_AVAILABLE = False

    def component(cls):  # type: ignore[no-redef]
        return cls


def _project_replies(result: dict[str, Any]) -> str:
    """Pull a hashable text projection from a Haystack generator's output dict."""
    for key in ("replies", "answers", "results", "content", "output"):
        if key in result:
            value = result[key]
            if isinstance(value, list):
                return "\n".join(
                    v.content if hasattr(v, "content") else str(v) for v in value
                )
            if hasattr(value, "content"):
                return str(value.content)
            return str(value)
    return ""


@component
class LedgerProofGeneratorWrapper:
    """Wrap a Haystack 2.x generator and emit a generated_content/v1 receipt.

    Example:
        wrapped = LedgerProofGeneratorWrapper(
            inner=OpenAIGenerator(model="gpt-4o-mini"),
            signing_key=key,
            deployer="acme-bank-de",
        )
        pipeline.add_component("llm", wrapped)
    """

    def __init__(
        self,
        inner: Any,
        signing_key: SigningKey,
        deployer: str = "unspecified-deployer",
        emitter: Optional[Emitter] = None,
        model_id: Optional[str] = None,
        gdpr_lawful_basis: Optional[str] = None,
    ):
        self.inner = inner
        self.signing_key = signing_key
        self.deployer = deployer
        self.emitter = emitter if emitter is not None else MemoryEmitter()
        self.gdpr_lawful_basis = gdpr_lawful_basis
        # Try to discover model id from inner generator.
        self.model_id = (
            model_id
            or getattr(inner, "model", None)
            or getattr(inner, "model_name", None)
            or "unspecified-model"
        )
        self.generator_class = type(inner).__name__

    def run(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Delegate to inner.run, then sign+emit a receipt on its reply."""
        start = time.time()
        result = self.inner.run(*args, **kwargs)
        if not isinstance(result, dict):
            # Some generators may return a dataclass-like — coerce minimally.
            result = {"replies": [result]}

        reply_text = _project_replies(result)
        content_hash = sha256_hex(reply_text)
        content_length = len(reply_text.encode("utf-8"))

        receipt = build_receipt(
            "generated_content/v1",
            receipt_id=str(uuid.uuid4()),
            deployer=self.deployer,
            key_id=self.signing_key.key_id,
            gdpr_lawful_basis=self.gdpr_lawful_basis,
            content_type="text",
            content_hash=content_hash,
            content_length=content_length,
            model_id=self.model_id,
            generator_class=self.generator_class,
        )
        payload = receipt.model_dump()
        signature = self.signing_key.sign(canonical_cbor(payload))
        envelope = {
            "receipt": payload,
            "signature_alg": "ed25519",
            "signature_b64": base64.b64encode(signature).decode("ascii"),
            "public_key_b64": self.signing_key.public_key_b64(),
            "latency_ms": round((time.time() - start) * 1000, 3),
        }
        self.emitter.emit(envelope)

        # C7: do not mutate user-facing output — pass through unchanged.
        return result
