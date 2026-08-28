"""
Central guardrail pipeline.

All final claim decisions should pass through this pipeline
before being returned to the caller.
"""

from typing import Any

from .models import (
    GuardrailCheck,
    GuardrailResult,
    GuardrailStatus,
)

from .validators import ClaimValidator
from .financial_validator import FinancialValidator
from .policy_validator import PolicyValidator
from .decision_validator import DecisionValidator


class GuardrailPipeline:

    def __init__(self):

        self.claim_validator = (
            ClaimValidator()
        )

        self.financial_validator = (
            FinancialValidator()
        )

        self.policy_validator = (
            PolicyValidator()
        )

        self.decision_validator = (
            DecisionValidator()
        )

    def run(
        self,
        claim: dict[str, Any],
        decision_result: dict[str, Any],
        policy_result: dict[str, Any] | None = None,
    ) -> GuardrailResult:

        result = GuardrailResult(
            passed=True,
            status=GuardrailStatus.PASS,
        )

        # --------------------------------------------------------------
        # 1. Claim validation
        # --------------------------------------------------------------

        claim_errors = (
            self.claim_validator.validate(
                claim
            )
        )

        if claim_errors:

            for error in claim_errors:

                result.add_check(
                    GuardrailCheck(
                        name="claim_validation",
                        status=GuardrailStatus.FAIL,
                        message=error,
                    )
                )

        else:

            result.add_check(
                GuardrailCheck(
                    name="claim_validation",
                    status=GuardrailStatus.PASS,
                    message="Claim validation passed.",
                )
            )

        # --------------------------------------------------------------
        # 2. Financial validation
        # --------------------------------------------------------------

        claimed_amount = decision_result.get(
            "claimed_amount",
            claim.get("claimed_amount", 0),
        )

        payable_amount = decision_result.get(
            "payable_amount",
            0,
        )

        deductions = decision_result.get(
            "deductions",
            {},
        )

        financial_errors = (
            self.financial_validator.validate(
                claimed_amount=claimed_amount,
                payable_amount=payable_amount,
                deductions=deductions,
            )
        )

        if financial_errors:

            for error in financial_errors:

                result.add_check(
                    GuardrailCheck(
                        name="financial_validation",
                        status=GuardrailStatus.FAIL,
                        message=error,
                    )
                )

        else:

            result.add_check(
                GuardrailCheck(
                    name="financial_validation",
                    status=GuardrailStatus.PASS,
                    message="Financial validation passed.",
                )
            )

        # --------------------------------------------------------------
        # 3. Policy validation
        # --------------------------------------------------------------

        decision = decision_result.get(
            "decision"
        )

        policy_errors = (
            self.policy_validator.validate(
                decision=decision,
                policy_result=policy_result,
            )
        )

        if policy_errors:

            for error in policy_errors:

                result.add_check(
                    GuardrailCheck(
                        name="policy_validation",
                        status=GuardrailStatus.FAIL,
                        message=error,
                    )
                )

        else:

            result.add_check(
                GuardrailCheck(
                    name="policy_validation",
                    status=GuardrailStatus.PASS,
                    message="Policy validation passed.",
                )
            )

        # --------------------------------------------------------------
        # 4. Decision validation
        # --------------------------------------------------------------

        decision_errors = (
            self.decision_validator.validate(
                decision=decision,
                claimed_amount=claimed_amount,
                payable_amount=payable_amount,
            )
        )

        if decision_errors:

            for error in decision_errors:

                result.add_check(
                    GuardrailCheck(
                        name="decision_validation",
                        status=GuardrailStatus.FAIL,
                        message=error,
                    )
                )

        else:

            result.add_check(
                GuardrailCheck(
                    name="decision_validation",
                    status=GuardrailStatus.PASS,
                    message="Decision validation passed.",
                )
            )

        # --------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------

        result.metadata = {
            "claim_id": claim.get(
                "claim_id"
            ),
            "decision": decision,
            "claimed_amount": claimed_amount,
            "payable_amount": payable_amount,
        }

        return result