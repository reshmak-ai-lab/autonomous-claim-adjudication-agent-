from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="Compliance MCP Service",
    version="1.0.0",
)


class ComplianceRequest(BaseModel):
    merchant_id: str
    claim_amount: float
    policy_id: str


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "compliance_mcp",
    }


@app.post("/tools/check-compliance")
def check_compliance(
    request: ComplianceRequest,
) -> dict[str, Any]:

    violations = []

    if request.claim_amount < 0:
        violations.append(
            "Claim amount cannot be negative."
        )

    if not request.merchant_id.strip():
        violations.append(
            "Merchant ID is required."
        )

    if not request.policy_id.strip():
        violations.append(
            "Policy ID is required."
        )

    compliant = len(violations) == 0

    return {
        "source": "compliance_mcp",
        "compliant": compliant,
        "merchant_id": request.merchant_id,
        "policy_id": request.policy_id,
        "claim_amount": request.claim_amount,
        "violations": violations,
    }