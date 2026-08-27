"""
Unbundling detector.

Attempts to identify procedures that may have been billed separately
even though they could represent components of a bundled service.
"""
from app.fraud.unbundling_detector import UnbundlingDetector
import re
from typing import Any, dict, List


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


def normalize_procedure_name(value: str) -> str:
    """
    Normalize a billing procedure name.

    Examples:
        "Pre Op Consultation" -> "pre_op_consultation"
        "Surgical Procedure" -> "surgical_procedure"
        "Lens Implant" -> "lens_implant"
    """

    value = str(value).strip().lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "_",
        value,
    )

    return value.strip("_")


class UnbundlingDetector:

    def detect(
        self,
        billing_items: List[dict[str, Any]],
    ) -> dict[str, Any]:

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
                    "name": normalize_procedure_name(name),
                    "date": (
                        item.get("date")
                        or item.get("service_date")
                    ),
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
                        break

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
            confidence=min(
                0.90,
                0.60 + len(findings) * 0.08,
            ),
            severity="MEDIUM",
            reason=(
                f"Detected {len(findings)} "
                "possible unbundling pattern(s)."
            ),
            evidence=findings,
        )


def detect_unbundling(
    billing_items: List[dict[str, Any]],
) -> dict[str, Any]:

    return UnbundlingDetector().detect(
        billing_items
    )