"""
Example 03 — Audio synthesis (MusicGen) with an Article 50(2) receipt.

Uses MusicGen via Replicate to generate a 10-second ambient piano clip.
A synthetic_audio/v1 receipt is emitted that binds the model coordinate, the
prompt hash, and (after download) the SHA-256 of the audio bytes.

Run:
    export REPLICATE_API_TOKEN=r8_...
    python examples/03_audio_synthesis.py

NOTE: Not endorsed by Replicate. Not endorsed by Meta. Not endorsed by any
regulator. No Article 40 presumption of conformity.
"""

from __future__ import annotations

import sys
import urllib.request

from ledgerproof_replicate import (
    LedgerProofReplicateClient,
    LogEmitter,
    emit_receipt,
    hash_audio_bytes,
    build_model_ref_from_coordinate,
)

MUSICGEN = "meta/musicgen"


def main() -> int:
    client = LedgerProofReplicateClient(
        deployer_id="acme-eu",
        emitter=LogEmitter(),
    )

    output = client.run_audio(
        MUSICGEN,
        input={
            "prompt": "ambient piano with light rainfall, contemplative",
            "duration": 10,
            "model_version": "stereo-large",
            "output_format": "wav",
        },
    )

    # Resolve to a URL string
    url = None
    if isinstance(output, str):
        url = output
    elif isinstance(output, list) and output:
        first = output[0]
        url = first if isinstance(first, str) else getattr(first, "url", None)
    else:
        url = getattr(output, "url", None)

    if not url:
        print("warning: no audio URL returned", file=sys.stderr)
        return 0

    # Download + bind the actual bytes for a stronger receipt.
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            audio_bytes = resp.read()
    except Exception as exc:
        print(f"warning: could not download audio: {exc}", file=sys.stderr)
        return 0

    emit_receipt(
        deployer_id="acme-eu",
        model_ref=build_model_ref_from_coordinate(
            MUSICGEN,
            prediction_id="post-download-bind",
            status="succeeded",
        ),
        schema="synthetic_audio/v1",
        prompt_text="ambient piano with light rainfall, contemplative",
        inputs={
            "prompt": "ambient piano with light rainfall, contemplative",
            "duration": 10,
            "model_version": "stereo-large",
        },
        output_artifacts=[
            hash_audio_bytes(
                audio_bytes,
                media_type="audio/wav",
                duration_seconds=10.0,
                sample_rate_hz=32000,
            )
        ],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
