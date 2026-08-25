import pytest

from app.rules.deductible import apply_deductible


def test_deductible_with_claim_above_deductible():
    result = apply_deductible(
        eligible_amount=10000,
        deductible=2000,
    )

    assert result["rule"] == "deductible"
    assert result["eligible_amount"] == 10000
    assert result["deductible"] == 2000
    assert result["payable_amount"] == 8000


def test_deductible_equal_to_claim():
    result = apply_deductible(
        eligible_amount=10000,
        deductible=10000,
    )

    assert result["eligible_amount"] == 10000
    assert result["deductible"] == 10000
    assert result["payable_amount"] == 0


def test_deductible_greater_than_claim():
    result = apply_deductible(
        eligible_amount=5000,
        deductible=10000,
    )

    # Deductible cannot exceed eligible amount
    assert result["eligible_amount"] == 5000
    assert result["deductible"] == 5000
    assert result["payable_amount"] == 0


def test_zero_deductible():
    result = apply_deductible(
        eligible_amount=10000,
        deductible=0,
    )

    assert result["eligible_amount"] == 10000
    assert result["deductible"] == 0
    assert result["payable_amount"] == 10000


def test_zero_eligible_amount():
    result = apply_deductible(
        eligible_amount=0,
        deductible=1000,
    )

    assert result["eligible_amount"] == 0
    assert result["deductible"] == 0
    assert result["payable_amount"] == 0


def test_fractional_amounts():
    result = apply_deductible(
        eligible_amount=12345.67,
        deductible=1234.56,
    )

    assert result["eligible_amount"] == 12345.67
    assert result["deductible"] == 1234.56
    assert result["payable_amount"] == 11111.11


def test_negative_eligible_amount():
    with pytest.raises(
        ValueError,
        match="Eligible amount cannot be negative",
    ):
        apply_deductible(
            eligible_amount=-1000,
            deductible=500,
        )


def test_negative_deductible():
    with pytest.raises(
        ValueError,
        match="Deductible cannot be negative",
    ):
        apply_deductible(
            eligible_amount=10000,
            deductible=-500,
        )