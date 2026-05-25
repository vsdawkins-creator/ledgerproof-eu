"""Ed25519 keypair management for LedgerProof signing.

Each publisher owns one or more signing keypairs. The private key signs each
receipt's ``entry_hash``; the public key is registered with the LedgerProof
operator at ``POST /v1/keys``. The server stores ``verifying_key_b64`` and
uses it to verify every subsequent publish from that ``key_id``.

This module handles:

- Generating fresh keypairs (``Keypair.generate()``).
- Loading from disk (``Keypair.load()``) — default path
  ``~/.config/ledgerproof/signing_key.bin`` with 0600 permissions.
- Loading from env var (``Keypair.from_env()``) — reads
  ``LEDGERPROOF_SIGNING_KEY_HEX`` for stateless deployments.
- Saving with secure permissions (``Keypair.save()``).
- Signing arbitrary bytes (``Keypair.sign()``).
- Exposing the base64-encoded public key for server registration.

It does **not** handle:

- Hardware HSMs — that lives in a future ``ledgerproof.hsm`` module for
  enterprise customers with a YubiHSM, AWS CloudHSM, or similar.
- Key rotation — that's a server-side concern initiated by the publisher
  via ``LedgerProof.rotate_key()``.
- Backup or recovery — the user is responsible for backing up the key file.
  We strongly recommend an offline encrypted backup; see the
  ``backup-to-encrypted-dmg.sh`` pattern in ``~/.ledgerproof-secrets``.
"""

from __future__ import annotations

import base64
import os
import stat
from pathlib import Path
from typing import Final

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .errors import KeyManagementError

# Default key store path. Users can override with ``LEDGERPROOF_KEY_PATH``.
_DEFAULT_KEY_DIR: Final = Path.home() / ".config" / "ledgerproof"
_DEFAULT_KEY_PATH: Final = _DEFAULT_KEY_DIR / "signing_key.bin"

# Required file permissions: rw for owner only (0600).
_SECURE_FILE_MODE: Final = 0o600
_SECURE_DIR_MODE: Final = 0o700


class Keypair:
    """An Ed25519 keypair used to sign LPR receipts.

    Always created via one of the class methods (``generate``, ``load``,
    ``from_env``, ``from_hex``) — the constructor takes the underlying
    cryptography object directly and is intended for internal use.

    Instances are immutable. To rotate, create a new ``Keypair`` and update
    your ``LedgerProof`` client.
    """

    __slots__ = ("_private",)

    def __init__(self, private_key: Ed25519PrivateKey) -> None:
        self._private = private_key

    # ── Construction ─────────────────────────────────────────────────────

    @classmethod
    def generate(cls) -> Keypair:
        """Generate a fresh random Ed25519 keypair using the OS CSPRNG."""
        return cls(Ed25519PrivateKey.generate())

    @classmethod
    def from_hex(cls, hex_seed: str) -> Keypair:
        """Construct from a 64-character hex-encoded 32-byte private key seed.

        :param hex_seed: 64 hex characters representing the 32-byte private key.
        :raises KeyManagementError: If the seed is malformed.
        """
        if len(hex_seed) != 64:
            raise KeyManagementError(
                "signing key hex must be exactly 64 characters (32 bytes)",
                context={"got_length": len(hex_seed)},
            )
        try:
            seed = bytes.fromhex(hex_seed)
            return cls(Ed25519PrivateKey.from_private_bytes(seed))
        except ValueError as exc:
            raise KeyManagementError(f"invalid hex in signing key: {exc}") from exc

    @classmethod
    def from_env(cls, *, var: str = "LEDGERPROOF_SIGNING_KEY_HEX") -> Keypair | None:
        """Load a keypair from an environment variable, or return None.

        Intended for stateless deployments (containers, serverless) where a
        file-based key store is impractical. Returns None if the variable is
        unset, so callers can fall through to ``load()`` or ``generate()``.

        :param var: Environment variable name (default ``LEDGERPROOF_SIGNING_KEY_HEX``).
        """
        value = os.environ.get(var)
        if not value:
            return None
        return cls.from_hex(value.strip())

    @classmethod
    def load(cls, path: str | Path | None = None) -> Keypair:
        """Load a keypair from a file. Default path: ``~/.config/ledgerproof/signing_key.bin``.

        The file must contain exactly 32 raw bytes of private key material.
        File permissions are verified — if the file is readable by anyone
        other than the owner, this raises :class:`KeyManagementError`.

        :param path: Override the default path. Honored via
            ``LEDGERPROOF_KEY_PATH`` env var if ``path`` is None.
        :raises KeyManagementError: If the file is missing, malformed, or
            insecurely permissioned.
        """
        key_path = _resolve_path(path)
        if not key_path.exists():
            raise KeyManagementError(
                f"signing key file not found: {key_path}. "
                f"Generate one with Keypair.generate() and save() it, or set "
                f"LEDGERPROOF_SIGNING_KEY_HEX in the environment.",
                context={"path": str(key_path)},
            )
        _verify_secure_perms(key_path)
        try:
            raw = key_path.read_bytes()
        except OSError as exc:
            raise KeyManagementError(f"failed to read {key_path}: {exc}") from exc
        if len(raw) != 32:
            raise KeyManagementError(
                f"signing key file must be exactly 32 bytes; got {len(raw)}",
                context={"path": str(key_path)},
            )
        try:
            return cls(Ed25519PrivateKey.from_private_bytes(raw))
        except ValueError as exc:
            raise KeyManagementError(f"malformed signing key in {key_path}: {exc}") from exc

    @classmethod
    def load_or_generate(cls, path: str | Path | None = None) -> tuple[Keypair, bool]:
        """Load a key from disk if it exists, otherwise generate and save one.

        Returns a tuple of ``(keypair, was_generated)``. Use ``was_generated``
        to decide whether you also need to register the key with the server.

        :param path: Override the default path.
        :returns: ``(keypair, was_generated)``.
        """
        key_path = _resolve_path(path)
        if key_path.exists():
            return cls.load(key_path), False
        kp = cls.generate()
        kp.save(key_path)
        return kp, True

    # ── Persistence ──────────────────────────────────────────────────────

    def save(self, path: str | Path | None = None) -> Path:
        """Write the private key to disk with 0600 permissions.

        Creates the parent directory with 0700 if it doesn't exist. Refuses
        to overwrite an existing file unless the existing file already
        contains an identical key (idempotent).

        :param path: Target file path. Default
            ``~/.config/ledgerproof/signing_key.bin``.
        :returns: The path the key was written to.
        :raises KeyManagementError: If the file exists with different
            contents, or if permissions cannot be set.
        """
        key_path = _resolve_path(path)
        key_dir = key_path.parent
        try:
            key_dir.mkdir(parents=True, exist_ok=True, mode=_SECURE_DIR_MODE)
        except OSError as exc:
            raise KeyManagementError(f"failed to create {key_dir}: {exc}") from exc

        # Idempotent overwrite check.
        new_bytes = self._private.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        if key_path.exists():
            existing = key_path.read_bytes()
            if existing == new_bytes:
                return key_path
            raise KeyManagementError(
                f"refusing to overwrite existing signing key at {key_path} "
                f"with a different key. Move or delete the existing file first.",
                context={"path": str(key_path)},
            )

        try:
            # Write atomically with secure permissions.
            tmp_path = key_path.with_suffix(".tmp")
            fd = os.open(
                tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, _SECURE_FILE_MODE
            )
            try:
                os.write(fd, new_bytes)
            finally:
                os.close(fd)
            os.replace(tmp_path, key_path)
            os.chmod(key_path, _SECURE_FILE_MODE)
        except OSError as exc:
            raise KeyManagementError(f"failed to write {key_path}: {exc}") from exc
        return key_path

    # ── Operations ───────────────────────────────────────────────────────

    def sign(self, data: bytes) -> bytes:
        """Sign ``data`` and return the raw 64-byte Ed25519 signature."""
        return self._private.sign(data)

    def verify(self, signature: bytes, data: bytes) -> bool:
        """Verify ``signature`` over ``data`` using this keypair's public key.

        Returns True if valid, False if invalid (does not raise).
        """
        try:
            self.public_key().verify(signature, data)
            return True
        except InvalidSignature:
            return False

    def public_key(self) -> Ed25519PublicKey:
        """Return the underlying public-key object."""
        return self._private.public_key()

    def public_b64(self) -> str:
        """Base64-encoded public key, the format expected by ``POST /v1/keys``."""
        pub_bytes = self.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return base64.b64encode(pub_bytes).decode("ascii")

    def private_hex(self) -> str:
        """Hex-encoded private key, for the ``LEDGERPROOF_SIGNING_KEY_HEX`` env var.

        Handle with care. Never log this. Never commit it. Prefer
        :meth:`save` to a 0600 file unless you specifically need an env var
        (e.g., for a serverless deployment).
        """
        raw = self._private.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return raw.hex()

    def __repr__(self) -> str:
        # Never leak the private key in repr — only the first 8 hex chars of
        # the public key, which is non-secret.
        pub = self.public_b64()
        return f"Keypair(pub_b64={pub[:11]}…)"


# ── Internal helpers ────────────────────────────────────────────────────────


def _resolve_path(path: str | Path | None) -> Path:
    """Resolve the key file path with env override."""
    if path is not None:
        return Path(path).expanduser()
    env_override = os.environ.get("LEDGERPROOF_KEY_PATH")
    if env_override:
        return Path(env_override).expanduser()
    return _DEFAULT_KEY_PATH


def _verify_secure_perms(path: Path) -> None:
    """Raise if the file is readable by anyone other than the owner.

    Skipped on Windows (where POSIX modes don't apply); we only enforce on
    POSIX systems where the threat model is meaningful.
    """
    if os.name == "nt":  # pragma: no cover
        return
    st = path.stat()
    mode = stat.S_IMODE(st.st_mode)
    # Reject any group or world bits set.
    if mode & 0o077:
        raise KeyManagementError(
            f"insecure permissions on signing key {path}: mode is "
            f"{oct(mode)}, must be 0600 (rw for owner only). "
            f"Fix with: chmod 600 {path}",
            context={"path": str(path), "mode": oct(mode)},
        )


__all__ = ["Keypair"]
