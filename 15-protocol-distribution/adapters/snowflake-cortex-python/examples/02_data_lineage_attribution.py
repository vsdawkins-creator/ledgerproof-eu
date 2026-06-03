"""Article 50(2) synthetic content with warehouse + database + schema +
table-source attribution.

Pattern: a Cortex `Complete` call that summarises governed warehouse data,
and the deployer wants the transparency receipt to carry the upstream
lineage so an auditor can reconstruct *which governed dataset* produced
the synthetic content — without leaking the rows themselves.
"""

from __future__ import annotations

import os

from snowflake.snowpark import Session

from ledgerproof_snowflake_cortex import LedgerProofCortex
from ledgerproof_snowflake_cortex.emitter import FileSink


def main() -> None:
    session = Session.builder.configs({
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "password": os.environ["SNOWFLAKE_PASSWORD"],
        "role": os.environ.get("SNOWFLAKE_ROLE", "AI_APP_RW"),
        "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        "database": "CRM_PROD",
        "schema": "ACCOUNTS",
    }).create()

    cortex = LedgerProofCortex(
        session=session,
        lpr_signing_key_path="signing-key.pem",
        lpr_deployer_id="acme-eu-deployer-001",
        lpr_sink=FileSink("receipts.jsonl"),
    )

    # Imagine the prompt has been built by interpolating governed warehouse
    # rows into a Cortex template. We attest to the *tables* that fed it,
    # not the row content.
    prompt = (
        "Draft a one-paragraph executive summary of this enterprise "
        "account, suitable for inclusion in a Tuesday CRO briefing."
    )

    answer = cortex.complete(
        model="claude-3-5-sonnet",
        prompt=prompt,
        lpr_schema="enterprise_data_lineage/v1",
        lpr_warehouse="COMPUTE_WH",
        lpr_source_database="CRM_PROD",
        lpr_source_schema="ACCOUNTS",
        lpr_source_tables=[
            "CUSTOMER_360",
            "INTERACTION_LOG",
            "REVENUE_FACT",
        ],
        # If you have the query id (e.g. from a wrapping SQL call) include
        # it so the receipt can be cross-referenced with Snowflake's own
        # ACCESS_HISTORY / QUERY_HISTORY views.
        lpr_query_id="01abcd-0000-0001",
        lpr_role="AI_APP_RW",
        lpr_marking_method="visible-label",
    )
    print("Cortex says:", answer)
    cortex.flush()


if __name__ == "__main__":
    main()
