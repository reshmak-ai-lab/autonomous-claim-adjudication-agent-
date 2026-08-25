from typing import Any


class EmbeddingService:
    """
    Generates vector embeddings for policy text.
    """

    def __init__(
        self,
        model_name: str = (
            "sentence-transformers/"
            "all-MiniLM-L6-v2"
        ),
    ):
        from sentence_transformers import (
            SentenceTransformer,
        )

        self.model = SentenceTransformer(
            model_name
        )

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def embed_one(
        self,
        text: str,
    ) -> list[float]:

        return self.embed([text])[0]