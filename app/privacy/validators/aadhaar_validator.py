import re


AADHAAR_PATTERN = re.compile(
    r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)"
)


def normalize_aadhaar(value: str) -> str:
    return re.sub(r"[\s-]", "", value)


def is_valid_aadhaar_format(value: str) -> bool:
    """
    Validate Aadhaar number format.

    This validates structure only, not whether the number
    actually belongs to a person.
    """

    if not value:
        return False

    normalized = normalize_aadhaar(value)

    return bool(
        re.fullmatch(r"\d{12}", normalized)
    )


def find_aadhaar_numbers(text: str) -> list[str]:
    if not text:
        return []

    return AADHAAR_PATTERN.findall(text)