from typing import Any


class PolicyReranker:
    """
    Basic policy result reranker.

    Prioritizes semantic similarity while giving a small
    boost to exact keyword matches.
    """

    def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:

        query_words = {
            word.lower()
            for word in query.split()
            if len(word) > 2
        }

        scored = []

        for document in documents:

            text = document.get(
                "text",
                "",
            ).lower()

            keyword_matches = sum(
                1
                for word in query_words
                if word in text
            )

            original_score = float(
                document.get("score", 0)
            )

            final_score = (
                original_score
                + 0.01 * keyword_matches
            )

            item = document.copy()

            item["rerank_score"] = (
                final_score
            )

            scored.append(item)

        scored.sort(
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        return scored[:top_k]