from __future__ import annotations

import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PII_FILE = (
    PROJECT_ROOT
    / "data"
    / "test_cases"
    / "pii_test_cases.json"
)


def load_cases():

    if not PII_FILE.exists():
        return []

    with PII_FILE.open(
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


def get_text(case):

    if isinstance(case, str):
        return case

    for key in (
        "text",
        "input",
        "query",
        "document",
    ):

        value = case.get(key)

        if value:
            return value

    return ""


def get_expected_entities(case):

    if not isinstance(case, dict):
        return []

    for key in (
        "expected_entities",
        "entities",
        "pii_types",
    ):

        value = case.get(key)

        if isinstance(value, list):
            return value

    return []


def anonymize_text(text):

    try:

        from app.privacy.presidio_anonymizer import (
            anonymize_text,
        )

        return anonymize_text(text)

    except ImportError:
        pass

    try:

        from app.privacy.presidio_anonymizer import (
            PresidioAnonymizer,
        )

        anonymizer = PresidioAnonymizer()

        if hasattr(
            anonymizer,
            "anonymize",
        ):

            return anonymizer.anonymize(
                text
            )

    except ImportError:
        pass

    pytest.fail(
        "No supported Presidio anonymization "
        "interface found."
    )


@pytest.mark.evaluation
def test_pii_cases_are_loaded():

    cases = load_cases()

    if not cases:
        pytest.skip(
            f"No PII evaluation cases found in "
            f"{PII_FILE}"
        )

    assert len(cases) > 0



@pytest.mark.evaluation
def test_pii_is_redacted():

    cases = load_cases()

    if not cases:
        pytest.skip(
            f"No PII evaluation cases found in "
            f"{PII_FILE}"
        )

    failures = []

    for index, case in enumerate(cases):

        text = get_text(case)

        if not text:
            failures.append(
                f"Case {index}: missing input text"
            )
            continue

        try:
            from app.privacy.presidio_anonymizer import (
                anonymize_text,
            )

            result_text = anonymize_text(text)

        except Exception as exc:

            failures.append(
                f"Case {index}: "
                f"anonymization error: {exc}"
            )
            continue

        expected_entities = get_expected_entities(case)

        # ---------------------------------------------------------
        # No PII expected
        #
        # Correct behavior: input must remain unchanged.
        # ---------------------------------------------------------
        if not expected_entities:

            if result_text != text:

                failures.append(
                    f"Case {index}: "
                    "text changed although no PII "
                    "was expected."
                )

            continue

        # ---------------------------------------------------------
        # PII expected
        #
        # Correct behavior: anonymized output must differ.
        # ---------------------------------------------------------
        if result_text == text:

            failures.append(
                f"Case {index}: "
                "PII anonymization did not "
                "modify the input."
            )
            continue

        # ---------------------------------------------------------
        # Verify the actual sensitive values are gone.
        #
        # We do NOT search for strings such as:
        # PERSON, PAN, PHONE
        #
        # because those are entity TYPE names, not PII values.
        # ---------------------------------------------------------
        try:
            from app.privacy.presidio_analyzer import (
                PrivacyAnalyzer,
            )

            analyzer = PrivacyAnalyzer()

            detected = analyzer.analyze_with_details(
                text
            )

        except Exception as exc:

            failures.append(
                f"Case {index}: "
                f"PII detection error: {exc}"
            )
            continue

        for entity in detected:

            original_value = entity.get("text")

            if (
                original_value
                and original_value in result_text
            ):

                failures.append(
                    f"Case {index}: "
                    f"PII value "
                    f"'{original_value}' "
                    "remains in output."
                )

    assert not failures, (
        "PII evaluation failures:\n"
        + "\n".join(failures)
    )