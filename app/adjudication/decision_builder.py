"""
Build the final claim decision from financial and policy results.
"""

from typing import Any


class DecisionBuilder:

    def build(
        self,
        claimed_amount: float,
        payable_amount: float,
        fraud_detected: bool = False,
        fraud_risk_level: str = "MINIMAL",
        policy_issue: bool = False,
        query_required: bool = False,
    ) -> dict[str, Any]:

        claimed_amount = max(0.0, float(claimed_amount))
        payable_amount = max(
            0.0,
            min(float(payable_amount), claimed_amount),
        )

        # Query takes priority when required information is missing.
        if query_required:

            decision = "QUERY_RAISED"

            reason = (
                "Additional information or clarification is required "
                "before the claim can be finalized."
            )

        elif policy_issue and payable_amount <= 0:

            decision = "REJECTED"

            reason = (
                "The claim is not payable under the applicable "
                "policy rules."
            )

        elif payable_amount <= 0:

            decision = "REJECTED"

            reason = (
                "No payable amount remains after applicable "
                "deductions and policy rules."
            )

        elif payable_amount < claimed_amount:

            decision = "PARTIAL_APPROVAL"

            reason = (
                "The claim is partially payable after applying "
                "eligible deductions and policy rules."
            )

        else:

            decision = "APPROVED"

            reason = "The claim is fully payable."

        return {
            "decision": decision,
            "reason": reason,
            "claimed_amount": round(claimed_amount, 2),
            "payable_amount": round(payable_amount, 2),
            "fraud_detected": fraud_detected,
            "fraud_risk_level": fraud_risk_level,
            "policy_issue": policy_issue,
            "query_required": query_required,
        }