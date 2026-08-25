from typing import Any

from .mem0_client import Mem0Client


class PatientMemory:
    """
    Stores and retrieves relevant long-term patient information.

    Only information necessary for claim adjudication should be
    persisted.
    """

    def __init__(self, memory_client: Mem0Client | None = None):
        self.memory = memory_client or Mem0Client()

    def store_patient_context(
        self,
        patient_id: str,
        context: str,
    ) -> dict[str, Any]:
        """
        Store patient context in long-term memory.
        """

        if not patient_id:
            raise ValueError(
                "patient_id is required"
            )

        if not context:
            return {
                "success": False,
                "message": "No context provided",
            }

        messages = [
            {
                "role": "user",
                "content": context,
            }
        ]

        return self.memory.add_memory(
            messages=messages,
            user_id=patient_id,
        )

    def search_patient_memory(
        self,
        patient_id: str,
        query: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        """
        Retrieve relevant patient memory.
        """

        return self.memory.search_memory(
            query=query,
            user_id=patient_id,
            limit=limit,
        )