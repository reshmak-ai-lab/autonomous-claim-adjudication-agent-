"""
Financial guardrails.

Ensures that adjudication calculations do not produce
invalid or contradictory amounts.
"""

from typing import Any, Dict, List


class FinancialValidator:

    def validate(
        self,
        claimed_amount: float,
        payable_amount: float,
        deductions: Dict[str, Any] | None = None,
    ) -> List[str]:

        errors = []

        deductions = deductions or {}

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

        if claimed < 0:

            errors.append(
                "Claimed amount cannot be negative."
            )

        if payable < 0:

            errors.append(
                "Payable amount cannot be negative."
            )

        if payable > claimed:

            errors.append(
                "Payable amount cannot exceed claimed amount."
            )

        total_deductions = deductions.get(
            "total_deductions"
        )

        if total_deductions is not None:

            try:

                total_deductions = float(
                    total_deductions
                )

                expected = (
                    claimed - payable
                )

                # Small tolerance for floating point calculations.
                if abs(
                    total_deductions - expected
                ) > 0.01:

                    errors.append(
                        "Total deductions do not match "
                        "claimed amount minus payable amount."
                    )

            except (
                TypeError,
                ValueError,
            ):

                errors.append(
                    "Total deductions must be numeric."
                )

        return errors