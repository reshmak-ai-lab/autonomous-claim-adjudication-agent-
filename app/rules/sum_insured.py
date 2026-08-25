from typing import Any


def evaluate_sum_insured(
    claimed_amount: float,
    sum_insured: float,
    already_paid: float = 0.0,
) -> dict[str, Any]:
    """
    Determine the amount available under the sum insured.
    """

    if claimed_amount < 0:
        raise ValueError(
            "Claimed amount cannot be negative"
        )

    if sum_insured < 0:
        raise ValueError(
            "Sum insured cannot be negative"
        )

    if already_paid < 0:
        raise ValueError(
            "Already paid amount cannot be negative"
        )

    remaining_sum_insured = max(
        0.0,
        sum_insured - already_paid,
    )

    eligible_amount = min(
        claimed_amount,
        remaining_sum_insured,
    )

    excess_amount = max(
        0.0,
        claimed_amount - remaining_sum_insured,
    )

    return {
        "rule": "sum_insured",
        "sum_insured": sum_insured,
        "already_paid": already_paid,
        "remaining_sum_insured": remaining_sum_insured,
        "claimed_amount": claimed_amount,
        "eligible_amount": eligible_amount,
        "excess_amount": excess_amount,
    }