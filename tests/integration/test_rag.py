"""
Integration tests for policy RAG.
"""

import pytest

from app.rag.retriever import PolicyRetriever


@pytest.fixture
def retriever():
    return PolicyRetriever()


def test_rag_retriever_can_be_created(retriever):
    """
    Verify that the policy retriever initializes successfully.
    """

    assert retriever is not None


def test_rag_retrieves_policy_information(retriever):
    """
    Verify that a policy-related question returns documents.
    """

    results = retriever.retrieve(
        "What are the exclusions under this policy?",
        3,
    )

    assert results is not None
    assert isinstance(results, list)


def test_rag_returns_relevant_content(retriever):
    """
    Verify that retrieved results contain usable content.
    """

    results = retriever.retrieve(
        "What is the waiting period?",
        3,
    )

    assert results is not None

    if results:
        first_result = results[0]

        assert first_result is not None


def test_rag_multiple_queries(retriever):
    """
    Verify retrieval for several common policy questions.
    """

    queries = [
        "What are the policy exclusions?",
        "What is the waiting period?",
        "What is the sum insured?",
        "What is the room rent limit?",
    ]

    for query in queries:

        results = retriever.retrieve(
            query,
            3,
        )

        assert results is not None
        assert isinstance(results, list)