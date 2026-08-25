from app.privacy.presidio_analyzer import PrivacyAnalyzer
from functools import lru_cache
from typing import Any

def test_analyzer_returns_empty_for_empty_text():
    analyzer = PrivacyAnalyzer()

    result = analyzer.analyze("")

    assert result == []


def test_analyzer_detects_email():
    analyzer = PrivacyAnalyzer()

    text = "Patient email is patient@example.com."

    result = analyzer.analyze(text)

    assert result

    entities = [item.entity_type for item in result]

    assert "EMAIL_ADDRESS" in entities


def test_analyzer_detects_phone():
    analyzer = PrivacyAnalyzer()

    text = "Patient phone number is 9876543210."

    result = analyzer.analyze(text)

    assert result

    entities = [item.entity_type for item in result]

    assert any(
        entity in entities
        for entity in ["PHONE_NUMBER", "IN_PHONE"]
    )


def test_analyzer_detects_credit_card():
    analyzer = PrivacyAnalyzer()

    text = "Card number is 4111111111111111."

    result = analyzer.analyze(text)

    assert result

    entities = [item.entity_type for item in result]

    assert "CREDIT_CARD" in entities


def test_analyzer_detects_aadhaar():
    analyzer = PrivacyAnalyzer()

    text = "Aadhaar number: 2345 6789 0123."

    result = analyzer.analyze(text)

    assert result

    entities = [item.entity_type for item in result]

    assert "IN_AADHAAR" in entities


def test_analyzer_detects_pan():
    analyzer = PrivacyAnalyzer()

    text = "PAN number: ABCDE1234F."

    result = analyzer.analyze(text)

    assert result

    entities = [item.entity_type for item in result]

    assert "IN_PAN" in entities


def test_analyzer_detects_abha():
    analyzer = PrivacyAnalyzer()

    text = "ABHA number: 12-3456-7890-1234."

    result = analyzer.analyze(text)

    assert result

    entities = [item.entity_type for item in result]

    assert "IN_ABHA" in entities


def test_analyzer_with_details():
    analyzer = PrivacyAnalyzer()

    text = "Patient email is patient@example.com."

    result = analyzer.analyze_with_details(text)

    assert result
    assert isinstance(result, list)

    item = result[0]

    assert "entity_type" in item
    assert "start" in item
    assert "end" in item
    assert "score" in item
    assert "text" in item


def test_analyzer_with_details_empty_text():
    analyzer = PrivacyAnalyzer()

    result = analyzer.analyze_with_details("")

    assert result == []
