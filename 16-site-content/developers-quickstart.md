# Page: `/developers/quickstart`

**Drafted**: Mon Jun 1, 2026 — 22:35 PDT
**Target ship**: Mon Aug 2 (Article 50 enforcement day) — placeholder ships earlier
**Promise**: From this page opening to a Bitcoin-anchored receipt verified in your terminal — under 10 minutes.
**Brand discipline**: Same cream / navy / mint / serif system. Code blocks use the `--mono` font with a navy background and mint syntax highlighting where applicable. Numbered steps. Visual progress indicator.

---

## Page metadata

- **Title**: `LedgerProof Quickstart — Emit and verify your first receipt in 10 minutes`
- **Description**: Install the LedgerProof SDK, emit an EU AI Act Article 50 transparency receipt, and verify it offline against Bitcoin — under 10 minutes, no account required, no LedgerProof server in the path.
- **URL**: `https://ledgerproofhq.io/developers/quickstart`

---

## Hero

**Eyebrow** (mint small caps): `10-MINUTE QUICKSTART · NO ACCOUNT REQUIRED · LOCAL VERIFICATION`

**H1** (serif, navy):
> From `pip install` to a verified Bitcoin-anchored receipt — in ten minutes.

**Subhead** (sans, ink-soft):
> This quickstart walks you through emitting your first LedgerProof transparency receipt and verifying it offline against the Bitcoin chain. No LedgerProof account is required to run the quickstart. No call to LedgerProof's servers is required to verify. If you have Python 3.10+ or Node 20+ installed, you're ten minutes away from your first receipt.

**Two primary CTAs** (pill buttons):
1. `Start with Python` → jumps to Python track
2. `Start with TypeScript` → jumps to TypeScript track

**Tertiary text link**:
> `Read the protocol spec first` → `/spec`

---

## Visual progress indicator (at top, shows throughout)

```
[Step 1: Install] → [Step 2: Initialize] → [Step 3: Emit receipt] → [Step 4: Verify locally] → [Step 5: Production next steps]
```

Highlight current step in mint; completed steps in navy.

---

## Track A — Python (3.10+)

### Step 1 — Install (1 minute)

```bash
pip install ledgerproof==1.1.1rc0
```

What you just installed:
- The LedgerProof Python SDK at pre-release version 1.1.1rc0
- Ed25519 signing primitives (via `cryptography`)
- SHA-256 + RFC 6962 Merkle tree implementation
- Bitcoin block-header verifier (no full-node required)
- Pinned dependencies for reproducible verification

**Verify the install**:
```bash
python -c "import ledgerproof; print(ledgerproof.__version__)"
```
Expected output: `1.1.1rc0`

---

### Step 2 — Initialize (1 minute)

Create a new Python file `quickstart.py`:

```python
from ledgerproof import Deployer, Receipt

# Initialize a Deployer with a development signing key.
# In production, the signing key would be HSM-backed.
# For the quickstart, we generate an ephemeral Ed25519 key in memory.
deployer = Deployer.create_ephemeral(
    deployer_id="quickstart-dev",  # Note: schema rejects emails here (GDPR safety)
    regulatory_context="eu-ai-act-article-50",
)

print(f"Deployer initialized with public key: {deployer.public_key_b64}")
```

Run it:
```bash
python quickstart.py
```

Expected output (your key will differ):
```
Deployer initialized with public key: dG9rZW4tZXhhbXBsZQ==...
```

What you just did:
- Created an in-memory Deployer with an Ed25519 signing keypair
- Bound the deployer identity to a string identifier (the schema validator rejects email-shaped values per GDPR safety net)
- Declared the regulatory context (`eu-ai-act-article-50` is the protocol's reference profile)

---

### Step 3 — Emit your first receipt (2 minutes)

Append to `quickstart.py`:

```python
# Simulate an AI-touched interaction.
# In production this would wrap your actual LLM call.
receipt = deployer.emit(
    model_id="example/gpt-equivalent-1",
    prompt="What is the capital of France?",
    response="The capital of France is Paris.",
    interaction_id="qs-001",
)

print(f"Receipt emitted: {receipt.canonical_hash}")
print(f"Receipt size: {len(receipt.canonical_bytes)} bytes")
print(f"Receipt signature: {receipt.signature_b64[:32]}...")
```

Run again:
```bash
python quickstart.py
```

Expected output (your hash and signature will differ):
```
Deployer initialized with public key: dG9rZW4tZXhhbXBsZQ==...
Receipt emitted: a4f2c1d8e7b3...
Receipt size: 247 bytes
Receipt signature: MEUCIQDvKj8sP2x...
```

What you just did:
- Emitted a LedgerProof Protocol receipt for a single AI-touched interaction
- The receipt contains: canonical encoding of (model_id, prompt_hash, response_hash, timestamp_ns, deployer_id, regulatory_context)
- The receipt is signed with the Deployer's Ed25519 key
- The canonical hash is reproducible — anyone with the same inputs gets the same hash

**Save the receipt for the next step**:
```python
import json
with open("receipt.json", "w") as f:
    json.dump(receipt.to_dict(), f, indent=2)

with open("deployer_public_key.txt", "w") as f:
    f.write(deployer.public_key_b64)
```

---

### Step 4 — Verify the receipt locally (3 minutes)

The big property of LedgerProof: **anyone can verify the receipt without contacting LedgerProof**. We'll verify it now, simulating what an auditor or regulator would do.

Create a new file `verify.py`:

```python
from ledgerproof import Verifier
import json

# Load the receipt and the deployer's public key.
with open("receipt.json") as f:
    receipt_dict = json.load(f)
with open("deployer_public_key.txt") as f:
    deployer_pubkey = f.read().strip()

# Initialize a Verifier. No account, no API key, no LedgerProof connection required.
verifier = Verifier()

# Verify the cryptographic signature.
sig_valid = verifier.verify_signature(receipt_dict, deployer_pubkey)
print(f"Signature valid: {sig_valid}")

# Verify the canonical encoding (catches any post-emission tampering).
canon_valid = verifier.verify_canonical_encoding(receipt_dict)
print(f"Canonical encoding valid: {canon_valid}")

# Inspect what the receipt actually attests.
print("\n--- Receipt contents ---")
for key, value in receipt_dict.items():
    if key == "signature_b64":
        print(f"  {key}: {value[:32]}...")
    else:
        print(f"  {key}: {value}")
```

Run:
```bash
python verify.py
```

Expected output:
```
Signature valid: True
Canonical encoding valid: True

--- Receipt contents ---
  model_id: example/gpt-equivalent-1
  prompt_hash: 3f7e2d1c...
  response_hash: 8b4a9e5f...
  timestamp_ns: 1748834523000000000
  deployer_id: quickstart-dev
  regulatory_context: eu-ai-act-article-50
  signature_b64: MEUCIQDvKj8sP2x...
```

What you just proved:
- The receipt's Ed25519 signature is valid against the published deployer public key
- The canonical encoding is intact (no tampering)
- The receipt's contents are independently inspectable

**You did not contact LedgerProof at any step.** Verification ran entirely against local code and the deployer's public key. This is the protocol property the Foundation exists to protect.

---

### Step 5 — Anchor to Bitcoin (3 minutes — optional in quickstart)

In production, the receipt's Merkle root would be anchored to Bitcoin mainnet via OP_RETURN. The quickstart can simulate this against Bitcoin testnet (or the public OpenTimestamps service) without running a Bitcoin node:

```python
from ledgerproof import Anchor

# Anchor the receipt (uses OpenTimestamps for the quickstart;
# in production, you'd run your own Bitcoin RBF + OTS fallback pipeline).
anchor = Anchor.opentimestamps()
anchored_receipt = anchor.anchor([receipt])

print(f"Anchored to Bitcoin via OpenTimestamps proof.")
print(f"Wait ~6 confirmations (~60 min) then verify the anchor:")
print(f"  python -m ledgerproof.cli verify-anchor receipt.json")
```

The anchor confirms in approximately 60 minutes on Bitcoin mainnet. Until confirmed, the proof is pending — fully cryptographically valid but not yet on-chain.

**For production**: the recommended pattern is a Merkle-batch architecture — N receipts batch into a tree per anchoring window (default 60 minutes), the root signs once via HSM, individual receipts include inclusion proofs. The Kong plugin (target Aug 2) and Snowflake UDF (target Q3) implement this pattern. See `/developers/production-deployment` for the full pattern (post Aug 2 ship).

---

## Track B — TypeScript / Node 20+

### Step 1 — Install (1 minute)

```bash
npm install @ledgerproof/sdk@1.1.1-pre.0
```

Verify:
```bash
node -e "console.log(require('@ledgerproof/sdk').version)"
```
Expected: `1.1.1-pre.0`

### Step 2 — Initialize

Create `quickstart.ts`:

```typescript
import { Deployer } from "@ledgerproof/sdk";

const deployer = await Deployer.createEphemeral({
  deployerId: "quickstart-dev",
  regulatoryContext: "eu-ai-act-article-50",
});

console.log(`Deployer initialized with public key: ${deployer.publicKeyB64}`);
```

### Step 3 — Emit a receipt

```typescript
const receipt = await deployer.emit({
  modelId: "example/gpt-equivalent-1",
  prompt: "What is the capital of France?",
  response: "The capital of France is Paris.",
  interactionId: "qs-001",
});

console.log(`Receipt emitted: ${receipt.canonicalHash}`);
console.log(`Receipt size: ${receipt.canonicalBytes.length} bytes`);
```

### Step 4 — Verify locally

```typescript
import { Verifier } from "@ledgerproof/sdk";

const verifier = new Verifier();
const sigValid = await verifier.verifySignature(receipt, deployer.publicKeyB64);
const canonValid = verifier.verifyCanonicalEncoding(receipt);

console.log(`Signature valid: ${sigValid}`);
console.log(`Canonical encoding valid: ${canonValid}`);
```

### Step 5 — Anchor to Bitcoin (optional)

Same OpenTimestamps pattern as the Python track; full code at `/developers/sdk/typescript`.

---

## Verify a receipt in the browser

The reference verifier portal is open-source and runs entirely in your browser. To verify the receipt you just emitted:

1. Open `verify.ledgerproofhq.io` in any modern browser
2. Drag-drop `receipt.json` onto the page (or paste the JSON into the text area)
3. Paste the deployer public key (`deployer_public_key.txt`)
4. Click `Verify`

The portal will show:
- Signature validity (Ed25519 verification)
- Canonical encoding validity
- Receipt contents in a structured view
- If anchored: the Bitcoin transaction ID and block height; the anchor verification status

The verifier portal is a Vite/TypeScript SPA that does all verification client-side. No server contact required. You can view the source at `github.com/ledgerproof/ledgerproof-verifier`.

You can also run the verifier offline as a single-file HTML page (under 32 KB) — download from the Foundation transparency page.

---

## What you just learned

In ten minutes:
- The LedgerProof SDK is a single-package install in Python or TypeScript
- A receipt is a signed, canonically-encoded record of an AI-touched interaction
- Verification is structurally local — Bitcoin chain + public key + receipt — and does not depend on LedgerProof Inc.'s servers or any other operator's infrastructure
- The protocol property the Foundation exists to protect is exactly this: a regulator, an auditor, or you yourself can verify a receipt against the Bitcoin chain without any third-party service in the path

---

## Next steps

### If you're an engineer evaluating LedgerProof for your stack:

- **Read the spec**: IETF Internet-Draft `draft-dawkins-scitt-ai-article50-00` ([Datatracker](https://datatracker.ietf.org/doc/draft-dawkins-scitt-ai-article50/))
- **Read the SDK reference**: [`/developers/sdk/python`](/developers/sdk/python) | [`/developers/sdk/typescript`](/developers/sdk/typescript) | [`/developers/sdk/rust`](/developers/sdk/rust)
- **Try a production pattern**: [`/developers/patterns/streaming`](/developers/patterns/streaming) (stream-aware signing for chunked HTTP / SSE) | [`/developers/patterns/merkle-batch`](/developers/patterns/merkle-batch) (HSM-backed Merkle batching)
- **Plugin paths**: [`/developers/plugins/kong`](/developers/plugins/kong) (target ship Aug 2) | [`/developers/plugins/langchain`](/developers/plugins/langchain) (target ship Q4) | [`/developers/plugins/snowflake`](/developers/plugins/snowflake) (target Q3)

### If you're integrating LedgerProof in production:

- **Self-hosted operator**: run your own anchoring pipeline. The protocol is permissionless; the spec, SDK, and reference verifier are everything you need. Apache 2.0 license. See [`/developers/self-host`](/developers/self-host).
- **LedgerProof Inc. operator service**: hosted anchoring, SIEM connectors, white-glove implementation. See [`/commercial/founding-members`](/commercial/founding-members) for the tier structure (Standard $50–150K, Anchor $250–500K, Strategic Beta $1M).
- **Hybrid**: many production deployers use the Inc. operator for hosted anchoring while running their own verification infrastructure. The protocol supports either, and the migration path between them is just a configuration change.

### If you want to contribute to the protocol:

- **Read open issues**: [`github.com/ledgerproof/lpr-spec/issues`](https://github.com/ledgerproof/lpr-spec/issues)
- **Submit a PR**: against the spec, the SDKs, the verifier portal, or the plugins
- **Join the IETF SCITT WG conversation**: see [`spec.ledgerproofhq.io/ietf-participation`](https://spec.ledgerproofhq.io/ietf-participation)
- **Apply to the Foundation Technical Steering Committee**: opens Q4 2026 (post Foundation board seating Aug 30)

### If you're a regulator or auditor:

- **Read the Foundation governance**: [`/foundation`](/foundation)
- **Try the verifier portal**: [`verify.ledgerproofhq.io`](https://verify.ledgerproofhq.io)
- **Brief the Foundation team**: email [`foundation@ledgerproof.org`](mailto:foundation@ledgerproof.org)
- **Read the audit memo**: publishes Aug 31, 2026 at [`security.ledgerproofhq.io`](https://security.ledgerproofhq.io)

---

## Footer CTA

Quiet section, cream-on-cream:

**H4** (serif):
> Ten minutes to your first receipt. Twenty-five days to August 2 Article 50 enforcement.

**Two CTAs**:
1. `Read the open protocol spec` → `/spec`
2. `See the Founding Member tiers` → `/commercial/founding-members`

---

## Implementation notes

- HTML page at `/developers/quickstart/index.html` in `ledgerproof-site`
- Code blocks use existing `<pre><code>` pattern with `--mono` font + navy background + cream text
- Track switcher (Python ↔ TypeScript) is JavaScript-toggle on the same page, not separate routes
- Progress indicator at top: simple HTML/CSS, no JS framework
- All code blocks have a `Copy` button (standard pattern)
- All external links (`pip`, `npm`, GitHub) open in new tab with `rel="noopener"`
- Mobile: tracks stack vertically, no toggle

## Code-correctness checklist (engineering review before ship)

- [ ] `pip install ledgerproof==1.1.1rc0` actually works on a fresh venv
- [ ] `npm install @ledgerproof/sdk@1.1.1-pre.0` actually works on a fresh Node 20 install
- [ ] `Deployer.create_ephemeral()` is the actual API surface in the Python SDK (verify with `python -c "from ledgerproof import Deployer; help(Deployer.create_ephemeral)"`)
- [ ] `Deployer.createEphemeral` is the actual API surface in the TypeScript SDK
- [ ] `deployer.emit()` matches the actual signature in both SDKs
- [ ] `Verifier.verify_signature()` and `Verifier.verify_canonical_encoding()` are the actual method names
- [ ] `Anchor.opentimestamps()` is the actual anchor-class API
- [ ] All code blocks copy-paste cleanly without modification needed
- [ ] The "expected output" lines are plausible (not fabricated)

If any of these fails, the SDK API and the quickstart need to be reconciled BEFORE the page ships. Veronica or the senior protocol engineer (post Jul 13 start) should run through the full quickstart on a clean machine and confirm every step works as documented.

## Success criteria

- A developer who lands on this page from npm/PyPI search and follows every step ends up with a verified receipt in under 10 minutes wall-clock
- The page does not require account creation, API key registration, or any LedgerProof Inc. contact
- Every code block works as documented (run by engineering review before ship)
- The "next steps" section answers the question "where do I go from here?" for all five reader archetypes (eval engineer / production integrator / contributor / regulator / commercial buyer)
- Page renders correctly on mobile, loads under 3 seconds on 3G
