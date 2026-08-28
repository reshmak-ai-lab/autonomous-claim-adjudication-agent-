"""
Financial deduction engine.

Calculates eligible amount and deductions before final adjudication.
"""

from typing import Any


class DeductionEngine:

    def calculate(
        self,
        claimed_amount: float,
        non_payable_amount: float = 0.0,
        exclusion_amount: float = 0.0,
        room_rent_deduction: float = 0.0,
        proportional_deduction: float = 0.0,
        copay_percent: float = 0.0,
        deductible_amount: float = 0.0,
        sum_insured_remaining: float | None = None,
    ) -> dict[str, Any]:

        claimed_amount = max(0.0, float(claimed_amount))

        non_payable_amount = max(0.0, float(non_payable_amount))
        exclusion_amount = max(0.0, float(exclusion_amount))
        room_rent_deduction = max(0.0, float(room_rent_deduction))
        proportional_deduction = max(0.0, float(proportional_deduction))
        deductible_amount = max(0.0, float(deductible_amount))

        subtotal = (
            claimed_amount
            - non_payable_amount
            - exclusion_amount
            - room_rent_deduction
            - proportional_deduction
        )

        subtotal = max(0.0, subtotal)

        copay_amount = subtotal * (
            max(0.0, min(100.0, copay_percent)) / 100.0
        )

        payable_before_deductible = max(
            0.0,
            subtotal - copay_amount,
        )

        payable_amount = max(
            0.0,
            payable_before_deductible - deductible_amount,
        )

        # Apply remaining sum insured limit.
        if sum_insured_remaining is not None:

            sum_insured_remaining = max(
                0.0,
                float(sum_insured_remaining),
            )

            payable_amount = min(
                payable_amount,
                sum_insured_remaining,
            )

        total_deductions = max(
            0.0,
            claimed_amount - payable_amount,
        )

        return {
            "claimed_amount": round(claimed_amount, 2),
            "non_payable_amount": round(non_payable_amount, 2),
            "exclusion_amount": round(exclusion_amount, 2),
            "room_rent_deduction": round(room_rent_deduction, 2),
            "proportional_deduction": round(proportional_deduction, 2),
            "copay_percent": round(copay_percent, 2),
            "copay_amount": round(copay_amount, 2),
            "deductible_amount": round(deductible_amount, 2),
            "total_deductions": round(total_deductions, 2),
            "payable_amount": round(payable_amount, 2),
        }