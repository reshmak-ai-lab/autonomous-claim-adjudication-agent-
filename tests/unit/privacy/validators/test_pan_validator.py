from app.privacy.validators.pan_validator import (
    normalize_pan,
    is_valid_pan_format,
    find_pan_numbers,
)


def test_normalize_pan():
    value = " abcde1234f "

    result = normalize_pan(value)

    assert result == "ABCDE1234F"


def test_valid_pan_format():
    value = "ABCDE1234F"

    assert is_valid_pan_format(value) is True


def test_valid_pan_lowercase():
    value = "abcde1234f"

    assert is_valid_pan_format(value) is True


def test_valid_pan_with_whitespace():
    value = " ABCDE1234F "

    assert is_valid_pan_format(value) is True


def test_invalid_pan_length():
    value = "ABCDE123"

    assert is_valid_pan_format(value) is False


def test_invalid_pan_structure():
    value = "12345ABCDE"

    assert is_valid_pan_format(value) is False


def test_invalid_pan_special_character():
    value = "ABCDE-1234F"

    assert is_valid_pan_format(value) is False


def test_invalid_pan_empty():
    assert is_valid_pan_format("") is False


def test_invalid_pan_none():
    assert is_valid_pan_format(None) is False


def test_find_pan_numbers():
    text = """
    Patient PAN is ABCDE1234F.
    """

    result = find_pan_numbers(text)

    assert len(result) == 1
    assert result[0].upper() == "ABCDE1234F"


def test_find_multiple_pan_numbers():
    text = """
    Patient 1 PAN: ABCDE1234F
    Patient 2 PAN: XYZAB9876C
    """

    result = find_pan_numbers(text)

    assert len(result) == 2


def test_find_pan_numbers_empty_text():
    result = find_pan_numbers("")

    assert result == []