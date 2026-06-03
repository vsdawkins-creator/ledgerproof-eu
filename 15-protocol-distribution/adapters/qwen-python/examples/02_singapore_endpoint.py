"""
Cross-jurisdictional routing example: route through the DashScope Singapore
international endpoint and record that fact in the receipt.

Strategic context: EU deployers using Chinese-origin foundation models often
need to demonstrate that inference does NOT transit mainland-China data
residency, both for GDPR Schrems-II analysis and to manage sector-specific
overlays (FSI / DORA, banking secrecy regimes). The `cross_jurisdictional_routing/v1`
schema lets you record the endpoint region and the cross-border transfer
mechanism applied.

The attestation block is descriptive metadata only — see the C1 disclaimer in
the README. LedgerProof does NOT verify the endpoint URL out of band.
"""

from __future__ import annotations

import os

from ledgerproof_qwen import (
    CrossJurisdictionalRoute,
    LedgerProofQwen,
    RegulatoryContext,
    StderrEmitter,
)


def main() -> None:
    route = CrossJurisdictionalRoute(
        endpoint_region="singapore",
        endpoint_base_url="https://dashscope-intl.aliyuncs.com",
        avoids_mainland_residency=True,
        transfer_mechanism="SCCs-2021/914 + supplementary measures",
        provider_legal_entity="Alibaba Cloud (Singapore) Private Limited",
        notes="EU deployer; inference routed via Singapore to avoid mainland-CN residency.",
    )

    client = LedgerProofQwen(
        deployer_id="acme-bank-eu",
        api_key=os.environ["DASHSCOPE_API_KEY"],
        # Pin DashScope to the Singapore international endpoint.
        base_url="https://dashscope-intl.aliyuncs.com",
        emitter=StderrEmitter(),
        schema="cross_jurisdictional_routing/v1",
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="DE",
            end_user_disclosure_made=True,
            notes="Inference routed via Singapore endpoint; Schrems-II SCCs in place.",
        ),
        cross_jurisdictional_route=route,
    )

    response = client.generation.call(
        model="qwen-max",
        messages=[
            {"role": "user", "content": "Summarise the Article 50 transparency obligation."},
        ],
    )

    print("---- Assistant reply ----")
    if response.output.choices:
        print(response.output.choices[0].message.content)
    else:
        print(response.output.text)
    print("---- (Signed receipt with cross-jurisdictional-routing attestation emitted on stderr) ----")


if __name__ == "__main__":
    main()
