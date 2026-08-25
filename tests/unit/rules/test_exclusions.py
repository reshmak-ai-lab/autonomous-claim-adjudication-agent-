from app.rules.exclusions import evaluate_exclusion


def test_excluded_item():
    result = evaluate_exclusion(
        item="cosmetic surgery",
        exclusions=[
            "cosmetic surgery",
            "dental treatment",
        ],
    )

    assert result["excluded"] is True
    assert result["matched_exclusion"] == "cosmetic surgery"
    assert result["decision"] == "NOT_PAYABLE"


def test_non_excluded_item():
    result = evaluate_exclusion(
        item="appendectomy",
        exclusions=[
            "cosmetic surgery",
            "dental treatment",
        ],
    )

    assert result["excluded"] is False
    assert result["decision"] == "PAYABLE_IF_OTHER_RULES_PASS"


def test_case_insensitive_exclusion():
    result = evaluate_exclusion(
        item="Cosmetic Surgery",
        exclusions=["cosmetic surgery"],
    )

    assert result["excluded"] is True
    assert result["matched_exclusion"] == "cosmetic surgery"


def test_partial_exclusion_match():
    result = evaluate_exclusion(
        item="Emergency cosmetic surgery procedure",
        exclusions=["cosmetic surgery"],
    )

    assert result["excluded"] is True
    assert result["matched_exclusion"] == "cosmetic surgery"


def test_empty_exclusions():
    result = evaluate_exclusion(
        item="appendectomy",
        exclusions=[],
    )

    assert result["excluded"] is False
    assert result["decision"] == "PAYABLE_IF_OTHER_RULES_PASS"


def test_empty_item():
    result = evaluate_exclusion(
        item="",
        exclusions=["cosmetic surgery"],
    )

    assert result["excluded"] is False
    assert result["reason"] == "No item provided"


def test_whitespace_is_normalized():
    result = evaluate_exclusion(
        item="  Cosmetic Surgery  ",
        exclusions=["  cosmetic surgery  "],
    )

    assert result["excluded"] is True
    assert result["decision"] == "NOT_PAYABLE"


def test_rule_name_is_present():
    result = evaluate_exclusion(
        item="appendectomy",
        exclusions=[],
    )

    assert result["rule"] == "exclusions"