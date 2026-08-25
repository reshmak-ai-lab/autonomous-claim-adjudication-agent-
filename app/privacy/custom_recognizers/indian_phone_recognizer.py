from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer


class IndianPhoneRecognizer(PatternRecognizer):
    """
    Detects Indian mobile phone numbers.
    """

    def __init__(self):
        patterns = [
            Pattern(
                name="indian_mobile",
                regex=r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
                score=0.85,
            )
        ]

        super().__init__(
            supported_entity="IN_PHONE",
            patterns=patterns,
        )