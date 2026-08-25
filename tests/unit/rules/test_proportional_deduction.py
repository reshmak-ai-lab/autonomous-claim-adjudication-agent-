import pytest

from app.rules.proportional_deduction import (
    calculate_proportional_deduction,
)


def test_no_proportional_deduction_when_room_is_within_limit():
    result = calculate_proportional_deduction(
        actual_room_rent=4000,
        eligible_room_rent=5000,
        bill_amount=20000,
    )

    assert result["rule"] == "proportional_deduction"
    assert result["applicable"] is False
    assert result["ratio"] == 1.0
    assert result["eligible_amount"] == 20000
    assert result["deduction"] == 0.0


def test_proportional_deduction_when_room_exceeds_limit():
    result = calculate_proportional_deduction(
        actual_room_rent=6000,
        eligible_room_rent=4000,
        bill_amount=20000,
    )

    # Ratio = 4000 / 6000 = 0.6667
    # Eligible = 20000 * 4000 / 6000 = 13333.33
    # Deduction = 6666.67
    assert result["rule"] == "proportional_deduction"
    assert result["applicable"] is True
    assert result["ratio"] == 0.6667
    assert result["eligible_amount"] == 13333.33
    assert result["deduction"] == 6666.67


def test_zero_bill_amount():
    result = calculate_proportional_deduction(
        actual_room_rent=6000,
        eligible_room_rent=4000,
        bill_amount=0,
    )

    assert result["applicable"] is True
    assert result["ratio"] == 0.6667
    assert result["eligible_amount"] == 0.0
    assert result["deduction"] == 0.0


def test_equal_room_rent():
    result = calculate_proportional_deduction(
        actual_room_rent=5000,
        eligible_room_rent=5000,
        bill_amount=20000,
    )

    assert result["applicable"] is False
    assert result["ratio"] == 1.0
    assert result["eligible_amount"] == 20000
    assert result["deduction"] == 0.0


def test_zero_actual_room_rent():
    with pytest.raises(
        ValueError,
        match="Actual room rent must be greater than zero",
    ):
        calculate_proportional_deduction(
            actual_room_rent=0,
            eligible_room_rent=4000,
            bill_amount=20000,
        )


def test_negative_actual_room_rent():
    with pytest.raises(
        ValueError,
        match="Actual room rent must be greater than zero",
    ):
        calculate_proportional_deduction(
            actual_room_rent=-1000,
            eligible_room_rent=4000,
            bill_amount=20000,
        )


def test_negative_eligible_room_rent():
    with pytest.raises(
        ValueError,
        match="Eligible room rent cannot be negative",
    ):
        calculate_proportional_deduction(
            actual_room_rent=6000,
            eligible_room_rent=-4000,
            bill_amount=20000,
        )


def test_negative_bill_amount():
    with pytest.raises(
        ValueError,
        match="Bill amount cannot be negative",
    ):
        calculate_proportional_deduction(
            actual_room_rent=6000,
            eligible_room_rent=4000,
            bill_amount=-20000,
        )


def test_full_proportional_deduction():
    result = calculate_proportional_deduction(
        actual_room_rent=10000,
        eligible_room_rent=5000,
        bill_amount=10000,
    )

    assert result["ratio"] == 0.5
    assert result["eligible_amount"] == 5000
    assert result["deduction"] == 5000