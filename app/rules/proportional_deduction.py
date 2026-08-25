from typing import Any


def calculate_proportional_deduction(
    actual_room_rent: float,
    eligible_room_rent: float,
    bill_amount: float,
) -> dict[str, Any]:
    """
    Calculate proportional deduction when actual room rent
    exceeds the eligible room-rent limit.
    """

    if actual_room_rent <= 0:
        raise ValueError(
            "Actual room rent must be greater than zero"
        )

    if eligible_room_rent < 0:
        raise ValueError(
            "Eligible room rent cannot be negative"
        )

    if bill_amount < 0:
        raise ValueError(
            "Bill amount cannot be negative"
        )

    if actual_room_rent <= eligible_room_rent:
        return {
            "rule": "proportional_deduction",
            "applicable": False,
            "ratio": 1.0,
            "eligible_amount": bill_amount,
            "deduction": 0.0,
        }

    ratio = eligible_room_rent / actual_room_rent

    eligible_amount = bill_amount * ratio
    deduction = bill_amount - eligible_amount

    return {
        "rule": "proportional_deduction",
        "applicable": True,
        "ratio": round(ratio, 4),
        "eligible_amount": round(eligible_amount, 2),
        "deduction": round(deduction, 2),
    }