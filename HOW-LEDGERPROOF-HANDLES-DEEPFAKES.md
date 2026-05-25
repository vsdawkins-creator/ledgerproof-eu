# How LedgerProof Handles Deepfakes Under EU AI Act Article 50

**Audience:** Regulators, journalists, customers, investors asking specifically about deepfake compliance.
**Tone:** Sober institutional. Includes honest limits.
**Companion document:** `WHAT-LEDGERPROOF-EU-DOES.md`

---

## What Article 50 actually requires for deepfakes

EU AI Act Article 50 distinguishes between four obligations:

| Subsection | Obligation | On whom |
|---|---|---|
| **50(1)** | Mark AI-generated synthetic content (audio/image/video/text) in **machine-readable** form | Providers of the AI system |
| **50(2)** | Disclose that content **constituting a deepfake** is artificially generated or manipulated | Deployers of the system |
| **50(3)** | Disclose AI-generated text published on matters of public interest | Deployers |
| **50(4)** | Exception for evidently artistic / satirical / fictional works | (carve-out) |

A "deepfake" under the Act is AI-generated or AI-manipulated **image, audio, or
video** that resembles real persons, objects, places, entities, or events and
would **appear authentic** to a reasonable observer.

The compliance obligation is **disclosure**, not detection. The law does not
say "stop deepfakes from existing." It says "if you deploy AI to create one,
you must disclose it, machine-readably, in a way regulators can audit later."

That is exactly the gap LedgerProof fills.

---

## How LedgerProof handles deepfakes specifically

The `AiArticle50Content` schema in LPR v1.0 has a `content_category` field
with this enumeration:

```
SYNTHETIC_TEXT
SYNTHETIC_IMAGE
SYNTHETIC_AUDIO
SYNTHETIC_VIDEO
DEEPFAKE             ← Article 50(2) — the specifically-regulated case
SYNTHETIC_MULTIMODAL
AI_ASSISTED_DOCUMENT
```

When a deployer creates a deepfake, the receipt explicitly carries
`content_category: "DEEPFAKE"` — a self-declared, signed, anchored statement:

> *"I, deployer LEI X, on date Y, used AI system Z to produce content
> matching artifact hash H, and I am classifying it as a deepfake under
> Article 50(2)."*

That single declaration is what Article 50 demands, in the **machine-readable**
form Article 50(1) demands, with the **immutability** that 18-month audit
windows demand.

---

## Concrete scenario: a legitimate political campaign

A German political party generates an AI ad featuring a synthetic spokesperson.
Article 50(2) requires disclosure.

### At creation time (under one second):

```
POST /v1/publish
{
  content_type: "ai/article-50/v1",
  content: {
    ai_system_id:           "runwayml/gen-3-alpha",
    deployer_id:            "LEI:54930012ABC...",
    deployer_name:          "Demokratische Partei Bayern",
    deployer_country:       "DE",
    content_category:       "DEEPFAKE",          ← Article 50(2) declaration
    artifact_hash:          "<sha256 of the video file>",
    artifact_content_type:  "video/mp4",
    artifact_bytes:         14823991,
    supervisory_authority:  "BfDI"
  }
}
```

The campaign:
- Embeds a verify link in the ad's description:
  `https://verify.ledgerproofhq.io/r/{receipt_id}`
- Stores the receipt in their media management system
- 24 hours later the receipt is anchored to Bitcoin block N

### At audit time (months or years later):

A regulator (or journalist, or platform safety team) takes the video, hashes
it, looks up the receipt, and confirms:

- ✅ The party publicly attested to its synthetic nature
- ✅ The attestation predates any claim of forgery (Bitcoin proof-of-work
  establishes the timestamp)
- ✅ The exact AI system is named (Runway Gen-3 Alpha)
- ✅ The deployer is identified by LEI, not pseudonymously

**Article 50(2) compliance is now provable, not just claimed.**

---

## What this gives regulators — the asymmetric value

This is the part most people miss when they first hear about LedgerProof:

| Deepfake provenance status | What it tells the regulator |
|---|---|
| Has an LPR receipt with `content_category: DEEPFAKE` | Deployer made the Article 50(2) disclosure. Compliant. Audit trail intact. |
| Has an LPR receipt with `content_category: SYNTHETIC_VIDEO` but not flagged as deepfake | Deployer disclosed AI-generation but classified differently — regulator can investigate the classification call |
| No LPR receipt at all | Either no Article 50 disclosure was made (potential violation) **OR** the content came from outside the regulated EU deployer ecosystem (potential malicious actor) |

This creates an **economic pressure** for legitimate deployers: issuing a
receipt is essentially free (~$0.0001 in Bitcoin fee amortized across the
daily batch) and proves compliance forever. So legitimate deployers issue
them. **Unattributed deepfakes therefore stand out** — their absence of a
receipt becomes a signal.

That is how compliance regimes actually work: not by stopping bad actors,
but by making compliance cheap and visible, so the absence of compliance is
itself evidence.

---

## What LedgerProof does NOT do — honest limits

These limits matter for any regulator conversation. Saying them out loud is
how an institutional protocol earns trust.

| Question | Honest answer |
|---|---|
| Can LedgerProof detect a deepfake? | **No.** Detection is a separate problem solved by tools like Reality Defender, Truepic, Sensity, Hive. LedgerProof is a disclosure layer, not a detection layer. |
| Can LedgerProof prevent malicious deepfakes from being created? | **No.** Nothing can — that's a generation-side problem. LedgerProof makes the *legitimate* disclosure ecosystem auditable, which is what the Act requires. |
| Can LedgerProof force bad actors to issue receipts? | **No.** Bad actors won't comply. The value is making legitimate compliance cheap and provable, so non-compliance becomes anomalous and investigable. |
| If a deepfake has no LedgerProof receipt, does that prove it's malicious? | **No.** Absence is not proof of malice. It's a signal worth investigating — that's all the Act requires from a disclosure mechanism. |
| Can LedgerProof verify the deployer's identity claim is genuine? | **Indirectly.** The LEI is registered with GLEIF; the Ed25519 public key is registered with LedgerProof at onboarding. We do not perform KYC ourselves, but we anchor the deployer's prior public commitment. |

---

## How LedgerProof composes with the full deepfake-regulation stack

A complete deepfake regulatory regime needs three layers, and LedgerProof is
exactly one of them:

```
┌─────────────────────────────────────────────────────────────────┐
│  GENERATION SIDE                                                │
│  ─ AI providers (OpenAI, Anthropic, Runway, etc.) mark outputs  │
│    with C2PA Content Credentials per Article 50(1)              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  DISCLOSURE SIDE  ← LedgerProof EU operates here                │
│  ─ Deployer issues LPR receipt with content_category: DEEPFAKE  │
│  ─ Receipt commits AI system + deployer + hash + date to        │
│    Bitcoin mainnet                                              │
│  ─ Anyone can verify the disclosure independently               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  DETECTION SIDE                                                 │
│  ─ Platforms / fact-checkers / regulators use detection tools   │
│    to flag suspected AI content (Reality Defender, Truepic,     │
│    Sensity, Hive)                                               │
│  ─ When a flagged item lacks an LPR receipt → escalate          │
│  ─ When a flagged item has an LPR receipt → check the           │
│    disclosure was correct                                       │
└─────────────────────────────────────────────────────────────────┘
```

LedgerProof does not compete with C2PA or with detection vendors. It composes
with them. The disclosure layer is where Article 50 lives, and that is the
layer LedgerProof owns.

---

## The one-sentence regulator answer

> *"Under EU AI Act Article 50(2), a deployer who creates a deepfake must
> disclose that fact in a machine-readable form auditable for the lifetime of
> the content. LedgerProof gives that deployer a one-second cryptographic
> receipt naming the AI system, the deployer's LEI, the content category as
> DEEPFAKE, and the document hash — anchored on Bitcoin so the disclosure
> cannot be backdated, retracted, or denied. Regulators verify against
> Bitcoin directly; LedgerProof is not in the trust path after the receipt
> is issued."*

That is the answer. It is true, defensible to a hostile journalist, and
useful at the institutional investor table.

---

*LedgerProof Foundation · How LedgerProof Handles Deepfakes Under EU AI Act Article 50 · May 24, 2026*
