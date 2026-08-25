"""
Central fraud detection rules and thresholds.

Keep configurable thresholds here instead of hard-coding them
inside individual fraud detectors.
"""

from typing import Any, Dict


# ---------------------------------------------------------------------------
# Fraud scoring thresholds
# ---------------------------------------------------------------------------

FRAUD_THRESHOLDS = {
    "LOW": 0.30,
    "MEDIUM": 0.60,
    "HIGH": 0.80,
}


# ---------------------------------------------------------------------------
# Detector weights
# ---------------------------------------------------------------------------

DETECTOR_WEIGHTS = {
    "anomaly": 0.15,
    "unbundling": 0.20,
    "duplicate_charge": 0.25,
    "timeline": 0.15,
    "clinical_billing_mismatch": 0.25,
}


# ---------------------------------------------------------------------------
# Detection thresholds
# ---------------------------------------------------------------------------

ANOMALY_RULES = {
    "high_amount": 100000.0,
    "very_high_amount": 250000.0,
    "amount_multiplier": 3.0,
}


UNBUNDLING_RULES = {
    "same_day_procedure_limit": 2,
}


DUPLICATE_RULES = {
    "same_procedure_same_date": True,
    "same_procedure_same_amount": True,
}


TIMELINE_RULES = {
    "discharge_before_admission": True,
    "procedure_before_admission": True,
    "procedure_after_discharge": True,
}


CLINICAL_BILLING_RULES = {
    "require_diagnosis_for_procedure": True,
    "mismatch_confidence_threshold": 0.70,
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def risk_level_from_score(score: float) -> str:
    """
    Convert fraud score into the evaluation risk vocabulary:
    LOW, MEDIUM, HIGH.
    """

    score = max(
        0.0,
        min(1.0, float(score)),
    )

    if score >= FRAUD_THRESHOLDS["HIGH"]:
        return "HIGH"

    if score >= FRAUD_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"

    return "LOW"


def clamp_score(score: float) -> float:
    """
    Ensure fraud score stays between 0 and 1.
    """

    return max(0.0, min(1.0, float(score)))


def make_finding(
    detector: str,
    detected: bool,
    confidence: float,
    severity: str,
    reason: str,
    evidence: Any = None,
) -> Dict[str, Any]:
    """
    Standard finding format used by all fraud detectors.
    """

    return {
        "detector": detector,
        "detected": detected,
        "confidence": clamp_score(confidence),
        "severity": severity,
        "reason": reason,
        "evidence": evidence or [],
    }