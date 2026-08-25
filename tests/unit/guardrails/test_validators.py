from typing import Any

def validate_required(
    data: dict[str, Any],
    required_fields: list[str],
) -> list[str]:
    """
    Validate that required fields are present and not empty.

    Returns a list of validation errors.
    """

    errors: list[str] = []

    if not isinstance(data, dict):
        return ["Input data must be a dictionary."]

    for field in required_fields:
        if field not in data:
            errors.append(
                f"Missing required field: {field}"
            )
            continue

        value = data[field]

        if value is None:
            errors.append(
                f"Required field is empty: {field}"
            )
            continue

        if isinstance(value, str) and not value.strip():
            errors.append(
                f"Required field is empty: {field}"
            )

    return errors


def validate_positive(
    value: float,
    field_name: str = "field",
) -> bool:
    """
    Validate that a numeric value is greater than zero.
    """

    if value is None:
        return False

    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def validate_non_negative(
    value: float,
    field_name: str = "field",
) -> bool:
    """
    Validate that a numeric value is zero or greater.
    """

    if value is None:
        return False

    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False


def validate_percentage(
    value: float,
    field_name: str = "field",
) -> bool:
    """
    Validate percentage values from 0 to 100.
    """

    if value is None:
        return False

    try:
        value = float(value)
    except (TypeError, ValueError):
        return False

    return 0 <= value <= 100


def validate_date_order(
    start_date,
    end_date,
) -> bool:
    """
    Validate that end_date is not before start_date.
    """

    if start_date is None or end_date is None:
        return False

    return end_date >= start_date


def validate_enum(
    value: Any,
    allowed_values: list[Any],
) -> bool:
    """
    Validate that value belongs to an allowed set.
    """

    return value in allowed_values