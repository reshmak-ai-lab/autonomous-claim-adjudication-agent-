"""
Common utility functions for the Autonomous Claim Adjudication system.
"""

from .dates import (
    parse_date,
    days_between,
    months_between,
    is_within_waiting_period,
)

from .amounts import (
    to_decimal,
    money,
    calculate_percentage,
    safe_add,
    safe_subtract,
)

from .hashing import (
    generate_hash,
    hash_text,
    generate_claim_hash,
)

from .security import (
    sanitize_text,
    mask_identifier,
    generate_request_id,
)

__all__ = [
    "parse_date",
    "days_between",
    "months_between",
    "is_within_waiting_period",
    "to_decimal",
    "money",
    "calculate_percentage",
    "safe_add",
    "safe_subtract",
    "generate_hash",
    "hash_text",
    "generate_claim_hash",
    "sanitize_text",
    "mask_identifier",
    "generate_request_id",
]