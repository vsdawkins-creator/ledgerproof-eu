"""Quickstart: wrap a Snowflake Cortex `Complete` call and emit a
chatbot_session/v1 transparency receipt via side-channel.

Run from a host with an authenticated Snowflake account / Snowpark session.
"""

from __future__ import annotations

import os

from snowflake.snowpark import Session

from ledgerproof_snowflake_cortex import LedgerProofCortex, hash_str
from ledgerproof_snowflake_cortex.emitter import FileSink


def main() -> None:
    session = Session.builder.configs({
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "password": os.environ["SNOWFLAKE_PASSWORD"],
        "role": os.environ.get("SNOWFLAKE_ROLE", "PUBLIC"),
        "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        "database": os.environ.get("SNOWFLAKE_DATABASE", "AI_APP"),
        "schema": os.environ.get("SNOWFLAKE_SCHEMA", "PUBLIC"),
    }).create()

    # Receipts are written, one per line, to ./receipts.jsonl
    cortex = LedgerProofCortex(
        session=session,
        lpr_signing_key_path="signing-key.pem",
        lpr_deployer_id="acme-eu-deployer-001",
        lpr_sink=FileSink("receipts.jsonl"),
    )

    answer = cortex.complete(
        model="llama3.1-70b",
        prompt=[
            {"role": "user",
             "content": "I'm a customer asking about my account. What is "
                        "your name and are you an AI?"},
        ],
        # Pseudonymous identifier for the natural person (Article 50(1)).
        lpr_subject_id_hash=hash_str("user-42@example.com"),
        lpr_session_id_hash=hash_str("session-2026-06-03-001"),
        # We have shown the natural person the required AI-interaction
        # disclosure in our UI:
        lpr_disclosure_shown=True,
    )
    print("Cortex says:", answer)

    # Best-effort flush before we exit.
    cortex.flush()


if __name__ == "__main__":
    main()
