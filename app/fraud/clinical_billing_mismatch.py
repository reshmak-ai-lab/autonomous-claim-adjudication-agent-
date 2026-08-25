"""
Clinical vs billing mismatch detector.

Compares diagnoses/clinical information with billed procedures.

This is a rule-based screening layer. It should flag cases for
further review rather than independently determine fraud.
"""

from typing import Any, Dict, List

from .fraud_rules import make_finding


# Basic procedure-to-clinical keyword mappings.
# Extend this using your ICD-10 and hospital procedure mappings.
PROCEDURE_CLINICAL_MAP = {

    "appendectomy": {
        "appendicitis",
        "appendix",
        "acute appendicitis",
    },

    "cholecystectomy": {
        "cholecystitis",
        "gallbladder",
        "gallstone",
        "cholelithiasis",
    },

    "ultrasound": {
        "abdomen",
        "abdominal",
        "pregnancy",
        "pelvis",
        "kidney",
        "liver",
    },

    "ct scan": {
        "trauma",
        "abdomen",
        "head",
        "brain",
        "chest",
        "tumor",
        "mass",
    },

    "mri": {
        "brain",
        "spine",
        "knee",
        "shoulder",
        "tumor",
        "lesion",
    },
}


class ClinicalBillingMismatchDetector:

    def detect(
        self,
        diagnosis_data: Any,
        clinical_data: Any,
        billing_items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        findings = []

        clinical_text = self._build_text(
            diagnosis_data,
            clinical_data,
        )

        if not clinical_text:

            return make_finding(
                detector="clinical_billing_mismatch",
                detected=False,
                confidence=0.0,
                severity="UNKNOWN",
                reason="Insufficient clinical information for comparison.",
            )

        for item in billing_items:

            procedure_name = (
                item.get("procedure_name")
                or item.get("description")
                or item.get("procedure_code")
                or ""
            )

            procedure = str(procedure_name).lower().strip()

            if not procedure:
                continue

            matched_rule = None

            for known_procedure, keywords in PROCEDURE_CLINICAL_MAP.items():

                if known_procedure in procedure:
                    matched_rule = (
                        known_procedure,
                        keywords,
                    )
                    break

            if not matched_rule:
                continue

            known_procedure, keywords = matched_rule

            matched_keywords = [
                keyword
                for keyword in keywords
                if keyword.lower() in clinical_text
            ]

            if not matched_keywords:

                findings.append(
                    {
                        "procedure": procedure_name,
                        "expected_clinical_keywords": list(keywords),
                        "matched_keywords": [],
                        "reason": (
                            f"Procedure '{procedure_name}' does not have "
                            "supporting clinical terminology in the "
                            "available diagnosis/clinical information."
                        ),
                    }
                )

        if not findings:

            return make_finding(
                detector="clinical_billing_mismatch",
                detected=False,
                confidence=0.10,
                severity="NONE",
                reason="No clinical/billing mismatches detected.",
            )

        confidence = min(
            0.90,
            0.55 + 0.07 * len(findings),
        )

        return make_finding(
            detector="clinical_billing_mismatch",
            detected=True,
            confidence=confidence,
            severity="MEDIUM",
            reason=(
                f"Detected {len(findings)} possible clinical/billing mismatch(es)."
            ),
            evidence=findings,
        )

    @staticmethod
    def _build_text(
        diagnosis_data: Any,
        clinical_data: Any,
    ) -> str:

        values = []

        def collect(value: Any):

            if value is None:
                return

            if isinstance(value, str):
                values.append(value)

            elif isinstance(value, dict):

                for v in value.values():
                    collect(v)

            elif isinstance(value, list):

                for v in value:
                    collect(v)

            else:
                values.append(str(value))

        collect(diagnosis_data)
        collect(clinical_data)

        return " ".join(values).lower()


def detect_clinical_billing_mismatch(
    diagnosis_data: Any,
    clinical_data: Any,
    billing_items: List[Dict[str, Any]],
) -> Dict[str, Any]:

    return ClinicalBillingMismatchDetector().detect(
        diagnosis_data,
        clinical_data,
        billing_items,
    )