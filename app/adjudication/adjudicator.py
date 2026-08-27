"""
Main claim adjudicator.

Coordinates:
- Financial deductions
- Decision generation
- Evidence construction

It does not perform document extraction or policy retrieval itself.
Those responsibilities belong to their respective modules.
"""

from typing import Any, dict, List

from .deduction_engine import DeductionEngine
from .decision_builder import DecisionBuilder
from .evidence_builder import EvidenceBuilder


class Adjudicator:

    def __init__(self):

        self.deduction_engine = DeductionEngine()
        self.decision_builder = DecisionBuilder()
        self.evidence_builder = EvidenceBuilder()

    def adjudicate(
        self,
        claim: dict[str, Any],
        financial_inputs: dict[str, Any] | None = None,
        policy_evidence: List[dict[str, Any]] | None = None,
        clinical_evidence: List[dict[str, Any]] | None = None,
        billing_evidence: List[dict[str, Any]] | None = None,
        rule_evidence: List[dict[str, Any]] | None = None,
        fraud_result: dict[str, Any] | None = None,
        query_required: bool = False,
        policy_issue: bool = False,
    ) -> dict[str, Any]:

        financial_inputs = financial_inputs or {}
        fraud_result = fraud_result or {}

        claim_financials = claim.get("financials", {})

        if not isinstance(claim_financials, dict):
            claim_financials = {}

        claimed_amount = float(
            financial_inputs.get(
                "claimed_amount",
                claim_financials.get(
                    "claimed_amount",
                    claim_financials.get(
                        "requested_amount",
                        claim.get("claimed_amount", 0),
                    ),
                ),
            ) or 0
        )

        if not isinstance(claim_financials, dict):
            claim_financials = {}

        claimed_amount = financial_inputs.get(
            "claimed_amount"
        )

        if claimed_amount is None:
            claimed_amount = claim_financials.get(
                "claimed_amount"
            )

        # Your sample claims use requested_amount
        if claimed_amount is None:
            claimed_amount = claim_financials.get(
                "requested_amount"
            )

        if claimed_amount is None:
            claimed_amount = claim_financials.get(
                "total_bill_amount"
            )

        if claimed_amount is None:
            claimed_amount = claim_financials.get(
                "bill_amount"
            )

        if claimed_amount is None:
            claimed_amount = claim.get(
                "claimed_amount"
            )

        if claimed_amount is None:
            claimed_amount = 0

        claimed_amount = float(claimed_amount)

        # ---------------------------------------------------------------
        # Financial calculation
        # ---------------------------------------------------------------

        deductions = self.deduction_engine.calculate(
            claimed_amount=claimed_amount,
            non_payable_amount=financial_inputs.get(
                "non_payable_amount",
                0,
            ),
            exclusion_amount=financial_inputs.get(
                "exclusion_amount",
                0,
            ),
            room_rent_deduction=financial_inputs.get(
                "room_rent_deduction",
                0,
            ),
            proportional_deduction=financial_inputs.get(
                "proportional_deduction",
                0,
            ),
            copay_percent=financial_inputs.get(
                "copay_percent",
                0,
            ),
            deductible_amount=financial_inputs.get(
                "deductible_amount",
                0,
            ),
            sum_insured_remaining=financial_inputs.get(
                "sum_insured_remaining",
            ),
        )

        payable_amount = deductions["payable_amount"]

        # ---------------------------------------------------------------
        # Fraud result
        # ---------------------------------------------------------------

        fraud_detected = bool(
            fraud_result.get("fraud_detected", False)
        )

        fraud_risk_level = fraud_result.get(
            "risk_level",
            "MINIMAL",
        )

        fraud_evidence = fraud_result.get(
            "findings",
            [],
        )

        # ---------------------------------------------------------------
        # Decision
        # ---------------------------------------------------------------

        decision = self.decision_builder.build(
            claimed_amount=claimed_amount,
            payable_amount=payable_amount,
            fraud_detected=fraud_detected,
            fraud_risk_level=fraud_risk_level,
            policy_issue=policy_issue,
            query_required=query_required,
        )

        # ---------------------------------------------------------------
        # Evidence
        # ---------------------------------------------------------------

        evidence = self.evidence_builder.build(
            claim=claim,
            policy_evidence=policy_evidence,
            clinical_evidence=clinical_evidence,
            billing_evidence=billing_evidence,
            rule_evidence=rule_evidence,
            fraud_evidence=fraud_evidence,
        )

        # ---------------------------------------------------------------
        # Final result
        # ---------------------------------------------------------------

        return {
            "claim_id": claim.get("claim_id"),
            "decision": decision["decision"],
            "reason": decision["reason"],
            "claimed_amount": claimed_amount,
            "payable_amount": payable_amount,
            "deductions": deductions,
            "fraud": {
                "fraud_detected": fraud_detected,
                "risk_level": fraud_risk_level,
                "fraud_score": fraud_result.get(
                    "fraud_score",
                    0.0,
                ),
                "findings": fraud_evidence,
            },
            "evidence": evidence,
        }


def adjudicate_claim(
    claim: dict[str, Any],
    financial_inputs: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Convenience function.
    """

    return Adjudicator().adjudicate(
        claim=claim,
        financial_inputs=financial_inputs,
        **kwargs,
    )


def _extract_claimed_amount(
    self,
    claim: dict[str, Any],
    financial_inputs: dict[str, Any],
) -> float:
    """
    Extract the claimed amount from all supported
    claim financial structures.
    """

    if financial_inputs.get("claimed_amount") is not None:
        return float(
            financial_inputs["claimed_amount"]
        )

    financials = claim.get("financials", {})

    if not isinstance(financials, dict):
        financials = {}

    candidates = [
        financials.get("claimed_amount"),
        financials.get("requested_amount"),
        claim.get("claimed_amount"),
        claim.get("requested_amount"),
    ]

    for amount in candidates:
        if amount is not None:
            try:
                return float(amount)
            except (TypeError, ValueError):
                continue

    return 0.0