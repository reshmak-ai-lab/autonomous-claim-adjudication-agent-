from app.fraud.duplicate_charge_detector import DuplicateChargeDetector


def test_duplicate_charge_detector_can_be_created():
    detector = DuplicateChargeDetector()
    assert detector is not None


def test_unique_charges():
    detector = DuplicateChargeDetector()

    charges = [
        {
            "item": "Room Rent",
            "amount": 5000,
        },
        {
            "item": "Doctor Fee",
            "amount": 3000,
        },
    ]

    result = detector.detect(charges)

    assert result is not None


def test_duplicate_charges():
    detector = DuplicateChargeDetector()

    charges = [
        {
            "item": "Room Rent",
            "amount": 5000,
        },
        {
            "item": "Room Rent",
            "amount": 5000,
        },
    ]

    result = detector.detect(charges)

    assert result is not None


def test_empty_charges():
    detector = DuplicateChargeDetector()

    result = detector.detect([])

    assert result is not None