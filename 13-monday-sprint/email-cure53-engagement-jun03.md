# Cure53 — Engagement Email (Jun 3, 2026)

**To**: Dr. Mario Heiderich — mario@cure53.de
**Cc**: contact@cure53.de
**From**: Veronica S. Dawkins — veronica@ledgerproof.org
**Subject**: LPR SDK + verifier portal — fast-scoped fuzz + black-box review (Article 50, Aug 2 enforcement)
**Send window**: Wed Jun 3 09:00-09:15 PDT
**Attachment**: `14-seed-close-pack/02-threat-model-briefing.md` (Cure53-scope sections highlighted)

---

Mario —

I'm engaging Cure53 for a fast-scoped, high-yield implementation review on the SDK + verifier-portal layer of an open AI-compliance protocol with a hard EU regulatory deadline. We have two larger firms running enterprise-architecture and Rust/crypto-primitive scopes in parallel; Cure53 is the firm I want for the implementation-fuzzing + slug-router + verifier-portal scope because that's where your team's reputation for finding the bugs that ship in production is unmatched.

**LedgerProof Protocol (LPR) v1.1** is the open IETF SCITT-track protocol (`draft-dawkins-scitt-ai-article50-00`) that anchors AI Article 50 transparency receipts to Bitcoin. EU AI Act Article 50 enforcement begins Aug 2, 2026; combined audit memo published Aug 31.

**Why Cure53, specifically — the scope:**

1. **SDK black-box and white-box fuzzing matrix.** Two SDKs in scope:
   - `ledgerproof` (Python) 1.1.1rc0 — installation: `pip install ledgerproof==1.1.1rc0`
   - `@ledgerproof/sdk` (TypeScript) 1.1.1-pre.0 — installation: `npm install @ledgerproof/sdk@1.1.1-pre.0`

   Public APIs only: receipt creation, receipt verification, Merkle inclusion proof verification, Bitcoin anchor verification (against an offline-snapshot of chain headers), canonical encoding/decoding. Looking for: input-validation bypasses, type-confusion in CBOR decoding, length-prefix attacks, allocation DoS, panic-on-malformed-input.

2. **Slug-router authorization logic.** The verifier portal (`https://ledgerproofhq.io/v/{slug}`) implements a slug-based routing layer that maps human-readable slugs (`founding-declaration`, `0`, etc.) to receipt hashes via two JSON files: `public/aliases.json` and `public/pre-v1-entries.json`. Looking for: authorization bypass (can a user surface a receipt that should not be publicly visible?), slug collision (can two slugs resolve to the same receipt?), TOCTOU between alias resolution and receipt fetch, path-traversal in the slug component.

3. **Verifier portal black-box.** Vite/TypeScript SPA at `https://ledgerproofhq.io/v/`. Looking for: XSS in receipt-content rendering, CSP bypass, postMessage misuse, supply-chain risk in `@noble/ed25519` 2.3.0 + `@noble/hashes` 1.8.0 (both pinned exact; we want you to validate the pinning AND audit the dependency tree).

4. **`/r/{slug}` redirect surface.** The commercial site (`https://ledgerproof.org/r/{slug}`) redirects to the verifier portal. Looking for: open-redirect, mixed-content bypass, referrer leakage.

**What I'm not asking you to scope (going to other firms):**
- Rust + canonicalization + Ed25519 RFC 8032 strict-mode + Merkle proof correctness → Trail of Bits
- HSM integration + stream-aware signing + Merkle-batch + GDPR-soft-delete on Bitcoin → NCC Group

**Budget framework:** $60-90K for the verifier-portal-and-SDK scope as detailed above. 2-week fieldwork window. Memo finalization Aug 17; publication Aug 31 on `security.ledgerproofhq.io/cure53/2026-08-verifier-sdk-audit`.

**Timeline ask:**
- Engagement-letter response by **Mon Jun 8 EOD CET**
- Kickoff call week of Jun 15
- Fieldwork Jun 15 → Jul 26
- Draft memo Aug 3
- Final memo Aug 17
- Combined publication Aug 31

The threat-model briefing attached covers the six-component system architecture. The Cure53-specific drill targets are sections §7 (SDK), §9 (slug-router), and §10 (verifier portal).

I'm available for a 30-min kickoff call Mon Jun 8 or Tue Jun 9, any time PT or CET. Cure53 is the lightest-weight engagement of the three; if your June schedule doesn't accommodate, I'd appreciate knowing by Wed Jun 10 so I can route the SDK-fuzz scope to a contingency provider.

Thanks Mario.

Veronica S. Dawkins
Founder, LedgerProof
veronica@ledgerproof.org · +1-XXX-XXX-XXXX
spec.ledgerproofhq.io · github.com/ledgerproof
