from app.privacy.token_vault import TokenVault


def test_create_token():
    vault = TokenVault()

    token = vault.create_token(
        "9876543210",
        "IN_PHONE",
    )

    assert token is not None
    assert token != "9876543210"


def test_resolve_token():
    vault = TokenVault()

    original = "9876543210"

    token = vault.create_token(
        original,
        "IN_PHONE",
    )

    result = vault.resolve(token)

    assert result == original


def test_token_does_not_contain_sensitive_value():
    vault = TokenVault()

    sensitive_value = "9876543210"

    token = vault.create_token(
        sensitive_value,
        "IN_PHONE",
    )

    assert sensitive_value not in token


def test_multiple_tokens_are_unique():
    vault = TokenVault()

    token1 = vault.create_token(
        "9876543210",
        "IN_PHONE",
    )

    token2 = vault.create_token(
        "9123456780",
        "IN_PHONE",
    )

    assert token1 != token2


def test_unknown_token_returns_none():
    vault = TokenVault()

    result = vault.resolve("<UNKNOWN_TOKEN>")

    assert result is None


def test_delete_token():
    vault = TokenVault()

    token = vault.create_token(
        "ABCDE1234F",
        "IN_PAN",
    )

    assert vault.resolve(token) == "ABCDE1234F"

    deleted = vault.delete(token)

    assert deleted is True
    assert vault.resolve(token) is None


def test_delete_unknown_token():
    vault = TokenVault()

    result = vault.delete("<UNKNOWN_TOKEN>")

    assert result is False


def test_clear_tokens():
    vault = TokenVault()

    vault.create_token(
        "9876543210",
        "IN_PHONE",
    )

    vault.create_token(
        "ABCDE1234F",
        "IN_PAN",
    )

    assert vault.size() == 2

    vault.clear()

    assert vault.size() == 0


def test_size():
    vault = TokenVault()

    assert vault.size() == 0

    vault.create_token(
        "9876543210",
        "IN_PHONE",
    )

    assert vault.size() == 1

    vault.create_token(
        "ABCDE1234F",
        "IN_PAN",
    )

    assert vault.size() == 2