from app.agent import ClaimAgent


def test_claim_agent():

    agent = ClaimAgent()

    claim = {
        "claim_id": "CLM-TEST-001",
        "claimed_amount": 50000,
        "admission_date": "2026-08-10",
        "discharge_date": "2026-08-12",
    }

    result = agent.adjudicate(claim)

    assert result["claim_id"] == "CLM-TEST-001"

    assert result["decision"] in {
        "APPROVED",
        "PARTIAL_APPROVAL",
        "REJECTED",
        "QUERY_RAISED",
    }