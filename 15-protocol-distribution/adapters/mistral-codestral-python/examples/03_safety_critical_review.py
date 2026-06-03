"""
Article 50(4) editorial-control attestation for AI-generated code that is about
to be deployed to a safety-critical or business-critical system.

The flow:
  1. Codestral generates a candidate code artefact (e.g. a money-movement
     handler, an access-control check, a settlement reconciliation function).
  2. A static analyser runs over it and reports a single boolean
     `has_security_pattern` (e.g. semgrep / bandit / CodeQL aggregate verdict).
  3. A human reviewer either approves, approves-with-changes, or rejects.
  4. The deployer calls `emit_safety_critical_review_receipt(...)` BEFORE the
     code is deployed, recording the review outcome under the deployer's
     review-policy ID.

The resulting receipt is signed Ed25519 over deterministic CBOR (RFC 8949),
suitable for anchoring into the LedgerProof Merkle tree.

This receipt does NOT certify that the reviewed code is safe. It records that
a documented review step happened. Liability remains with the deployer.

Requires:
    pip install ledgerproof-mistral-codestral
    (no API key — this example does not call Codestral)
"""

from __future__ import annotations

from datetime import datetime, timezone

from ledgerproof_mistral_codestral import (
    StderrEmitter,
    emit_safety_critical_review_receipt,
)


# Pretend Codestral just returned this candidate. (We do not call the API in
# this example so it runs without an API key.)
CANDIDATE_CODE = (
    "def settle_payment(txn):\n"
    "    if txn.amount <= 0:\n"
    "        raise ValueError('non-positive amount')\n"
    "    if txn.currency not in ALLOWED_CCY:\n"
    "        raise ValueError('currency not allowed')\n"
    "    ledger.debit(txn.src, txn.amount, txn.currency)\n"
    "    ledger.credit(txn.dst, txn.amount, txn.currency)\n"
    "    audit.record(txn)\n"
    "    return True\n"
)


def main() -> int:
    # Step 1: pretend Codestral returned this with response_id 'cmpl_abc_123'.
    response_id = "cmpl_abc_123"
    model_id = "codestral-latest"

    # Step 2: pretend semgrep ran and reported clean.
    has_security_pattern = False
    static_analyser = "semgrep-1.45 OWASP-top-10"

    # Step 3: human reviewer signs off under the bank's documented policy.
    signed = emit_safety_critical_review_receipt(
        deployer_id="acme-bank-eu",
        model_id=model_id,
        response_id=response_id,
        generated_code=CANDIDATE_CODE,
        reviewer_id="reviewer-alice-01",  # opaque internal handle (no PII)
        review_outcome="approved",
        review_completed_at=datetime.now(timezone.utc),
        review_policy_id="acme-bank-payments-secrev-v7",
        deployed=True,
        deployment_target="prod-payments-eu",
        language="python",
        has_security_pattern=has_security_pattern,
        static_analyser=static_analyser,
        emitter=StderrEmitter(),
    )

    print("Emitted safety_critical_code_review/v1 receipt:")
    print("  receipt_id     :", signed["receipt"]["receipt_id"])
    print("  schema         :", signed["receipt"]["schema"])
    print("  reviewer_id    :", signed["receipt"]["safety_review"]["reviewer_id"])
    print("  outcome        :", signed["receipt"]["safety_review"]["review_outcome"])
    print("  policy_id      :", signed["receipt"]["safety_review"]["review_policy_id"])
    print("  deployed       :", signed["receipt"]["safety_review"]["deployed"])
    print("  signature_alg  :", signed["signature_alg"])
    print("  signer_key_id  :", signed["signer_key_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
