# Foundation Governance Event — consultation_submission_eu_ai_office

**Event timestamp**: 2026-06-02T22:18:55.527642+00:00
**Anchored file**: `consultation-01-article-50-guidelines-jun02.pdf` (SHA-256: `753e48d51fddfcd7776b0fcbb9777d1d4216716391ff3d424ea10f6701552c98`)
**Receipt**: `receipt.json` (canonical SHA-256: `20bcf1aa275268ebe1418c7b4ccb7eb0ecfb3ab7c9547b9af0c321024344b25f`)
**OpenTimestamps proof**: `receipt.json.ots`

## Verification

To verify the anchor (after Bitcoin confirmation, typically within 1-6 hours):

```bash
ots upgrade receipt.json.ots
ots verify receipt.json
```

To verify the signature:

```python
import json, base64, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

receipt = json.load(open("receipt.json"))
canonical = json.dumps(receipt["body"], sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")

pub_b64 = receipt["body"]["signing_key"]["public_key_b64"]
pub_raw = base64.b64decode(pub_b64)
pub_key = Ed25519PublicKey.from_public_bytes(pub_raw)

sig = base64.b64decode(receipt["signature_b64"])
pub_key.verify(sig, canonical)
print("Signature verified.")
```

## Interim key disclosure

This receipt is signed by the Foundation's interim Ed25519 signing key (created
2026-06-02 when no Foundation governance
events had yet been anchored). The Foundation root-key ceremony scheduled for
August 15, 2026 will rotate to a 2-of-3 multisig. The rotation will be itself
recorded as a Foundation governance event, signed by this interim key,
establishing an unbroken key authority chain.

## Self-attesting metadata

- **consultation_target**: European Commission DG-CNECT AI Office
- **consultation_topic**: Draft Guidelines on transparency obligations under Article 50 AI Act
- **submission_platform**: ec.europa.eu/eusurvey/runner/contactform/Art50guidelines
- **closing_date**: 2026-06-03
- **foundation_voice**: institutional Foundation submission on Foundation letterhead
- **sections_addressed**: II III IV VI VII
- **submission_confirmed**: Your request has been sent to the survey owner
- **submission_date**: 2026-06-02