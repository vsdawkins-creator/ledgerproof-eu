"""
LedgerProof adapter for the IBM watsonx.ai Python SDK.

Side-channel cryptographic transparency receipts for EU AI Act Article 50,
with first-class support for:
  - EU-DE (Frankfurt) data residency attestation for German enterprise
    customers under GDPR + EU AI Act.
  - IBM Granite open-weights model attribution (Apache-2.0, reproducible
    weights published on Hugging Face) — materially strengthens the deployer's
    Article 50 disclosure.
  - watsonx project / tenant / deployment-space scoping.

Usage (drop-in wrapper):

    from ibm_watsonx_ai import Credentials
    from watsonx_ledgerproof import LedgerProofModelInference

    credentials = Credentials(
        url="https://eu-de.ml.cloud.ibm.com",
        api_key="...",
    )

    model = LedgerProofModelInference(
        deployer_id="acme-eu-bank",
        model_id="ibm/granite-3-8b-instruct",
        credentials=credentials,
        project_id="<project-uuid>",
        attest_residency=True,
        attest_granite_open_weights=True,
        sccs_in_place=True,
    )

    response = model.chat(messages=[{"role": "user", "content": "Hallo"}])

The wrapper intercepts chat / chat_stream / generate_text /
generate_text_stream. It emits a signed Ed25519 receipt on the configured
side-channel (stdout by default) AFTER the response is materialised. The
response object is returned UNCHANGED — constraint C7.

LedgerProof is an open protocol, Foundation-stewarded. It is NOT endorsed by
IBM, by any EU regulator, and does NOT establish an Article 40 presumption of
conformity. See README for the full disclaimer.
"""

from .canonical import (
    IncrementalTextHasher,
    canonical_encode,
    canonical_hash,
    hash_bytes,
    hash_text,
)
from .decorator import lpr_track
from .emitter import (
    Emitter,
    IbmCloudLogsEmitter,
    LogEmitter,
    MultiEmitter,
    QueueEmitter,
    StderrEmitter,
    WebhookEmitter,
)
from .manual import (
    build_model_ref,
    emit_receipt,
    extract_assistant_text,
    extract_tool_uses,
    extract_user_message_text,
    extract_user_prompt_from_generate,
    make_eu_residency_attestation,
    make_granite_attestation,
)
from .model_wrapper import LedgerProofModelInference
from .schema import (
    EEA_AND_ADJACENT_REGIONS,
    EU_WATSONX_REGIONS,
    ContentRef,
    DataResidencyAttestation,
    ModelRef,
    OpenWeightsAttestation,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_eu_residency_receipt,
    build_generated_content_receipt,
    build_granite_open_model_receipt,
    infer_provider,
    is_eea_or_adjacent,
    is_eu_region,
    is_granite_open_model,
    region_from_watsonx_url,
)
from .signer import (
    Ed25519Signer,
    IbmHpcsEd25519Signer,
    IbmKeyProtectEd25519Signer,
    Signer,
    verify,
)
from .version import __version__


def make_model(deployer_id: str, **kwargs):  # type: ignore[no-untyped-def]
    """Convenience factory: returns a LedgerProofModelInference instance."""
    return LedgerProofModelInference(deployer_id=deployer_id, **kwargs)


__all__ = [
    "LedgerProofModelInference",
    "make_model",
    "lpr_track",
    "emit_receipt",
    "Ed25519Signer",
    "IbmKeyProtectEd25519Signer",
    "IbmHpcsEd25519Signer",
    "Signer",
    "verify",
    "LogEmitter",
    "WebhookEmitter",
    "QueueEmitter",
    "IbmCloudLogsEmitter",
    "MultiEmitter",
    "StderrEmitter",
    "Emitter",
    "ReceiptV1",
    "ModelRef",
    "ContentRef",
    "ToolUseRef",
    "RegulatoryContext",
    "DataResidencyAttestation",
    "OpenWeightsAttestation",
    "SchemaName",
    "EU_WATSONX_REGIONS",
    "EEA_AND_ADJACENT_REGIONS",
    "build_chatbot_session_receipt",
    "build_generated_content_receipt",
    "build_eu_residency_receipt",
    "build_granite_open_model_receipt",
    "make_eu_residency_attestation",
    "make_granite_attestation",
    "infer_provider",
    "is_eu_region",
    "is_eea_or_adjacent",
    "is_granite_open_model",
    "region_from_watsonx_url",
    "canonical_encode",
    "canonical_hash",
    "hash_text",
    "hash_bytes",
    "IncrementalTextHasher",
    "extract_assistant_text",
    "extract_tool_uses",
    "extract_user_message_text",
    "extract_user_prompt_from_generate",
    "build_model_ref",
    "__version__",
]
