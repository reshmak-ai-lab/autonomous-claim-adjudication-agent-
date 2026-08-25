from app.extraction.timeline_extractor import TimelineExtractor


def test_timeline_extractor_returns_result():
    extractor = TimelineExtractor()

    text = """
    Date of Admission: 10 August 2026
    Date of Surgery: 12 August 2026
    Date of Discharge: 15 August 2026
    """

    result = extractor.extract(text)

    assert result is not None


def test_timeline_extractor_extracts_dates():
    extractor = TimelineExtractor()

    text = """
    Date of Admission: 10 August 2026
    Date of Discharge: 15 August 2026
    """

    result = extractor.extract(text)

    assert result is not None
    assert "2026" in str(result)


def test_timeline_extractor_handles_empty_input():
    extractor = TimelineExtractor()

    result = extractor.extract("")

    assert result is not None