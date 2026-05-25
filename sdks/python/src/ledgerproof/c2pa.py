"""C2PA assertion bridge — produce/consume ``org.ledgerproof.receipt.v1`` assertions.

C2PA Content Credentials embed provenance metadata in a file's manifest.
LedgerProof complements C2PA by anchoring the same content's identity to
Bitcoin — meaning that even when a C2PA manifest is stripped (which it
routinely is by social platforms and re-encoding pipelines), the LPR receipt
remains discoverable by content hash.

This module provides:

- :func:`build_assertion` — given an LPR :class:`Receipt`, produce the
  ``org.ledgerproof.receipt.v1`` assertion dict for embedding in a C2PA
  manifest.
- :func:`extract_assertion` — given a C2PA manifest dict, find and return
  the LPR assertion, or None.
- :func:`verify_assertion` — given an extracted assertion, fetch the live
  receipt and confirm the embedded hashes match.

This is a thin specification helper, not a full C2PA toolkit. For full
C2PA manifest construction, use ``c2pa-python`` (the official C2PA SDK)
and pass the result of :func:`build_assertion` as one of your assertions.

See ``04-lpr-spec/C2PA-ASSERTION-SPEC.md`` in the ledgerproof-eu repo for
the assertion structure rationale and registration status.
"""

from __future__ import annotations

from typing import Any, Optional

from .canonical import sha256_hex
from .client import LedgerProof
from .types import Receipt

ASSERTION_LABEL = "org.ledgerproof.receipt.v1"


def build_assertion(
    receipt: Receipt,
    *,
    artifact_hash: str,
    api_base: str = "https://api-eu.ledgerproofhq.io",
    profile_version: str = "EU-AI-ACT-50-v1.1",
    transparency_marker: str = "LPR-EU-AI-ACT-50",
    anchor_substrate: str = "bitcoin-mainnet",
    anchor_status: str = "PENDING",
    anchor_btc_txid: Optional[str] = None,
    anchor_btc_height: Optional[int] = None,
) -> dict[str, Any]:
    """Build the C2PA assertion dict for an LPR receipt.

    Pair this with a c2pa-python ``ManifestBuilder.add_assertion()`` call,
    using ``label = "org.ledgerproof.receipt.v1"`` and ``data =`` the dict
    returned here.

    :param receipt: The :class:`Receipt` returned by ``LedgerProof.publish_*``.
    :param artifact_hash: SHA-256 of the artifact (the same hash the C2PA
        manifest will identify the artifact by — they MUST match).
    :param api_base: LedgerProof operator base URL. Defaults to EU.
    :param profile_version: LPR profile version tag.
    :param transparency_marker: Human-readable disclosure string.
    :param anchor_substrate: ``"bitcoin-mainnet"`` (default), or the substrate
        identifier for an alternate-profile receipt.
    :param anchor_status: ``"PENDING"`` immediately after publish; the
        anchor worker upgrades to ``"ANCHORED"`` then ``"CONFIRMED"`` as
        Bitcoin confirmations accumulate. Update the assertion if you
        re-embed later.
    :param anchor_btc_txid: Bitcoin transaction ID, once anchored.
    :param anchor_btc_height: Bitcoin block height, once confirmed.
    :returns: A dict suitable for use as the ``data`` of a C2PA assertion.
    """
    return {
        "receipt_id": str(getattr(receipt, "receipt_id", "") or receipt.entry_hash),
        "entry_hash": receipt.entry_hash,
        "verify_url": f"{api_base.rstrip('/')}/v1/verify/{receipt.sequence}",
        "anchor_substrate": anchor_substrate,
        "anchor_status": anchor_status,
        "anchor_btc_txid": anchor_btc_txid or "",
        "anchor_btc_height": anchor_btc_height or 0,
        "artifact_hash": artifact_hash,
        "profile_version": profile_version,
        "transparency_marker": transparency_marker,
    }


def extract_assertion(manifest: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Find the LPR assertion in a parsed C2PA manifest, or None.

    Walks ``manifest["assertions"]`` looking for ``label == ASSERTION_LABEL``.
    Returns the assertion's ``data`` dict, or None if absent.

    :param manifest: A parsed C2PA manifest (the dict produced by
        ``c2pa-python``'s ``Reader.json()`` or equivalent).
    """
    assertions = manifest.get("assertions") or []
    if isinstance(assertions, dict):
        # Some C2PA tooling represents assertions as a label-keyed dict.
        data = assertions.get(ASSERTION_LABEL)
        if isinstance(data, dict):
            return data.get("data") if "data" in data else data
        return None
    for assertion in assertions:
        if not isinstance(assertion, dict):
            continue
        if assertion.get("label") == ASSERTION_LABEL:
            data = assertion.get("data")
            return data if isinstance(data, dict) else None
    return None


def verify_assertion(
    assertion: dict[str, Any],
    *,
    artifact: bytes | str,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    """Verify an extracted LPR assertion against the live receipt.

    Checks:

    1. ``artifact_hash`` in the assertion matches SHA-256(artifact) locally.
    2. The receipt at ``verify_url`` exists and its ``entry_hash`` matches.
    3. (Optional) Bitcoin anchor status is currently ``ANCHORED`` or
       ``CONFIRMED`` — caller can choose to enforce.

    :param assertion: The assertion dict from :func:`extract_assertion`.
    :param artifact: The artifact bytes (or text) to verify against. The
        SHA-256 is computed locally.
    :param api_key: Optional — only required if the receipt's operator
        requires authentication for verify (the default EU operator does not).
    :returns: A verification result dict with keys ``valid`` (bool),
        ``artifact_hash_match`` (bool), ``entry_hash_match`` (bool),
        ``anchor_status``, ``receipt`` (the parsed EntryResponse, or None).
    """
    artifact_hash_local = sha256_hex(artifact)
    artifact_hash_match = artifact_hash_local == assertion.get("artifact_hash")

    # Use the verify_url directly. Parse base + sequence.
    verify_url = assertion.get("verify_url", "")
    parts = verify_url.rstrip("/").rsplit("/", 1)
    if len(parts) != 2 or not parts[1].isdigit():
        return {
            "valid": False,
            "artifact_hash_match": artifact_hash_match,
            "entry_hash_match": False,
            "anchor_status": None,
            "receipt": None,
            "error": "malformed verify_url",
        }
    sequence = int(parts[1])
    # Base from verify_url: drop /v1/verify/{n}
    api_base = parts[0].rsplit("/v1/", 1)[0]

    # Use a temporary LedgerProof client just to invoke the public verify endpoint.
    lp = LedgerProof(
        publisher_id="DID:verifier-only",  # not used for unauthenticated verify
        deployer_country="XX",
        api_key=api_key or "noop",
        api_base=api_base,
    )
    try:
        entry = lp.verify(sequence)
        entry_hash_match = entry.entry_hash == assertion.get("entry_hash")
        return {
            "valid": artifact_hash_match and entry_hash_match,
            "artifact_hash_match": artifact_hash_match,
            "entry_hash_match": entry_hash_match,
            "anchor_status": assertion.get("anchor_status"),
            "receipt": entry,
            "error": None,
        }
    except Exception as exc:
        return {
            "valid": False,
            "artifact_hash_match": artifact_hash_match,
            "entry_hash_match": False,
            "anchor_status": None,
            "receipt": None,
            "error": str(exc),
        }
    finally:
        lp.close()


__all__ = [
    "ASSERTION_LABEL",
    "build_assertion",
    "extract_assertion",
    "verify_assertion",
]
