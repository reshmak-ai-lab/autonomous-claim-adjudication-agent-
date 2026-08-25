from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer


class ABHARecognizer(PatternRecognizer):
    """
    Detects ABHA identifiers.
    """

    def __init__(self):
        patterns = [
            Pattern(
                name="abha",
                regex=r"\b\d{2}-\d{4}-\d{4}-\d{4}\b",
                score=0.90,
            )
        ]

        super().__init__(
            supported_entity="IN_ABHA",
            patterns=patterns,
        )