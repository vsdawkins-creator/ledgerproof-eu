"""Canonical JSON serialization and content hashing.

The single most safety-critical module in the SDK. Every byte produced here
must match what the LPR Rust server produces when it re-serializes the same
JSON value, or signatures will not verify and receipts will not issue.

The contract is:

  canonical_json(obj) == server's serde_json::to_string(value) where
  value was parsed from any JSON encoding of the same logical object.

This holds because the server parses our JSON into ``serde_json::Value`` and
then re-serializes for hashing. Since ``Value`` uses ``IndexMap`` (insertion-
ordered), the round-trip is stable ONLY IF both sides emit keys in the same
order. We achieve that by sorting on the way in.

If you change this module, regenerate the byte-for-byte fixtures in
``tests/fixtures/canonical/`` against the live Rust server and commit them
alongside.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(obj: Any) -> str:
    """Serialize ``obj`` to compact, deterministically sorted JSON.

    Matches the LPR server's ``serde_json::to_string()`` output when the
    server parses our payload into a ``serde_json::Value`` and re-emits it.

    Properties:
    - Keys sorted lexicographically at every depth.
    - Compact separators (no whitespace between tokens).
    - ASCII-safe (``ensure_ascii=True``) so non-ASCII characters are
      escaped, matching Rust's default JSON behavior for strings.
    - No NaN, Infinity, or -Infinity (raises ``ValueError`` if present).

    :param obj: Any JSON-serializable value (dict, list, str, int, float,
        bool, None).
    :returns: A canonical JSON string ready for SHA-256 hashing or
        transmission as ``entry_json_canonical``.
    :raises ValueError: If ``obj`` contains a non-JSON-serializable value
        or a non-finite float.

    .. note::

       This function is intentionally not async and not retryable. It is
       a pure function. If you need to canonicalize many objects, just call
       it many times — the overhead is dominated by ``json.dumps`` which
       releases the GIL during work.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def sha256_hex(data: bytes | str) -> str:
    """Compute the lowercase-hex SHA-256 of ``data``.

    If ``data`` is a string, it is encoded as UTF-8 before hashing. The
    output is exactly 64 lowercase hexadecimal characters, matching the
    LPR specification's ``artifact_hash``, ``content_hash``, and
    ``entry_hash`` field formats.

    :param data: Bytes or string to hash.
    :returns: 64-character lowercase hex string.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def content_hash(content: dict[str, Any]) -> str:
    """SHA-256 of the canonical JSON encoding of a content payload.

    This is what gets stored in the receipt's ``content_hash`` field. The
    server re-computes the same hash from its own canonical re-serialization
    of the parsed ``content`` object; both hashes must match or publish
    is rejected.

    :param content: The Article 50 (or other) content payload as a dict.
    :returns: 64-character lowercase hex SHA-256.
    """
    return sha256_hex(canonical_json(content))


def entry_hash(entry: dict[str, Any]) -> str:
    """SHA-256 of the canonical JSON encoding of an entry.

    This is what the server stores in ``entry_hash`` and what the publisher
    must sign with its Ed25519 key. Used in the publish request and in
    every verifier path.

    :param entry: The entry envelope (sequence, prev_hash, content, etc.).
    :returns: 64-character lowercase hex SHA-256.
    """
    return sha256_hex(canonical_json(entry))


def artifact_hash(artifact: bytes | str) -> str:
    """SHA-256 of an artifact (the thing being attested to).

    The artifact itself never leaves the local machine; only this hash is
    transmitted to LedgerProof. If ``artifact`` is a string, it's encoded
    as UTF-8 first.

    :param artifact: Bytes (image, audio, video, file) or string (text).
    :returns: 64-character lowercase hex SHA-256.
    """
    return sha256_hex(artifact)


__all__ = [
    "artifact_hash",
    "canonical_json",
    "content_hash",
    "entry_hash",
    "sha256_hex",
]
