from __future__ import annotations

import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CLAIMS_DIR = (
    PROJECT_ROOT
    / "data"
    / "sample_claims"
)


EXPECTED_CLAIMS = {
    "approved/claim_CLM-2026-01012.json": "APPROVED",
    "partial_approval/claim_CLM-2026-00981.json": "PARTIAL_APPROVAL",
    "rejected/claim_rejected_sample.json": "REJECTED",
    "query_raised/claim_CLM-2026-01035.json": "QUERY_RAISED",
}


def load_claim(relative_path: str) -> dict:
    """
    Load a sample claim.

    The project sample files contain the claim
    fields directly at the top level.
    """

    path = CLAIMS_DIR / relative_path

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
        pytest.fail(
            f"Claim file must contain a JSON object: {path}"
        )

    return data

def run_claim_pipeline(claim: dict):
    """
    Run the project's ClaimWorkflow using the state
    structure expected by the workflow.
    """

    try:
        from app.agent.workflows.claim_workflow import ClaimWorkflow
    except ImportError as exc:
        pytest.fail(
            f"Could not import ClaimWorkflow: {exc}"
        )

    workflow = ClaimWorkflow()

    # ClaimWorkflow expects:
    #
    # {
    #     "claim": <claim data>
    # }
    #
    # rather than receiving the raw claim directly.

    state = {
        "claim": claim
    }

    if hasattr(workflow, "run"):
        return workflow.run(state)

    if hasattr(workflow, "execute"):
        return workflow.execute(state)

    if hasattr(workflow, "invoke"):
        return workflow.invoke(state)

    pytest.fail(
        "ClaimWorkflow must expose "
        "run(), execute(), or invoke()."
    )

def extract_decision(result):
    if result is None:
        return None

    if isinstance(result, str):
        return result.upper()

    if isinstance(result, dict):

        # ClaimWorkflow final decision
        value = result.get("final_decision")
        if value:
            return str(value).upper()

        # Direct decision
        value = result.get("decision")
        if value:
            return str(value).upper()


        # Adjudication result
        adjudication = result.get("adjudication_result")

        if isinstance(adjudication, dict):
            value = adjudication.get("decision")
            if value:
                return str(value).upper()

        # Nested state
        state = result.get("state")

        if isinstance(state, dict):
            return extract_decision(state)

    return None


def extract_amounts(result):
    """
    Extract claimed and payable amounts.
    """

    if not isinstance(result, dict):
        return None, None

    claimed = result.get(
        "claimed_amount"
    )

    payable = result.get(
        "payable_amount"
    )

    # Check nested workflow state.
    if claimed is None or payable is None:

        state = result.get("state")

        if isinstance(state, dict):

            if claimed is None:
                claimed = state.get(
                    "claimed_amount"
                )

            if payable is None:
                payable = state.get(
                    "payable_amount"
                )

    return claimed, payable


@pytest.mark.evaluation
@pytest.mark.parametrize(
    "relative_path,expected_decision",
    EXPECTED_CLAIMS.items(),
)
def test_adjudication_decision_accuracy(
    relative_path,
    expected_decision,
):
    """
    Verify that every sample claim receives
    the expected adjudication decision.
    """

    claim = load_claim(
        relative_path
    )

    result = run_claim_pipeline(
        claim
    )

    print("\n" + "=" * 70)
    print("EVALUATION WORKFLOW RESULT")
    print("=" * 70)
    print(result)
    print("=" * 70)

    actual_decision = extract_decision(
        result
    )

    assert actual_decision is not None, (
        f"No adjudication decision returned "
        f"for {relative_path}.\n"
        f"Pipeline result: {result}"
    )

    assert actual_decision == expected_decision, (
        f"Decision mismatch for "
        f"{relative_path}.\n"
        f"Expected: {expected_decision}\n"
        f"Actual: {actual_decision}\n"
        f"Result: {result}"
    )


@pytest.mark.evaluation
def test_payable_amount_not_greater_than_claimed():
    """
    Payable amount must never exceed claimed amount.
    """

    for relative_path in EXPECTED_CLAIMS:

        claim = load_claim(
            relative_path
        )

        result = run_claim_pipeline(
            claim
        )

        claimed, payable = extract_amounts(
            result
        )

        if claimed is None:

            # Fall back to input claim.
            claimed = claim.get(
                "claimed_amount"
            )

        if payable is None:

            payable = result.get(
                "payable_amount"
            ) if isinstance(
                result,
                dict,
            ) else None

        if claimed is not None and payable is not None:

            assert float(payable) <= float(claimed), (
                f"{relative_path}: "
                f"payable amount {payable} "
                f"exceeds claimed amount {claimed}"
            )
            