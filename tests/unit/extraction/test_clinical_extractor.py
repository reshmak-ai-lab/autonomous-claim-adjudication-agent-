from app.extraction.clinical_extractor import ClinicalExtractor


def test_clinical_extractor_returns_result():
    extractor = ClinicalExtractor()

    text = """
    Patient presented with severe abdominal pain and vomiting.
    Clinical examination indicated acute appendicitis.
    Patient was admitted for surgical management.
    """

    result = extractor.extract(text)

    assert result is not None


def test_clinical_extractor_identifies_clinical_information():
    extractor = ClinicalExtractor()

    text = """
    Patient presented with severe abdominal pain.
    Diagnosis: acute appendicitis.
    """

    result = extractor.extract(text)

    assert result is not None
    assert "append" in str(result).lower()


def test_clinical_extractor_handles_empty_input():
    extractor = ClinicalExtractor()

    result = extractor.extract("")

    assert result is not None