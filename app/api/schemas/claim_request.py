from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PatientInfo(BaseModel):
    """
    Basic patient information.

    Sensitive identifiers should be redacted before
    reaching downstream LLM/agent components.
    """

    model_config = ConfigDict(extra="allow")

    patient_id: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    name: str | None = Field(
        default=None,
        max_length=200,
    )

    age: int | None = Field(
        default=None,
        ge=0,
        le=120,
    )

    gender: str | None = None


class AdmissionInfo(BaseModel):
    """
    Hospital admission information.
    """

    admission_date: str
    expected_discharge_date: str | None = None

    emergency: bool = False


class ClaimRequest(BaseModel):
    """
    Input contract for claim adjudication.
    """

    model_config = ConfigDict(
        extra="allow",
        str_strip_whitespace=True,
    )

    claim_id: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    patient_id: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    policy_id: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    hospital_id: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    requested_amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
    )

    claim_type: str = Field(
        default="cashless_pre_authorization",
    )

    patient: PatientInfo | None = None

    admission: AdmissionInfo | None = None

    diagnosis: str | None = None

    procedure: str | None = None

    document_ids: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )