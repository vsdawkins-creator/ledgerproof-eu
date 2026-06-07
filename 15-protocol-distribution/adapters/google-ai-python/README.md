# ledgerproof-google-ai

LedgerProof adapter for the official Google AI (Gemini) Python SDK
(`google-generativeai`).

Side-channel cryptographic transparency receipts for **EU AI Act Article 50**
evidence. Drop-in wrappers around `GenerativeModel`, `ChatSession`, and
streaming responses produce signed, deterministically encoded receipts on a
side channel without ever modifying the response payload.

---

## Disclaimers (please read)

- **Not endorsed by Google.** This is an independent open-source adapter built
  on the public `google-generativeai` SDK. Google has not reviewed, approved,
  certified, or endorsed this package. "Gemini" and "Google AI" are
  trademarks of Google LLC.
- **No regulator endorsement.** This adapter has not been reviewed, approved,
  or certified by the European Commission, the EU AI Office, any national
  competent authority, or any standards body.
- **No Article 40 presumption of conformity.** Receipts produced here are
  evidentiary artifacts the deployer may choose to keep. They do not create a
  presumption of conformity with the EU AI Act, do not constitute legal
  advice, and do not substitute for the deployer's own Article 50 disclosure
  obligations.
- **Deployer accountability.** The deployer is solely responsible for
  Article 50 compliance, the lawfulness of any data fed to Gemini, the
  end-user disclosures they make, GDPR responsibilities (Articles 5, 6, 13,
  14, 32), and downstream use of the receipts.

(Constraint C1.)

---

## Install

```bash
pip install ledgerproof-google-ai
```

Requires Python 3.10+.

---

## Quickstart

```python
import google.generativeai as genai
from google_ai_ledgerproof import LedgerProofGenerativeModel

genai.configure(api_key="...")

model = LedgerProofGenerativeModel(
    "gemini-2.0-flash",
    deployer_id="acme-eu-bank",
)

response = model.generate_content("Summarize Article 50 of the EU AI Act.")
print(response.text)
# A signed receipt has been emitted on the side channel (LogEmitter by default).
```

## Streaming

```python
response = model.generate_content("Explain transformers.", stream=True)
for chunk in response:
    print(chunk.text, end="")
# Incremental SHA-256 (constraint C6) -- no body buffering.
```

## Chat sessions

```python
chat = model.start_chat()
chat.send_message("Hello.")
chat.send_message("What is Article 50?")
# Each turn emits a chatbot_session/v1 receipt.
```

## Decorator

```python
from google_ai_ledgerproof import lpr_track

@lpr_track(deployer_id="acme-eu-bank", user_message_kwarg="prompt")
def ask(prompt: str):
    return model.generate_content(prompt)
```

## Manual emission

```python
from google_ai_ledgerproof import emit_receipt

response = raw_model.generate_content("Hi.")
signed = emit_receipt(response, deployer_id="acme-eu-bank",
                      user_message_text="Hi.")
```

---

## Design constraints

| ID | Constraint                                                         |
|----|--------------------------------------------------------------------|
| C1 | No regulator/Google endorsement, no Article 40 presumption.        |
| C4 | Local verification only. No phone-home to LedgerProof.             |
| C6 | Stream-aware incremental SHA-256. Never buffer response bodies.    |
| C7 | Side-channel only. Never modify the Gemini response payload.       |

---

## Receipt schemas

- `chatbot_session/v1` — Article 50(1), direct chat interactions.
- `generated_content/v1` — Article 50(2), synthetic content generation.
- `multimodal_generation/v1` — Article 50(2) variant capturing input
  modality types (text/image/audio/video).
- `gemini_function_call/v1` — Article 50(1) variant for tool / function-call
  invocations.

All receipts are deterministically CBOR-encoded (RFC 8949 §4.2), signed with
Ed25519, and verifiable offline.

---

## GDPR guardrails

Receipts MUST NOT contain raw prompt or response text. Content is referenced
by SHA-256 hash only. Identifier fields (`deployer_id`, `session_id`) reject
email-shaped strings to discourage embedding personal data.

---

## License

Apache 2.0. See `LICENSE`.
