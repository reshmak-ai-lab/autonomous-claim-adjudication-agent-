import pytest

from app.rules.copay import calculate_copay


def test_no_copay():
    result = calculate_copay(
        eligible_amount=10000,
        copay_percentage=0,
    )

    assert result["rule"] == "copay"
    assert result["eligible_amount"] == 10000
    assert result["copay_percentage"] == 0
    assert result["copay_amount"] == 0
    assert result["payable_amount"] == 10000


def test_twenty_percent_copay():
    result = calculate_copay(
        eligible_amount=10000,
        copay_percentage=20,
    )

    assert result["rule"] == "copay"
    assert result["copay_amount"] == 2000
    assert result["payable_amount"] == 8000


def test_ten_percent_copay():
    result = calculate_copay(
        eligible_amount=50000,
        copay_percentage=10,
    )

    assert result["copay_amount"] == 5000
    assert result["payable_amount"] == 45000


def test_full_copay():
    result = calculate_copay(
        eligible_amount=10000,
        copay_percentage=100,
    )

    assert result["copay_amount"] == 10000
    assert result["payable_amount"] == 0


def test_fractional_copay():
    result = calculate_copay(
        eligible_amount=12345.67,
        copay_percentage=15,
    )

    assert result["copay_amount"] == 1851.85
    assert result["payable_amount"] == 10493.82


def test_zero_eligible_amount():
    result = calculate_copay(
        eligible_amount=0,
        copay_percentage=20,
    )

    assert result["copay_amount"] == 0
    assert result["payable_amount"] == 0


def test_negative_eligible_amount():
    with pytest.raises(
        ValueError,
        match="Eligible amount cannot be negative",
    ):
        calculate_copay(
            eligible_amount=-1000,
            copay_percentage=20,
        )


def test_negative_copay_percentage():
    with pytest.raises(
        ValueError,
        match="Co-pay percentage must be between 0 and 100",
    ):
        calculate_copay(
            eligible_amount=10000,
            copay_percentage=-1,
        )


def test_copay_percentage_above_100():
    with pytest.raises(
        ValueError,
        match="Co-pay percentage must be between 0 and 100",
    ):
        calculate_copay(
            eligible_amount=10000,
            copay_percentage=101,
        )