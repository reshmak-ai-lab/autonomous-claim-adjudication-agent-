from typing import Any


class ICD10Tools:
    """Tools for ICD-10 diagnosis lookup and validation."""

    ICD10_CODES = {
        "K35.80": {
            "description": "Acute appendicitis, unspecified",
            "category": "Digestive system",
        },
        "K80.00": {
            "description": "Calculus of gallbladder with acute cholecystitis",
            "category": "Digestive system",
        },
        "K81.0": {
            "description": "Acute cholecystitis",
            "category": "Digestive system",
        },
        "E11.9": {
            "description": "Type 2 diabetes mellitus without complications",
            "category": "Endocrine system",
        },
        "I10": {
            "description": "Essential hypertension",
            "category": "Circulatory system",
        },
    }

    def lookup_code(self, code: str) -> dict[str, Any]:
        """Look up an ICD-10 code."""

        if not code:
            return {
                "valid": False,
                "error": "ICD-10 code is required",
            }

        normalized_code = code.strip().upper()

        result = self.ICD10_CODES.get(normalized_code)

        if result is None:
            return {
                "valid": False,
                "code": normalized_code,
                "message": "ICD-10 code not found in local reference data",
            }

        return {
            "valid": True,
            "code": normalized_code,
            **result,
        }

    def search_diagnosis(
        self,
        diagnosis: str,
    ) -> list[dict[str, Any]]:
        """Search ICD-10 codes by diagnosis description."""

        if not diagnosis:
            return []

        query = diagnosis.lower().strip()
        results = []

        for code, details in self.ICD10_CODES.items():
            if query in details["description"].lower():
                results.append(
                    {
                        "code": code,
                        **details,
                    }
                )

        return results