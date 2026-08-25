from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer


class AddressRecognizer(PatternRecognizer):
    """
    Basic address pattern recognizer.

    This is intentionally conservative because address detection
    using regex alone can produce many false positives.
    """

    def __init__(self):
        patterns = [
            Pattern(
                name="indian_address",
                regex=(
                    r"\b\d{1,5}\s+"
                    r"[A-Za-z0-9\s,.-]{5,80}"
                    r"\b(?:Road|Rd|Street|St|"
                    r"Avenue|Ave|Nagar|Layout|"
                    r"Colony|Main Road)\b"
                ),
                score=0.55,
            )
        ]

        super().__init__(
            supported_entity="IN_ADDRESS",
            patterns=patterns,
        )