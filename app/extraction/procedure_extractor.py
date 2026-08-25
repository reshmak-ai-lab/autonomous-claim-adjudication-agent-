from __future__ import annotations

import re


class ProcedureExtractor:
    """
    Extract medical procedures from clinical documents.
    """

    PROCEDURES = {
        "laparoscopic cholecystectomy": "LAP_CHOLE",
        "cholecystectomy": "CHOLECYSTECTOMY",
        "appendectomy": "APPENDECTOMY",
        "laparoscopic appendectomy": "LAP_APPENDectomy",
        "ultrasound": "ULTRASOUND",
        "ct scan": "CT_SCAN",
        "mri": "MRI",
        "blood transfusion": "BLOOD_TRANSFUSION",
        "endoscopy": "ENDOSCOPY",
        "colonoscopy": "COLONOSCOPY",
    }

    def extract(self, text: str) -> list[dict[str, str]]:
        normalized = text.lower()

        results: list[dict[str, str]] = []

        for procedure, procedure_code in self.PROCEDURES.items():
            pattern = rf"\b{re.escape(procedure)}\b"

            if re.search(pattern, normalized):
                results.append(
                    {
                        "procedure": procedure,
                        "procedure_code": procedure_code,
                    }
                )

        return results