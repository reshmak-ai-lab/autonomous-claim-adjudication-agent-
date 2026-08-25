from app.extraction.billing_extractor import BillingExtractor


def test_billing_extractor_returns_result():
    extractor = BillingExtractor()

    text = """
    Room Rent: Rs. 5000
    Doctor Charges: Rs. 10000
    Surgery Charges: Rs. 40000
    Medicines: Rs. 15000
    Total Bill: Rs. 70000
    """

    result = extractor.extract(text)

    assert result is not None


def test_billing_extractor_extracts_amounts():
    extractor = BillingExtractor()

    text = """
    Room Rent: Rs. 5000
    Doctor Charges: Rs. 10000
    Surgery Charges: Rs. 40000
    Total Bill: Rs. 55000
    """

    result = extractor.extract(text)

    assert result is not None

    result_text = str(result)

    assert "5000" in result_text
    assert "10000" in result_text
    assert "40000" in result_text
    assert "55000" in result_text


def test_billing_extractor_handles_empty_input():
    extractor = BillingExtractor()

    result = extractor.extract("")

    assert result is not None