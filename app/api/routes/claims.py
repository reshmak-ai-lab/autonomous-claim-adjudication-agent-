from fastapi import APIRouter, HTTPException

from app.api.schemas.claim_request import ClaimRequest
from app.api.schemas.claim_response import (
    ClaimResponse,
)

router = APIRouter(
    prefix="/claims",
    tags=["Claims"],
)


@router.post(
    "/adjudicate",
    response_model=ClaimResponse,
)
def adjudicate_claim(
    request: ClaimRequest,
):
    """
    Submit a claim for autonomous adjudication.
    """

    if request.requested_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Claim amount must be greater than zero.",
        )

    # Temporary response.
    # Replace this with claim_workflow.py later.

    return {
        "claim_id": request.claim_id,

        "decision": "HUMAN_REVIEW",

        "fraud": {
            "risk_level": "UNKNOWN",
            "risk_score": 0.0,
            "indicators": [],
            "duplicate_claim_detected": False,
            "clinical_billing_mismatch": False,
        },

        "policy": {
            "policy_active": True,
            "coverage_supported": False,
            "room_rent_limit": None,
            "room_rent_exceeded": False,
            "ped_applicable": False,
            "ped_waiting_period_months": None,
            "exclusions_applied": [],
            "policy_references": [],
        },

        "requested_amount": request.requested_amount,
        "approved_amount": 0,
        "total_deductions": 0,
        "deductions": [],

        "confidence_score": 0.0,

        "human_review_required": True,

        "review_reasons": [
            "Claim workflow has not yet completed."
        ],

        "evidence": [],

        "explanation": (
            "Claim received and awaiting adjudication."
        ),

        "trace_id": None,
        "processing_time_ms": 0,
    }