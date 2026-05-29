# Quantum Computing & Post-Quantum Cryptography Trajectory, 2026–2036

**LedgerProof Foundation — 2036 Architecture Research Dossier, Wave 1, Domain 1**
*Prepared: May 20, 2026. Sources verified via WebSearch on the date of preparation. Citations inline; full source list at end.*

---

## Executive summary

The transition from classical to post-quantum cryptography is a fully-funded, regulator-mandated, time-bound migration with binding deadlines between **2027 and 2035** across the United States (NSA CNSA 2.0), United Kingdom (NCSC), and European Union (ENISA + ANSSI + BSI), all aligned around 2035 as the date by which national security systems must be quantum-resistant. The NIST post-quantum standards (FIPS 203 ML-KEM, FIPS 204 ML-DSA, FIPS 205 SLH-DSA) were finalized **August 2024**; HQC was added as a fifth algorithm in **March 2025**; Falcon (FIPS 206 / FN-DSA) is the remaining signature algorithm under finalization.

Hybrid classical+post-quantum signatures (notably **Composite ML-DSA + Ed25519**) are nearing IETF RFC status (`draft-ietf-lamps-pq-composite-sigs-13`), with multi-implementation interoperability successfully demonstrated at IETF 124 in November 2025. This is the migration architecture the industry has converged on.

The **Harvest-Now-Decrypt-Later (HNDL)** threat is officially acknowledged by FBI, CISA, NIST, and corresponding agencies in major democracies. Resource estimates for the cryptographically-relevant quantum computer (CRQC) capable of breaking 2048-bit RSA were reduced from approximately 20 million qubits (Google, 2019) to **under 100,000 physical qubits** in a February 2026 Google preprint — a 200-fold compression in the estimated hardware requirement. Logical-qubit counts in industry roadmaps now suggest 200 logical qubits by 2029 (IBM) and approach 1,000 by the early 2030s.

For **SHA-256**, Grover's algorithm reduces security from 256-bit to 128-bit effective preimage resistance, but 2^128 operations remains computationally infeasible under any credible quantum scenario this decade. SHA-256 is not the bottleneck. **Ed25519, ECDSA, and RSA are**.

---

## 1 · CRQC timeline — probability-weighted forecast

### Best-case (most optimistic credible source) — CRQC by 2028–2030

IonQ's 2025 roadmap explicitly targets a cryptographically-relevant quantum computer by 2028. (Source: IonQ public roadmap via postquantum.com industry tracker.)

Utimaco's 2025 expert survey estimated a **1-in-7 (~14%) probability of CRQC by 2026** and a **1-in-2 (~50%) probability by 2031** — a substantial upward revision from prior years' estimates. Google and Cloudflare have **publicly committed to PQC migration by 2029**, an industry signal that the leading hyperscalers do not believe CRQC will arrive later than the early 2030s.

### Central case (consensus of NIST/NSA/Big-Tech roadmaps) — CRQC between 2030 and 2035

IBM's June 2025 roadmap targets approximately **200 logical qubits by 2029**, scaling to **over 1,000 logical qubits by the early 2030s**. Google Quantum AI targets approximately **100+ logical qubits by 2028**, scaling to thousands in the early 2030s. Quantinuum and IBM have stated joint goals of quantum systems with hundreds of thousands to a million physical qubits by the early 2030s.

The NIST and NSA migration deadlines (2030–2035) implicitly assume the threat materializes inside that window. The NSA's CNSA 2.0 timeline — mandating PQC across all national security systems by 2035 — is the most authoritative forecast embedded in US policy.

### Worst-case (delayed CRQC) — CRQC after 2035

Even in a pessimistic scenario where engineering challenges delay CRQC beyond 2035, the **Harvest-Now-Decrypt-Later threat** means that data encrypted today with Ed25519 / ECDSA / RSA is at risk of decryption **once** CRQC arrives, regardless of timing. Documents anchored today must be designed with the assumption that their signatures may be retroactively forgeable within 10–20 years.

### What this means for LedgerProof

A receipt produced in 2026 under Ed25519 alone has a non-trivial probability of being retroactively forgeable by an adversary with CRQC capability between 2029 and 2035. **The migration path must be designed into the receipt format today, not retrofitted later.**

---

## 2 · NIST PQC standardization — finalization status, May 2026

| Standard | Algorithm | Type | Status |
|---|---|---|---|
| **FIPS 203** | ML-KEM (formerly Kyber) | Key encapsulation | **Finalized August 2024** |
| **FIPS 204** | ML-DSA (formerly Dilithium / CRYSTALS-Dilithium) | Digital signatures | **Finalized August 2024** |
| **FIPS 205** | SLH-DSA (formerly SPHINCS+) | Stateless hash-based signatures | **Finalized August 2024** |
| **FIPS 206** | FN-DSA (formerly Falcon) | Digital signatures (compact) | **Draft, finalization pending** |
| **HQC** | Hamming Quasi-Cyclic | Key encapsulation backup | **Added March 11, 2025** as fifth algorithm |

FIPS 203, 204, and 205 are the global regulatory reference standards. They underpin CNSA 2.0, UK NCSC guidance, and EU migration frameworks. Implementers operating in regulated sectors will be expected to support **ML-DSA-87 + ML-KEM-1024** at the highest assurance tier per NSA guidance.

---

## 3 · Global PQC migration mandates — sector-by-sector

### United States — NSA CNSA 2.0 (announced September 10, 2022; revisions through 2025)

- **By January 1, 2027**: All new NSS deployments must comply with CNSA 2.0.
- **By December 31, 2030**: All NSS network equipment must use CNSA 2.0 exclusively. Equipment that cannot support CNSA 2.0 is phased out.
- **By end of 2031**: Full enforcement across all NSS cryptographic implementations.
- **By 2033**: Custom applications, legacy equipment, and operating systems must use CNSA 2.0 exclusively.
- **By 2035**: Ultimate goal — all US national security systems quantum-resistant. *Aligned with White House National Security Memorandum 10 (NSM-10).*

### United Kingdom — NCSC (Timelines for migration to post-quantum cryptography)

- **By 2028**: Identify cryptographic services needing upgrade and build migration plans.
- **2028–2031**: Execute high-priority upgrades.
- **2031–2035**: Complete migration across all systems, services, and products.

UK guidance applies to critical infrastructure and government as mandate; advisory for private sector. Key deadlines: **2028 plan complete, 2031 critical systems, 2035 full migration.**

### European Union — ENISA + NIS Cooperation Group (Coordinated Implementation Roadmap, June 2025)

- **By 2026**: First-phase milestone (planning, identification).
- **By 2030**: Secure high-risk systems by end of year. EU Commission's hard target.
- **By 2035**: Full system transition to PQC.

**Germany (BSI):** aligned with EU 2030 deadline; mandates hybrid approaches including ML-KEM + FrodoKEM + Classic McEliece.

**France (ANSSI):** aligned with EU 2030 deadline; requires ML-KEM + FrodoKEM hybrid, with hybrid required for signatures.

### Financial services — DORA (EU)

The Digital Operational Resilience Act (DORA) has required **active monitoring of quantum risk** from all EU financial entities since **January 2025**.

### Industry adoption — corporate

Google publicly committed in February 2026 to PQC migration completion by 2029. Cloudflare similarly committed to 2029. These commitments compress the de facto migration window for any vendor whose products touch hyperscaler infrastructure.

---

## 4 · SHA-256 quantum resistance analysis

Grover's algorithm provides only a **square-root speedup** against unstructured search problems, including preimage attacks on hash functions. For SHA-256:

- Classical preimage security: 2^256 operations
- Quantum preimage security under Grover: 2^128 operations
- Quantum collision attack (Brassard-Høyer-Tapp): 2^85 operations

The most credible estimates suggest that breaking SHA-256 via Grover would require **on the order of 2^144 T-gates on approximately 2,400 logical qubits**, which is computationally infeasible under any quantum scenario credibly forecast for this decade or the next.

**NIST guidance** (NIST SP 800-131A Rev 3): from now through 2030, organizations are expected to phase out weak cryptographic algorithms (SHA-1, SHA-224, AES-ECB). SHA-256 remains acceptable as a hash function. By 2035, the broader transition is expected to be complete.

### Implication for LedgerProof

**SHA-256 is not the architectural bottleneck.** It remains acceptable for content hashing through 2036 and likely well beyond. The architectural issue is the **signature scheme** (Ed25519), not the hash.

A future LedgerProof profile may introduce SHA-3 (Keccak) or BLAKE3 as a permitted hash alternative for diversification, but SHA-256 does not require immediate migration.

---

## 5 · Hybrid signature deployment — IETF status and interoperability

### Standards status

- **draft-ietf-lamps-pq-composite-sigs (version 13 as of mid-2026)** is nearing RFC publication. The draft defines Composite ML-DSA — a hybrid that combines ML-DSA (post-quantum) with traditional algorithms including Ed25519, Ed448, ECDSA, and RSA.
- **draft-ietf-pquip-hybrid-signature-spectrums (version 7)** defines the broader hybrid-signature design space.

### Interoperability

**SafeLogic implemented and tested ML-DSA-65 + Ed25519** at the **IETF 124 hackathon in November 2025**. Multiple independent implementations demonstrated successful interoperability — the maturity signal that the standards work is real and adoption-ready.

### Composite ML-DSA architecture

The composite scheme presents a single public key and a single signature value treated as one atomic algorithm at the protocol level. Security holds as long as **at least one** of the component algorithms remains unbroken — the conservative "belt-and-suspenders" approach favored by regulated industries during the migration window.

### Size and performance penalties

- ML-DSA-65 signature: approximately **3,309 bytes** vs. Ed25519's 64 bytes — a **50× increase**.
- ML-DSA-65 public key: approximately **1,952 bytes** vs. Ed25519's 32 bytes — **60×**.
- Signing/verification cost: ML-DSA is slower than Ed25519 by approximately 5–10×, but still in the microsecond range on commodity hardware.
- Composite signature (Ed25519 + ML-DSA-65): approximately **3,373 bytes** — bandwidth and storage implications must be planned for.

### Implication for LedgerProof

The hybrid migration architecture exists, is standardized, is interoperable in production, and is the consensus answer across NIST, IETF, and the leading PQC vendors. **The architectural question is not whether to support hybrid signatures — it is when to require them.**

---

## 6 · Economic and operational implications of PQC migration

### Costs

- **US federal government** PQC migration cost estimate: **$7.1 billion** (across all agencies, 2024–2035).
- **Typical enterprise** PQC migration: **$8M–$25M** depending on cryptographic footprint complexity, with 2–4 year implementation timelines using internal teams.
- Cost rises as timelines compress and resource demand grows. Late starters face premium pricing for specialist talent.

### Sector readiness

- **Furthest ahead**: defense (under NSA mandate), large financial institutions (DORA monitoring active since January 2025), hyperscalers (Google, Cloudflare, AWS, Microsoft — all with public 2029–2030 commitments).
- **Behind**: healthcare, mid-market enterprises, government contractors below the prime-contractor tier, education, non-FAANG technology companies.
- **ISACA 2025 survey** (2,600+ security professionals): **62% concerned** quantum computing will compromise today's encryption; **only 5%** have a defined quantum strategy in place. This is the gap LedgerProof customers will pay to close.

---

## 7 · Harvest-Now-Decrypt-Later threat assessment

Officially acknowledged as an active threat by **FBI, CISA, NIST**, and corresponding agencies in major democracies.

### State-actor capability

The National Security Agency operates infrastructure specifically designed to capture and store massive volumes of encrypted data for future analysis. Similar capabilities exist in China, Russia, and other states with mature signals-intelligence programs. A National Endowment for Democracy report specifically identifies China's HNDL strategy as a major concern; China has dedicated substantial resources to quantum research and is building quantum communication infrastructure.

### Specific risks for anchored documents

- A document anchored in 2026 with an Ed25519 signature is at risk of **retroactive signature forgery** if an adversary obtains CRQC capability within the document's expected verification horizon.
- A document anchored in 2026 with **only a SHA-256 content hash and no signature** (e.g., a pure OpenTimestamps-style proof) is **not at risk from CRQC** for content integrity. The CRQC threat applies to *authorship signatures*, not to *content integrity*, given current Grover analysis of SHA-256.

### Time horizons

The most consequential documents — court records, sovereign archives, healthcare records, AI lab safety attestations, legal contracts with long enforceability windows, IP filings, journalistic accounts of pivotal events — are precisely the documents whose verification horizons exceed the CRQC timeline.

---

## 8 · Architectural recommendation for LedgerProof Receipt v1.0

### The decision

**Ship hybrid Ed25519 + ML-DSA-65 signatures as an *opt-in profile* in LPR v1.0, with the receipt schema designed from Day 1 to accommodate them at signing time (not as retrofitted re-signatures).**

### Specific recommended changes to the LPR v1.0 specification

The current LPR v1.0 spec (`~/Documents/LedgerProof-Launch-July6/04-lpr-spec/LPR-1.0-SPECIFICATION.md`) has the following signature structure:

```cbor
signature: {
  sig_algo: "Ed25519",
  sig_bytes: <64-byte Ed25519 signature>,
  signer_pubkey: <32-byte Ed25519 public key>
}
```

**Recommended revision to add hybrid-signature capability:**

```cbor
signature: {
  sig_algo: "Ed25519",
  sig_bytes: <64-byte Ed25519 signature>,
  signer_pubkey: <32-byte Ed25519 public key>
},
additional_signatures: [
  {
    sig_algo: "ML-DSA-65" | "ML-DSA-87" | "Composite-ML-DSA-65-Ed25519",
    sig_bytes: <variable-length signature>,
    signer_pubkey: <variable-length public key>
  }
  // ... zero or more additional algorithm signatures
]
```

### Three deployment profiles in LPR v1.0

| Profile | Signature suite | Receipt size | Use case |
|---|---|---|---|
| **Standard** | Ed25519 only | ~64 bytes | Document-volume use cases; the 99% case for v1.0 (2026–2029). |
| **Long-Horizon** | Composite ML-DSA-65 + Ed25519 (per draft-ietf-lamps-pq-composite-sigs) | ~3,400 bytes | Sovereign records, court archives, healthcare records, IP filings, AI safety attestations — anything with a verification horizon past 2035. |
| **High-Assurance** | Composite ML-DSA-87 + Ed25519, with optional SLH-DSA-256 backup | ~10,000 bytes | National-security-grade deployments; intelligence community use; ultra-long-horizon archives. |

### Failure-mode analysis

**Option A — Defer hybrid entirely (Ed25519 only, plan to re-anchor later).** *Failure mode:* receipts produced today become retroactively forgeable when CRQC arrives. The re-anchoring service must work perfectly across the entire 2026 cohort of receipts; any gap leaves documents permanently unverifiable. This option also forecloses LedgerProof's ability to win sovereign and national-security-grade customers in the window 2027–2030 (CNSA 2.0 deadline).

**Option B (RECOMMENDED) — Hybrid as an opt-in profile in v1.0.** *Failure mode:* none significant. Standard-profile customers pay no cost. Long-Horizon-profile customers absorb the size penalty in exchange for guaranteed forward verifiability. The Foundation operates a re-anchoring service for Standard-profile receipts that need to be upgraded later, but this is no longer the *only* migration path.

**Option C — Mandate hybrid for all v1.0 receipts.** *Failure mode:* 50× signature-size penalty on the 99% of customers who do not need long-horizon verifiability, with corresponding bandwidth and storage costs on the verifier infrastructure. This option also makes LedgerProof slower than every incumbent in the document-anchoring space (OpenTimestamps, OriginStamp, Simple Proof, Woleet) for no near-term gain.

### What this means for the v1.0 release

The Long-Horizon profile **must be defined in the v1.0 specification text**, even if reference implementations of the Composite-ML-DSA signing path are not delivered until a v1.0.1 release later in 2026. The schema must accommodate them so that v1.0 customers who anchor documents under the Long-Horizon profile receive future-proof receipts on Day 1.

The migration architecture — re-anchoring of Standard-profile receipts under post-quantum profiles — must be a documented operational commitment of the Foundation, with a target operational date no later than **January 1, 2028**, aligned with the NSA CNSA 2.0 deadline for new NSS systems.

---

## 9 · Day-1 architectural commitments derived from this dossier

These commitments must be embedded in the LPR v1.0 specification text published on July 6, 2026:

1. **Multi-signature receipt schema**: `additional_signatures` array (zero or more), supporting heterogeneous algorithm identifiers. *Required.*
2. **Algorithm-identifier registry**: maintained by the Foundation, with a documented deprecation policy and a published timeline for adding new algorithms (ML-DSA-65, ML-DSA-87, SLH-DSA, FN-DSA when finalized).
3. **Three named profiles** in v1.0: Standard, Long-Horizon, High-Assurance (defined above).
4. **The migration architecture in writing**: published operational commitment that the Foundation operates a re-anchoring service for Standard-profile receipts under post-quantum profiles, operational by **January 1, 2028**.
5. **Conformance test suite**: includes hybrid-signature verification test vectors at v1.0 publication, even if production hybrid-signing tools are not delivered until v1.0.1.
6. **Hash agility — deferred but designed for**: the spec MUST permit future profiles to use SHA-3 or BLAKE3 in place of SHA-256, even though SHA-256 remains the v1.0 default.
7. **Quantum-readiness disclosure**: every receipt's `profile` field explicitly indicates the cryptographic-strength tier, so verifiers and downstream applications can make policy decisions about acceptance.

---

## 10 · Sources

- [Quantum Threat Timeline Report 2025 (Utimaco / postquantum.com)](https://postquantum.com/security-pqc/quantum-threat-timeline-report-2025/)
- [IonQ's 2025 Roadmap: Toward a CRQC by 2028 (postquantum.com)](https://postquantum.com/industry-news/ionqroadmap-crqc/)
- [What 60+ Quantum Hardware Roadmaps Actually Tell Us (postquantum.com)](https://postquantum.com/quantum-computing-companies/quantum-computing-companies-roadmaps/)
- [Google, Cloudflare want post-quantum cryptography by 2029 (ACS Information Age)](https://ia.acs.org.au/article/2026/google--cloudflare-want-post-quantum-cryptography-by-2029.html)
- [NIST Releases First 3 Finalized Post-Quantum Encryption Standards, Aug 2024 (NIST)](https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards)
- [NIST Post-Quantum Cryptography Standardization (Wikipedia)](https://en.wikipedia.org/wiki/NIST_Post-Quantum_Cryptography_Standardization)
- [CNSA 2.0 Algorithms — DoD/NSA published Sep 2022, May 2025 revision](https://media.defense.gov/2025/May/30/2003728741/-1/-1/0/CSA_CNSA_2.0_ALGORITHMS.PDF)
- [CNSA 2.0: Complete Guide to NSA's PQC Requirements (postquantum.com)](https://postquantum.com/cnsa-2-0/complete-guide/)
- [NCSC Releases Timelines for migration to post-quantum cryptography (UK NCSC)](https://www.ncsc.gov.uk/guidance/pqc-migration-timelines)
- [UK NCSC Sets 2035 Deadline for National Migration to Post-Quantum Cryptography (Quantum Computing Report)](https://quantumcomputingreport.com/uks-ncsc-sets-2035-deadline-for-national-migration-to-post-quantum-cryptography/)
- [Post-Quantum Cryptography Compliance Deadlines: EU/ANSSI/BSI (SoftwareSeni)](https://www.softwareseni.com/post-quantum-cryptography-compliance-deadlines-and-what-the-global-regulatory-mandates-require/)
- [Eurosmart on Europe's PQC Competitive Edge](https://www.eurosmart.com/europes-competitive-edge-leading-the-charge-in-post-quantum-cryptography/)
- [Composite ML-DSA Signature Internet-Draft (draft-ietf-lamps-pq-composite-sigs)](https://datatracker.ietf.org/doc/html/draft-ietf-lamps-pq-composite-sigs)
- [Advancing Hybrid Signatures Toward Standardization (SafeLogic, IETF 124)](https://www.safelogic.com/blog/advancing-hybrid-signatures-toward-standardization)
- [A Signature Fit for a Post Quantum Era: Dilithium-Ed25519 (Bill Buchanan)](https://medium.com/asecuritysite-when-bob-met-alice/a-signature-fit-for-a-post-quantum-era-dilithium-ed25519-8e3563be17d9)
- [Estimating the cost of generic quantum pre-image attacks on SHA-2 and SHA-3 (arXiv)](https://arxiv.org/pdf/1603.09383)
- [Quantum Computers Are Not a Threat to 128-bit Symmetric Keys (Valsorda)](https://words.filippo.io/128-bits/)
- [Harvest Now, Decrypt Later: Why the Quantum Threat Is Active Today (Horizen Labs)](https://horizenlabs.io/blog/harvest-now-decrypt-later-the-quantum-threat-your-risk-register-isn-t-tracking)
- [Harvest-Now, Decrypt-Later: A Temporal Cybersecurity Risk in the Quantum Transition (MDPI)](https://www.mdpi.com/2673-4001/6/4/100)
- ["Harvest Now, Decrypt Later": Examining Post-Quantum risks (Federal Reserve FEDS Notes)](https://www.federalreserve.gov/econres/feds/files/2025093pap.pdf)
- [On the Practical Feasibility of Harvest-Now, Decrypt-Later Attacks (arXiv)](https://arxiv.org/pdf/2603.01091)
- [The Post-Quantum Cryptography Transition: Making Progress, But Still a Long Road Ahead (arXiv)](https://arxiv.org/pdf/2503.04806)
- [Google's timeline for PQC migration (Google blog, Feb 2026)](https://blog.google/innovation-and-ai/technology/safety-security/cryptography-migration-timeline/)
- [The Financial Impact of Delaying PQC Migration (Quantum Insider, May 2026)](https://thequantuminsider.com/2026/05/15/why-timing-affects-the-cost-of-post-quantum-migration/)
- [Quantum Security Deadlines are Here – What Happens Next? (Quantum Insider, May 2026)](https://thequantuminsider.com/2026/05/08/post-quantum-migration-timelines-government-industry-impact/)

---

*End of Wave 1 / Domain 1 Dossier. Next domains in Wave 1: IETF SCITT working group + cryptographic provenance standards (Domain 2), AI agent economy growth forecasts (Domain 3), real-world-asset tokenization + stablecoin infrastructure (Domain 4), deepfake/synthetic media volume trajectory (Domain 5), global digital sovereignty + AI regulation (Domain 6), Bitcoin institutional + sovereign adoption (Domain 7), verifiable-AI-provenance commercial landscape (Domain 8).*
