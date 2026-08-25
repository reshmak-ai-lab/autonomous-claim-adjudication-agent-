import pytest

from app.fraud.fraud_engine import FraudEngine


def test_fraud_engine_can_be_created():
    engine = FraudEngine()
    assert engine is not None


def test_fraud_engine_returns_result():
    engine = FraudEngine()

    claim = {
        "claim_id": "CLM-TEST-001",
        "claimed_amount": 10000,
    }

    result = engine.analyze(claim)

    assert result is not None


def test_fraud_engine_handles_empty_claim():
    engine = FraudEngine()

    result = engine.analyze({})

    assert result is not None