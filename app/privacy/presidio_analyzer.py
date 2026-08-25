from typing import Any

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer import RecognizerRegistry

from .custom_recognizers.aadhaar_recognizer import AadhaarRecognizer
from .custom_recognizers.pan_recognizer import PANRecognizer
from .custom_recognizers.abha_recognizer import ABHARecognizer
from .custom_recognizers.indian_phone_recognizer import IndianPhoneRecognizer
from .custom_recognizers.hospital_id_recognizer import HospitalIDRecognizer
from .custom_recognizers.address_recognizer import AddressRecognizer


class PrivacyAnalyzer:
    """
    Central PII detection service.
    """

    def __init__(self):
        registry = RecognizerRegistry()

        registry.load_predefined_recognizers()

        registry.add_recognizer(AadhaarRecognizer())
        registry.add_recognizer(PANRecognizer())
        registry.add_recognizer(ABHARecognizer())
        registry.add_recognizer(IndianPhoneRecognizer())
        registry.add_recognizer(HospitalIDRecognizer())
        registry.add_recognizer(AddressRecognizer())

        self.analyzer = AnalyzerEngine(
            registry=registry
        )

    def analyze(self, text: str) -> list[Any]:
        """
        Detect PII entities.

        Indian-specific recognizers take precedence over generic
        Presidio recognizers when their spans overlap.
        """

        if not text:
            return []

        results = self.analyzer.analyze(
            text=text,
            language="en",
        )

        if not results:
            return []

        # --------------------------------------------------------------
        # Indian-specific entities have priority.
        # --------------------------------------------------------------

        priority_entities = {
            "IN_AADHAAR",
            "IN_PAN",
            "IN_ABHA",
            "IN_PHONE",
            "HOSPITAL_ID",
            "IN_ADDRESS",
        }

        prioritized = [
            result
            for result in results
            if result.entity_type in priority_entities
        ]

        # --------------------------------------------------------------
        # Remove generic overlapping entities when a specific
        # Indian recognizer already identified the same PII.
        # --------------------------------------------------------------

        filtered = []

        for result in results:

            is_generic = result.entity_type not in priority_entities

            overlaps_specific = any(
                specific.start <= result.start
                and specific.end >= result.end
                for specific in prioritized
            )

            if is_generic and overlaps_specific:
                continue

            filtered.append(result)

        return filtered

    def analyze_with_details(
        self,
        text: str,
    ) -> list[dict[str, Any]]:
        """
        Return JSON-friendly PII results.
        """

        results = self.analyze(text)

        return [
            {
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": round(result.score, 4),
                "text": text[result.start:result.end],
            }
            for result in results
        ]
