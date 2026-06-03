"""
Safety-critical code review (Article 50(4) editorial-control) tests.

This schema is emitted *manually* after a human reviewer signs off on generated
code. The receipt records the deployer-asserted facts of the review; it does
NOT certify that the reviewed code is fit for purpose.
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone

from ledgerproof_mistral_codestral import (
    QueueEmitter,
    emit_safety_critical_review_receipt,
)
from ledgerproof_mistral_codestral.canonical import canonical_encode
from ledgerproof_mistral_codestral.signer import Ed25519Signer, verify


_SAMPLE_CODE = (
    "def transfer_funds(src, dst, amount):\n"
    "    assert amount > 0\n"
    "    src.balance -= amount\n"
    "    dst.balance += amount\n"
    "    return True\n"
)


def test_safety_critical_review_receipt_basic_fields():
    captured = []
    signed = emit_safety_critical_review_receipt(
        deployer_id="acme-bank-eu",
        model_id="codestral-latest",
        response_id="cmpl_xyz",
        generated_code=_SAMPLE_CODE,
        reviewer_id="reviewer-alice-01",
        review_outcome="approved",
        review_completed_at=datetime.now(timezone.utc),
        review_policy_id="acme-bank-payments-secrev-v7",
        deployed=True,
        deployment_target="prod-payments-eu",
        language="python",
        has_security_pattern=False,
        static_analyser="semgrep-1.45",
        emitter=QueueEmitter(captured.append),
    )

    assert signed["receipt"]["schema"] == "safety_critical_code_review/v1"
    assert signed["receipt"]["regulatory_context"]["article_50_paragraph"] == "4"
    sr = signed["receipt"]["safety_review"]
    assert sr["reviewer_id"] == "reviewer-alice-01"
    assert sr["review_outcome"] == "approved"
    assert sr["deployed"] is True
    assert sr["deployment_target"] == "prod-payments-eu"
    assert sr["review_policy_id"] == "acme-bank-payments-secrev-v7"

    attrs = signed["receipt"]["code_attributes"]
    assert attrs["language"] == "python"
    # line_count = number of newlines in _SAMPLE_CODE
    assert attrs["line_count"] == _SAMPLE_CODE.count("\n")
    assert attrs["has_security_pattern"] is False
    assert attrs["static_analyser"] == "semgrep-1.45"

    # captured by side-channel emitter (C7)
    assert len(captured) == 1
    assert captured[0] is signed


def test_safety_critical_review_receipt_signature_verifies_offline():
    """C4: offline verification."""
    captured = []
    signer = Ed25519Signer()
    signed = emit_safety_critical_review_receipt(
        deployer_id="acme-bank-eu",
        model_id="codestral-latest",
        response_id="cmpl_zzz",
        generated_code=_SAMPLE_CODE,
        reviewer_id="reviewer-bob-02",
        review_outcome="approved_with_changes",
        review_completed_at=datetime.now(timezone.utc),
        review_policy_id="policy-v1",
        signer=signer,
        emitter=QueueEmitter(captured.append),
    )
    canonical = canonical_encode(signed["receipt"])
    sig = base64.b64decode(signed["signature_b64"])
    assert verify(signer.public_key_bytes(), canonical, sig)


def test_safety_critical_review_does_not_contain_raw_code():
    """GDPR + IP guard: receipt MUST hash the code, never carry it raw."""
    captured = []
    emit_safety_critical_review_receipt(
        deployer_id="acme-bank-eu",
        model_id="codestral-latest",
        response_id="cmpl_no_raw",
        generated_code=_SAMPLE_CODE,
        reviewer_id="r1",
        review_outcome="approved",
        review_completed_at=datetime.now(timezone.utc),
        review_policy_id="p1",
        emitter=QueueEmitter(captured.append),
    )
    # The raw source string must not appear anywhere in the serialised receipt.
    import json
    blob = json.dumps(captured[0], default=str)
    assert "transfer_funds" not in blob
    assert "src.balance" not in blob


def test_rejected_outcome_does_not_imply_deployed():
    captured = []
    signed = emit_safety_critical_review_receipt(
        deployer_id="acme-bank-eu",
        model_id="codestral-latest",
        response_id="cmpl_rej",
        generated_code=_SAMPLE_CODE,
        reviewer_id="r2",
        review_outcome="rejected",
        review_completed_at=datetime.now(timezone.utc),
        review_policy_id="p1",
        deployed=False,
        emitter=QueueEmitter(captured.append),
    )
    sr = signed["receipt"]["safety_review"]
    assert sr["review_outcome"] == "rejected"
    assert sr["deployed"] is False
