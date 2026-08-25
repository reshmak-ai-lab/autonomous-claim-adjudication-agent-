from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer


class AadhaarRecognizer(PatternRecognizer):
    """
    Detects Indian Aadhaar numbers.
    """

    def __init__(self):
        patterns = [
            Pattern(
                name="aadhaar",
                regex=r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
                score=0.85,
            )
        ]

        super().__init__(
            supported_entity="IN_AADHAAR",
            patterns=patterns,
        )