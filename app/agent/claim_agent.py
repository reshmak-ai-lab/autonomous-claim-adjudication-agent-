"""
Main claim adjudication agent.

The agent orchestrates the claim workflow. Domain-specific
logic remains in the appropriate modules.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .state import AgentState
from .workflows.claim_workflow import ClaimWorkflow


class ClaimAgent:

    def __init__(
        self,
        workflow: Optional[ClaimWorkflow] = None,
    ):

        self.workflow = (
            workflow
            or ClaimWorkflow()
        )

    def process(
        self,
        claim: Dict[str, Any],
    ) -> AgentState:

        state: AgentState = {
            "claim_id": claim.get(
                "claim_id",
                "UNKNOWN",
            ),
            "claim": claim,
            "errors": [],
            "warnings": [],
            "execution_trace": [],
        }

        return self.workflow.run(state)

    def adjudicate(
        self,
        claim: Dict[str, Any],
    ) -> Dict[str, Any]:

        state = self.process(claim)

        return state.get(
            "final_response",
            {},
        )