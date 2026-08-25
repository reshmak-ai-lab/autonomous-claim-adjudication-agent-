"""
Policy validation guardrails.

Validates that a claim contains the minimum policy and claim
identifiers required for adjudication.
"""

from typing import Any, List


class PolicyValidator:

    def validate(
        self,
        claim: dict[str, Any],
    ) -> List[str]:
        """
        Validate required policy and claim information.

        Expected claim structure:

        {
            "policy_id": "...",
            "claim_id": "...",
            ...
        }

        Returns:
            List of validation errors.
            Empty list means the claim is valid.
        """

        errors: List[str] = []

        # ---------------------------------------------------------
        # Validate input
        # ---------------------------------------------------------

        if not isinstance(claim, dict):
            return [
                "Claim must be a dictionary."
            ]

        # ---------------------------------------------------------
        # Policy ID
        # ---------------------------------------------------------

        policy_id = claim.get("policy_id")

        if policy_id is None or (
            isinstance(policy_id, str)
            and not policy_id.strip()
        ):
            errors.append(
                "Missing policy_id."
            )

        # ---------------------------------------------------------
        # Claim ID
        # ---------------------------------------------------------

        claim_id = claim.get("claim_id")

        if claim_id is None or (
            isinstance(claim_id, str)
            and not claim_id.strip()
        ):
            errors.append(
                "Missing claim_id."
            )

        return errors