from app.extraction.diagnosis_extractor import DiagnosisExtractor


def test_diagnosis_extractor_returns_result():
    extractor = DiagnosisExtractor()

    text = """
    Final Diagnosis:
    Acute appendicitis with localized peritonitis.
    """

    result = extractor.extract(text)

    assert result is not None


def test_diagnosis_extractor_identifies_diagnosis():
    extractor = DiagnosisExtractor()

    text = """
    Final Diagnosis:
    Acute appendicitis.
    """

    result = extractor.extract(text)

    assert result is not None
    assert "append" in str(result).lower()


def test_diagnosis_extractor_handles_missing_diagnosis():
    extractor = DiagnosisExtractor()

    text = """
    Patient admitted for observation.
    No confirmed diagnosis was documented.
    """

    result = extractor.extract(text)

    assert result is not None