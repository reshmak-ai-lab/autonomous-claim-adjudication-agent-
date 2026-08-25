from app.rules.non_payable_items import evaluate_non_payable_item


def test_non_payable_item():
    result = evaluate_non_payable_item(
        item="registration fee",
        non_payable_items=[
            "registration fee",
            "administrative charges",
        ],
    )

    assert result["rule"] == "non_payable_items"
    assert result["non_payable"] is True
    assert result["matched_item"] == "registration fee"
    assert result["decision"] == "DEDUCT"


def test_payable_item():
    result = evaluate_non_payable_item(
        item="surgery",
        non_payable_items=[
            "registration fee",
            "administrative charges",
        ],
    )

    assert result["rule"] == "non_payable_items"
    assert result["non_payable"] is False
    assert result["decision"] == "PAYABLE_IF_OTHER_RULES_PASS"


def test_case_insensitive_matching():
    result = evaluate_non_payable_item(
        item="Registration Fee",
        non_payable_items=["registration fee"],
    )

    assert result["non_payable"] is True
    assert result["matched_item"] == "registration fee"
    assert result["decision"] == "DEDUCT"


def test_partial_match():
    result = evaluate_non_payable_item(
        item="Hospital registration fee charges",
        non_payable_items=["registration fee"],
    )

    assert result["non_payable"] is True
    assert result["matched_item"] == "registration fee"


def test_empty_non_payable_list():
    result = evaluate_non_payable_item(
        item="surgery",
        non_payable_items=[],
    )

    assert result["non_payable"] is False
    assert result["decision"] == "PAYABLE_IF_OTHER_RULES_PASS"


def test_empty_item():
    result = evaluate_non_payable_item(
        item="",
        non_payable_items=["registration fee"],
    )

    assert result["rule"] == "non_payable_items"
    assert result["non_payable"] is False


def test_whitespace_is_normalized():
    result = evaluate_non_payable_item(
        item="  Registration Fee  ",
        non_payable_items=["  registration fee  "],
    )

    assert result["non_payable"] is True
    assert result["decision"] == "DEDUCT"


def test_rule_name_is_present():
    result = evaluate_non_payable_item(
        item="surgery",
        non_payable_items=[],
    )

    assert result["rule"] == "non_payable_items"