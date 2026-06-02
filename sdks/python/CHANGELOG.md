# Changelog — `ledgerproof` (Python SDK)

All notable changes to the LedgerProof Python SDK. The format adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.1.1rc0 — 2026-06-01 (release-candidate; not yet published to PyPI)

### Added
- This CHANGELOG (back-filling the 1.0.0 release notes from the launch announcement).
- Documentation reference in README pointing to `spec.ledgerproofhq.io/errata/001` (LPR-ERRATA-001) for the Entry #0 historical artifact; clarifies that v1.1+ entries verify correctly under this SDK's content-hash computation.

### Changed
- Dependency pinning narrowed where supply-chain risk is material:
  - `cryptography>=42` (unchanged; Python community broadly trusts this surface)
  - `httpx>=0.27,<1.0` (unchanged)
  - `pydantic>=2.5,<3.0` (unchanged)
- This release is a release-candidate (`rc0`) on the PEP 440 pre-release channel. Install with `pip install --pre ledgerproof==1.1.1rc0`. Promotion to `1.1.1` (final, on the stable channel) is gated on the published Trail of Bits canonicalization audit completion (target: 2026-06-08) per LPR-ERRATA-001.

### Reaffirmed (commitments unchanged from 1.0.0)
- Receipt format is append-only; v1.0 receipts continue to verify under this SDK.
- No PII at the anchor layer; the schema rejects email addresses in policy-protected fields at parse time.
- No content data leaves the customer perimeter; the SDK hashes locally, transmits only hash + non-PII metadata + the receipt structure.
- Receipt fields not understood by older versions are ignored (forward compatibility); never breaking semantics.

### CI / supply-chain
- Cross-language canonical-hash conformance test added to `ledgerproof-platform` CI (PR #3, June 1, 2026). Runs on every PR, every push to main/dev, and nightly. Enforces that no SDK or verifier release exhibits canonicalization drift against the public API for any post-v1.0 entry. The empirical PASS is verified across entries 1+ today; this CI step makes that property a release-gate going forward.

## 1.0.0 — 2026-05-26

### Initial release
- Stripe-style `attach()` pattern for OpenAI, Anthropic, Google Generative AI, Mistral.
- Direct `LedgerProof` API for arbitrary AI artifact issuance.
- Compatible with LangChain via the companion package `langchain-ledgerproof==1.0.0`.
- Production-tested against the LedgerProof Frankfurt EU operator.
- Python 3.9–3.13 compatibility matrix.
- Apache 2.0 license.
