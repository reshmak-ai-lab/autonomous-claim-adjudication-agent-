from decimal import Decimal, ROUND_HALF_UP
from typing import Any


class CalculationTools:
    """Deterministic financial calculation tools."""

    @staticmethod
    def money(value: float | int | str) -> Decimal:
        """Convert a value into Decimal safely."""

        return Decimal(str(value))

    @staticmethod
    def calculate_copay(
        eligible_amount: float,
        copay_percentage: float,
    ) -> dict[str, Any]:
        """Calculate co-pay deduction."""

        eligible = CalculationTools.money(eligible_amount)
        percentage = CalculationTools.money(copay_percentage)

        copay_amount = (
            eligible * percentage / Decimal("100")
        )

        payable_amount = eligible - copay_amount

        return {
            "eligible_amount": float(eligible),
            "copay_percentage": float(percentage),
            "copay_amount": float(
                copay_amount.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            ),
            "payable_amount": float(
                payable_amount.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            ),
        }

    @staticmethod
    def calculate_deductible(
        eligible_amount: float,
        deductible: float,
    ) -> dict[str, Any]:
        """Apply deductible to eligible amount."""

        eligible = CalculationTools.money(eligible_amount)
        deductible_amount = CalculationTools.money(deductible)

        payable = max(
            Decimal("0"),
            eligible - deductible_amount,
        )

        return {
            "eligible_amount": float(eligible),
            "deductible": float(deductible_amount),
            "payable_amount": float(
                payable.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            ),
        }

    @staticmethod
    def calculate_proportional_deduction(
        actual_room_rent: float,
        eligible_room_rent: float,
        total_bill: float,
    ) -> dict[str, Any]:
        """
        Calculate proportional deduction when room eligibility
        is lower than the actual room selected.
        """

        actual_room = CalculationTools.money(actual_room_rent)
        eligible_room = CalculationTools.money(eligible_room_rent)
        bill = CalculationTools.money(total_bill)

        if actual_room <= 0:
            raise ValueError(
                "Actual room rent must be greater than zero"
            )

        if eligible_room >= actual_room:
            deduction = Decimal("0")
            eligible_bill = bill
            ratio = Decimal("1")
        else:
            ratio = eligible_room / actual_room
            eligible_bill = bill * ratio
            deduction = bill - eligible_bill

        return {
            "actual_room_rent": float(actual_room),
            "eligible_room_rent": float(eligible_room),
            "total_bill": float(bill),
            "eligible_ratio": float(ratio),
            "proportional_deduction": float(
                deduction.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            ),
            "eligible_bill": float(
                eligible_bill.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            ),
        }

    @staticmethod
    def calculate_final_payable(
        claimed_amount: float,
        non_payable_amount: float = 0,
        deductible: float = 0,
        copay_percentage: float = 0,
    ) -> dict[str, Any]:
        """
        Calculate final payable amount.

        Order:
        1. Remove non-payable amount.
        2. Apply deductible.
        3. Apply co-pay.
        """

        claimed = CalculationTools.money(claimed_amount)
        non_payable = CalculationTools.money(non_payable_amount)
        deductible_amount = CalculationTools.money(deductible)
        copay = CalculationTools.money(copay_percentage)

        eligible = max(
            Decimal("0"),
            claimed - non_payable,
        )

        after_deductible = max(
            Decimal("0"),
            eligible - deductible_amount,
        )

        copay_amount = (
            after_deductible * copay / Decimal("100")
        )

        payable = max(
            Decimal("0"),
            after_deductible - copay_amount,
        )

        return {
            "claimed_amount": float(claimed),
            "non_payable_amount": float(non_payable),
            "eligible_amount": float(eligible),
            "deductible": float(deductible_amount),
            "copay_percentage": float(copay),
            "copay_amount": float(
                copay_amount.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            ),
            "payable_amount": float(
                payable.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            ),
        }