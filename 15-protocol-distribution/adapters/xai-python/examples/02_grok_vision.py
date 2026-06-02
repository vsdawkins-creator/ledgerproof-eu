"""Grok-2-vision inference with the `vision_inference/v1` schema.

The adapter detects OpenAI-style `image_url` content blocks in the messages
and records `image_count` + `content_modality="image"` in the receipt. The
deployer may also pre-compute `image_input_sha256` (SHA-256 over the canonical
representation of the image bytes or URL list) and pass it via
`regulatory_context["image_input_sha256"]` to bind the receipt cryptographically
to the exact image input.

    pip install ledgerproof-xai
    export XAI_API_KEY=xai-...
    python examples/02_grok_vision.py
"""

from __future__ import annotations

import hashlib

from ledgerproof_xai import LedgerProofXAI


IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"


def main() -> None:
    # Pre-compute a hash binding the receipt to this exact image URL.
    image_input_sha256 = hashlib.sha256(IMAGE_URL.encode("utf-8")).hexdigest()

    client = LedgerProofXAI(
        deployer_id="urn:eu:deployer:acme-media-de",
        regulatory_context={
            "schema": "vision_inference/v1",
            "jurisdiction": "EU",
            "image_input_sha256": image_input_sha256,
        },
    )

    resp = client.chat.completions.create(
        model="grok-2-vision",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in this image?"},
                    {"type": "image_url", "image_url": {"url": IMAGE_URL}},
                ],
            }
        ],
    )

    print("--- assistant response ---")
    print(resp.choices[0].message.content)
    print("--- vision_inference/v1 receipt was emitted to stdout ---")


if __name__ == "__main__":
    main()
