from __future__ import annotations
from decimal import ROUND_HALF_UP, Decimal
from typing import Union


Number = Union[int, float, str, Decimal]


def to_decimal(value: Number) -> Decimal:
    """
    Convert numeric input safely to Decimal.
    """

    if isinstance(value, Decimal):
        return value

    return Decimal(str(value))


def money(value: Number) -> Decimal:
    """
    Round an amount to two decimal places.
    """

    amount = to_decimal(value)

    return amount.quantize(
        Decimal(0.01),
        rounding=ROUND_HALF_UP,
    )


def calculate_percentage(
    amount: Number,
    percentage: Number,
) -> Decimal:
    """
    Calculate percentage of an amount.

    Example:
        calculate_percentage(500000, 1)
        -> 5000
    """

    result = (
        to_decimal(amount)
        * to_decimal(percentage)
        / Decimal(100)
    )

    return money(result)


def safe_add(*values: Number) -> Decimal:
    """
    Safely add multiple monetary values.
    """

    total = Decimal(0)

    for value in values:
        total += to_decimal(value)

    return money(total)


def safe_subtract(
    amount: Number,
    *deductions: Number,
) -> Decimal:
    """
    Subtract deductions from an amount.

    Result will never be negative.
    """

    result = to_decimal(amount)

    for deduction in deductions:
        result -= to_decimal(deduction)

    return money(max(result, Decimal(0)))