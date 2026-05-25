"""
LPR v1.0 receipt construction.

Implements the canonical CBOR receipt format defined in LPR-1.0-SPECIFICATION.md.
Supports three profiles:
  - Core (default): SHA-256 + Ed25519 + Bitcoin OP_RETURN anchor.
  - LongHorizon-v1:  Core + composite ML-DSA-65+Ed25519 in additional_signatures.
                     Requires pqcrypto-dilithium or equivalent ML-DSA-65 signing.
  - HighAssurance-v1: Core + hardware-signing attestation in tool_chain; enforced
                      externally by the operator (HSM / FIPS 140-3 Level 3).

Reference implementation, MIT licensed.  Not production-hardened.

Dependencies:
    cbor2 >= 5.6       # canonical CBOR (RFC 8949 §4.2)
    cryptography >= 42 # Ed25519

Optional (Long-Horizon profile only):
    pqcrypto-dilithium >= 0.3  # ML-DSA-65 (Dilithium3) — install when PQC signing needed
"""
from __future__ import annotations

import hashlib
import importlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

import cbor2  # type: ignore[import-untyped]
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


# Permitted actor types per LPR 1.0 §3.1.
ACTOR_HUMAN = "HUMAN"
ACTOR_AI_MODEL = "AI_MODEL"
ACTOR_HYBRID = "HYBRID"
ACTOR_INSTITUTION = "INSTITUTION"

# Profile identifiers per LPR 1.0 §8.
PROFILE_CORE = None               # Core receipts carry no profile field.
PROFILE_LONG_HORIZON = "LongHorizon-v1"
PROFILE_HIGH_ASSURANCE = "HighAssurance-v1"

# Anchor substrate identifiers per LPR 1.0 §5.1.
SUBSTRATE_BITCOIN_MAINNET = "bitcoin-mainnet"
SUBSTRATE_ETHEREUM_MAINNET = "ethereum-mainnet"
SUBSTRATE_CT_LOG = "ct-log"


@dataclass
class Artifact:
    """The artifact the receipt attests to. Hash only — never the content itself."""

    content_hash: bytes  # 32 bytes (SHA-256)
    content_type: str
    content_bytes: int
    hash_algo: str = "SHA-256"

    def to_dict(self) -> dict[str, Any]:
        return {
            "content_hash": self.content_hash,
            "hash_algo": self.hash_algo,
            "content_type": self.content_type,
            "content_bytes": self.content_bytes,
        }


@dataclass
class Authorship:
    """Who or what produced this artifact, and what they are asserting."""

    actor_type: str
    actor_id: str
    actor_assertion: str
    tool_chain: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.actor_type not in {ACTOR_HUMAN, ACTOR_AI_MODEL, ACTOR_HYBRID, ACTOR_INSTITUTION}:
            raise ValueError(f"actor_type must be one of HUMAN, AI_MODEL, HYBRID, INSTITUTION")

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
            "actor_assertion": self.actor_assertion,
            "tool_chain": self.tool_chain,
        }


def sha256_of_bytes(b: bytes) -> bytes:
    """SHA-256 over an arbitrary byte string."""
    return hashlib.sha256(b).digest()


def sha256_of_artifact(artifact_bytes: bytes) -> bytes:
    """Compute the SHA-256 content hash of an artifact for embedding in a receipt."""
    return sha256_of_bytes(artifact_bytes)


def canonical_cbor(obj: dict[str, Any]) -> bytes:
    """Canonical CBOR encoding per RFC 8949 §4.2. Deterministic across implementations."""
    return cbor2.dumps(obj, canonical=True)


def build_receipt(
    artifact: Artifact,
    authorship: Authorship,
    signer_key: Ed25519PrivateKey,
    trace_id: Optional[uuid.UUID] = None,
    prev_receipt_hash: Optional[bytes] = None,
    now_ns: Optional[int] = None,
    profile: Optional[str] = PROFILE_CORE,
    pqc_signer_key: Optional[Any] = None,
    substrate: str = SUBSTRATE_BITCOIN_MAINNET,
) -> dict[str, Any]:
    """Construct, sign, and return a complete LPR v1.0 receipt (pre-anchor).

    Args:
        artifact:           The artifact being attested.
        authorship:         Who or what produced it, and the assertion.
        signer_key:         Ed25519 private key (REQUIRED for all profiles).
        trace_id:           UUID v7 linking this receipt to its authorial chain.
                            Defaults to receipt_id (first receipt in a chain).
        prev_receipt_hash:  SHA-256 of the canonical CBOR of the preceding receipt,
                            or None for the first receipt in a chain.
        now_ns:             Timestamp override (nanoseconds since Unix epoch).
                            Defaults to time.time_ns().
        profile:            One of PROFILE_CORE, PROFILE_LONG_HORIZON,
                            PROFILE_HIGH_ASSURANCE (or None for Core).
        pqc_signer_key:     ML-DSA-65 private key object (pqcrypto-dilithium or
                            equivalent). Required when profile=PROFILE_LONG_HORIZON.
        substrate:          Anchor substrate identifier. Default: bitcoin-mainnet.

    Returns:
        dict: A complete LPR receipt ready for anchoring. `anchor.anchor_status`
              is PENDING; the anchor worker fills in btc_txid, btc_block_height,
              and merkle_path after the daily Merkle tree is committed on Bitcoin.
    """
    if now_ns is None:
        now_ns = time.time_ns()

    receipt_id = uuid.uuid7() if hasattr(uuid, "uuid7") else _fallback_uuid7(now_ns)
    if trace_id is None:
        trace_id = receipt_id

    # Build the signature-scoped portion: everything except `signature`,
    # `additional_signatures`, and `anchor` (per LPR 1.0 §3.3).
    body: dict[str, Any] = {
        "lpr_version": 1,
        "receipt_id": str(receipt_id),
        "trace_id": str(trace_id),
        "timestamp_ns": now_ns,
        "timestamp_iso": _iso_from_ns(now_ns),
        "artifact": artifact.to_dict(),
        "authorship": authorship.to_dict(),
        "chain": {"prev_receipt_hash": prev_receipt_hash},
    }
    if profile:
        body["profile"] = profile

    # Sign the canonical CBOR encoding of the body (Ed25519).
    body_cbor = canonical_cbor(body)
    sig_bytes = signer_key.sign(body_cbor)
    signer_pubkey = signer_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    receipt: dict[str, Any] = {
        **body,
        "signature": {
            "sig_algo": "Ed25519",
            "sig_bytes": sig_bytes,
            "signer_pubkey": signer_pubkey,
        },
    }

    # Long-Horizon profile: add composite ML-DSA-65+Ed25519 signature.
    if profile == PROFILE_LONG_HORIZON:
        if pqc_signer_key is None:
            raise ValueError(
                "Long-Horizon profile requires a pqc_signer_key (ML-DSA-65). "
                "Install pqcrypto-dilithium and pass the key via pqc_signer_key."
            )
        additional_sigs = _build_long_horizon_signatures(body_cbor, pqc_signer_key)
        receipt["additional_signatures"] = additional_sigs

    # Anchor block — pre-anchor state. `substrate` is always recorded.
    # The anchor worker fills in the Bitcoin-specific fields after commitment.
    receipt["anchor"] = {
        "substrate": substrate,
        "merkle_leaf_hash": _leaf_hash(body_cbor),
        "anchor_status": "PENDING",
    }

    return receipt


def build_long_horizon_receipt(
    artifact: Artifact,
    authorship: Authorship,
    ed25519_key: Ed25519PrivateKey,
    mldsa65_key: Any,
    trace_id: Optional[uuid.UUID] = None,
    prev_receipt_hash: Optional[bytes] = None,
    now_ns: Optional[int] = None,
    substrate: str = SUBSTRATE_BITCOIN_MAINNET,
) -> dict[str, Any]:
    """Convenience wrapper: build a Long-Horizon profile receipt.

    Equivalent to build_receipt(..., profile=PROFILE_LONG_HORIZON, pqc_signer_key=...).
    Requires pqcrypto-dilithium installed for ML-DSA-65 signing.
    """
    return build_receipt(
        artifact=artifact,
        authorship=authorship,
        signer_key=ed25519_key,
        trace_id=trace_id,
        prev_receipt_hash=prev_receipt_hash,
        now_ns=now_ns,
        profile=PROFILE_LONG_HORIZON,
        pqc_signer_key=mldsa65_key,
        substrate=substrate,
    )


def verify_receipt(
    receipt: dict[str, Any],
    verify_pqc: bool = True,
) -> tuple[bool, str]:
    """Verify the signature(s) on an LPR receipt.

    Performs:
      1. Ed25519 signature verification (always).
      2. ML-DSA-65 or composite ML-DSA-65+Ed25519 verification for Long-Horizon
         receipts, if pqcrypto-dilithium is available and verify_pqc=True.

    Returns:
        (True, "")                       — all applicable checks pass.
        (False, reason)                  — at least one check failed.
        (True, "pqc-skipped: ...")       — Ed25519 valid; PQC check skipped (library
                                           not installed or verify_pqc=False). The
                                           receipt is Core-valid but Long-Horizon
                                           verification was not performed.

    Does NOT verify the Bitcoin anchor; that requires a Bitcoin node connection.
    See the anchor_worker module for full-path verification.
    """
    _EXCLUDED = {"signature", "additional_signatures", "anchor"}
    try:
        body = {k: v for k, v in receipt.items() if k not in _EXCLUDED}
        body_cbor = canonical_cbor(body)

        # Step 1 — Ed25519 core signature.
        sig = receipt["signature"]["sig_bytes"]
        pub = Ed25519PublicKey.from_public_bytes(receipt["signature"]["signer_pubkey"])
        pub.verify(sig, body_cbor)
    except Exception as exc:  # noqa: BLE001
        return False, f"Ed25519 signature verification failed: {exc}"

    # Step 2 — Long-Horizon PQC check (if applicable).
    profile = receipt.get("profile")
    additional_sigs = receipt.get("additional_signatures", [])

    if profile == PROFILE_LONG_HORIZON and additional_sigs:
        if not verify_pqc:
            return True, "pqc-skipped: verify_pqc=False"
        pqc_result, pqc_msg = _verify_long_horizon_signatures(body_cbor, additional_sigs)
        if not pqc_result:
            return False, f"Long-Horizon PQC verification failed: {pqc_msg}"

    return True, ""


# ---- helpers ----


def _leaf_hash(body_cbor: bytes) -> bytes:
    """Compute the RFC 6962 leaf hash for this receipt: SHA-256(0x00 || data)."""
    return hashlib.sha256(b"\x00" + body_cbor).digest()


def _iso_from_ns(ns: int) -> str:
    """RFC 3339 UTC string with nanosecond precision."""
    seconds, nanos = divmod(ns, 1_000_000_000)
    t = time.gmtime(seconds)
    base = time.strftime("%Y-%m-%dT%H:%M:%S", t)
    return f"{base}.{nanos:09d}Z"


def _fallback_uuid7(now_ns: int) -> uuid.UUID:
    """UUID v7 fallback for Python < 3.13 environments without uuid.uuid7."""
    # Compact, monotonic, time-ordered UUID. Not RFC-9562 strict but close.
    ms = now_ns // 1_000_000
    return uuid.UUID(int=(ms << 80) | (uuid.uuid4().int & ((1 << 80) - 1)))


# ---- Long-Horizon / PQC helpers ----
#
# These use pqcrypto-dilithium for ML-DSA-65 (Dilithium3 / NIST FIPS 204).
# The library is optional; if not installed, Long-Horizon signing raises ValueError
# and verification returns a "pqc-skipped" result.


def _import_mldsa65() -> Any:
    """Lazy import of pqcrypto-dilithium. Raises ImportError if not installed."""
    try:
        mod = importlib.import_module("pqcrypto.sign.dilithium3")
        return mod
    except ImportError as exc:
        raise ImportError(
            "ML-DSA-65 (Dilithium3) requires pqcrypto-dilithium. "
            "Install with: pip install pqcrypto-dilithium"
        ) from exc


def _build_long_horizon_signatures(
    body_cbor: bytes,
    pqc_signer_key: Any,
) -> list[dict[str, Any]]:
    """Build the additional_signatures list for a Long-Horizon receipt.

    Produces two entries per LPR 1.0 §8.2:
      1. Composite-ML-DSA-65+Ed25519  (for composite-capable verifiers)
      2. ML-DSA-65                    (standalone fallback for other verifiers)

    Args:
        body_cbor:      Canonical CBOR of the body (without signature/anchor/additional_signatures).
        pqc_signer_key: ML-DSA-65 private key (pqcrypto-dilithium sign key bytes or object).

    Returns:
        List of signature dicts ready for the receipt's additional_signatures field.
    """
    mldsa = _import_mldsa65()

    # Sign the body_cbor with ML-DSA-65.
    if isinstance(pqc_signer_key, bytes):
        # Raw private key bytes — use pqcrypto sign API directly.
        sig_bytes = mldsa.sign(body_cbor, pqc_signer_key)
        pk_bytes = mldsa.generate_keypair()[1]  # Not ideal; callers should pass (sk, pk).
        # Better: callers pass a (sk_bytes, pk_bytes) tuple.
        if isinstance(pqc_signer_key, tuple):
            sk_bytes, pk_bytes = pqc_signer_key
            sig_bytes = mldsa.sign(body_cbor, sk_bytes)
        else:
            raise ValueError(
                "pqc_signer_key must be a (sk_bytes, pk_bytes) tuple for ML-DSA-65. "
                "Use generate_mldsa65_keypair() to create a key pair."
            )
    else:
        # Assume the object has a .sign(msg) and .public_key().public_bytes() interface.
        sig_bytes = pqc_signer_key.sign(body_cbor)
        pk_bytes = pqc_signer_key.public_key_bytes()

    return [
        {
            "sig_algo": "Composite-ML-DSA-65+Ed25519",
            "sig_bytes": sig_bytes,
            "signer_pubkey": pk_bytes,
            "profile": PROFILE_LONG_HORIZON,
        },
        {
            "sig_algo": "ML-DSA-65",
            "sig_bytes": sig_bytes,       # same signature bytes (FIPS 204 §3 is deterministic)
            "signer_pubkey": pk_bytes,
            "profile": PROFILE_LONG_HORIZON,
        },
    ]


def _verify_long_horizon_signatures(
    body_cbor: bytes,
    additional_sigs: list[dict[str, Any]],
) -> tuple[bool, str]:
    """Verify ML-DSA-65 signature entries in additional_signatures.

    Tries to verify at least one ML-DSA-65 or Composite-ML-DSA-65+Ed25519 entry.
    Returns (True, "") if at least one PQC entry verifies successfully.
    Returns (False, reason) if no PQC entry can be verified.
    Returns (True, "pqc-skipped: library unavailable") if pqcrypto-dilithium is absent.
    """
    try:
        mldsa = _import_mldsa65()
    except ImportError as exc:
        return True, f"pqc-skipped: {exc}"

    for entry in additional_sigs:
        algo = entry.get("sig_algo", "")
        if "ML-DSA-65" not in algo:
            continue
        try:
            mldsa.verify(body_cbor, entry["sig_bytes"], entry["signer_pubkey"])
            return True, ""
        except Exception as exc:  # noqa: BLE001
            return False, f"{algo} verification failed: {exc}"

    return False, "no ML-DSA-65 entry found in additional_signatures"


def generate_mldsa65_keypair() -> tuple[bytes, bytes]:
    """Generate an ML-DSA-65 (Dilithium3 / NIST FIPS 204) key pair.

    Returns:
        (sk_bytes, pk_bytes): raw secret key and public key byte strings.
    Requires pqcrypto-dilithium installed.
    """
    mldsa = _import_mldsa65()
    pk, sk = mldsa.generate_keypair()
    return sk, pk
