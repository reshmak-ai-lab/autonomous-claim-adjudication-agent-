from app.fraud.anomaly_detector import AnomalyDetector


def test_normal_amount_is_not_anomalous():
    detector = AnomalyDetector()

    claim = {
        "claimed_amount": 10000,
    }

    result = detector.detect(
        claim=claim,
        billing_items=[],
    )

    assert result is not None
    assert result["detected"] is False


def test_high_amount_is_detected_as_anomaly():
    detector = AnomalyDetector()

    claim = {
        "claimed_amount": 100000,
    }

    result = detector.detect(
        claim=claim,
        billing_items=[],
    )

    assert result["detected"] is True
    assert len(result["evidence"]) > 0


def test_zero_amount():
    detector = AnomalyDetector()

    claim = {
        "claimed_amount": 0,
    }

    result = detector.detect(
        claim=claim,
        billing_items=[],
    )

    assert result is not None
    assert result["detected"] is False


def test_anomaly_detects_very_high_billing_item():
    detector = AnomalyDetector()

    claim = {
        "claimed_amount": 10000,
    }

    billing_items = [
        {
            "procedure_name": "Surgery",
            "amount": 250000,
        }
    ]

    result = detector.detect(
        claim=claim,
        billing_items=billing_items,
    )

    assert result["detected"] is True


def test_historical_amount_anomaly():
    detector = AnomalyDetector()

    claim = {
        "claimed_amount": 100000,
    }

    historical_claims = [
        {"claimed_amount": 10000},
        {"claimed_amount": 12000},
        {"claimed_amount": 11000},
    ]

    result = detector.detect(
        claim=claim,
        billing_items=[],
        historical_claims=historical_claims,
    )

    assert result["detected"] is True