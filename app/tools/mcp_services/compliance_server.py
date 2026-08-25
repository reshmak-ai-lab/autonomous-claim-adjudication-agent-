from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(
    title="Merchant Compliance MCP Service",
    version="1.0.0",
)


class ComplianceRequest(BaseModel):
    merchant_id: str = Field(..., min_length=1)

    transaction_id: str | None = None

    amount: float = Field(
        default=0.0,
        ge=0,
    )

    country: str = ""

    query: str | None = None


class ComplianceResponse(BaseModel):
    source: str
    data: dict[str, Any]


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "merchant_compliance_mcp",
    }


@app.post(
    "/tools/check-compliance",
    response_model=ComplianceResponse,
)
def check_compliance(
    request: ComplianceRequest,
) -> ComplianceResponse:

    country = (
        request.country or ""
    ).strip().lower()

    restricted_countries = {
        "north korea",
        "iran",
        "syria",
    }

    if country in restricted_countries:

        compliant = False
        status = "NON_COMPLIANT"

        reason = (
            "Transaction originates from "
            "a restricted country."
        )

    else:

        compliant = True
        status = "COMPLIANT"

        reason = (
            "No basic compliance violation detected."
        )

    return ComplianceResponse(
        source="merchant_compliance_mcp",
        data={
            "service": "merchant_compliance",
            "merchant_id": request.merchant_id,
            "transaction_id": request.transaction_id,
            "amount": request.amount,
            "country": request.country,
            "compliant": compliant,
            "status": status,
            "reason": reason,
        },
    )