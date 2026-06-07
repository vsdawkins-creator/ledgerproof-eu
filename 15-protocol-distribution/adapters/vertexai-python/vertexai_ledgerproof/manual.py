"""Manual receipt emission for advanced / atypical call sites.

For cases where neither the wrapper nor decorator fit — e.g., direct
`aiplatform.Endpoint.predict()` calls, embeddings, or custom REST
invocations against Vertex AI predictive endpoints.
"""
from __future__ import annotations

from typing import Any

from .emitter import emit_receipt


def emit(
    *,
    schema: str,
    model: str,
    project: str | None = None,
    location: str | None = None,
    input_text: str | None = None,
    output_text: str | None = None,
    deployer_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Explicitly emit a LedgerProof receipt. Returns the signed envelope.

    Typical use:

        from vertexai_ledgerproof import manual

        manual.emit(
            schema="eu_data_residency/v1",
            model="text-bison@002",
            project="acme-eu",
            location="europe-west4",
            input_text=prompt,
            output_text=response_text,
        )
    """
    return emit_receipt(
        schema,
        model=model,
        project=project,
        location=location,
        input_text=input_text,
        output_text=output_text,
        deployer_id=deployer_id,
        extra=extra,
    )
