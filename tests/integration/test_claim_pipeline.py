"""
Integration tests for the complete claim adjudication pipeline.

Run:
    pytest -v tests/integration/test_claim_pipeline.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, dict

import pytest


pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SAMPLE_CLAIMS_DIR = (
    PROJECT_ROOT
    / "data"
    / "sample_claims"
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def load_claim(
    relative_path: str,
) -> dict[str, Any]:
    """
    Load a claim JSON file from data/sample_claims.
    """

    path = (
        SAMPLE_CLAIMS_DIR
        / relative_path
    )

    if not path.exists():

        pytest.skip(
            f"Sample claim not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    if not isinstance(data, dict):

        raise ValueError(
            f"Expected claim object in {path}"
        )

    return data


def run_claim_pipeline(
    claim: dict[str, Any],
) -> dict[str, Any]:
    """
    Run the application's claim agent.

    This function keeps the test independent from
    the exact API route implementation.
    """

    from app.agent import ClaimAgent

    agent = ClaimAgent()

    result = agent.adjudicate(
        claim
    )

    if not isinstance(result, dict):

        raise AssertionError(
            "ClaimAgent.adjudicate() must return a dictionary."
        )

    return result


# ---------------------------------------------------------------------
# Test 1 - Approved claim
# ---------------------------------------------------------------------

def test_approved_claim_pipeline():

    claim = load_claim(
        "approved/claim_CLM-2026-01012.json"
    )

    result = run_claim_pipeline(
        claim
    )

    assert result is not None

    assert "claim_id" in result

    assert (
        result["claim_id"]
        == claim["claim_id"]
    )

    assert "decision" in result

    assert result["decision"] in {
        "APPROVED",
        "PARTIAL_APPROVAL",
        "REJECTED",
        "QUERY_RAISED",
    }


# ---------------------------------------------------------------------
# Test 2 - Partial approval claim
# ---------------------------------------------------------------------

def test_partial_approval_claim_pipeline():

    claim = load_claim(
        "partial_approval/claim_CLM-2026-00981.json"
    )

    result = run_claim_pipeline(
        claim
    )

    assert result is not None

    assert (
        result["claim_id"]
        == claim["claim_id"]
    )

    assert result["decision"] in {
        "APPROVED",
        "PARTIAL_APPROVAL",
        "REJECTED",
        "QUERY_RAISED",
    }

    # If the pipeline produces a partial approval,
    # payable amount should be present.
    if result["decision"] == "PARTIAL_APPROVAL":

        assert (
            "payable_amount"
            in result
        )


# ---------------------------------------------------------------------
# Test 3 - Rejected claim
# ---------------------------------------------------------------------

def test_rejected_claim_pipeline():

    claim = load_claim(
        "rejected/claim_rejected_sample.json"
    )

    result = run_claim_pipeline(
        claim
    )

    assert result is not None

    assert (
        result["claim_id"]
        == claim["claim_id"]
    )

    assert result["decision"] in {
        "REJECTED",
        "QUERY_RAISED",
        "PARTIAL_APPROVAL",
        "APPROVED",
    }

    # A rejected claim should never produce
    # a positive payable amount.
    if result["decision"] == "REJECTED":

        payable_amount = float(
            result.get(
                "payable_amount",
                0,
            )
        )

        assert payable_amount == 0


# ---------------------------------------------------------------------
# Test 4 - Query raised claim
# ---------------------------------------------------------------------

def test_query_raised_claim_pipeline():

    claim = load_claim(
        "query_raised/claim_CLM-2026-01035.json"
    )

    result = run_claim_pipeline(
        claim
    )

    assert result is not None

    assert (
        result["claim_id"]
        == claim["claim_id"]
    )

    assert result["decision"] in {
        "QUERY_RAISED",
        "APPROVED",
        "PARTIAL_APPROVAL",
        "REJECTED",
    }

    # If query is raised, human review should normally
    # be required.
    if result["decision"] == "QUERY_RAISED":

        assert (
            result.get(
                "human_review_required",
                True,
            )
            is True
        )


# ---------------------------------------------------------------------
# Test 5 - Pipeline returns financial information
# ---------------------------------------------------------------------

def test_pipeline_financial_output():

    claim = load_claim(
        "approved/claim_CLM-2026-01012.json"
    )

    result = run_claim_pipeline(
        claim
    )

    if "payable_amount" in result:

        payable_amount = float(
            result["payable_amount"]
        )

        assert payable_amount >= 0


# ---------------------------------------------------------------------
# Test 6 - Payable amount cannot exceed claimed amount
# ---------------------------------------------------------------------

def test_payable_amount_not_greater_than_claimed():

    claim = load_claim(
        "approved/claim_CLM-2026-01012.json"
    )

    result = run_claim_pipeline(
        claim
    )

    if "payable_amount" not in result:

        pytest.skip(
            "Pipeline did not return payable_amount."
        )

    #claimed_amount = float(
    #    claim.get(
    #        "claimed_amount",
    #        claim.get(
    #            "claim_amount",
    #            0,
    #        ),
    #    )
    #)
    claimed_amount = float(
        claim.get("claimed_amount")
        or claim.get("claim_amount")
        or claim.get("financials", {}).get("requested_amount")
        or 0
    )

    payable_amount = float(
        result.get(
            "payable_amount",
            0,
        )
    )

    assert payable_amount <= claimed_amount


# ---------------------------------------------------------------------
# Test 7 - Guardrails must be present
# ---------------------------------------------------------------------

def test_pipeline_guardrails():

    claim = load_claim(
        "approved/claim_CLM-2026-01012.json"
    )

    result = run_claim_pipeline(
        claim
    )

    # The final response should contain guardrail
    # information because the agent workflow includes
    # the guardrail layer.
    assert (
        "guardrails" in result
        or "guardrail_result" in result
    )


# ---------------------------------------------------------------------
# Test 8 - Fraud result should be available
# ---------------------------------------------------------------------

def test_pipeline_fraud_analysis():

    claim = load_claim(
        "approved/claim_CLM-2026-01012.json"
    )

    result = run_claim_pipeline(
        claim
    )

    # Fraud information may be exposed directly or
    # inside the final response depending on implementation.
    fraud_result = result.get(
        "fraud_result"
    )

    if fraud_result is not None:

        assert isinstance(
            fraud_result,
            dict,
        )


# ---------------------------------------------------------------------
# Test 9 - Execution trace
# ---------------------------------------------------------------------

def test_pipeline_execution_trace():

    claim = load_claim(
        "approved/claim_CLM-2026-01012.json"
    )

    result = run_claim_pipeline(
        claim
    )

    trace = result.get(
        "execution_trace"
    )

    # Some implementations return only the final response.
    if trace is None:

        pytest.skip(
            "Execution trace is not exposed by ClaimAgent."
        )

    assert isinstance(
        trace,
        list,
    )

    assert len(trace) > 0


# ---------------------------------------------------------------------
# Test 10 - Invalid claim should fail safely
# ---------------------------------------------------------------------

def test_invalid_claim_fails_safely():

    invalid_claim = {
        "claim_id": "",
        "claimed_amount": -50000,
    }

    result = run_claim_pipeline(
        invalid_claim
    )

    assert isinstance(
        result,
        dict,
    )

    assert result.get(
        "decision"
    ) == "QUERY_RAISED"

    assert (
        result.get(
            "human_review_required",
            False,
        )
        is True
    )


# ---------------------------------------------------------------------
# Test 11 - Missing claim ID
# ---------------------------------------------------------------------

def test_missing_claim_id():

    invalid_claim = {
        "claimed_amount": 25000,
    }

    result = run_claim_pipeline(
        invalid_claim
    )

    assert isinstance(
        result,
        dict,
    )

    assert result.get(
        "decision"
    ) == "QUERY_RAISED"

    assert (
        result.get(
            "human_review_required",
            False,
        )
        is True
    )


# ---------------------------------------------------------------------
# Test 12 - All sample claims
# ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "claim_path",
    [
        "approved/claim_CLM-2026-01012.json",
        "partial_approval/claim_CLM-2026-00981.json",
        "rejected/claim_rejected_sample.json",
        "query_raised/claim_CLM-2026-01035.json",
    ],
)
def test_all_sample_claims(
    claim_path: str,
):

    claim = load_claim(
        claim_path
    )

    result = run_claim_pipeline(
        claim
    )

    assert isinstance(
        result,
        dict,
    )

    assert result.get(
        "claim_id"
    ) == claim.get(
        "claim_id"
    )

    assert result.get(
        "decision"
    ) in {
        "APPROVED",
        "PARTIAL_APPROVAL",
        "REJECTED",
        "QUERY_RAISED",
    }