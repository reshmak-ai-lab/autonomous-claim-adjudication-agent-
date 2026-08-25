from typing import Any


def apply_deductible(
    eligible_amount: float,
    deductible: float,
) -> dict[str, Any]:
    """
    Apply policy deductible.
    """

    if eligible_amount < 0:
        raise ValueError(
            "Eligible amount cannot be negative"
        )

    if deductible < 0:
        raise ValueError(
            "Deductible cannot be negative"
        )

    applied_deductible = min(
        eligible_amount,
        deductible,
    )

    payable_amount = (
        eligible_amount - applied_deductible
    )

    return {
        "rule": "deductible",
        "eligible_amount": round(
            eligible_amount,
            2,
        ),
        "deductible": round(
            applied_deductible,
            2,
        ),
        "payable_amount": round(
            payable_amount,
            2,
        ),
    }