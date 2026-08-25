"""
Discharge claim workflow.

Handles final information available at discharge.
"""

from __future__ import annotations

from typing import Any, Dict

from ..state import AgentState


class DischargeWorkflow:

    def run(
        self,
        claim: Dict[str, Any],
    ) -> AgentState:

        claim_id = claim.get(
            "claim_id",
            "DISCHARGE-UNKNOWN",
        )

        state: AgentState = {
            "claim_id": claim_id,
            "claim": claim,
            "execution_trace": [
                {
                    "event": "discharge_processing_started"
                }
            ],
            "errors": [],
            "warnings": [],
        }

        required_fields = [
            "admission_date",
            "discharge_date",
        ]

        missing = [
            field
            for field in required_fields
            if not claim.get(field)
        ]

        if missing:

            state["final_decision"] = (
                "QUERY_RAISED"
            )

            state["final_response"] = {
                "claim_id": claim_id,
                "decision": "QUERY_RAISED",
                "reason": (
                    "Required discharge information "
                    "is missing."
                ),
                "missing_fields": missing,
                "human_review_required": True,
            }

            return state

        state["final_decision"] = (
            "QUERY_RAISED"
        )

        state["final_response"] = {
            "claim_id": claim_id,
            "decision": "QUERY_RAISED",
            "reason": (
                "Discharge claim requires full "
                "clinical, billing and policy evaluation."
            ),
            "human_review_required": True,
        }

        state["execution_trace"].append(
            {
                "event": "discharge_processing_completed"
            }
        )

        return state