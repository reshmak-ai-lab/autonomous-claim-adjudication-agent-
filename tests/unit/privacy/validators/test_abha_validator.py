from app.privacy.validators.abha_validator import (
    normalize_abha,
    is_valid_abha_format,
    find_abha_numbers,
)


def test_normalize_abha():
    value = " 12-3456-7890-1234 "

    result = normalize_abha(value)

    assert result == "12-3456-7890-1234"


def test_valid_abha_format():
    value = "12-3456-7890-1234"

    assert is_valid_abha_format(value) is True


def test_invalid_abha_without_hyphens():
    value = "12345678901234"

    assert is_valid_abha_format(value) is False


def test_invalid_abha_wrong_first_group():
    value = "123-4567-8901-2345"

    assert is_valid_abha_format(value) is False


def test_invalid_abha_wrong_group_length():
    value = "12-345-7890-1234"

    assert is_valid_abha_format(value) is False


def test_invalid_abha_letters():
    value = "12-ABCD-7890-1234"

    assert is_valid_abha_format(value) is False


def test_invalid_abha_empty():
    assert is_valid_abha_format("") is False


def test_invalid_abha_none():
    assert is_valid_abha_format(None) is False


def test_find_abha_numbers():
    text = """
    Patient ABHA number: 12-3456-7890-1234
    """

    result = find_abha_numbers(text)

    assert len(result) == 1
    assert result[0] == "12-3456-7890-1234"


def test_find_multiple_abha_numbers():
    text = """
    Patient 1: 12-3456-7890-1234
    Patient 2: 98-7654-3210-9876
    """

    result = find_abha_numbers(text)

    assert len(result) == 2


def test_find_abha_numbers_empty_text():
    result = find_abha_numbers("")

    assert result == []