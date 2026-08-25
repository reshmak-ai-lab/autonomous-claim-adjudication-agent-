"""
Preauthorization workflow.

Determines whether a proposed treatment is eligible
before the treatment takes place.
"""

from __future__ import annotations

from typing import Any, Dict

from ..state import AgentState


class PreAuthWorkflow:

    def run(
        self,
        request: Dict[str, Any],
    ) -> AgentState:

        claim_id = request.get(
            "claim_id",
            "PREAUTH-UNKNOWN",
        )

        state: AgentState = {
            "claim_id": claim_id,
            "claim": request,
            "execution_trace": [],
            "errors": [],
            "warnings": [],
        }

        state["execution_trace"].append(
            {
                "event": "preauth_started"
            }
        )

        # Basic validation.
        if not request.get(
            "procedure"
        ):

            state["final_decision"] = (
                "QUERY_RAISED"
            )

            state["final_response"] = {
                "claim_id": claim_id,
                "decision": "QUERY_RAISED",
                "reason": (
                    "Procedure information is required "
                    "for preauthorization."
                ),
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
                "Preauthorization requires policy, "
                "clinical necessity and coverage "
                "evaluation."
            ),
            "human_review_required": True,
        }

        state["execution_trace"].append(
            {
                "event": "preauth_completed"
            }
        )

        return state