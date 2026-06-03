"""Quickstart: wrap Cerebras with LedgerProof transparency receipts.

Requires: CEREBRAS_API_KEY in env.
"""

from ledgerproof_cerebras import LedgerProofCerebras, hash_str


def main() -> None:
    client = LedgerProofCerebras(
        # api_key=...  # or set CEREBRAS_API_KEY env var
        lpr_deployer_id="demo-deployer-001",
    )

    resp = client.chat.completions.create(
        model="llama3.1-70b",
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
