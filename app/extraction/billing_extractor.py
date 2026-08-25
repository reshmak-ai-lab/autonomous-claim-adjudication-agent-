from __future__ import annotations

import re
from typing import Any


class BillingExtractor:

    FIELD_PATTERNS = {
        "room_rent_per_day": [
            r"room\s+rent(?:\s+per\s+day)?\s*[:\-]?\s*(?:rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)"
        ],
        "doctor_charges": [
            r"(?:doctor|physician|consultation)\s+(?:charges?|fee)\s*[:\-]?\s*(?:rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)"
        ],
        "surgery_charges": [
            r"surgery\s+charges?\s*[:\-]?\s*(?:rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)"
        ],
        "medicine_amount": [
            r"(?:medicine|medicines|pharmacy)\s*(?:charges?|amount)?\s*[:\-]?\s*(?:rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)"
        ],
        "total_bill": [
            r"(?:total\s+bill|total\s+amount|grand\s+total)\s*[:\-]?\s*(?:rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)"
        ],
    }

    def extract(self, text: str) -> dict[str, Any]:
        if not text or not text.strip():
            return {}

        result: dict[str, Any] = {
            "total_bill": None,
            "room_rent_per_day": None,
            "doctor_charges": None,
            "surgery_charges": None,
            "medicine_amount": None,
            "hospitalization_days": None,
            "non_medical_amount": None,
        }

        for field, patterns in self.FIELD_PATTERNS.items():
            for pattern in patterns:
                match = re.search(
                    pattern,
                    text,
                    flags=re.IGNORECASE,
                )

                if match:
                    result[field] = self._to_amount(match.group(1))
                    break

        return result

    @staticmethod
    def _to_amount(value: str) -> float:
        return float(value.replace(",", ""))