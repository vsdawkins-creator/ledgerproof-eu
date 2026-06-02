"""
Multimodal example: text + image input.

When the input contains a non-text modality, the receipt schema is promoted to
multimodal_generation/v1 (Article 50(2) variant). The image bytes are NOT
included in the receipt — only the modality types are recorded.
"""

from __future__ import annotations

import os
import sys

import google.generativeai as genai

from ledgerproof_google_ai import (
    LedgerProofGenerativeModel,
    StderrEmitter,
)


def main() -> None:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Set GOOGLE_API_KEY before running this example.", file=sys.stderr)
        sys.exit(1)
    genai.configure(api_key=api_key)

    model = LedgerProofGenerativeModel(
        "gemini-2.0-flash",
        deployer_id="acme-eu-bank",
        emitter=StderrEmitter(),
    )

    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not image_path or not os.path.isfile(image_path):
        print(
            "Usage: python 03_multimodal.py path/to/image.png",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Inline-data dict form — matches google-generativeai's expected schema.
    image_part = {
        "inline_data": {
            "mime_type": "image/png",
            "data": image_bytes,
        }
    }

    response = model.generate_content(
        [
            "Describe this image for an accessibility report:",
            image_part,
        ]
    )
    print(response.text)


if __name__ == "__main__":
    main()
