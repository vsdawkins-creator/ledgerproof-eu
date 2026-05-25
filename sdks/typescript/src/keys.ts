/**
 * Ed25519 keypair management using @noble/ed25519.
 *
 * Pure web-platform implementation — works in Node, Bun, Deno, Cloudflare
 * Workers, Vercel Edge, browsers. No `node:crypto`. No filesystem by default
 * (Workers and browsers don't have one).
 *
 * For Node-only callers who want filesystem-based key persistence, use the
 * `loadOrGenerateFromFile` helper. Edge callers should pass `signingKeyHex`
 * in config or use the WebAuthn / WebCrypto integration (future).
 */

import * as ed from "@noble/ed25519";
import { sha512 } from "@noble/hashes/sha512";
import { bytesToHex, hexToBytes } from "@noble/hashes/utils";

import { KeyManagementError } from "./errors.js";

// @noble/ed25519 v2 requires you to wire up SHA-512 explicitly (so it works
// on platforms without it built-in). We do that here once at module load.
ed.etc.sha512Sync = (...m: Uint8Array[]) => sha512(ed.etc.concatBytes(...m));

export class Keypair {
  private constructor(private readonly privateKey: Uint8Array) {
    if (privateKey.length !== 32) {
      throw new KeyManagementError("private key must be exactly 32 bytes", {
        gotLength: privateKey.length,
      });
    }
  }

  /** Generate a fresh random Ed25519 keypair via the platform CSPRNG. */
  static generate(): Keypair {
    return new Keypair(ed.utils.randomPrivateKey());
  }

  /** Construct from a 64-character hex-encoded 32-byte private key seed. */
  static fromHex(hex: string): Keypair {
    if (hex.length !== 64) {
      throw new KeyManagementError("signing key hex must be 64 characters", {
        gotLength: hex.length,
      });
    }
    try {
      return new Keypair(hexToBytes(hex));
    } catch (exc) {
      throw new KeyManagementError(`invalid hex: ${(exc as Error).message}`);
    }
  }

  /** Read `LEDGERPROOF_SIGNING_KEY_HEX` from the environment, or return null. */
  static fromEnv(varName = "LEDGERPROOF_SIGNING_KEY_HEX"): Keypair | null {
    const value =
      typeof process !== "undefined" && process.env
        ? process.env[varName]
        : undefined;
    if (!value) return null;
    return Keypair.fromHex(value.trim());
  }

  /** Sign `data` with this keypair, returning the raw 64-byte signature. */
  sign(data: Uint8Array): Uint8Array {
    return ed.sign(data, this.privateKey);
  }

  /** Verify a signature over `data` using this keypair's public key. */
  verify(signature: Uint8Array, data: Uint8Array): boolean {
    try {
      return ed.verify(signature, data, this.publicKey());
    } catch {
      return false;
    }
  }

  /** Derive the public key bytes (32 bytes). */
  publicKey(): Uint8Array {
    return ed.getPublicKey(this.privateKey);
  }

  /** Base64-encoded public key, matching `POST /v1/keys` body format. */
  publicKeyBase64(): string {
    const pub = this.publicKey();
    // Node has Buffer; browsers/edge have btoa(); use a polyfill-friendly path.
    if (typeof Buffer !== "undefined") {
      return Buffer.from(pub).toString("base64");
    }
    let binary = "";
    for (const b of pub) binary += String.fromCharCode(b);
    return btoa(binary);
  }

  /** Hex-encoded private key. Handle with care — never log or persist insecurely. */
  privateKeyHex(): string {
    return bytesToHex(this.privateKey);
  }

  toString(): string {
    return `Keypair(pub_b64=${this.publicKeyBase64().slice(0, 11)}…)`;
  }
}
