# LPR 2.0 — Post-Quantum Cryptography Annex (Outline / Spec Draft)

**Document:** LedgerProof Receipt Specification, version 2.0 (Post-Quantum Annex)
**Status:** **Outline — for review and ratification in Q1 2027**
**Editor:** Veronica S. Dawkins, LedgerProof Foundation
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
**Relationship to LPR 1.x:** Additive. All v1.x receipts MUST remain verifiable indefinitely. v2.0 receipts use hybrid classical + PQ signatures by default.
**Target ratification:** Q1 2027, with implementation rollout through 2027–2028.

> The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** are interpreted per RFC 2119 / RFC 8174.

---

## 1 · Abstract

LedgerProof receipts are designed for indefinite verifiability. The current LPR 1.x specification uses Ed25519 signatures and SHA-256 hashing. Both schemes are vulnerable to attack by a cryptographically-relevant quantum computer (CRQC):
- **Ed25519** is broken by Shor's algorithm in polynomial time.
- **SHA-256** is weakened by Grover's algorithm from 256-bit security to ~128-bit security (still computationally infeasible to brute-force, but the safety margin halves).

While the timeline for a CRQC capable of breaking Ed25519 at 256-bit security is debated (estimates range from 2030 to 2045), **the EU AI Act, MiFID II, and Solvency II all require record retention periods of 5–10 years.** A receipt issued today must be verifiable in 2031–2036, which falls within the projected CRQC timeline.

This annex specifies LPR 2.0's post-quantum cryptographic stack and the migration procedure from LPR 1.x.

---

## 2 · Scope

### 2.1 In scope

- Hybrid classical + post-quantum signature scheme for ordinary receipts
- Hash-based signature scheme (SPHINCS+) for high-assurance long-horizon receipts
- Migration semantics from LPR 1.x
- Key generation, distribution, and rotation
- Verifier behavior for mixed-version environments
- Cryptographic agility framework for future PQ scheme transitions

### 2.2 Out of scope (deferred or addressed elsewhere)

- **Quantum key distribution (QKD)** — operational, not protocol-level
- **Post-quantum key encapsulation** (Kyber, BIKE, etc.) — receipts are publicly readable; encryption is not required
- **Post-quantum hash** — SHA-256 + SHA-3 dual-hashing addresses this; full migration to SHA-3-512 deferred to LPR 2.1
- **Threshold post-quantum signing** — FROST-Dilithium variants are not yet stable; deferred to LPR 2.1

---

## 3 · Hybrid signature scheme (LPR 2.0 default)

### 3.1 Algorithm selection

LPR 2.0 ordinary receipts SHALL be signed with **both**:

- **Ed25519** (existing classical signature, per LPR 1.0 §4)
- **ML-DSA-65** (Dilithium3, the NIST-standardized PQ signature scheme; FIPS 204)

The receipt is valid only if **both signatures verify**. If either scheme is broken in the future, the other provides residual security.

### 3.2 Wire format

```cbor
LprEntry-v2.0 = LprEntry-v1.2 .and {
    "sig_classical" : tstr        ; Ed25519 signature, hex (existing)
    "sig_pq"        : tstr        ; ML-DSA-65 signature, base64
    "pq_alg"        : tstr        ; "ml-dsa-65" (extensible)
}
```

The `signature` field from LPR 1.x is renamed to `sig_classical` in v2.0 receipts. Verifiers MUST accept both forms during the transition window (§7).

### 3.3 Public key distribution

The DID document for an issuer SHALL include both classical and PQ public keys:

```json
{
  "id": "did:web:example.com",
  "verificationMethod": [
    {
      "id": "did:web:example.com#key-1",
      "type": "Ed25519VerificationKey2020",
      "publicKeyMultibase": "z6Mk..."
    },
    {
      "id": "did:web:example.com#key-1-pq",
      "type": "MLDSAVerificationKey2026",
      "publicKeyJwk": { "alg": "ML-DSA-65", "k": "..." }
    }
  ]
}
```

### 3.4 Performance considerations

ML-DSA-65 signatures are ~3,309 bytes (vs Ed25519's 64 bytes). Receipt size increases by ~3.3 KB. For high-throughput operators, this is acceptable but non-trivial. Mitigations:

- Receipts continue to be off-chain; only Merkle roots are anchored
- Signature compression via Merkle aggregation (single PQ signature per batch root, per-receipt classical signatures)
- Optional `compact_pq` mode using ML-DSA-44 (smaller, lower security margin) for low-stakes use cases

---

## 4 · High-assurance profile (SPHINCS+ / SLH-DSA)

### 4.1 When to use

For receipts that MUST remain verifiable for 30+ years (legal contracts, court filings, government records, IP filings), the LPR 2.0 `HighAssurance-v1.0` profile uses:

- **SLH-DSA-SHA2-256s** (SPHINCS+, NIST FIPS 205) for the primary signature
- **Ed25519** for the secondary (hybrid) signature
- **SHA-256 + SHA-3-256** dual hashing in the Merkle tree

### 4.2 Security rationale

SPHINCS+ is a **hash-based signature scheme**. Its security reduces only to the underlying hash function — there is no number-theoretic assumption. As long as SHA-256 (or its successor) is preimage-resistant, SPHINCS+ signatures cannot be forged. This is the most conservative known choice for indefinite verifiability.

### 4.3 Trade-offs

- SPHINCS+ signatures are **~30 KB** (much larger than Dilithium)
- Signing is ~10× slower than Ed25519
- Verification is comparable to Ed25519

Acceptable for low-volume, high-stakes deployments. NOT recommended for default usage.

### 4.4 Wire format

```cbor
LprEntry-v2.0-HighAssurance = LprEntry-v2.0 .and {
    "sig_sphincs"   : tstr        ; SLH-DSA signature, base64
    "merkle_alg"    : "sha256+sha3-256" ; dual-hashing identifier
}
```

---

## 5 · Cryptographic agility framework

LPR 2.0 introduces a structured way to add new signature schemes without re-rev'ing the spec.

### 5.1 Algorithm Identifier Registry

A new Foundation-maintained registry at `https://spec.ledgerproofhq.io/registry/signature-algorithms` lists:

| Identifier | Scheme | Security level | Status |
|---|---|---|---|
| `ed25519` | Ed25519 | Classical 128-bit | Stable (LPR 1.x baseline) |
| `ml-dsa-44` | Dilithium2 | PQ NIST Level 2 | Stable |
| `ml-dsa-65` | Dilithium3 | PQ NIST Level 3 | **LPR 2.0 default** |
| `ml-dsa-87` | Dilithium5 | PQ NIST Level 5 | Optional high-security |
| `slh-dsa-sha2-128s` | SPHINCS+ short | PQ Level 1, hash-based | Available |
| `slh-dsa-sha2-256s` | SPHINCS+ long | PQ Level 5, hash-based | **HighAssurance default** |
| `falcon-512` | FALCON | PQ Level 1 | Reserved (smaller sigs, side-channel concerns) |
| `falcon-1024` | FALCON | PQ Level 5 | Reserved |
| `cn-sm2` | SM2 | Classical, Chinese national crypto | Reserved (PRC-Deep-Synthesis profile) |
| `ru-gost-3410` | GOST R 34.10 | Classical, Russian national crypto | Reserved |

### 5.2 Adding a new algorithm

To register a new signature algorithm:

1. NIST or equivalent standards-body finalization
2. Submission to Foundation Technical Steering Committee
3. Reference implementation in at least two languages
4. Public test vectors
5. 90-day public comment period
6. TSC vote

### 5.3 Deprecation policy

When a scheme is broken or weakened:
1. TSC publishes a deprecation notice
2. New receipts MUST NOT use the deprecated scheme as primary
3. Existing receipts signed under the deprecated scheme remain verifiable but display a "deprecated cryptography" warning in verifier UIs
4. Foundation may issue **re-attestation receipts** (counter-signing old receipts with current cryptography) — see §6.5 of LPR 1.2

---

## 6 · Migration from LPR 1.x

### 6.1 Reverse compatibility

LPR 2.0 verifiers MUST verify LPR 1.x receipts using only the classical signature. No automatic upgrade is performed.

### 6.2 Forward compatibility

LPR 1.x verifiers encountering LPR 2.0 receipts MUST:
- Verify the classical `sig_classical` field (renamed from `signature` — accept either name during transition)
- Ignore the `sig_pq` field
- Display "PQ signature present but not verified" to users

### 6.3 Migration timeline

| Phase | Date | Activity |
|---|---|---|
| Pre-announcement | Q3 2026 | Publish LPR 2.0 outline (this document) |
| Public review | Q4 2026 | 90-day comment period |
| Ratification | Q1 2027 | TSC vote, freeze v2.0 spec |
| SDK rollout | Q2 2027 | All SDKs support v2.0 issuance and verification |
| Operator default | Q3 2027 | Operators default new receipts to v2.0 |
| Legacy verification | Indefinite | v1.x receipts remain verifiable forever |

### 6.4 Re-anchoring (optional)

Issuers who need their existing v1.x receipts to gain PQ protection MAY:

1. Generate a PQ keypair tied to their existing DID
2. Issue a `pq_reattest/v1` entry per receipt, counter-signing the original receipt with the new PQ key
3. Anchor the re-attestation in the next Merkle tree
4. Verifiers thereafter present the receipt with "PQ re-attested by issuer on [date]"

Re-anchoring is OPTIONAL. v1.x receipts that are not re-anchored remain valid under classical cryptography until such time as a CRQC actually exists.

### 6.5 Foundation re-attestation

For high-value v1.x receipts that lose their issuer's PQ key access (issuer no longer operates, key lost), the LedgerProof Foundation MAY issue a **Foundation re-attestation** under its PQ keypair. This is a FROST-Dilithium aggregated signature attesting that the Foundation has verified the v1.x receipt's classical signature at a time when classical cryptography is still trusted.

---

## 7 · Operator obligations

LPR 2.0 operators SHALL:

1. Maintain a PQ keypair per operator key (Mechanism 2.1 in unstoppability framework)
2. Publish their PQ public key in their DID document
3. Sign all v2.0 receipts with both classical and PQ keys
4. Verify all incoming v2.0 receipts against both schemes
5. Continue to verify v1.x receipts with classical-only signatures
6. Publish a quarterly "PQ posture report" describing key custody, rotation schedule, and any incidents

---

## 8 · Verifier obligations

LPR 2.0 verifiers SHALL:

1. For v2.0 receipts: verify both signatures; reject if either fails
2. For v1.x receipts: verify the classical signature only
3. Display the signature regime used (classical-only, hybrid, high-assurance)
4. Surface deprecated-cryptography warnings for receipts using algorithms marked deprecated in the Algorithm Registry
5. Validate the algorithm identifier against the Foundation's Algorithm Registry; reject unknown identifiers with `LPR2010_UNKNOWN_PQ_ALGORITHM`

---

## 9 · Threshold post-quantum (deferred to LPR 2.1)

Operator key custody currently relies on **FROST-Ed25519** (see LPR 1.2 §6.7). A post-quantum threshold scheme is not yet stable in the cryptographic literature. Candidates under active research:

- **Threshold Dilithium** — research-stage; no IRTF/IETF draft yet
- **Threshold SPHINCS+** — known impractical due to signature size and statefulness
- **Lattice-based MPC** — research-stage

LPR 2.1 will adopt whichever scheme reaches stable standardization first, expected 2028–2029.

**Interim solution:** Operator PQ keys are held via M-of-N hardware HSMs with cooperative signing via TSS-style key-share refresh, NOT a true threshold PQ scheme. This is operationally adequate but cryptographically less elegant than the eventual threshold-PQ solution.

---

## 10 · Test vectors

Reference test vectors for hybrid signing and verification will be published at `github.com/ledgerproof/lpr-test-vectors/v2.0/` upon ratification. Test vectors will include:

- 1,000 hybrid-signed receipts with known keypairs
- 100 high-assurance receipts using SPHINCS+
- Cross-validation against NIST FIPS 204 / FIPS 205 reference implementations
- Re-attestation flow examples

All compliant LPR 2.0 implementations MUST pass all published test vectors.

---

## 11 · Security considerations

### 11.1 "Harvest now, decrypt later" attack

A capable adversary may today be collecting LPR 1.x receipts in bulk, with the intent of forging successors once a CRQC is available. The hybrid scheme (§3) prevents this: an attacker would need to break **both** Ed25519 AND ML-DSA-65 to forge a v2.0 receipt.

For v1.x receipts not migrated to v2.0, the attack surface is: an attacker with a CRQC could forge a v1.x signature backdated to a time when classical crypto was trusted. The Foundation Canonical Registry (LPR 1.2 §6) and Bitcoin's totally-ordered timestamp mitigate this — the attacker cannot retroactively insert a receipt into a Bitcoin block. They can only forge signatures on already-anchored receipts, which still produces detectably inconsistent records.

### 11.2 Side-channel resistance

ML-DSA-65 is more side-channel-resistant than ML-KEM, but operator implementations SHOULD use constant-time libraries (e.g., `pqcrypto-dilithium` for Rust) and run signing in HSM-attested environments where possible.

### 11.3 Standardization risk

NIST's FIPS 204 (ML-DSA) and FIPS 205 (SLH-DSA) are recent standards (2024). The cryptographic community continues to scrutinize them. The cryptographic agility framework (§5) is the explicit hedge: if a NIST PQ scheme is broken, the Foundation can transition to an alternate without re-spec'ing the protocol.

### 11.4 Operator key migration

Operators upgrading from v1.x to v2.0 must generate fresh PQ keys (Ed25519 keys cannot be "upgraded"). Key generation, distribution to the DID document, and rotation should be planned at least 90 days in advance of v2.0 production rollout.

---

## 12 · IANA / registry considerations

This annex extends the LedgerProof Foundation registries with:

1. **Signature Algorithm Registry** (§5.1)
2. **Deprecation Registry** (§5.3 — tracks deprecated algorithms with deprecation dates and reasons)

Registry changes follow the same governance process as LPR 1.2 registries (Foundation TSC + 30-day public comment).

---

## 13 · References

### 13.1 Normative

- [FIPS-204] NIST, "Module-Lattice-Based Digital Signature Standard", FIPS PUB 204, August 2024.
- [FIPS-205] NIST, "Stateless Hash-Based Digital Signature Standard", FIPS PUB 205, August 2024.
- [RFC-9380] Faz-Hernández, A., et al., "Hashing to Elliptic Curves", RFC 9380, August 2023.
- [LPR-1.0] Dawkins, V. S., "LedgerProof Receipt Specification, version 1.0", LedgerProof Foundation, 2026.
- [LPR-1.2] Dawkins, V. S., "LedgerProof 1.2 Canonicality Annex", LedgerProof Foundation, 2026.

### 13.2 Informative

- [NIST-PQC] NIST, "Post-Quantum Cryptography Standardization Project", 2016–2024.
- [QSAFE-FAQ] CSA, "Post-Quantum Cryptography Threat and Mitigation FAQ", 2023.
- [SCITT-PQ] IETF SCITT Working Group, "Post-Quantum Considerations for SCITT", in progress.

---

## 14 · Open questions for review

This is an **outline document** intended to seed the formal LPR 2.0 spec. The following questions are explicitly unresolved and require working-group discussion:

1. Should the default PQ scheme be ML-DSA-65 (NIST Level 3) or ML-DSA-87 (NIST Level 5)?
2. Should re-attestation be issuer-initiated (§6.4) or operator-initiated by default?
3. Should the high-assurance profile (§4) be a separate spec or a sub-profile of v2.0?
4. What is the right cadence for the operator PQ-posture report (§7.6)?
5. How does the Foundation Arbitration Panel sign in a post-quantum world (depends on Threshold-PQ availability — §9)?
6. How should the cryptographic agility framework (§5) handle nation-state crypto (SM2, GOST) requested by jurisdictional profiles?

These will be addressed in the public comment period (Q4 2026 per §6.3).

---

## 15 · Authors and acknowledgements

**Editor:** Veronica S. Dawkins, LedgerProof Foundation, <spec@ledgerproofhq.io>

**Acknowledgements:** This outline was developed referencing the work of the IETF CFRG, the NIST PQC standardization team, the C2PA cryptographic working group, and conversations with [TBD post-quantum cryptographer].

---

*End of LPR 2.0 Post-Quantum Annex Outline.*
*This document is a working draft intended to seed the formal specification process beginning Q4 2026.*
