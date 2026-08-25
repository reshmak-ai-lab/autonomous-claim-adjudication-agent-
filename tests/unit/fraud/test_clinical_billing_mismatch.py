from app.fraud.clinical_billing_mismatch import (
    ClinicalBillingMismatchDetector,
    detect_clinical_billing_mismatch,
)


def test_detector_can_be_created():
    detector = ClinicalBillingMismatchDetector()

    assert detector is not None


def test_matching_appendectomy_does_not_flag_mismatch():
    detector = ClinicalBillingMismatchDetector()

    diagnosis_data = {
        "diagnosis": "Acute appendicitis"
    }

    clinical_data = {
        "clinical_notes": "Patient has acute appendicitis."
    }

    billing_items = [
        {
            "procedure_name": "Appendectomy",
            "amount": 30000,
        }
    ]

    result = detector.detect(
        diagnosis_data=diagnosis_data,
        clinical_data=clinical_data,
        billing_items=billing_items,
    )

    assert result is not None
    assert result["detected"] is False
    assert result["severity"] == "NONE"


def test_appendectomy_without_appendicitis_flags_mismatch():
    detector = ClinicalBillingMismatchDetector()

    diagnosis_data = {
        "diagnosis": "Common cold"
    }

    clinical_data = {
        "clinical_notes": "Patient has fever and cough."
    }

    billing_items = [
        {
            "procedure_name": "Appendectomy",
            "amount": 30000,
        }
    ]

    result = detector.detect(
        diagnosis_data=diagnosis_data,
        clinical_data=clinical_data,
        billing_items=billing_items,
    )

    assert result is not None
    assert result["detected"] is True
    assert result["severity"] == "MEDIUM"
    assert len(result["evidence"]) == 1


def test_matching_cholecystectomy_does_not_flag_mismatch():
    detector = ClinicalBillingMismatchDetector()

    diagnosis_data = {
        "diagnosis": "Acute cholecystitis"
    }

    clinical_data = {
        "clinical_notes": "Gallbladder inflammation with gallstones."
    }

    billing_items = [
        {
            "procedure_name": "Cholecystectomy",
            "amount": 50000,
        }
    ]

    result = detector.detect(
        diagnosis_data=diagnosis_data,
        clinical_data=clinical_data,
        billing_items=billing_items,
    )

    assert result["detected"] is False


def test_cholecystectomy_without_supporting_clinical_data_flags_mismatch():
    detector = ClinicalBillingMismatchDetector()

    diagnosis_data = {
        "diagnosis": "Migraine"
    }

    clinical_data = {
        "clinical_notes": "Patient reports headache."
    }

    billing_items = [
        {
            "procedure_name": "Cholecystectomy",
            "amount": 50000,
        }
    ]

    result = detector.detect(
        diagnosis_data=diagnosis_data,
        clinical_data=clinical_data,
        billing_items=billing_items,
    )

    assert result["detected"] is True
    assert len(result["evidence"]) == 1


def test_matching_ultrasound_does_not_flag_mismatch():
    detector = ClinicalBillingMismatchDetector()

    diagnosis_data = {
        "diagnosis": "Abdominal pain"
    }

    clinical_data = {
        "clinical_notes": "Patient has abdominal discomfort."
    }

    billing_items = [
        {
            "procedure_name": "Ultrasound abdomen",
            "amount": 5000,
        }
    ]

    result = detector.detect(
        diagnosis_data=diagnosis_data,
        clinical_data=clinical_data,
        billing_items=billing_items,
    )

    assert result["detected"] is False


def test_ct_scan_without_supporting_clinical_information_flags_mismatch():
    detector = ClinicalBillingMismatchDetector()

    diagnosis_data = {
        "diagnosis": "Routine fever"
    }

    clinical_data = {
        "clinical_notes": "Mild fever."
    }

    billing_items = [
        {
            "procedure_name": "CT scan",
            "amount": 15000,
        }
    ]

    result = detector.detect(
        diagnosis_data=diagnosis_data,
        clinical_data=clinical_data,
        billing_items=billing_items,
    )

    assert result["detected"] is True


def test_mri_with_supporting_clinical_information_does_not_flag():
    detector = ClinicalBillingMismatchDetector()

    diagnosis_data = {
        "diagnosis": "Knee lesion"
    }

    clinical_data = {
        "clinical_notes": "MRI required for evaluation of knee lesion."
    }

    billing_items = [
        {
            "procedure_name": "MRI",
            "amount": 12000,
        }
    ]

    result = detector.detect(
        diagnosis_data=diagnosis_data,
        clinical_data=clinical_data,
        billing_items=billing_items,
    )

    assert result["detected"] is False


def test_unknown_procedure_is_ignored():
    detector = ClinicalBillingMismatchDetector()

    diagnosis_data = {
        "diagnosis": "Common cold"
    }

    clinical_data = {
        "clinical_notes": "Fever and cough."
    }

    billing_items = [
        {
            "procedure_name": "General consultation",
            "amount": 2000,
        }
    ]

    result = detector.detect(
        diagnosis_data=diagnosis_data,
        clinical_data=clinical_data,
        billing_items=billing_items,
    )

    assert result["detected"] is False


def test_empty_clinical_information():
    detector = ClinicalBillingMismatchDetector()

    result = detector.detect(
        diagnosis_data={},
        clinical_data={},
        billing_items=[
            {
                "procedure_name": "Appendectomy",
                "amount": 30000,
            }
        ],
    )

    assert result is not None
    assert result["detected"] is False
    assert result["severity"] == "UNKNOWN"


def test_empty_billing_items():
    detector = ClinicalBillingMismatchDetector()

    result = detector.detect(
        diagnosis_data={
            "diagnosis": "Acute appendicitis"
        },
        clinical_data={
            "clinical_notes": "Appendicitis confirmed."
        },
        billing_items=[],
    )

    assert result is not None
    assert result["detected"] is False


def test_multiple_mismatches_are_detected():
    detector = ClinicalBillingMismatchDetector()

    diagnosis_data = {
        "diagnosis": "Common cold"
    }

    clinical_data = {
        "clinical_notes": "Fever and cough."
    }

    billing_items = [
        {
            "procedure_name": "Appendectomy",
            "amount": 30000,
        },
        {
            "procedure_name": "Cholecystectomy",
            "amount": 50000,
        },
    ]

    result = detector.detect(
        diagnosis_data=diagnosis_data,
        clinical_data=clinical_data,
        billing_items=billing_items,
    )

    assert result["detected"] is True
    assert len(result["evidence"]) == 2


def test_procedure_code_can_be_used():
    detector = ClinicalBillingMismatchDetector()

    diagnosis_data = {
        "diagnosis": "Appendicitis"
    }

    clinical_data = {
        "notes": "Appendix inflammation confirmed."
    }

    billing_items = [
        {
            "procedure_code": "appendectomy",
            "amount": 30000,
        }
    ]

    result = detector.detect(
        diagnosis_data=diagnosis_data,
        clinical_data=clinical_data,
        billing_items=billing_items,
    )

    assert result["detected"] is False


def test_function_wrapper_works():
    result = detect_clinical_billing_mismatch(
        diagnosis_data={
            "diagnosis": "Acute appendicitis"
        },
        clinical_data={
            "notes": "Appendix inflammation."
        },
        billing_items=[
            {
                "procedure_name": "Appendectomy",
                "amount": 30000,
            }
        ],
    )

    assert result is not None
    assert result["detected"] is False