"""
Policy guardrails.

Checks whether the final decision is consistent with
the policy evaluation result.
"""

from typing import Any


class PolicyValidator:

    VALID_DECISIONS = {
        "APPROVED",
        "PARTIAL_APPROVAL",
        "REJECTED",
        "QUERY_RAISED",
    }

    def validate(
        self,
        decision: str,
        policy_result: dict[str, Any] | None = None,
    ) -> list[str]:

        errors = []

        policy_result = policy_result or {}

        if decision not in self.VALID_DECISIONS:

            errors.append(
                f"Invalid adjudication decision: {decision}"
            )

        policy_covered = policy_result.get(
            "covered"
        )

        if (
            decision == "APPROVED"
            and policy_covered is False
        ):

            errors.append(
                "Claim cannot be APPROVED because "
                "the policy evaluation indicates it is not covered."
            )

        exclusion_applies = policy_result.get(
            "exclusion_applies",
            False,
        )

        if (
            decision == "APPROVED"
            and exclusion_applies
        ):

            errors.append(
                "Claim cannot be APPROVED because "
                "a policy exclusion applies."
            )

        return errors