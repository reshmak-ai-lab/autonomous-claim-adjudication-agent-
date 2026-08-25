from typing import Any


class MetadataBuilder:
    """Builds metadata for policy chunks."""

    def build(
        self,
        chunk: dict[str, Any],
    ) -> dict[str, Any]:

        source = chunk["source"]

        return {
            "source": source,
            "chunk_id": chunk["chunk_id"],
            "chunk_number": chunk["chunk_number"],
            "document_type": "health_insurance_policy",
            "domain": self._detect_domain(source),
        }

    def _detect_domain(
        self,
        source: str,
    ) -> str:

        source_lower = source.lower()

        if "room" in source_lower:
            return "room_rent"

        if "exclusion" in source_lower:
            return "exclusions"

        if "ped" in source_lower:
            return "pre_existing_disease"

        if "adjudication" in source_lower:
            return "claim_adjudication"

        if "policy" in source_lower:
            return "policy_terms"

        return "general"