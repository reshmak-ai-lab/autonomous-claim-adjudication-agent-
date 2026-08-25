from __future__ import annotations

import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAG_CASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "test_cases"
    / "rag_test_cases.json"
)


def load_cases():

    if not RAG_CASE_FILE.exists():
        return []

    with RAG_CASE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in (
            "test_cases",
            "cases",
            "tests",
        ):

            value = data.get(key)

            if isinstance(value, list):
                return value

    return []


def get_query(case):

    if isinstance(case, str):
        return case

    for key in (
        "query",
        "question",
        "input",
    ):

        value = case.get(key)

        if value:
            return value

    return ""


def get_expected_keywords(case):

    if not isinstance(case, dict):
        return []

    for key in (
        "expected_keywords",
        "keywords",
        "expected",
    ):

        value = case.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            return [value]

    return []


def retrieve_policy(query):

    try:
        from app.rag.retriever import PolicyRetriever
    except ImportError as exc:
        pytest.fail(
            f"Could not import PolicyRetriever: {exc}"
        )

    retriever = PolicyRetriever()

    if hasattr(retriever, "retrieve"):
        return retriever.retrieve(
            query,
            5,
        )

    if hasattr(retriever, "search"):
        return retriever.search(
            query,
            5,
        )

    pytest.fail(
        "PolicyRetriever must expose "
        "retrieve() or search()."
    )


def result_to_text(results):

    if results is None:
        return ""

    if isinstance(results, str):
        return results

    if isinstance(results, list):

        parts = []

        for item in results:

            if isinstance(item, str):
                parts.append(item)

            elif isinstance(item, dict):

                for key in (
                    "text",
                    "content",
                    "page_content",
                ):

                    if item.get(key):
                        parts.append(
                            str(item[key])
                        )
                        break

            else:
                parts.append(str(item))

        return " ".join(parts)

    return str(results)


@pytest.mark.evaluation
def test_rag_cases_are_loaded():

    cases = load_cases()

    if not cases:
        pytest.skip(
            f"No RAG evaluation cases found in "
            f"{RAG_CASE_FILE}"
        )

    assert len(cases) > 0


@pytest.mark.evaluation
def test_policy_retrieval_accuracy():

    cases = load_cases()

    if not cases:
        pytest.skip(
            f"No RAG evaluation cases found in "
            f"{RAG_CASE_FILE}"
        )

    failures = []

    for index, case in enumerate(cases):

        query = get_query(case)

        if not query:
            failures.append(
                f"Case {index}: missing query"
            )
            continue

        try:
            results = retrieve_policy(query)

            text = result_to_text(
                results
            ).lower()

        except Exception as exc:
            failures.append(
                f"Case {index}: "
                f"retrieval error: {exc}"
            )
            continue

        if not text:
            failures.append(
                f"Case {index}: "
                f"no results for query: {query}"
            )
            continue

        expected_keywords = (
            get_expected_keywords(case)
        )

        if expected_keywords:

            matched = [
                keyword
                for keyword in expected_keywords
                if str(keyword).lower() in text
            ]

            if not matched:

                failures.append(
                    f"Case {index}: "
                    f"no expected keywords found.\n"
                    f"Query: {query}\n"
                    f"Expected: {expected_keywords}"
                )

    assert not failures, (
        "RAG evaluation failures:\n"
        + "\n".join(failures)
    )