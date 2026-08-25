from typing import Any

from .claim_history import ClaimHistory
from .patient_memory import PatientMemory


class MemoryRetriever:
    """
    Unified memory retrieval layer.

    Combines:
    - Patient long-term memory
    - Historical claims
    """

    def __init__(
        self,
        patient_memory: PatientMemory | None = None,
        claim_history: ClaimHistory | None = None,
    ):
        self.patient_memory = (
            patient_memory or PatientMemory()
        )

        self.claim_history = (
            claim_history or ClaimHistory()
        )

    def retrieve(
        self,
        patient_id: str,
        query: str,
    ) -> dict[str, Any]:
        """
        Retrieve all relevant memory for a claim.
        """

        patient_memory = (
            self.patient_memory.search_patient_memory(
                patient_id=patient_id,
                query=query,
                limit=5,
            )
        )

        claims = (
            self.claim_history.get_patient_claims(
                patient_id
            )
        )

        summary = (
            self.claim_history.get_summary(
                patient_id
            )
        )

        return {
            "patient_id": patient_id,
            "query": query,
            "patient_memory": patient_memory,
            "claim_history": claims,
            "claim_summary": summary,
        }