from __future__ import annotations

from typing import Any

from app.extraction.diagnosis_extractor import DiagnosisExtractor
from app.extraction.procedure_extractor import ProcedureExtractor
from app.extraction.timeline_extractor import TimelineExtractor


class ClinicalExtractor:
    """
    Extract structured clinical information from
    sanitized medical documents.
    """

    def __init__(self) -> None:
        self.diagnosis_extractor = DiagnosisExtractor()
        self.procedure_extractor = ProcedureExtractor()
        self.timeline_extractor = TimelineExtractor()

    def extract(self, text: str) -> dict[str, Any]:
        if not text or not text.strip():
            return {
                "diagnoses": [],
                "procedures": [],
                "timeline": [],
            }

        return {
            "diagnoses": self.diagnosis_extractor.extract(text),
            "procedures": self.procedure_extractor.extract(text),
            "timeline": self.timeline_extractor.extract(text),
        }