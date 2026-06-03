"""Reasoning-model demo — distilled chain-of-thought models on Cerebras.

Uses the `reasoning_distilled/v1` schema, which captures reasoning-trace
token usage alongside the final completion. Auto-routes by model name when
no `lpr_schema` is given.
"""

from ledgerproof_cerebras import LedgerProofCerebras


def main() -> None:
    client = LedgerProofCerebras(lpr_deployer_id="demo-deployer-001")

    resp = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {"role": "user", "content": "If a train leaves Munich at 09:00 going 120 km/h..."},
        ],
        # No lpr_schema — adapter auto-routes reasoning models to
        # reasoning_distilled/v1.
        lpr_disclosure_shown=True,
    )

    print(resp.choices[0].message.content)
    client.flush()
    client.close()


if __name__ == "__main__":
    main()
