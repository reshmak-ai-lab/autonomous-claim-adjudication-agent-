"""
Final decision guardrails.
"""

from typing import list


class DecisionValidator:

    def validate(
        self,
        decision: str,
        claimed_amount: float,
        payable_amount: float,
    ) -> list[str]:

        errors = []

        try:

            claimed = float(
                claimed_amount
            )

            payable = float(
                payable_amount
            )

        except (
            TypeError,
            ValueError,
        ):

            return [
                "Claimed and payable amounts must be numeric."
            ]

        if decision == "APPROVED":

            if payable < claimed:

                errors.append(
                    "APPROVED decision requires payable "
                    "amount to equal claimed amount."
                )

        elif decision == "PARTIAL_APPROVAL":

            if not (
                0 < payable < claimed
            ):

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

            # A query can have a provisional payable amount.
            pass

        else:

            errors.append(
                f"Unknown decision: {decision}"
            )

        return errors