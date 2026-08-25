import re


PAN_PATTERN = re.compile(
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    re.IGNORECASE,
)


def normalize_pan(value: str) -> str:
    return value.strip().upper()


def is_valid_pan_format(value: str) -> bool:
    if not value:
        return False

    return bool(
        PAN_PATTERN.fullmatch(
            normalize_pan(value)
        )
    )


def find_pan_numbers(text: str) -> list[str]:
    if not text:
        return []

    return PAN_PATTERN.findall(text)