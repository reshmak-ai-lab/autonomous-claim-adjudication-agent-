from app.extraction.procedure_extractor import ProcedureExtractor


def test_procedure_extractor_returns_result():
    extractor = ProcedureExtractor()

    text = """
    Procedure performed:
    Laparoscopic appendectomy.
    """

    result = extractor.extract(text)

    assert result is not None


def test_procedure_extractor_identifies_procedure():
    extractor = ProcedureExtractor()

    text = """
    Patient underwent laparoscopic appendectomy.
    """

    result = extractor.extract(text)

    assert result is not None
    assert "appendectomy" in str(result).lower()


def test_procedure_extractor_handles_no_procedure():
    extractor = ProcedureExtractor()

    text = """
    Patient evaluated in outpatient department.
    No surgical procedure was performed.
    """

    result = extractor.extract(text)

    assert result is not None