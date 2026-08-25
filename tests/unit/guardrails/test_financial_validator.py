"""
Financial validation guardrails.

Validates claim amounts against financial constraints such as
sum insured and ensures monetary values are valid.
"""

from typing import List


class FinancialValidator:

    def validate(
        self,
        claim_amount: float,
        sum_insured: float,
    ) -> List[str]:
        """
        Validate claim amount against the insured amount.

        Returns:
            List of validation errors.
            Empty list means the financial data is valid.
        """

        errors: List[str] = []

        # ---------------------------------------------------------
        # Validate claim amount
        # ---------------------------------------------------------

        try:
            claim = float(claim_amount)
        except (TypeError, ValueError):
            return [
                "Claim amount must be numeric."
            ]

        if claim < 0:
            errors.append(
                "Claim amount cannot be negative."
            )

        # ---------------------------------------------------------
        # Validate sum insured
        # ---------------------------------------------------------

        try:
            insured = float(sum_insured)
        except (TypeError, ValueError):
            errors.append(
                "Sum insured must be numeric."
            )
            return errors

        if insured < 0:
            errors.append(
                "Sum insured cannot be negative."
            )

        # ---------------------------------------------------------
        # Stop if basic validation already failed
        # ---------------------------------------------------------

        if errors:
            return errors

        # ---------------------------------------------------------
        # Validate claim against sum insured
        # ---------------------------------------------------------

        if claim > insured:
            errors.append(
                "Claim amount cannot exceed sum insured."
            )

        return errors