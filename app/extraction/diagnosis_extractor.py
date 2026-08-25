from __future__ import annotations

import re


class DiagnosisExtractor:
    """
    Extract diagnoses from medical text.

    This is a deterministic baseline implementation.
    It can later be enhanced with an ICD-10 MCP/API tool.
    """

    DIAGNOSES = {
        "cholecystitis": "K81.9",
        "acute cholecystitis": "K81.0",
        "cholelithiasis": "K80.20",
        "appendicitis": "K35.80",
        "hypertension": "I10",
        "diabetes mellitus": "E11.9",
        "type 2 diabetes": "E11.9",
        "anemia": "D64.9",
        "gastritis": "K29.70",
        "urinary tract infection": "N39.0",
        "uti": "N39.0",
    }

    def extract(self, text: str) -> list[dict[str, str]]:
        normalized = text.lower()

        results: list[dict[str, str]] = []

        for diagnosis, icd10_code in self.DIAGNOSES.items():
            pattern = rf"\b{re.escape(diagnosis)}\b"

            if re.search(pattern, normalized):
                results.append(
                    {
                        "diagnosis": diagnosis,
                        "icd10_code": icd10_code,
                    }
                )

        return results