from typing import Any

from .embeddings import EmbeddingService
from .vector_store import VectorStore


class PolicyRetriever:
    """Retrieves relevant policy chunks."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ):
        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        self.vector_store = (
            vector_store
            or VectorStore()
        )

        # Load the persisted FAISS index
        if self.vector_store.index is None:
            self.vector_store.load()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:

        query_embedding = (
            self.embedding_service.embed_one(
                query
            )
        )

        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )