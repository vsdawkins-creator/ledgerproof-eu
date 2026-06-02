"""Quickstart: wrap Groq with LedgerProof transparency receipts.

Requires: GROQ_API_KEY in env.
"""

from ledgerproof_groq import LedgerProofGroq, hash_str
from ledgerproof_groq.schema import hash_str as _hash  # noqa: F401


def main() -> None:
    client = LedgerProofGroq(
        # api_key=...  # or set GROQ_API_KEY env var
        lpr_deployer_id="demo-deployer-001",
    )

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Summarise the EU AI Act in one sentence."},
        ],
        lpr_schema="chatbot_session/v1",
        lpr_subject_id_hash=hash_str("user-42@example.com"),
        lpr_disclosure_shown=True,
    )

    print(resp.choices[0].message.content)
    client.flush()
    client.close()


if __name__ == "__main__":
    main()
