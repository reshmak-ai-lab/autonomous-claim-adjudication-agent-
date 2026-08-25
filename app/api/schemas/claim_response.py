from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


DecisionType = Literal[
    "APPROVE",
    "PARTIAL_APPROVAL",
    "REJECT",
    "HUMAN_REVIEW",
]

RiskLevel = Literal[
    "LOW",
    "MEDIUM",
    "HIGH",
    "UNKNOWN",
]


class Deduction(BaseModel):
    """
    Individual claim deduction.
    """

    category: str

    amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
    )

    reason: str

    policy_reference: str | None = None


class FraudAssessment(BaseModel):
    """
    Fraud detection result.
    """

    risk_level: RiskLevel

    risk_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )

    indicators: list[str] = Field(
        default_factory=list,
    )

    duplicate_claim_detected: bool = False

    clinical_billing_mismatch: bool = False


class PolicyAssessment(BaseModel):
    """
    Policy evaluation result.
    """

    policy_active: bool

    coverage_supported: bool

    room_rent_limit: Decimal | None = None

    room_rent_exceeded: bool = False

    ped_applicable: bool = False

    ped_waiting_period_months: int | None = None

    exclusions_applied: list[str] = Field(
        default_factory=list,
    )

    policy_references: list[str] = Field(
        default_factory=list,
    )


class ClaimResponse(BaseModel):
    """
    Final structured adjudication response.
    """

    claim_id: str

    decision: DecisionType

    fraud: FraudAssessment

    policy: PolicyAssessment

    requested_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
    )

    approved_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
    )

    total_deductions: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
    )

    deductions: list[Deduction] = Field(
        default_factory=list,
    )

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )

    human_review_required: bool = False

    review_reasons: list[str] = Field(
        default_factory=list,
    )

    evidence: list[str] = Field(
        default_factory=list,
    )

    explanation: str

    trace_id: str | None = None

    processing_time_ms: float | None = Field(
        default=None,
        ge=0,
    )