from __future__ import annotations

from pathlib import Path


class DocumentClassifier:
    """
    Classifies medical/claim documents using
    filename and basic content keywords.
    """

    KEYWORDS = {
        "ultrasound": [
            "ultrasound",
            "sonography",
            "usg",
        ],
        "blood_report": [
            "blood report",
            "cbc",
            "hemoglobin",
            "platelet",
            "blood test",
        ],
        "doctor_note": [
            "doctor note",
            "clinical note",
            "physician",
            "consultation",
        ],
        "discharge_summary": [
            "discharge summary",
            "discharge",
            "hospital course",
        ],
        "bill": [
            "hospital bill",
            "invoice",
            "billing",
            "total bill",
            "amount payable",
        ],
        "prescription": [
            "prescription",
            "medicine",
            "dosage",
            "tablet",
        ],
        "claim_form": [
            "claim form",
            "claim number",
            "insurance claim",
        ],
    }

    def classify(
        self,
        file_path: str | Path,
    ) -> str:
        """
        Classify based on filename.
        """

        path = Path(file_path)

        filename = path.name.lower()

        for document_type, keywords in self.KEYWORDS.items():

            for keyword in keywords:

                if keyword in filename:
                    return document_type

        return "unknown"

    def classify_text(
        self,
        text: str,
    ) -> str:
        """
        Classify based on extracted text.
        """

        normalized = text.lower()

        scores: dict[str, int] = {}

        for document_type, keywords in self.KEYWORDS.items():

            score = sum(
                1
                for keyword in keywords
                if keyword in normalized
            )

            scores[document_type] = score

        best_type = max(
            scores,
            key=scores.get,
        )

        if scores[best_type] == 0:
            return "unknown"

        return best_type