"""Perceptual hashing for image, audio, and video — survives re-encoding.

SHA-256 of an artifact is fragile: changing a single bit produces a totally
different hash. That's correct cryptographically, but useless when a regulator
or journalist finds your AI-generated image *after* it's been recompressed
by Facebook, screenshotted, and re-uploaded. The artifact still smells the
same to a human; it hashes completely differently.

Perceptual hashes are designed to survive those transformations:

- **pHash** (DCT-based) — robust against scaling, color shifts, mild edits.
- **dHash** (gradient-based) — fastest; good for "approximately the same image".
- **aHash** (average) — simplest; least robust.
- **chromaprint** — for audio, the standard fingerprint used by AcoustID.

The LPR receipt's `perceptual_hash` field carries one of these alongside the
exact SHA-256. The server's `GET /v1/receipts/by-perceptual-hash/:algo/:hash`
endpoint then returns receipts within a configurable Hamming distance.

Optional dependencies (install via `pip install ledgerproof[perceptual]`):

- `imagehash` + `Pillow` for image hashing
- (Future) `chromaprint` for audio

If you call into this module without the deps installed, you get a clear
ImportError suggesting the extra to install.
"""

from __future__ import annotations

from typing import Optional

from .types import PerceptualHash


def image_phash(image_path_or_bytes: str | bytes, hash_size: int = 8) -> PerceptualHash:
    """Compute the perceptual hash (pHash) of an image.

    :param image_path_or_bytes: Either a filesystem path to the image or the
        raw bytes of the image file.
    :param hash_size: Side of the hash matrix; default 8 → 64-bit hash.
    :returns: A :class:`PerceptualHash` populated for the LPR receipt.
    :raises ImportError: If the ``perceptual`` extra is not installed.
    """
    try:
        import imagehash  # type: ignore[import-untyped]
        from PIL import Image
    except ImportError as exc:
        raise ImportError(
            "image perceptual hashing requires the 'perceptual' extra: "
            "pip install ledgerproof[perceptual]"
        ) from exc

    if isinstance(image_path_or_bytes, str):
        img = Image.open(image_path_or_bytes)
    else:
        from io import BytesIO

        img = Image.open(BytesIO(image_path_or_bytes))

    h = imagehash.phash(img, hash_size=hash_size)
    bits = hash_size * hash_size
    return PerceptualHash(algorithm="pHash", value=str(h), bits=bits)


def image_dhash(image_path_or_bytes: str | bytes, hash_size: int = 8) -> PerceptualHash:
    """Compute the difference hash (dHash) of an image — faster than pHash, similar robustness."""
    try:
        import imagehash  # type: ignore[import-untyped]
        from PIL import Image
    except ImportError as exc:
        raise ImportError(
            "image perceptual hashing requires the 'perceptual' extra: "
            "pip install ledgerproof[perceptual]"
        ) from exc

    if isinstance(image_path_or_bytes, str):
        img = Image.open(image_path_or_bytes)
    else:
        from io import BytesIO

        img = Image.open(BytesIO(image_path_or_bytes))

    h = imagehash.dhash(img, hash_size=hash_size)
    bits = hash_size * hash_size
    return PerceptualHash(algorithm="dHash", value=str(h), bits=bits)


def hamming_distance(a: PerceptualHash, b: PerceptualHash) -> Optional[int]:
    """Bit-wise Hamming distance between two perceptual hashes.

    Returns None if the algorithms or bit lengths don't match (you can't
    compare a pHash to a chromaprint meaningfully).

    The server uses this to find "approximately matching" receipts: a
    distance of 0 means identical hashes; distances ≤ 10 (for 64-bit
    pHash) are typically considered visually similar; > 20 is typically
    a different image.
    """
    if a.algorithm != b.algorithm or a.bits != b.bits:
        return None
    a_int = int(a.value, 16)
    b_int = int(b.value, 16)
    return bin(a_int ^ b_int).count("1")


__all__ = ["hamming_distance", "image_dhash", "image_phash"]
