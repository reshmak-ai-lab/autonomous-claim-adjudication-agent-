from app.adjudication import Adjudicator


def test_partial_approval():
    adjudicator = Adjudicator()

    claim = {
        "claim_id": "CLM-TEST-001",
        "claimed_amount": 100000,
    }

    result = adjudicator.adjudicate(
        claim=claim,
        financial_inputs={
            "claimed_amount": 100000,
            "non_payable_amount": 10000,
            "copay_percent": 10,
            "deductible_amount": 5000,
        },
    )

    assert result["decision"] == "PARTIAL_APPROVAL"
    assert result["payable_amount"] < 100000
    assert result["payable_amount"] >= 0