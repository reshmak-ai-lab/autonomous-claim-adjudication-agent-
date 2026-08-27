"""
General claim validation.
"""

from typing import Any, Dict, list


class ClaimValidator:

    REQUIRED_CLAIM_FIELDS = [
        "claim_id",
    ]

    def validate_claim(
        self,
        claim: Dict[str, Any],
    ) -> list[str]:

        errors = []

        if not isinstance(claim, dict):

            return [
                "Claim must be a dictionary."
            ]

        for field in self.REQUIRED_CLAIM_FIELDS:

            if not claim.get(field):

                errors.append(
                    f"Missing required claim field: {field}"
                )

        if "claimed_amount" in claim:

            try:

                amount = float(
                    claim["claimed_amount"]
                )

                if amount < 0:

                    errors.append(
                        "Claimed amount cannot be negative."
                    )

            except (
                TypeError,
                ValueError,
            ):

                errors.append(
                    "Claimed amount must be numeric."
                )

        return errors

    def validate_dates(
        self,
        claim: Dict[str, Any],
    ) -> list[str]:

        errors = []

        admission = claim.get(
            "admission_date"
        )

        discharge = claim.get(
            "discharge_date"
        )

        if admission and discharge:

            if str(discharge) < str(admission):

                errors.append(
                    "Discharge date cannot be before admission date."
                )

        return errors

    def validate(
        self,
        claim: Dict[str, Any],
    ) -> list[str]:

        return (
            self.validate_claim(claim)
            + self.validate_dates(claim)
        )