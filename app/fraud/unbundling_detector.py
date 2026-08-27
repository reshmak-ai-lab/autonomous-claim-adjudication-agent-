"""
Unbundling detector.

Attempts to identify procedures that may have been billed separately
even though they could represent components of a bundled service.
"""

from typing import Any, Dict, list

from .fraud_rules import make_finding


# Example configurable procedure relationships.
# Extend this based on your hospital tariff master/policy.
BUNDLED_PROCEDURES = {
    "surgery": {
        "pre_op_consultation",
        "surgical_procedure",
        "post_op_followup",
    },
    "cataract_surgery": {
        "cataract_surgery",
        "lens_implant",
    },
    "appendectomy": {
        "appendectomy",
        "surgical_anesthesia",
    },
}


class UnbundlingDetector:

    def detect(
        self,
        billing_items: list[Dict[str, Any]],
    ) -> Dict[str, Any]:

        findings = []

        normalized_items = []

        for item in billing_items:

            name = (
                item.get("procedure_name")
                or item.get("description")
                or item.get("procedure_code")
                or ""
            )

            normalized_items.append(
                {
                    "name": str(name).strip().lower(),
                    "date": item.get("date") or item.get("service_date"),
                    "amount": item.get("amount", 0),
                    "item": item,
                }
            )

        for bundle_name, bundle_items in BUNDLED_PROCEDURES.items():

            present_items = []

            for item in normalized_items:

                item_name = item["name"]

                for expected in bundle_items:

                    if expected in item_name:
                        present_items.append(item)

            unique_names = {
                item["name"]
                for item in present_items
            }

            if len(unique_names) >= 2:

                findings.append(
                    {
                        "bundle": bundle_name,
                        "procedures": list(unique_names),
                        "items": present_items,
                        "reason": (
                            f"Multiple components associated with the "
                            f"'{bundle_name}' bundle were billed separately."
                        ),
                    }
                )

        if not findings:
            return make_finding(
                detector="unbundling",
                detected=False,
                confidence=0.05,
                severity="NONE",
                reason="No potential unbundling detected.",
            )

        return make_finding(
            detector="unbundling",
            detected=True,
            confidence=min(0.90, 0.60 + len(findings) * 0.08),
            severity="MEDIUM",
            reason=f"Detected {len(findings)} possible unbundling pattern(s).",
            evidence=findings,
        )


def detect_unbundling(
    billing_items: list[Dict[str, Any]],
) -> Dict[str, Any]:

    return UnbundlingDetector().detect(billing_items)