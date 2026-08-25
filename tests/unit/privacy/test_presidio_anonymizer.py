from app.privacy.presidio_anonymizer import PrivacyAnonymizer


def test_anonymizer_returns_expected_structure():
    anonymizer = PrivacyAnonymizer()

    text = "Patient email is patient@example.com."

    result = anonymizer.anonymize(text)

    assert isinstance(result, dict)

    assert "original_text" in result
    assert "anonymized_text" in result
    assert "entities_detected" in result
    assert "entity_count" in result


def test_anonymizer_redacts_email():
    anonymizer = PrivacyAnonymizer()

    text = "Patient email is patient@example.com."

    result = anonymizer.anonymize(text)

    anonymized = result["anonymized_text"]

    assert "patient@example.com" not in anonymized
    assert "[EMAIL_REDACTED]" in anonymized


def test_anonymizer_redacts_phone():
    anonymizer = PrivacyAnonymizer()

    text = "Patient phone number is 9876543210."

    result = anonymizer.anonymize(text)

    anonymized = result["anonymized_text"]

    assert "9876543210" not in anonymized
    assert "[PHONE_REDACTED]" in anonymized


def test_anonymizer_redacts_aadhaar():
    anonymizer = PrivacyAnonymizer()

    text = "Patient Aadhaar: 2345 6789 0123."

    result = anonymizer.anonymize(text)

    anonymized = result["anonymized_text"]

    assert "2345 6789 0123" not in anonymized
    assert "[AADHAAR_REDACTED]" in anonymized


def test_anonymizer_redacts_pan():
    anonymizer = PrivacyAnonymizer()

    text = "Patient PAN: ABCDE1234F."

    result = anonymizer.anonymize(text)

    anonymized = result["anonymized_text"]

    assert "ABCDE1234F" not in anonymized
    assert "[PAN_REDACTED]" in anonymized


def test_anonymizer_redacts_abha():
    anonymizer = PrivacyAnonymizer()

    text = "Patient ABHA: 12-3456-7890-1234."

    result = anonymizer.anonymize(text)

    anonymized = result["anonymized_text"]

    assert "12-3456-7890-1234" not in anonymized
    assert "[ABHA_REDACTED]" in anonymized


def test_anonymizer_redacts_credit_card():
    anonymizer = PrivacyAnonymizer()

    text = "Card number: 4111111111111111."

    result = anonymizer.anonymize(text)

    anonymized = result["anonymized_text"]

    assert "4111111111111111" not in anonymized
    assert "[CARD_REDACTED]" in anonymized


def test_anonymizer_preserves_non_pii_text():
    anonymizer = PrivacyAnonymizer()

    text = "Patient underwent appendectomy."

    result = anonymizer.anonymize(text)

    assert result["anonymized_text"] == text
    assert result["entity_count"] == 0


def test_anonymizer_empty_text():
    anonymizer = PrivacyAnonymizer()

    result = anonymizer.anonymize("")

    assert result["original_text"] == ""
    assert result["anonymized_text"] == ""
    assert result["entity_count"] == 0