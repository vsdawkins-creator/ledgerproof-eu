"""
Multilingual disclosure binding.

Article 50(5) requires the AI-interaction disclosure to be made in a language
the natural person understands — typically the official language of the
Member State where the system is deployed. This example shows how a deployer
operating across DE / FR / IT can emit a `multilingual_disclosure/v1` receipt
that proves the exact disclosure string (and its language tag) shown to the
user, without storing the raw user locale or any PII.

Run:
    export COHERE_API_KEY=...
    python examples/03_multilingual_disclosure.py
"""

from __future__ import annotations

import os

from ledgerproof_cohere import (
    Ed25519Signer,
    LedgerProofCohere,
    LogEmitter,
    RegulatoryContext,
)


# Locale -> (BCP-47 tag, disclosure copy, Cohere chat seed)
DISCLOSURES = {
    "DE": ("de-DE", "Sie chatten mit einer KI.", "Hallo, kannst du mir bei einer Frage helfen?"),
    "FR": ("fr-FR", "Vous discutez avec une IA.", "Bonjour, peux-tu m'aider avec une question?"),
    "IT": ("it-IT", "Stai chattando con un'intelligenza artificiale.", "Ciao, puoi aiutarmi con una domanda?"),
    "NL": ("nl-NL", "U chat met een AI.", "Hallo, kun je me met een vraag helpen?"),
}


def run_for_jurisdiction(client: LedgerProofCohere, member_state: str) -> None:
    lang_tag, disclosure_text, user_message = DISCLOSURES[member_state]

    response = client.chat_with_disclosure(
        disclosure_text=disclosure_text,
        disclosure_language=lang_tag,
        disclosure_channel="chat-ui-banner",
        model="command-a-03-2025",
        messages=[{"role": "user", "content": user_message}],
    )
    print(f"[{member_state} / {lang_tag}]  -> {response.message.content[0].text[:120]}...")


def main() -> None:
    api_key = os.environ.get("COHERE_API_KEY")
    if not api_key:
        raise SystemExit("Set COHERE_API_KEY to run this example.")

    client = LedgerProofCohere(
        deployer_id="acme-corp-eu",
        api_key=api_key,
        signer=Ed25519Signer(),
        emitter=LogEmitter(),
        regulatory_context=RegulatoryContext(
            article_50_paragraph="1",
            deployer_jurisdiction="EU",  # multi-MS deployer
            end_user_disclosure_made=True,
            notes="Per-MS language disclosure under Article 50(5)",
        ),
    )

    for ms in ("DE", "FR", "IT", "NL"):
        run_for_jurisdiction(client, ms)


if __name__ == "__main__":
    main()
