from __future__ import annotations

import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Evaluation expectations
FRAUD_CASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "test_cases"
    / "fraud_test_cases.json"
)

# Actual claim fixtures
CLAIMS_ROOT = (
    PROJECT_ROOT
    / "data"
    / "sample_claims"
)


def load_cases():
    """Load fraud evaluation expectations."""

    if not FRAUD_CASE_FILE.exists():
        return []

    with FRAUD_CASE_FILE.open(
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


def find_claim_file(claim_id: str) -> Path | None:
    """
    Locate a claim JSON file by claim_id.

    Claims are stored under category directories such as:

        data/sample_claims/approved/
        data/sample_claims/partial_approval/
        data/sample_claims/query_raised/
        data/sample_claims/rejected/
    """

    expected_filename = f"claim_{claim_id}.json"

    matches = list(
        CLAIMS_ROOT.rglob(expected_filename)
    )

    if matches:
        return matches[0]

    return None


def load_claim(claim_id: str) -> dict:
    """Load the actual claim fixture."""

    claim_file = find_claim_file(claim_id)

    if claim_file is None:
        raise FileNotFoundError(
            f"Claim file not found for {claim_id} "
            f"under {CLAIMS_ROOT}"
        )

    with claim_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        claim = json.load(file)

    if not isinstance(claim, dict):
        raise ValueError(
            f"Claim file must contain an object: "
            f"{claim_file}"
        )

    return claim


def expected_risk(case):
    """Extract expected fraud risk."""

    if not isinstance(case, dict):
        return None

    return case.get(
        "expected_risk"
    )


def expected_flags(case):
    """Extract expected fraud flags."""

    if not isinstance(case, dict):
        return []

    flags = case.get(
        "expected_flags",
        [],
    )

    return (
        flags
        if isinstance(flags, list)
        else []
    )


def run_fraud_engine(claim):

    from app.fraud.fraud_engine import FraudEngine

    engine = FraudEngine()

    # Your workflow currently calls:
    #
    # engine.analyze(
    #     claim=claim,
    #     billing_items=...,
    #     diagnosis_data=...,
    #     clinical_data=...,
    #
    # But the evaluation test should also support
    # a simple analyze(claim) implementation.

    try:
        return engine.analyze(
            claim=claim,
            billing_items=claim.get(
                "billing_items",
                [],
            ),
            diagnosis_data=claim.get(
                "diagnosis",
                {},
            ),
            clinical_data=claim.get(
                "clinical_data",
                {},
            ),
        )

    except TypeError:
        return engine.analyze(
            claim
        )


def extract_risk(result):
    """Extract normalized fraud risk."""

    if not isinstance(result, dict):
        return None

    risk = result.get(
        "risk_level"
    )

    if risk is None:
        risk = result.get(
            "risk"
        )

    if risk is None:
        return None

    return str(risk).upper()


def extract_flags(result):
    """
    Extract fraud findings/flags from the engine result.

    Supports several result formats so the evaluation
    remains compatible with the existing FraudEngine.
    """

    if not isinstance(result, dict):
        return []

    flags = []

    # Existing engine format:
    #
    # {
    #   "findings": [...]
    # }

    findings = result.get(
        "findings",
        [],
    )

    if isinstance(findings, list):
        for finding in findings:

            if isinstance(finding, str):
                flags.append(
                    finding
                )

            elif isinstance(finding, dict):

                for key in (
                    "flag",
                    "code",
                    "type",
                    "name",
                    "reason",
                ):
                    value = finding.get(
                        key
                    )

                    if value:
                        flags.append(
                            str(value)
                        )
                        break

    # Optional explicit flags
    explicit_flags = result.get(
        "flags",
        []
    )

    if isinstance(
        explicit_flags,
        list,
    ):
        flags.extend(
            str(flag)
            for flag in explicit_flags
        )

    return sorted(
        set(flags)
    )


@pytest.mark.evaluation
def test_fraud_cases_are_loaded():

    cases = load_cases()

    if not cases:
        pytest.skip(
            f"No fraud evaluation cases found in "
            f"{FRAUD_CASE_FILE}"
        )

    assert len(cases) > 0


@pytest.mark.evaluation
def test_fraud_detection_accuracy():

    cases = load_cases()

    if not cases:
        pytest.skip(
            f"No fraud evaluation cases found in "
            f"{FRAUD_CASE_FILE}"
        )

    failures = []

    for index, case in enumerate(cases):

        if not isinstance(case, dict):
            failures.append(
                f"Case {index}: invalid case format"
            )
            continue

        claim_id = case.get(
            "claim_id"
        )

        if not claim_id:
            failures.append(
                f"Case {index}: missing claim_id"
            )
            continue

        expected_risk_value = (
            expected_risk(case)
        )

        expected_flag_values = (
            expected_flags(case)
        )

        if expected_risk_value is None:
            failures.append(
                f"Case {index} "
                f"({claim_id}): "
                "missing expected_risk"
            )
            continue

        # ----------------------------------------------------------
        # Load actual sample claim
        # ----------------------------------------------------------

        try:
            claim = load_claim(
                claim_id
            )

        except Exception as exc:
            failures.append(
                f"Case {index} "
                f"({claim_id}): "
                f"{exc}"
            )
            continue

        # ----------------------------------------------------------
        # Run fraud engine
        # ----------------------------------------------------------

        try:
            result = run_fraud_engine(
                claim
            )

        except Exception as exc:
            failures.append(
                f"Case {index} "
                f"({claim_id}): "
                f"fraud engine error: {exc}"
            )
            continue

        # ----------------------------------------------------------
        # Extract actual result
        # ----------------------------------------------------------

        actual_risk = extract_risk(
            result
        )

        actual_flags = extract_flags(
            result
        )

        # ----------------------------------------------------------
        # Risk validation
        # ----------------------------------------------------------

        if actual_risk is None:
            failures.append(
                f"Case {index} "
                f"({claim_id}): "
                f"could not extract risk from result: "
                f"{result}"
            )
            continue

        expected_risk_normalized = (
            str(
                expected_risk_value
            ).upper()
        )

        if actual_risk != expected_risk_normalized:

            failures.append(
                f"Case {index} "
                f"({claim_id}): "
                f"risk mismatch; "
                f"expected={expected_risk_normalized}, "
                f"actual={actual_risk}, "
                f"result={result}"
            )

        # ----------------------------------------------------------
        # Flag validation
        # ----------------------------------------------------------

        missing_flags = [
            flag
            for flag in expected_flag_values
            if flag not in actual_flags
        ]

        if missing_flags:

            failures.append(
                f"Case {index} "
                f"({claim_id}): "
                f"missing fraud flags "
                f"{missing_flags}; "
                f"actual_flags={actual_flags}; "
                f"result={result}"
            )

    assert not failures, (
        "Fraud evaluation failures:\n"
        + "\n".join(failures)
    )