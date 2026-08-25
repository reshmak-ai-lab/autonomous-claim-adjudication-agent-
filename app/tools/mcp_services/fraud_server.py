from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(
    title="Fraud Analytics MCP Service",
    version="1.0.0",
)


class FraudRequest(BaseModel):
    transaction_id: str = Field(..., min_length=1)
    amount: float = Field(..., ge=0)
    merchant_id: str = Field(..., min_length=1)
    country: str = ""


class FraudResponse(BaseModel):
    source: str
    data: dict[str, Any]


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "fraud_analytics_mcp",
    }


@app.post(
    "/tools/analyze-fraud",
    response_model=FraudResponse,
)
def analyze_fraud(request: FraudRequest) -> FraudResponse:

    risk_score = 0.25

    # High-value transaction
    if request.amount >= 5000:
        risk_score = 0.75

    # Unusual country
    country = (request.country or "").strip().lower()

    if country and country not in {
        "india",
        "us",
        "uk",
    }:
        risk_score = max(risk_score, 0.80)

    if risk_score >= 0.80:
        risk_level = "HIGH"
    elif risk_score >= 0.50:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    fraud_detected = risk_score >= 0.80

    return FraudResponse(
        source="fraud_analytics_mcp",
        data={
            "service": "fraud_analytics",
            "transaction_id": request.transaction_id,
            "merchant_id": request.merchant_id,
            "amount": request.amount,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "fraud_detected": fraud_detected,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        },
    )