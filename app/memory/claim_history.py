from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ClaimHistory:
    """
    Stores and retrieves historical claim information.

    Current implementation:
        JSON-backed local persistence.

    This class is intentionally kept as an application-level
    abstraction so it can later be backed by Mem0 or a database.
    """

    def __init__(
        self,
        history_file: str = "data/claim_history.json",
    ):
        self.history_file = Path(history_file)

    # ========================================================
    # Internal helpers
    # ========================================================

    def _load(self) -> list[dict[str, Any]]:
        """
        Load claim history from JSON.
        """

        if not self.history_file.exists():
            return []

        try:
            with self.history_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if isinstance(data, list):
                return data

            return []

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return []

    def _save(
        self,
        claims: list[dict[str, Any]],
    ) -> None:
        """
        Save claim history to JSON.
        """

        self.history_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.history_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                claims,
                file,
                indent=2,
                default=str,
            )

    # ========================================================
    # Add claim
    # ========================================================

    def add_claim(
        self,
        claim: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Add a claim to history.

        Existing records with the same claim_id are replaced.
        """

        if not isinstance(claim, dict):
            raise TypeError(
                "claim must be a dictionary"
            )

        claim_id = claim.get(
            "claim_id"
        )

        if not claim_id:
            raise ValueError(
                "claim_id is required"
            )

        claims = self._load()

        # Prevent duplicate claim records.
        claims = [
            existing
            for existing in claims
            if existing.get("claim_id")
            != claim_id
        ]

        claims.append(claim)

        self._save(claims)

        return {
            "success": True,
            "claim_id": claim_id,
        }

    # ========================================================
    # Get single claim
    # ========================================================

    def get_claim(
        self,
        claim_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve one claim by claim ID.
        """

        if not claim_id:
            return None

        claims = self._load()

        for claim in claims:

            if claim.get(
                "claim_id"
            ) == claim_id:

                return claim

        return None

    # ========================================================
    # Get patient claims
    # ========================================================

    def get_patient_claims(
        self,
        patient_id: str,
    ) -> list[dict[str, Any]]:
        """
        Retrieve all historical claims belonging
        to a patient.
        """

        if not patient_id:
            return []

        claims = self._load()

        return [
            claim
            for claim in claims
            if claim.get(
                "patient_id"
            ) == patient_id
        ]

    # ========================================================
    # Get history summary
    # ========================================================

    def get_summary(
        self,
        patient_id: str,
    ) -> dict[str, Any]:
        """
        Generate a summary of a patient's claim history.
        """

        claims = self.get_patient_claims(
            patient_id=patient_id
        )

        total_claims = len(
            claims
        )

        approved = sum(
            1
            for claim in claims
            if str(
                claim.get(
                    "decision",
                    "",
                )
            ).upper()
            == "APPROVED"
        )

        rejected = sum(
            1
            for claim in claims
            if str(
                claim.get(
                    "decision",
                    "",
                )
            ).upper()
            == "REJECTED"
        )

        partial = sum(
            1
            for claim in claims
            if str(
                claim.get(
                    "decision",
                    "",
                )
            ).upper()
            in {
                "PARTIAL",
                "PARTIAL_APPROVAL",
            }
        )

        return {
            "patient_id": patient_id,
            "total_claims": total_claims,
            "approved": approved,
            "rejected": rejected,
            "partial_approval": partial,
        }