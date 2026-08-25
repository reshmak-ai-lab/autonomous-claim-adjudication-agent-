import pytest

from app.rules.sum_insured import evaluate_sum_insured


def test_claim_within_sum_insured():
    result = evaluate_sum_insured(
        claimed_amount=50000,
        sum_insured=100000,
    )

    assert result["rule"] == "sum_insured"
    assert result["sum_insured"] == 100000
    assert result["already_paid"] == 0.0
    assert result["remaining_sum_insured"] == 100000
    assert result["claimed_amount"] == 50000
    assert result["eligible_amount"] == 50000
    assert result["excess_amount"] == 0.0


def test_claim_exceeds_sum_insured():
    result = evaluate_sum_insured(
        claimed_amount=150000,
        sum_insured=100000,
    )

    assert result["remaining_sum_insured"] == 100000
    assert result["eligible_amount"] == 100000
    assert result["excess_amount"] == 50000


def test_claim_equal_to_sum_insured():
    result = evaluate_sum_insured(
        claimed_amount=100000,
        sum_insured=100000,
    )

    assert result["eligible_amount"] == 100000
    assert result["excess_amount"] == 0.0


def test_already_paid_reduces_available_sum_insured():
    result = evaluate_sum_insured(
        claimed_amount=50000,
        sum_insured=100000,
        already_paid=30000,
    )

    assert result["remaining_sum_insured"] == 70000
    assert result["eligible_amount"] == 50000
    assert result["excess_amount"] == 0.0


def test_claim_exceeds_remaining_sum_insured():
    result = evaluate_sum_insured(
        claimed_amount=80000,
        sum_insured=100000,
        already_paid=40000,
    )

    assert result["remaining_sum_insured"] == 60000
    assert result["eligible_amount"] == 60000
    assert result["excess_amount"] == 20000


def test_already_paid_equals_sum_insured():
    result = evaluate_sum_insured(
        claimed_amount=50000,
        sum_insured=100000,
        already_paid=100000,
    )

    assert result["remaining_sum_insured"] == 0.0
    assert result["eligible_amount"] == 0.0
    assert result["excess_amount"] == 50000


def test_already_paid_exceeds_sum_insured():
    result = evaluate_sum_insured(
        claimed_amount=50000,
        sum_insured=100000,
        already_paid=120000,
    )

    assert result["remaining_sum_insured"] == 0.0
    assert result["eligible_amount"] == 0.0
    assert result["excess_amount"] == 50000


def test_zero_claim():
    result = evaluate_sum_insured(
        claimed_amount=0,
        sum_insured=100000,
    )

    assert result["eligible_amount"] == 0.0
    assert result["excess_amount"] == 0.0


def test_zero_sum_insured():
    result = evaluate_sum_insured(
        claimed_amount=50000,
        sum_insured=0,
    )

    assert result["remaining_sum_insured"] == 0.0
    assert result["eligible_amount"] == 0.0
    assert result["excess_amount"] == 50000


def test_negative_claimed_amount():
    with pytest.raises(
        ValueError,
        match="Claimed amount cannot be negative",
    ):
        evaluate_sum_insured(
            claimed_amount=-1000,
            sum_insured=100000,
        )


def test_negative_sum_insured():
    with pytest.raises(
        ValueError,
        match="Sum insured cannot be negative",
    ):
        evaluate_sum_insured(
            claimed_amount=10000,
            sum_insured=-100000,
        )


def test_negative_already_paid():
    with pytest.raises(
        ValueError,
        match="Already paid amount cannot be negative",
    ):
        evaluate_sum_insured(
            claimed_amount=10000,
            sum_insured=100000,
            already_paid=-5000,
        )