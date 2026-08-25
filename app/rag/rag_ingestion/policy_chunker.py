from typing import Any


class PolicyChunker:
    """Splits policy documents into overlapping chunks."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        document: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Create chunks for one document."""

        text = document["text"]

        chunks = []

        start = 0
        chunk_number = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk_text = text[
                start:end
            ].strip()

            if chunk_text:
                chunks.append(
                    {
                        "text": chunk_text,
                        "source": document["source"],
                        "chunk_id": (
                            f"{document['source']}"
                            f"::chunk_{chunk_number}"
                        ),
                        "chunk_number": chunk_number,
                    }
                )

                chunk_number += 1

            if end >= len(text):
                break

            start = (
                end - self.chunk_overlap
            )

        return chunks

    def chunk_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Chunk multiple documents."""

        all_chunks = []

        for document in documents:
            all_chunks.extend(
                self.chunk_document(document)
            )

        return all_chunks