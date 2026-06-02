"""02 — On-prem sovereign deployment (Germany / BaFin-supervised).

Demonstrates the `on_prem_sovereign_deployment/v1` schema. The hosting
jurisdiction and operator attestation become part of every signed receipt,
so an auditor can verify after the fact that a given AI interaction was
served by a sovereign deployment inside Germany.

Run against a sovereign Aleph Alpha endpoint inside your own datacentre,
e.g. `https://luminous.acme-frankfurt-dc01.internal`.
"""

from __future__ import annotations

import os

from aleph_alpha_client import Client, CompletionRequest, Prompt

from ledgerproof_aleph_alpha import (
    InMemoryEmitter,
    LedgerProofAlephAlpha,
    verify_receipt,
)


def main() -> None:
    token = os.environ.get("AA_ON_PREM_TOKEN", "dev-token")
    host = os.environ.get(
        "AA_ON_PREM_HOST",
        "https://luminous.acme-frankfurt-dc01.internal",
    )

    upstream = Client(token=token, host=host)

    sink = InMemoryEmitter()
    client = LedgerProofAlephAlpha(
        upstream,
        article="50(1)",
        schema="on_prem_sovereign_deployment/v1",
        emitter=sink,
        extra={
            "hosting_jurisdiction": "DE",
            "operator": "Acme Bank AG",
            "sovereignty_attestation": "on-prem-frankfurt-dc01",
            "data_residency_confirmed": True,
            "egress_disabled": True,
        },
    )

    req = CompletionRequest(
        prompt=Prompt.from_text(
            "Summarise the BaFin requirements for AI model governance."
        ),
        maximum_tokens=128,
    )
    resp = client.complete(req, model="luminous-supreme-control")
    print("Completion:", resp.completions[0].completion)

    receipt = sink.receipts[0]
    assert verify_receipt(receipt)
    print("Sovereign attestation receipt verified.")
    print("  jurisdiction =", receipt["payload"]["hosting_jurisdiction"])
    print("  operator     =", receipt["payload"]["operator"])
    print("  attestation  =", receipt["payload"]["sovereignty_attestation"])


if __name__ == "__main__":
    main()
