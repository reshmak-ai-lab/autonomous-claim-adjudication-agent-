from typing import Any


def evaluate_non_payable_item(
    item: str,
    non_payable_items: list[str],
) -> dict[str, Any]:
    """
    Determine whether a billed item is non-payable.
    """

    if not item:
        return {
            "rule": "non_payable_items",
            "non_payable": False,
        }

    normalized_item = item.lower().strip()

    matched_item = None

    for non_payable in non_payable_items:
        if non_payable.lower().strip() in normalized_item:
            matched_item = non_payable
            break

    if matched_item:
        return {
            "rule": "non_payable_items",
            "non_payable": True,
            "matched_item": matched_item,
            "decision": "DEDUCT",
        }

    return {
        "rule": "non_payable_items",
        "non_payable": False,
        "decision": "PAYABLE_IF_OTHER_RULES_PASS",
    }