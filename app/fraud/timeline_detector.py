"""
Timeline anomaly detector.

Checks whether admission, discharge, procedure and service dates
are logically consistent.
"""

from datetime import datetime
from typing import Any, Optional

from .fraud_rules import make_finding


DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%d-%m-%Y",
    "%d/%m/%Y",
)


def parse_date(value: Any) -> Optional[datetime]:

    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    value = str(value).strip()

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


class TimelineDetector:

    def detect(
        self,
        claim: dict[str, Any],
        billing_items: list[dict[str, Any]],
    ) -> dict[str, Any]:

        findings = []

        admission = parse_date(
            claim.get("admission_date")
            or claim.get("date_of_admission")
        )

        discharge = parse_date(
            claim.get("discharge_date")
            or claim.get("date_of_discharge")
        )

        # ---------------------------------------------------------------
        # Admission vs discharge
        # ---------------------------------------------------------------

        if admission and discharge:

            if discharge < admission:

                findings.append(
                    {
                        "type": "invalid_admission_discharge",
                        "admission": admission.isoformat(),
                        "discharge": discharge.isoformat(),
                        "reason": "Discharge date occurs before admission date.",
                    }
                )

        # ---------------------------------------------------------------
        # Procedure dates
        # ---------------------------------------------------------------

        for item in billing_items:

            procedure_date = parse_date(
                item.get("date")
                or item.get("service_date")
                or item.get("procedure_date")
            )

            if not procedure_date:
                continue

            procedure_name = (
                item.get("procedure_name")
                or item.get("description")
                or item.get("procedure_code")
                or "Unknown procedure"
            )

            if admission and procedure_date < admission:

                findings.append(
                    {
                        "type": "procedure_before_admission",
                        "procedure": procedure_name,
                        "procedure_date": procedure_date.isoformat(),
                        "admission_date": admission.isoformat(),
                        "reason": (
                            "Procedure/service date occurs before "
                            "the admission date."
                        ),
                    }
                )

            if discharge and procedure_date > discharge:

                findings.append(
                    {
                        "type": "procedure_after_discharge",
                        "procedure": procedure_name,
                        "procedure_date": procedure_date.isoformat(),
                        "discharge_date": discharge.isoformat(),
                        "reason": (
                            "Procedure/service date occurs after "
                            "the discharge date."
                        ),
                    }
                )

        if not findings:

            return make_finding(
                detector="timeline",
                detected=False,
                confidence=0.05,
                severity="NONE",
                reason="No timeline anomalies detected.",
            )

        confidence = min(
            0.95,
            0.65 + 0.06 * len(findings),
        )

        return make_finding(
            detector="timeline",
            detected=True,
            confidence=confidence,
            severity="HIGH",
            reason=f"Detected {len(findings)} timeline inconsistency/inconsistencies.",
            evidence=findings,
        )


def detect_timeline_anomalies(
    claim: dict[str, Any],
    billing_items: list[dict[str, Any]],
) -> dict[str, Any]:

    return TimelineDetector().detect(
        claim,
        billing_items,
    )