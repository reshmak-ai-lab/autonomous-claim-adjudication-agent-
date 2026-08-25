from datetime import date
from typing import Any


def evaluate_waiting_period(
    policy_start_date: date,
    admission_date: date,
    waiting_period_days: int,
) -> dict[str, Any]:
    """
    Check whether the waiting period has been completed.
    """

    if waiting_period_days < 0:
        raise ValueError(
            "Waiting period cannot be negative"
        )

    if admission_date < policy_start_date:
        return {
            "rule": "waiting_period",
            "applicable": True,
            "eligible": False,
            "reason": "Admission occurred before policy start date",
        }

    elapsed_days = (
        admission_date - policy_start_date
    ).days

    eligible = elapsed_days >= waiting_period_days

    return {
        "rule": "waiting_period",
        "applicable": True,
        "eligible": eligible,
        "elapsed_days": elapsed_days,
        "required_days": waiting_period_days,
        "remaining_days": max(
            0,
            waiting_period_days - elapsed_days,
        ),
    }