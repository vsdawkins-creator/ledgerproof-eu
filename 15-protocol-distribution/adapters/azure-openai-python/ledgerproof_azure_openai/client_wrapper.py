"""Sync client wrapper for Azure OpenAI.

`LedgerProofAzureOpenAI` wraps `openai.AzureOpenAI` and intercepts
`chat.completions.create()` calls. For non-streaming requests, the receipt is
emitted once the full response is in hand. For streaming requests, we wrap the
returned iterator with a stream-aware SHA-256 (constraint **C6**) and emit the
receipt when the stream is fully drained.

Constraint **C7**: the Azure OpenAI response object is returned unmodified.

Azure-specific provenance (deployment, endpoint, region, api_version, tenant
hash, subscription hash) is sourced from the wrapper's `regulatory_context`
and from the underlying client's configuration where available.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import uuid
from typing import Any, Iterator

from openai import AzureOpenAI

from .canonical import canonical_encode
from .emitter import Emitter, LogEmitter
from .schema import build_receipt
from .signer import Ed25519Signer, Signer
from .version import __version__


# Schemas requiring Azure provenance fields.
_AZURE_PROVENANCE_SCHEMAS = {
    "azure_enterprise_session/v1",
    "azure_ad_authenticated_session/v1",
}


def _hash_messages(messages: list[dict[str, Any]] | None) -> str:
    if not messages:
        return hashlib.sha256(b"").hexdigest()
    payload = json.dumps(messages, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hash_non_streaming_response(response: Any) -> str:
    parts: list[str] = []
    for choice in getattr(response, "choices", None) or []:
        msg = getattr(choice, "message", None)
        if msg and getattr(msg, "content", None):
            parts.append(msg.content)
    return hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()


def _extract_chunk_text(chunk: Any) -> str:
    """Pull incremental assistant text out of a ChatCompletionChunk."""
    text = ""
    for choice in getattr(chunk, "choices", None) or []:
        delta = getattr(choice, "delta", None)
        if delta is None:
            continue
        content = getattr(delta, "content", None)
        if content:
            text += content
    return text


_REGION_FROM_HOST_RE = re.compile(r"^(?P<resource>[^.]+)\.openai\.azure\.com$")
# Map of common region suffixes to canonical Azure region names. Best-effort —
# the regulatory_context["azure_region"] override always wins.
_REGION_HINT_SUFFIXES = {
    "weu": "westeurope",
    "neu": "northeurope",
    "frc": "francecentral",
    "swc": "swedencentral",
    "swn": "switzerlandnorth",
    "itn": "italynorth",
    "gwc": "germanywestcentral",
    "ukw": "ukwest",
    "uks": "uksouth",
}


def _guess_region_from_endpoint(endpoint: str | None) -> str | None:
    if not endpoint:
        return None
    try:
        host = urllib.parse.urlparse(endpoint).hostname or ""
    except Exception:  # noqa: BLE001
        return None
    m = _REGION_FROM_HOST_RE.match(host)
    if not m:
        return None
    resource = m.group("resource")
    for suffix, region in _REGION_HINT_SUFFIXES.items():
        if resource.endswith(f"-{suffix}") or resource.endswith(suffix):
            return region
    return None


class _SignedReceiptBuilder:
    """Shared receipt-building helper used by sync + async wrappers."""

    def __init__(
        self,
        *,
        deployer_id: str,
        regulatory_context: dict[str, Any],
        signer: Signer,
        emitter: Emitter,
        azure_endpoint: str | None,
        api_version: str | None,
    ) -> None:
        self.deployer_id = deployer_id
        self.regulatory_context = regulatory_context
        self.signer = signer
        self.emitter = emitter
        self.azure_endpoint = azure_endpoint
        self.api_version = api_version

    def emit(
        self,
        *,
        model_id: str,
        interaction_id: str,
        prompt_sha256: str,
        response_sha256: str,
        azure_deployment: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        schema_id = self.regulatory_context.get("schema", "chatbot_session/v1")
        ctx = self.regulatory_context

        fields: dict[str, Any] = dict(
            deployer_id=self.deployer_id,
            model_id=model_id,
            interaction_id=interaction_id,
            prompt_sha256=prompt_sha256,
            response_sha256=response_sha256,
            user_pseudonym=ctx.get("user_pseudonym"),
            jurisdiction=ctx.get("jurisdiction", "EU"),
            extra=extra or {},
        )

        if schema_id in _AZURE_PROVENANCE_SCHEMAS:
            endpoint = ctx.get("azure_endpoint") or self.azure_endpoint
            if not endpoint:
                raise ValueError(
                    "Schema "
                    f"{schema_id!r} requires azure_endpoint; provide it in "
                    "regulatory_context['azure_endpoint'] or via the client "
                    "constructor."
                )
            fields["azure_endpoint"] = endpoint
            fields["azure_deployment"] = (
                ctx.get("azure_deployment")
                or azure_deployment
                or model_id  # in Azure, model arg = deployment name
            )
            fields["azure_region"] = (
                ctx.get("azure_region") or _guess_region_from_endpoint(endpoint)
            )
            fields["api_version"] = ctx.get("api_version") or self.api_version
            if "tenant_id_hash" in ctx:
                fields["tenant_id_hash"] = ctx["tenant_id_hash"]
            if "subscription_id_hash" in ctx:
                fields["subscription_id_hash"] = ctx["subscription_id_hash"]
            if schema_id == "azure_ad_authenticated_session/v1":
                if "azure_ad_principal_hash" not in ctx:
                    raise ValueError(
                        "azure_ad_authenticated_session/v1 requires "
                        "regulatory_context['azure_ad_principal_hash']."
                    )
                fields["azure_ad_principal_hash"] = ctx["azure_ad_principal_hash"]
                if "azure_ad_principal_type" in ctx:
                    fields["azure_ad_principal_type"] = ctx["azure_ad_principal_type"]
                if "auth_method" in ctx:
                    fields["auth_method"] = ctx["auth_method"]

        receipt = build_receipt(schema_id, **fields)
        receipt_dict = receipt.model_dump()
        signature = self.signer.sign(canonical_encode(receipt_dict))
        envelope = {
            "receipt": receipt_dict,
            "signature": signature.hex(),
            "signature_alg": "ed25519",
            "public_key": self.signer.public_key_bytes().hex(),
            "adapter": {
                "name": "ledgerproof-azure-openai",
                "version": __version__,
            },
        }
        self.emitter.emit(envelope)
        return envelope


class _StreamingProxy:
    """Wraps a streaming response iterator and emits a receipt on drain."""

    def __init__(
        self,
        stream: Iterator[Any],
        *,
        builder: _SignedReceiptBuilder,
        prompt_sha256: str,
        fallback_interaction_id: str,
        azure_deployment: str | None,
    ) -> None:
        self._stream = stream
        self._builder = builder
        self._prompt_sha256 = prompt_sha256
        self._fallback_interaction_id = fallback_interaction_id
        self._azure_deployment = azure_deployment
        self._hasher = hashlib.sha256()
        self._model_id = "unknown"
        self._interaction_id: str | None = None
        self._emitted = False

    def __iter__(self) -> "_StreamingProxy":
        return self

    def __next__(self) -> Any:
        try:
            chunk = next(self._stream)
        except StopIteration:
            self._flush()
            raise
        self._absorb(chunk)
        return chunk

    def __enter__(self) -> "_StreamingProxy":
        return self

    def __exit__(self, *exc: Any) -> None:
        self._flush()
        close = getattr(self._stream, "close", None)
        if callable(close):
            close()

    def _absorb(self, chunk: Any) -> None:
        if self._interaction_id is None:
            self._interaction_id = getattr(chunk, "id", None)
        model = getattr(chunk, "model", None)
        if model:
            self._model_id = model
        text = _extract_chunk_text(chunk)
        if text:
            self._hasher.update(text.encode("utf-8"))

    def _flush(self) -> None:
        if self._emitted:
            return
        self._emitted = True
        try:
            self._builder.emit(
                model_id=self._model_id,
                interaction_id=self._interaction_id
                or self._fallback_interaction_id,
                prompt_sha256=self._prompt_sha256,
                response_sha256=self._hasher.hexdigest(),
                azure_deployment=self._azure_deployment,
                extra={"streaming": True},
            )
        except Exception:  # noqa: BLE001
            # C7: receipt failure must never break the caller path
            pass


class _ChatCompletionsProxy:
    """Intercepts `client.chat.completions.create(...)`."""

    def __init__(self, inner: Any, builder: _SignedReceiptBuilder) -> None:
        self._inner = inner
        self._builder = builder

    def create(self, *args: Any, **kwargs: Any) -> Any:
        messages = kwargs.get("messages")
        prompt_sha256 = _hash_messages(messages)
        streaming = bool(kwargs.get("stream"))
        # In Azure OpenAI, `model` is the deployment name.
        azure_deployment = kwargs.get("model")
        result = self._inner.create(*args, **kwargs)

        if streaming:
            return _StreamingProxy(
                result,
                builder=self._builder,
                prompt_sha256=prompt_sha256,
                fallback_interaction_id=str(uuid.uuid4()),
                azure_deployment=azure_deployment,
            )

        try:
            self._builder.emit(
                model_id=getattr(result, "model", azure_deployment or "unknown"),
                interaction_id=getattr(result, "id", None) or str(uuid.uuid4()),
                prompt_sha256=prompt_sha256,
                response_sha256=_hash_non_streaming_response(result),
                azure_deployment=azure_deployment,
            )
        except Exception:  # noqa: BLE001
            # C7: receipt failure must never break the caller path
            pass
        return result

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class _ChatProxy:
    def __init__(self, inner: Any, builder: _SignedReceiptBuilder) -> None:
        self._inner = inner
        self._builder = builder
        self.completions = _ChatCompletionsProxy(inner.completions, builder)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class LedgerProofAzureOpenAI:
    """Wraps `openai.AzureOpenAI`. Same call surface; emits receipts on the side.

    Parameters
    ----------
    deployer_id:
        URN identifying the deployer organisation,
        e.g. `urn:eu:deployer:contoso-bank`.
    regulatory_context:
        Optional dict carrying `schema`, `jurisdiction`, `user_pseudonym`,
        `azure_endpoint`, `azure_deployment`, `azure_region`, `api_version`,
        `tenant_id_hash`, `subscription_id_hash`,
        `azure_ad_principal_hash`, `azure_ad_principal_type`, `auth_method`.
    signer:
        Optional `Signer`. Defaults to an ephemeral `Ed25519Signer` (MVP only).
    emitter:
        Optional `Emitter`. Defaults to `LogEmitter()` (stdout).
    azure_client:
        Optional pre-built `openai.AzureOpenAI` instance. If omitted, one is
        built with the remaining `**azure_kwargs`.
    azure_kwargs:
        Forwarded to `openai.AzureOpenAI(...)` if `azure_client` is omitted.
        Typical keys: `azure_endpoint`, `api_key`, `api_version`,
        `azure_ad_token`, `azure_ad_token_provider`, `azure_deployment`.
    """

    def __init__(
        self,
        deployer_id: str,
        *,
        regulatory_context: dict[str, Any] | None = None,
        signer: Signer | None = None,
        emitter: Emitter | None = None,
        azure_client: AzureOpenAI | None = None,
        **azure_kwargs: Any,
    ) -> None:
        self._client = azure_client or AzureOpenAI(**azure_kwargs)

        # Best-effort introspection of the constructed Azure client so receipts
        # can capture endpoint + api_version without the caller restating them.
        endpoint = (
            azure_kwargs.get("azure_endpoint")
            or getattr(self._client, "_azure_endpoint", None)
            or getattr(getattr(self._client, "base_url", None), "host", None)
        )
        api_version = azure_kwargs.get("api_version") or getattr(
            self._client, "_api_version", None
        )

        self._builder = _SignedReceiptBuilder(
            deployer_id=deployer_id,
            regulatory_context=regulatory_context or {},
            signer=signer or Ed25519Signer(),
            emitter=emitter or LogEmitter(),
            azure_endpoint=endpoint if isinstance(endpoint, str) else None,
            api_version=api_version if isinstance(api_version, str) else None,
        )
        self.chat = _ChatProxy(self._client.chat, self._builder)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)
