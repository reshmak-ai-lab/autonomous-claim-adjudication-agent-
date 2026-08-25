import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np


class VectorStore:
    """
    FAISS-based local vector store.
    """

    def __init__(
        self,
        index_path: str = "vectorstore/policies.index",
        metadata_path: str = "vectorstore/policies.json",
    ):
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        self.index = None
        self.metadata: list[dict[str, Any]] = []

    def build(
        self,
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> None:

        if not embeddings:
            raise ValueError(
                "No embeddings supplied"
            )

        vectors = np.asarray(
            embeddings,
            dtype="float32",
        )

        dimension = vectors.shape[1]

        index = faiss.IndexFlatIP(
            dimension
        )

        index.add(vectors)

        self.index = index
        self.metadata = metadata

    def save(self) -> None:

        if self.index is None:
            raise ValueError(
                "Vector index has not been built"
            )

        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            self.index,
            str(self.index_path),
        )

        self.metadata_path.write_text(
            json.dumps(
                self.metadata,
                indent=2,
            ),
            encoding="utf-8",
        )

    def load(self) -> None:

        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Index not found: {self.index_path}"
            )

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata not found: {self.metadata_path}"
            )

        self.index = faiss.read_index(
            str(self.index_path)
        )

        self.metadata = json.loads(
            self.metadata_path.read_text(
                encoding="utf-8"
            )
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:

        if self.index is None:
            raise RuntimeError(
                "Vector store is not loaded"
            )

        query = np.asarray(
            [query_embedding],
            dtype="float32",
        )

        scores, indices = self.index.search(
            query,
            top_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index < 0:
                continue

            item = self.metadata[index].copy()

            item["score"] = float(score)

            results.append(item)

        return results