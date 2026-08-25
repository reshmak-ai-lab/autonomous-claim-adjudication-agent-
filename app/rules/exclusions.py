from typing import Any


def evaluate_exclusion(
    item: str,
    exclusions: list[str],
) -> dict[str, Any]:
    """
    Check whether an item matches an exclusion.
    """

    if not item:
        return {
            "rule": "exclusions",
            "excluded": False,
            "reason": "No item provided",
        }

    normalized_item = item.lower().strip()

    matched_exclusion = None

    for exclusion in exclusions:
        if exclusion.lower().strip() in normalized_item:
            matched_exclusion = exclusion
            break

    if matched_exclusion:
        return {
            "rule": "exclusions",
            "excluded": True,
            "matched_exclusion": matched_exclusion,
            "decision": "NOT_PAYABLE",
        }

    return {
        "rule": "exclusions",
        "excluded": False,
        "decision": "PAYABLE_IF_OTHER_RULES_PASS",
    }