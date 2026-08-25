"""
Fraud detection package for the Autonomous Claim Adjudication Agent.

The package provides:
- Rule-based fraud detection
- Billing anomaly detection
- Unbundling detection
- Duplicate charge detection
- Timeline anomaly detection
- Clinical/billing mismatch detection
- Aggregated fraud scoring
"""

from .fraud_engine import FraudEngine

__all__ = ["FraudEngine"]