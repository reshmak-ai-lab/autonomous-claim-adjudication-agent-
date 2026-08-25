import json
from pathlib import Path
from typing import Any


class TariffTools:
    """Tools for hospital and procedure tariff lookup."""

    def __init__(
        self,
        tariff_file: str = "data/hospital/hospital_tariff_master.json",
    ):
        self.tariff_file = Path(tariff_file)

    def _load_tariffs(self) -> list[dict[str, Any]]:
        """Load tariff records from JSON."""

        if not self.tariff_file.exists():
            return []

        try:
            with self.tariff_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except (OSError, json.JSONDecodeError):
            return []

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            if "tariffs" in data:
                return data["tariffs"]

            return [data]

        return []

    def get_tariff(
        self,
        hospital_id: str,
        procedure_code: str,
    ) -> dict[str, Any]:
        """Get tariff for a specific hospital and procedure."""

        tariffs = self._load_tariffs()

        for tariff in tariffs:
            if (
                str(tariff.get("hospital_id", "")).upper()
                == hospital_id.upper()
                and str(tariff.get("procedure_code", "")).upper()
                == procedure_code.upper()
            ):
                return {
                    "found": True,
                    **tariff,
                }

        return {
            "found": False,
            "hospital_id": hospital_id,
            "procedure_code": procedure_code,
            "message": "Tariff not found",
        }

    def search_procedure(
        self,
        procedure: str,
    ) -> list[dict[str, Any]]:
        """Search tariff records by procedure name."""

        tariffs = self._load_tariffs()

        query = procedure.lower().strip()

        results = []

        for tariff in tariffs:
            procedure_name = str(
                tariff.get("procedure_name", "")
            ).lower()

            if query in procedure_name:
                results.append(tariff)

        return results