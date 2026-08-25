from __future__ import annotations

import re
import uuid


def sanitize_text(text: str) -> str:
    """
    Perform basic text sanitization.

    This is NOT a replacement for Microsoft Presidio.
    Presidio should perform actual PII/PHI detection and redaction.
    """

    if not text:
        return ""

    # Remove null bytes.
    text = text.replace("\x00", "")

    # Normalize excessive whitespace.
    text = re.sub(r"[ \t]+", " ", text)

    # Limit excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def mask_identifier(
    identifier: str,
    visible_start: int = 2,
    visible_end: int = 2,
    mask_char: str = "*",
) -> str:
    """
    Mask an identifier while preserving a small portion
    at the beginning and end.

    Example:
        PAT-10062
        -> PA****62
    """

    if not identifier:
        return ""

    if len(identifier) <= visible_start + visible_end:
        return mask_char * len(identifier)

    middle_length = (
        len(identifier)
        - visible_start
        - visible_end
    )

    return (
        identifier[:visible_start]
        + mask_char * middle_length
        + identifier[-visible_end:]
    )


def generate_request_id() -> str:
    """
    Generate a unique request identifier for tracing.
    """

    return str(uuid.uuid4())