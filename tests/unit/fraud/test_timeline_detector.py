from app.fraud.timeline_detector import (
    TimelineDetector,
    parse_date,
    detect_timeline_anomalies,
)


def test_no_timeline_anomaly():
    detector = TimelineDetector()

    claim = {
        "admission_date": "2026-08-10",
        "discharge_date": "2026-08-15",
    }

    billing_items = [
        {
            "procedure_name": "Appendectomy",
            "service_date": "2026-08-12",
        }
    ]

    result = detector.detect(claim, billing_items)

    assert result is not None
    assert result["detected"] is False


def test_discharge_before_admission():
    detector = TimelineDetector()

    claim = {
        "admission_date": "2026-08-15",
        "discharge_date": "2026-08-10",
    }

    result = detector.detect(claim, [])

    assert result is not None
    assert result["detected"] is True
    assert len(result["evidence"]) > 0

    evidence_types = [
        evidence["type"]
        for evidence in result["evidence"]
    ]

    assert "invalid_admission_discharge" in evidence_types


def test_procedure_before_admission():
    detector = TimelineDetector()

    claim = {
        "admission_date": "2026-08-10",
        "discharge_date": "2026-08-15",
    }

    billing_items = [
        {
            "procedure_name": "Appendectomy",
            "service_date": "2026-08-08",
        }
    ]

    result = detector.detect(claim, billing_items)

    assert result["detected"] is True

    evidence_types = [
        evidence["type"]
        for evidence in result["evidence"]
    ]

    assert "procedure_before_admission" in evidence_types


def test_procedure_after_discharge():
    detector = TimelineDetector()

    claim = {
        "admission_date": "2026-08-10",
        "discharge_date": "2026-08-15",
    }

    billing_items = [
        {
            "procedure_name": "Follow-up Procedure",
            "service_date": "2026-08-20",
        }
    ]

    result = detector.detect(claim, billing_items)

    assert result["detected"] is True

    evidence_types = [
        evidence["type"]
        for evidence in result["evidence"]
    ]

    assert "procedure_after_discharge" in evidence_types


def test_procedure_on_admission_date_is_valid():
    detector = TimelineDetector()

    claim = {
        "admission_date": "2026-08-10",
        "discharge_date": "2026-08-15",
    }

    billing_items = [
        {
            "procedure_name": "Initial Procedure",
            "service_date": "2026-08-10",
        }
    ]

    result = detector.detect(claim, billing_items)

    assert result["detected"] is False


def test_procedure_on_discharge_date_is_valid():
    detector = TimelineDetector()

    claim = {
        "admission_date": "2026-08-10",
        "discharge_date": "2026-08-15",
    }

    billing_items = [
        {
            "procedure_name": "Final Procedure",
            "service_date": "2026-08-15",
        }
    ]

    result = detector.detect(claim, billing_items)

    assert result["detected"] is False


def test_empty_billing_items():
    detector = TimelineDetector()

    claim = {
        "admission_date": "2026-08-10",
        "discharge_date": "2026-08-15",
    }

    result = detector.detect(claim, [])

    assert result is not None
    assert result["detected"] is False


def test_missing_dates_do_not_create_false_anomaly():
    detector = TimelineDetector()

    claim = {}

    billing_items = [
        {
            "procedure_name": "Appendectomy",
            "service_date": "2026-08-12",
        }
    ]

    result = detector.detect(claim, billing_items)

    assert result is not None
    assert result["detected"] is False


def test_parse_date_yyyy_mm_dd():
    result = parse_date("2026-08-10")

    assert result is not None
    assert result.year == 2026
    assert result.month == 8
    assert result.day == 10


def test_parse_date_dd_mm_yyyy():
    result = parse_date("10-08-2026")

    assert result is not None
    assert result.year == 2026
    assert result.month == 8
    assert result.day == 10


def test_parse_date_slash_format():
    result = parse_date("10/08/2026")

    assert result is not None
    assert result.year == 2026
    assert result.month == 8
    assert result.day == 10


def test_parse_date_invalid():
    result = parse_date("not-a-date")

    assert result is None


def test_parse_date_none():
    result = parse_date(None)

    assert result is None


def test_detect_timeline_wrapper():
    claim = {
        "admission_date": "2026-08-10",
        "discharge_date": "2026-08-15",
    }

    billing_items = [
        {
            "procedure_name": "Appendectomy",
            "service_date": "2026-08-20",
        }
    ]

    result = detect_timeline_anomalies(
        claim,
        billing_items,
    )

    assert result is not None
    assert result["detected"] is True