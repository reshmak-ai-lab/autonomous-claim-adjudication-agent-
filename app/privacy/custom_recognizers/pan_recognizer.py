from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer


class PANRecognizer(PatternRecognizer):
    """
    Detects Indian PAN numbers.
    """

    def __init__(self):
        patterns = [
            Pattern(
                name="pan",
                regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
                score=0.90,
            )
        ]

        super().__init__(
            supported_entity="IN_PAN",
            patterns=patterns,
        )