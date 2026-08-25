from __future__ import annotations

import re
from datetime import datetime
from typing import Any


class TimelineExtractor:
    """
    Extract clinically relevant timeline events from medical documents.
    """

    EVENT_PATTERNS = {
        "admission": r"(?:date\s+of\s+)?admission",
        "discharge": r"(?:date\s+of\s+)?discharge",
        "surgery": r"(?:date\s+of\s+)?surgery|operation",
        "procedure": r"(?:date\s+of\s+)?procedure",
        "consultation": r"(?:date\s+of\s+)?consultation",
        "diagnosis": r"(?:date\s+of\s+)?diagnosis",
    }

    DATE_PATTERN = (
        r"(?:"
        r"\d{1,2}\s+(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{4}"
        r"|"
        r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\.?\s+\d{4}"
        r"|"
        r"\d{1,2}[/-]\d{1,2}[/-]\d{4}"
        r"|"
        r"\d{4}[/-]\d{1,2}[/-]\d{1,2}"
        r")"
    )

    def extract(self, text: str | None) -> list[dict[str, Any]]:
        """
        Extract timeline events from text.

        Returns:
            List of dictionaries containing:
            - event
            - date
            - raw_date
        """

        if not text or not text.strip():
            return []

        events: list[dict[str, Any]] = []

        for event_type, event_pattern in self.EVENT_PATTERNS.items():

            pattern = (
                rf"{event_pattern}"
                rf"\s*[:\-]?\s*"
                rf"(?P<date>{self.DATE_PATTERN})"
            )

            matches = re.finditer(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            for match in matches:
                raw_date = match.group("date")

                normalized_date = self._normalize_date(raw_date)

                if normalized_date:
                    events.append(
                        {
                            "event": event_type,
                            "date": normalized_date,
                            "raw_date": raw_date,
                        }
                    )

        events.sort(key=lambda item: item["date"])

        return events

    @staticmethod
    def _normalize_date(value: str | None) -> str | None:
        """
        Convert supported date formats into YYYY-MM-DD.
        """

        if not value:
            return None

        value = value.strip()

        formats = [
            "%d %B %Y",
            "%d %b %Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date().isoformat()
            except ValueError:
                continue

        return None