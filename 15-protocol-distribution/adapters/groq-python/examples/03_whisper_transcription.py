"""Whisper transcription demo with Article 50(2) audio_transcription/v1 receipt."""

import sys

from ledgerproof_groq import LedgerProofGroq


def main(audio_path: str) -> None:
    client = LedgerProofGroq(lpr_deployer_id="demo-deployer-001")

    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            file=f,
            model="whisper-large-v3",
            lpr_schema="audio_transcription/v1",
            lpr_language="en",
            lpr_marking_method="visible-label",
        )

    print(transcript.text)
    client.flush()
    client.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 03_whisper_transcription.py <path/to/audio.wav>")
        sys.exit(2)
    main(sys.argv[1])
