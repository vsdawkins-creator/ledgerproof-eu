"""Manual receipt emission — for users who want explicit control.

```python
from huggingface_hub import InferenceClient
from ledgerproof_huggingface import emit_receipt

client = InferenceClient(model="meta-llama/Llama-3.1-70B-Instruct")
resp = client.chat_completion(messages=[{"role": "user", "content": "hi"}])
emit_receipt(resp, deployer_id="urn:eu:deployer:acme", messages=[...])
```
"""

from __future__ import annotations

import uuid
from typing import Any

from .canonical import canonical_encode
from .emitter import Emitter, LogEmitter
from .inference_client_wrapper import (
    _extract_interaction_id,
    _extract_model_id,
    _hash_messages,
    _hash_non_streaming_response,
    _hash_text_prompt,
)
from .pipeline_wrapper import _hash_pipeline_output, _hash_prompt
from .schema import build_receipt
from .signer import Ed25519Signer, Signer
from .version import __version__


def emit_receipt(
    response: Any,
    deployer_id: str,
    *,
    messages: list[dict[str, Any]] | None = None,
    prompt: str | None = None,
    regulatory_context: dict[str, Any] | None = None,
    signer: Signer | None = None,
    emitter: Emitter | None = None,
    user_pseudonym: str | None = None,
    extra: dict[str, Any] | None = None,
    schema_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build, sign, and emit a receipt for a Hugging Face response.

    Accepts:
    - A `ChatCompletionOutput` (pass `messages=`)
    - A `text_generation` string or object (pass `prompt=`)
    - A `transformers.Pipeline` output (pass `prompt=`)

    Returns the signed envelope dict so callers can also persist / inspect it.
    Does **not** modify `response`.
    """
    regulatory_context = regulatory_context or {}
    schema_id = regulatory_context.get("schema", "chatbot_session/v1")

    signer = signer or Ed25519Signer()
    emitter = emitter or LogEmitter()

    model_id = _extract_model_id(response, "unknown")
    interaction_id = _extract_interaction_id(response) or str(uuid.uuid4())

    if messages is not None:
        prompt_sha256 = _hash_messages(messages)
    elif prompt is not None and isinstance(prompt, str):
        prompt_sha256 = _hash_text_prompt(prompt)
    else:
        prompt_sha256 = _hash_prompt(prompt if prompt is not None else "")

    # Detect transformers pipeline-shaped output (list of dicts) vs HF API output
    if isinstance(response, list):
        response_sha256 = _hash_pipeline_output(response)
    else:
        response_sha256 = _hash_non_streaming_response(response)

    fields: dict[str, Any] = dict(
        deployer_id=deployer_id,
        model_id=model_id,
        interaction_id=interaction_id,
        prompt_sha256=prompt_sha256,
        response_sha256=response_sha256,
        user_pseudonym=user_pseudonym,
        jurisdiction=regulatory_context.get("jurisdiction", "EU"),
        extra=extra or {},
    )
    if schema_overrides:
        fields.update(schema_overrides)
    for k in (
        "hosting_provider_hq",
        "model_license",
        "open_weights",
        "host_environment",
        "device",
        "task",
        "content_modality",
        "machine_readable_marker",
        "disclosure_shown",
    ):
        if k in regulatory_context and k not in fields:
            fields[k] = regulatory_context[k]

    receipt = build_receipt(schema_id, **fields)
    receipt_dict = receipt.model_dump()
    canonical_bytes = canonical_encode(receipt_dict)
    signature = signer.sign(canonical_bytes)

    envelope = {
        "receipt": receipt_dict,
        "signature": signature.hex(),
        "signature_alg": "ed25519",
        "public_key": signer.public_key_bytes().hex(),
        "adapter": {"name": "ledgerproof-huggingface", "version": __version__},
    }
    emitter.emit(envelope)
    return envelope
