from typing import Any


def evaluate_room_rent(
    actual_room_rent: float,
    eligible_room_rent: float,
) -> dict[str, Any]:
    """
    Evaluate whether the selected room is within the policy limit.
    """

    if actual_room_rent < 0:
        raise ValueError("Actual room rent cannot be negative")

    if eligible_room_rent < 0:
        raise ValueError("Eligible room rent cannot be negative")

    if actual_room_rent <= eligible_room_rent:
        return {
            "rule": "room_rent",
            "applicable": True,
            "within_limit": True,
            "actual_room_rent": actual_room_rent,
            "eligible_room_rent": eligible_room_rent,
            "excess_room_rent": 0.0,
            "decision": "NO_DEDUCTION",
        }

    excess = actual_room_rent - eligible_room_rent

    return {
        "rule": "room_rent",
        "applicable": True,
        "within_limit": False,
        "actual_room_rent": actual_room_rent,
        "eligible_room_rent": eligible_room_rent,
        "excess_room_rent": excess,
        "decision": "PROPORTIONAL_DEDUCTION_REQUIRED",
    }