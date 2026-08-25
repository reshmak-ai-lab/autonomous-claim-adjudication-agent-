from __future__ import annotations

from datetime import date, datetime
from typing import Union


DateLike = Union[str, date, datetime]


def parse_date(value: DateLike) -> date:
    """
    Convert a string/date/datetime into a date object.

    Supported string format:
        YYYY-MM-DD
    """

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()

    raise TypeError(f"Unsupported date type: {type(value)}")


def days_between(start_date: DateLike, end_date: DateLike) -> int:
    """
    Return number of days between two dates.
    """

    start = parse_date(start_date)
    end = parse_date(end_date)

    return (end - start).days


def months_between(start_date: DateLike, end_date: DateLike) -> int:
    """
    Calculate completed calendar months between two dates.
    """

    start = parse_date(start_date)
    end = parse_date(end_date)

    months = (end.year - start.year) * 12
    months += end.month - start.month

    if end.day < start.day:
        months -= 1

    return max(months, 0)


def is_within_waiting_period(
    policy_start_date: DateLike,
    treatment_date: DateLike,
    waiting_period_months: int,
) -> bool:
    """
    Determine whether treatment occurs within the specified
    policy waiting period.
    """

    elapsed_months = months_between(
        policy_start_date,
        treatment_date,
    )

    return elapsed_months < waiting_period_months


def hospitalization_days(
    admission_date: DateLike,
    discharge_date: DateLike,
) -> int:
    """
    Calculate hospitalization duration.

    Minimum returned value is 1 day.
    """

    days = days_between(admission_date, discharge_date)

    return max(days, 1)