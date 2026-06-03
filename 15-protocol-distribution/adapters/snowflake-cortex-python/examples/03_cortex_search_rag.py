"""Article 50(1) chatbot answer grounded in a Cortex Search Service.

Pattern: a customer-support chatbot retrieves grounding chunks from a
Cortex Search Service over an enterprise knowledge base, then synthesises
an answer with Cortex `Complete`. Two receipts are emitted side-channel:

  1. `cortex_search_rag/v1` — captures the search service, retrieval
     fingerprint, and the final completion hash.
  2. (Optionally) `chatbot_session/v1` for the completion call itself.

The deployer here demonstrates the disclosure-shown flag so the receipt
attests that the natural person was informed they were interacting with
an AI system (Article 50(1)).
"""

from __future__ import annotations

import os

from snowflake.snowpark import Session

from ledgerproof_snowflake_cortex import (
    LedgerProofCortex,
    LedgerProofCortexSearch,
    hash_str,
)
from ledgerproof_snowflake_cortex.emitter import FileSink


def main() -> None:
    session = Session.builder.configs({
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "password": os.environ["SNOWFLAKE_PASSWORD"],
        "role": os.environ.get("SNOWFLAKE_ROLE", "AI_APP_RW"),
        "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        "database": "AI_APP",
        "schema": "PUBLIC",
    }).create()

    sink = FileSink("receipts.jsonl")
    deployer_id = "acme-eu-deployer-001"

    search = LedgerProofCortexSearch(
        session=session,
        lpr_signing_key_path="signing-key.pem",
        lpr_deployer_id=deployer_id,
        lpr_sink=sink,
    )
    cortex = LedgerProofCortex(
        session=session,
        lpr_signing_key_path="signing-key.pem",
        lpr_deployer_id=deployer_id,
        lpr_sink=sink,
    )

    subject = hash_str("user-42@example.com")
    session_hash = hash_str("session-2026-06-03-001")
    user_query = "How do I rotate the data masking policy on a column?"

    # --- 1. Retrieve grounding from the Cortex Search Service ----------
    retrieval = search.query(
        service_name="AI_APP.PUBLIC.SUPPORT_KB",
        query=user_query,
        columns=["CHUNK", "SOURCE_URL"],
        limit=5,
        lpr_subject_id_hash=subject,
        lpr_session_id_hash=session_hash,
        lpr_disclosure_shown=True,
    )

    # --- 2. Synthesise an answer with Cortex `Complete` ----------------
    grounding = "\n\n".join(
        r["CHUNK"] for r in retrieval.get("results", []) if "CHUNK" in r
    )
    prompt = [
        {"role": "system",
         "content": "You are an AI support assistant. Cite SOURCE_URL "
                    "when referencing grounding chunks."},
        {"role": "user",
         "content": f"Grounding:\n{grounding}\n\nQuestion: {user_query}"},
    ]
    answer = cortex.complete(
        model="claude-3-5-sonnet",
        prompt=prompt,
        lpr_subject_id_hash=subject,
        lpr_session_id_hash=session_hash,
        lpr_disclosure_shown=True,
    )
    print("Assistant:", answer)

    search.flush()
    cortex.flush()


if __name__ == "__main__":
    main()
