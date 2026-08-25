import re


ABHA_PATTERN = re.compile(
    r"(?<!\d)\d{2}-\d{4}-\d{4}-\d{4}(?!\d)"
)


def normalize_abha(value: str) -> str:
    return value.strip()


def is_valid_abha_format(value: str) -> bool:
    if not value:
        return False

    return bool(
        ABHA_PATTERN.fullmatch(
            normalize_abha(value)
        )
    )


def find_abha_numbers(text: str) -> list[str]:
    if not text:
        return []

    return ABHA_PATTERN.findall(text)