from datetime import date

import pytest

from app.rules.waiting_period import evaluate_waiting_period


def test_waiting_period_completed():
    result = evaluate_waiting_period(
        policy_start_date=date(2025, 1, 1),
        admission_date=date(2025, 7, 1),
        waiting_period_days=180,
    )

    assert result["rule"] == "waiting_period"
    assert result["applicable"] is True
    assert result["eligible"] is True
    assert result["elapsed_days"] == 181
    assert result["required_days"] == 180
    assert result["remaining_days"] == 0


def test_waiting_period_not_completed():
    result = evaluate_waiting_period(
        policy_start_date=date(2026, 1, 1),
        admission_date=date(2026, 2, 1),
        waiting_period_days=180,
    )

    assert result["rule"] == "waiting_period"
    assert result["applicable"] is True
    assert result["eligible"] is False
    assert result["elapsed_days"] == 31
    assert result["required_days"] == 180
    assert result["remaining_days"] == 149


def test_waiting_period_exactly_completed():
    result = evaluate_waiting_period(
        policy_start_date=date(2026, 1, 1),
        admission_date=date(2026, 6, 30),
        waiting_period_days=180,
    )

    assert result["elapsed_days"] == 180
    assert result["eligible"] is True
    assert result["remaining_days"] == 0


def test_zero_waiting_period():
    result = evaluate_waiting_period(
        policy_start_date=date(2026, 1, 1),
        admission_date=date(2026, 1, 1),
        waiting_period_days=0,
    )

    assert result["eligible"] is True
    assert result["elapsed_days"] == 0
    assert result["remaining_days"] == 0


def test_admission_before_policy_start():
    result = evaluate_waiting_period(
        policy_start_date=date(2026, 1, 10),
        admission_date=date(2026, 1, 5),
        waiting_period_days=30,
    )

    assert result["rule"] == "waiting_period"
    assert result["applicable"] is True
    assert result["eligible"] is False
    assert result["reason"] == (
        "Admission occurred before policy start date"
    )


def test_negative_waiting_period():
    with pytest.raises(
        ValueError,
        match="Waiting period cannot be negative",
    ):
        evaluate_waiting_period(
            policy_start_date=date(2026, 1, 1),
            admission_date=date(2026, 2, 1),
            waiting_period_days=-1,
        )