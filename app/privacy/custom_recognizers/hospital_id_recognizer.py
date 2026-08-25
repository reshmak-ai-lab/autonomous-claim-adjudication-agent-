from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer


class HospitalIDRecognizer(PatternRecognizer):
    """
    Detects internal hospital identifiers.
    """

    def __init__(self):
        patterns = [
            Pattern(
                name="hospital_id",
                regex=r"\bHOSP-\d{3,10}\b",
                score=0.85,
            )
        ]

        super().__init__(
            supported_entity="HOSPITAL_ID",
            patterns=patterns,
        )