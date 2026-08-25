from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from .presidio_analyzer import PrivacyAnalyzer


class PrivacyAnonymizer:
    """
    Detect and anonymize sensitive information.
    """

    def __init__(self):
        self.analyzer = PrivacyAnalyzer()
        self.anonymizer = AnonymizerEngine()

    def anonymize(
        self,
        text: str,
    ) -> dict:

        if not text:
            return {
                "original_text": text,
                "anonymized_text": text,
                "entities_detected": [],
                "entity_count": 0,
            }

        analyzer_results = self.analyzer.analyze(text)

        operators = {
            "IN_AADHAAR": OperatorConfig(
                "replace",
                {
                    "new_value": "[AADHAAR_REDACTED]"
                },
            ),
            "IN_PAN": OperatorConfig(
                "replace",
                {
                    "new_value": "[PAN_REDACTED]"
                },
            ),
            "IN_ABHA": OperatorConfig(
                "replace",
                {
                    "new_value": "[ABHA_REDACTED]"
                },
            ),
            "IN_PHONE": OperatorConfig(
                "replace",
                {
                    "new_value": "[PHONE_REDACTED]"
                },
            ),
            "PHONE_NUMBER": OperatorConfig(
                "replace",
                {
                    "new_value": "[PHONE_REDACTED]"
                },
            ),
            "HOSPITAL_ID": OperatorConfig(
                "replace",
                {
                    "new_value": "[HOSPITAL_ID_REDACTED]"
                },
            ),
            "IN_ADDRESS": OperatorConfig(
                "replace",
                {
                    "new_value": "[ADDRESS_REDACTED]"
                },
            ),
            "EMAIL_ADDRESS": OperatorConfig(
                "replace",
                {
                    "new_value": "[EMAIL_REDACTED]"
                },
            ),
            "CREDIT_CARD": OperatorConfig(
                "replace",
                {
                    "new_value": "[CARD_REDACTED]"
                },
            ),
            "PERSON": OperatorConfig(
                "replace",
                {
                    "new_value": "[PERSON_REDACTED]"
                },
            ),
        }

        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators=operators,
        )

        return {
            "original_text": text,
            "anonymized_text": anonymized.text,
            "entities_detected": [
                result.entity_type
                for result in analyzer_results
            ],
            "entity_count": len(analyzer_results),
        }


def anonymize_text(text: str) -> str:
    """
    Backward-compatible convenience function.

    Returns only the anonymized text.
    """

    result = PrivacyAnonymizer().anonymize(text)

    return result["anonymized_text"]


# Backward compatibility for the evaluation test.
PresidioAnonymizer = PrivacyAnonymizer