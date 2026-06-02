"""
Example 02 — Image generation with Article 50(2) content provenance.

Uses FLUX (Schnell) hosted on Replicate. The receipt binds:
  - the immutable Replicate version hash of the FLUX model,
  - the SHA-256 of every input parameter (prompt, seed, ...),
  - the SHA-256 of the generated image bytes (downloaded out-of-band).

The receipt is multimodel_attribution/v1 (the strongest binding — content-
addressed model identity proves which exact FLUX weights produced the image).

Run:
    export REPLICATE_API_TOKEN=r8_...
    python examples/02_image_generation_with_provenance.py

NOTE: Not endorsed by Replicate. Not endorsed by Black Forest Labs. Not endorsed
by any regulator. No Article 40 presumption of conformity.
"""

from __future__ import annotations

import sys
import urllib.request

from ledgerproof_replicate import (
    LedgerProofReplicateClient,
    StderrEmitter,
    emit_receipt,
    hash_image_bytes,
    build_model_ref_from_coordinate,
)

# A versioned FLUX coordinate — the suffix after ":" is the content-addressed
# Replicate version hash. Using this guarantees the receipt binds the exact
# weights used. (Example hash shown; in production look up the latest version
# of the model you intend to deploy.)
FLUX_VERSIONED = (
    "black-forest-labs/flux-schnell:"
    "bf2f2e683d03a9549f484a37a0df1c4c08e8e3fa3a18f3e1c1d4a4dba8c0bc0e"
)


def main() -> int:
    client = LedgerProofReplicateClient(
        deployer_id="acme-eu",
        emitter=StderrEmitter(),
    )

    # Step 1: run FLUX. The wrapper emits a multimodel_attribution/v1 receipt
    # automatically, but it can only hash the OUTPUT URL string (not the bytes),
    # because the adapter does not fetch URLs (we keep the protocol phone-home
    # free for the operational path).
    output = client.run_with_attribution(
        FLUX_VERSIONED,
        input={
            "prompt": "a serene mountain lake at dawn, photorealistic, 4k",
            "num_outputs": 1,
            "guidance_scale": 3.5,
            "num_inference_steps": 4,
        },
    )

    # Step 2 (optional, recommended for strongest binding): download the image
    # ourselves and emit a SECOND, more complete receipt that binds the actual
    # bytes. This is the receipt you keep for Article 50(2) evidence.
    if isinstance(output, list) and output:
        url = output[0] if isinstance(output[0], str) else getattr(output[0], "url", None)
    elif isinstance(output, str):
        url = output
    else:
        url = getattr(output, "url", None)

    if url:
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                image_bytes = resp.read()
        except Exception as exc:
            print(f"warning: could not download image for byte-level binding: {exc}",
                  file=sys.stderr)
            return 0

        emit_receipt(
            deployer_id="acme-eu",
            model_ref=build_model_ref_from_coordinate(
                FLUX_VERSIONED,
                prediction_id="post-download-bind",
                status="succeeded",
            ),
            schema="synthetic_image/v1",
            prompt_text="a serene mountain lake at dawn, photorealistic, 4k",
            inputs={
                "prompt": "a serene mountain lake at dawn, photorealistic, 4k",
                "guidance_scale": 3.5,
                "num_inference_steps": 4,
            },
            output_artifacts=[hash_image_bytes(image_bytes, media_type="image/webp")],
            emitter=StderrEmitter(),
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
