from app.privacy.validators.aadhaar_validator import (
    normalize_aadhaar,
    is_valid_aadhaar_format,
    find_aadhaar_numbers,
)


def test_normalize_aadhaar_removes_spaces():
    value = "2345 6789 0123"

    result = normalize_aadhaar(value)

    assert result == "234567890123"


def test_normalize_aadhaar_removes_hyphens():
    value = "2345-6789-0123"

    result = normalize_aadhaar(value)

    assert result == "234567890123"


def test_valid_aadhaar_format():
    value = "234567890123"

    assert is_valid_aadhaar_format(value) is True


def test_valid_aadhaar_with_spaces():
    value = "2345 6789 0123"

    assert is_valid_aadhaar_format(value) is True


def test_valid_aadhaar_with_hyphens():
    value = "2345-6789-0123"

    assert is_valid_aadhaar_format(value) is True


def test_invalid_aadhaar_length():
    value = "123456789"

    assert is_valid_aadhaar_format(value) is False


def test_invalid_aadhaar_letters():
    value = "12345678901A"

    assert is_valid_aadhaar_format(value) is False


def test_invalid_aadhaar_empty():
    assert is_valid_aadhaar_format("") is False


def test_invalid_aadhaar_none():
    assert is_valid_aadhaar_format(None) is False


def test_find_aadhaar_numbers():
    text = """
    Patient Aadhaar: 2345 6789 0123
    """

    result = find_aadhaar_numbers(text)

    assert len(result) == 1
    assert result[0] == "2345 6789 0123"


def test_find_multiple_aadhaar_numbers():
    text = """
    Patient 1: 2345 6789 0123
    Patient 2: 9876 5432 1098
    """

    result = find_aadhaar_numbers(text)

    assert len(result) == 2


def test_find_aadhaar_numbers_empty_text():
    result = find_aadhaar_numbers("")

    assert result == []