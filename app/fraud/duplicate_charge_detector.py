"""
Duplicate billing detector.

Detects situations where the same procedure/service appears to have
been billed multiple times for the same patient and date.
"""

from collections import defaultdict
from typing import Any 

from .fraud_rules import DUPLICATE_RULES, make_finding


class DuplicateChargeDetector:
    """
    Detect duplicate billing items.

    Expected billing item examples:

    {
        "procedure_code": "PROC-001",
        "procedure_name": "CT Scan",
        "date": "2026-08-10",
        "amount": 25000
    }
    """

    def detect(self, billing_items: list[dict[str, Any]]) -> dict[str, Any]:

        findings = []

        if not billing_items:
            return make_finding(
                detector="duplicate_charge",
                detected=False,
                confidence=0.0,
                severity="NONE",
                reason="No billing items available for duplicate analysis.",
            )

        groups = defaultdict(list)

        for item in billing_items:
            procedure = (
                item.get("procedure_code")
                or item.get("procedure_name")
                or item.get("description")
                or "UNKNOWN"
            )

            date = (
                item.get("date")
                or item.get("service_date")
                or item.get("billing_date")
                or "UNKNOWN"
            )

            amount = item.get("amount", 0)

            key = (str(procedure).lower(), str(date))

            groups[key].append(
                {
                    "procedure": procedure,
                    "date": date,
                    "amount": amount,
                    "item": item,
                }
            )

        for (procedure, date), items in groups.items():

            if len(items) <= 1:
                continue

            duplicate_reason = (
                f"Procedure '{procedure}' appears {len(items)} times "
                f"on the same date ({date})."
            )

            findings.append(
                {
                    "procedure": procedure,
                    "date": date,
                    "count": len(items),
                    "items": items,
                    "reason": duplicate_reason,
                }
            )

        if not findings:
            return make_finding(
                detector="duplicate_charge",
                detected=False,
                confidence=0.05,
                severity="NONE",
                reason="No duplicate charges detected.",
            )

        confidence = min(0.95, 0.65 + (0.05 * len(findings)))

        return make_finding(
            detector="duplicate_charge",
            detected=True,
            confidence=confidence,
            severity="HIGH",
            reason=f"Detected {len(findings)} possible duplicate billing group(s).",
            evidence=findings,
        )


def detect_duplicate_charges(
    billing_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Convenience function.
    """

    return DuplicateChargeDetector().detect(billing_items)