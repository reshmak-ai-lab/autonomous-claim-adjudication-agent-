import pytest

from app.rules.room_rent import evaluate_room_rent


def test_room_rent_within_limit():
    result = evaluate_room_rent(
        actual_room_rent=3000,
        eligible_room_rent=5000,
    )

    assert result["rule"] == "room_rent"
    assert result["applicable"] is True
    assert result["within_limit"] is True
    assert result["actual_room_rent"] == 3000
    assert result["eligible_room_rent"] == 5000
    assert result["excess_room_rent"] == 0.0
    assert result["decision"] == "NO_DEDUCTION"


def test_room_rent_exceeds_limit():
    result = evaluate_room_rent(
        actual_room_rent=7000,
        eligible_room_rent=5000,
    )

    assert result["rule"] == "room_rent"
    assert result["applicable"] is True
    assert result["within_limit"] is False
    assert result["actual_room_rent"] == 7000
    assert result["eligible_room_rent"] == 5000
    assert result["excess_room_rent"] == 2000
    assert result["decision"] == "PROPORTIONAL_DEDUCTION_REQUIRED"


def test_room_rent_equal_to_limit():
    result = evaluate_room_rent(
        actual_room_rent=5000,
        eligible_room_rent=5000,
    )

    assert result["within_limit"] is True
    assert result["excess_room_rent"] == 0.0
    assert result["decision"] == "NO_DEDUCTION"


def test_zero_room_rent():
    result = evaluate_room_rent(
        actual_room_rent=0,
        eligible_room_rent=5000,
    )

    assert result["within_limit"] is True
    assert result["excess_room_rent"] == 0.0
    assert result["decision"] == "NO_DEDUCTION"


def test_negative_actual_room_rent():
    with pytest.raises(
        ValueError,
        match="Actual room rent cannot be negative",
    ):
        evaluate_room_rent(
            actual_room_rent=-1000,
            eligible_room_rent=5000,
        )


def test_negative_eligible_room_rent():
    with pytest.raises(
        ValueError,
        match="Eligible room rent cannot be negative",
    ):
        evaluate_room_rent(
            actual_room_rent=5000,
            eligible_room_rent=-1000,
        )


def test_both_values_zero():
    result = evaluate_room_rent(
        actual_room_rent=0,
        eligible_room_rent=0,
    )

    assert result["within_limit"] is True
    assert result["excess_room_rent"] == 0.0
    assert result["decision"] == "NO_DEDUCTION"