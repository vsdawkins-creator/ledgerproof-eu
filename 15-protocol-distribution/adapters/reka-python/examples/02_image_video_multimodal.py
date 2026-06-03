"""
Multimodal-native example: text + image + video in a single Reka inference.

Demonstrates how the LedgerProof Reka adapter automatically promotes the
receipt schema:
  - text + image  -> multimodal_native_inference/v1
  - text + video  -> video_understanding/v1

C4: video_url is hashed by URI only; the adapter NEVER dereferences a URL.

Requires:  pip install ledgerproof-reka
           export REKA_API_KEY=...
"""

from __future__ import annotations

import base64
from pathlib import Path

from ledgerproof_reka import (
    LedgerProofReka,
    LogEmitter,
    RegulatoryContext,
)


def _b64(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


def main() -> None:
    client = LedgerProofReka(
        deployer_id="acme-corp-eu",
        emitter=LogEmitter(),
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="Multimodal customer feedback triage.",
        ),
    )

    # ----- Image + text (-> multimodal_native_inference/v1) -----
    image_response = client.chat.create(
        model="reka-core",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is shown in this screenshot?"},
                    # In a real script, replace with: _b64("path/to/screenshot.png")
                    {
                        "type": "image",
                        "image": {
                            "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9ZitR7gAAAAASUVORK5CYII=",
                            "media_type": "image/png",
                        },
                    },
                ],
            }
        ],
    )
    print("Image reply:", image_response.responses[0].message.content)

    # ----- Video (URL-only -> hashed by URI, no fetch) ----------
    video_response = client.chat.create(
        model="reka-core",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Summarise the safety briefing in this clip."},
                    {
                        "type": "video",
                        "url": "https://cdn.example.com/onboarding/safety-briefing.mp4",
                        "media_type": "video/mp4",
                    },
                ],
            }
        ],
    )
    print("Video reply:", video_response.responses[0].message.content)

    print(
        "---- Two signed receipts emitted: one multimodal_native_inference/v1, "
        "one video_understanding/v1 ----"
    )


if __name__ == "__main__":
    main()
