from app.guardrails import GuardrailPipeline


def test_valid_approved_claim():

    pipeline = GuardrailPipeline()

    claim = {
        "claim_id": "CLM-TEST-001",
        "claimed_amount": 50000,
        "admission_date": "2026-08-10",
        "discharge_date": "2026-08-12",
    }

    decision = {
        "decision": "APPROVED",
        "claimed_amount": 50000,
        "payable_amount": 50000,
        "deductions": {
            "total_deductions": 0,
        },
    }

    result = pipeline.run(
        claim=claim,
        decision_result=decision,
        policy_result={
            "covered": True,
            "exclusion_applies": False,
        },
    )

    assert result.passed is True
    assert result.status.value == "PASS"


def test_invalid_payable_amount():

    pipeline = GuardrailPipeline()

    claim = {
        "claim_id": "CLM-TEST-002",
        "claimed_amount": 50000,
    }

    decision = {
        "decision": "APPROVED",
        "claimed_amount": 50000,
        "payable_amount": 75000,
        "deductions": {
            "total_deductions": 0,
        },
    }

    result = pipeline.run(
        claim=claim,
        decision_result=decision,
    )

    assert result.passed is False
    assert result.status.value == "FAIL"