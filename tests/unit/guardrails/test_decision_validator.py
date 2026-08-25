"""
Final decision guardrails.

Validates whether a claim decision is one of the supported
adjudication decisions.
"""

from typing import List


class DecisionValidator:

    VALID_DECISIONS = {
        "APPROVED",
        "PARTIAL_APPROVAL",
        "REJECTED",
        "QUERY_RAISED",
    }

    def validate(
        self,
        decision: str,
        claimed_amount: float | None = None,
        payable_amount: float | None = None,
    ) -> List[str]:
        """
        Validate a claim decision.

        The decision itself is always validated.

        If claimed_amount and payable_amount are supplied,
        the financial consistency of the decision is also checked.

        Returns:
            List of validation errors.
            Empty list means the decision is valid.
        """

        errors: List[str] = []

        # ---------------------------------------------------------
        # Validate decision
        # ---------------------------------------------------------

        if not decision or not str(decision).strip():
            return ["Decision cannot be empty."]

        decision = str(decision).strip().upper()

        if decision not in self.VALID_DECISIONS:
            return [
                f"Unknown decision: {decision}"
            ]

        # ---------------------------------------------------------
        # If amounts were not supplied, decision validation is
        # sufficient.
        # ---------------------------------------------------------

        if claimed_amount is None or payable_amount is None:
            return errors

        # ---------------------------------------------------------
        # Validate amounts
        # ---------------------------------------------------------

        try:
            claimed = float(claimed_amount)
            payable = float(payable_amount)

        except (TypeError, ValueError):
            return [
                "Claimed and payable amounts must be numeric."
            ]

        if claimed < 0:
            errors.append(
                "Claimed amount cannot be negative."
            )

        if payable < 0:
            errors.append(
                "Payable amount cannot be negative."
            )

        if errors:
            return errors

        # ---------------------------------------------------------
        # Decision-specific financial validation
        # ---------------------------------------------------------

        if decision == "APPROVED":

            if payable != claimed:
                errors.append(
                    "APPROVED decision requires payable "
                    "amount to equal claimed amount."
                )

        elif decision == "PARTIAL_APPROVAL":

            if not (0 < payable < claimed):
                errors.append(
                    "PARTIAL_APPROVAL requires payable "
                    "amount to be greater than zero and "
                    "less than claimed amount."
                )

        elif decision == "REJECTED":

            if payable != 0:
                errors.append(
                    "REJECTED decision requires "
                    "payable amount to be zero."
                )

        elif decision == "QUERY_RAISED":
            # Query can have a provisional payable amount.
            pass

        return errors