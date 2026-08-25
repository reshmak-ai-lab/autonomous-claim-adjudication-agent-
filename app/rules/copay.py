from typing import Any


def calculate_copay(
    eligible_amount: float,
    copay_percentage: float,
) -> dict[str, Any]:
    """
    Calculate co-pay deduction.
    """

    if eligible_amount < 0:
        raise ValueError(
            "Eligible amount cannot be negative"
        )

    if not 0 <= copay_percentage <= 100:
        raise ValueError(
            "Co-pay percentage must be between 0 and 100"
        )

    copay_amount = (
        eligible_amount
        * copay_percentage
        / 100
    )

    payable_amount = (
        eligible_amount - copay_amount
    )

    return {
        "rule": "copay",
        "eligible_amount": round(
            eligible_amount,
            2,
        ),
        "copay_percentage": copay_percentage,
        "copay_amount": round(
            copay_amount,
            2,
        ),
        "payable_amount": round(
            payable_amount,
            2,
        ),
    }