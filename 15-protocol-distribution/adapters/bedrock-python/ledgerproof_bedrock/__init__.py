"""
LedgerProof adapter for the AWS Bedrock Runtime Python SDK (boto3).

Side-channel cryptographic transparency receipts for EU AI Act Article 50.

Usage (drop-in wrapper):

    import boto3, json
    from ledgerproof_bedrock import LedgerProofBedrockClient

    raw = boto3.client("bedrock-runtime", region_name="eu-west-1")
    client = LedgerProofBedrockClient(deployer_id="acme-eu", client=raw)

    response = client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=json.dumps({"messages": [{"role": "user", "content": "Hi"}],
                         "anthropic_version": "bedrock-2023-05-31",
                         "max_tokens": 100}),
    )

The wrapper intercepts invoke_model, invoke_model_with_response_stream,
converse, and converse_stream. It emits a signed Ed25519 receipt to the
configured side-channel (stdout by default) AFTER the response is materialised.
The response object is returned UNCHANGED — constraint C7.

LedgerProof is an open protocol, Foundation-stewarded. It is NOT endorsed by
AWS, by any EU regulator, and does NOT establish an Article 40 presumption of
conformity. See README for the full disclaimer.
"""

from .canonical import (
    IncrementalTextHasher,
    canonical_encode,
    canonical_hash,
    hash_bytes,
    hash_text,
)
from .client_wrapper import LedgerProofBedrockClient
from .converse_wrapper import install_converse_methods
from .decorator import lpr_track
from .emitter import (
    CloudWatchEmitter,
    Emitter,
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
    extract_user_message_text_from_converse,
    extract_user_message_text_from_invoke_body,
    make_eu_residency_attestation,
)
from .schema import (
    EU_AWS_REGIONS,
    ContentRef,
    DataResidencyAttestation,
    ModelRef,
    ReceiptV1,
    RegulatoryContext,
    SchemaName,
    ToolUseRef,
    build_chatbot_session_receipt,
    build_cross_provider_receipt,
    build_eu_residency_receipt,
    build_generated_content_receipt,
    infer_provider,
    is_eu_region,
)
from .signer import (
    AwsKmsEd25519Signer,
    Ed25519Signer,
    GcpKmsEd25519Signer,
    Signer,
    verify,
)
from .version import __version__


def make_client(deployer_id: str, **kwargs):  # type: ignore[no-untyped-def]
    """
    Convenience factory: returns a LedgerProofBedrockClient with both the legacy
    (invoke_model) and Converse APIs wired up.
    """
    client = LedgerProofBedrockClient(deployer_id=deployer_id, **kwargs)
    install_converse_methods(client)
    return client


__all__ = [
    "LedgerProofBedrockClient",
    "install_converse_methods",
    "make_client",
    "lpr_track",
    "emit_receipt",
    "Ed25519Signer",
    "AwsKmsEd25519Signer",
    "GcpKmsEd25519Signer",
    "Signer",
    "verify",
    "LogEmitter",
    "WebhookEmitter",
    "QueueEmitter",
    "CloudWatchEmitter",
    "MultiEmitter",
    "StderrEmitter",
    "Emitter",
    "ReceiptV1",
    "ModelRef",
    "ContentRef",
    "ToolUseRef",
    "RegulatoryContext",
    "DataResidencyAttestation",
    "SchemaName",
    "EU_AWS_REGIONS",
    "build_chatbot_session_receipt",
    "build_generated_content_receipt",
    "build_cross_provider_receipt",
    "build_eu_residency_receipt",
    "make_eu_residency_attestation",
    "infer_provider",
    "is_eu_region",
    "canonical_encode",
    "canonical_hash",
    "hash_text",
    "hash_bytes",
    "IncrementalTextHasher",
    "extract_assistant_text",
    "extract_tool_uses",
    "extract_user_message_text_from_converse",
    "extract_user_message_text_from_invoke_body",
    "build_model_ref",
    "__version__",
]
