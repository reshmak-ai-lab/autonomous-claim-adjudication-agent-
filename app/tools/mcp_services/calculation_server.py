from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from app.tools.calculation_tools import CalculationTools


app = FastAPI(
    title="Claim Adjudication Calculation Tool Server",
    version="1.0.0",
)


class CopayRequest(BaseModel):
    eligible_amount: float
    copay_percentage: float


class DeductibleRequest(BaseModel):
    eligible_amount: float
    deductible: float


class ProportionalDeductionRequest(BaseModel):
    actual_room_rent: float
    eligible_room_rent: float
    total_bill: float


class FinalPayableRequest(BaseModel):
    claimed_amount: float
    non_payable_amount: float = 0
    deductible: float = 0
    copay_percentage: float = 0


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "healthy": True,
        "service": "calculation_tool_server",
    }


@app.post("/tools/calculate-copay")
def calculate_copay(
    request: CopayRequest,
) -> dict[str, Any]:

    return CalculationTools.calculate_copay(
        eligible_amount=request.eligible_amount,
        copay_percentage=request.copay_percentage,
    )


@app.post("/tools/calculate-deductible")
def calculate_deductible(
    request: DeductibleRequest,
) -> dict[str, Any]:

    return CalculationTools.calculate_deductible(
        eligible_amount=request.eligible_amount,
        deductible=request.deductible,
    )


@app.post("/tools/calculate-proportional-deduction")
def calculate_proportional_deduction(
    request: ProportionalDeductionRequest,
) -> dict[str, Any]:

    return CalculationTools.calculate_proportional_deduction(
        actual_room_rent=request.actual_room_rent,
        eligible_room_rent=request.eligible_room_rent,
        total_bill=request.total_bill,
    )


@app.post("/tools/calculate-final-payable")
def calculate_final_payable(
    request: FinalPayableRequest,
) -> dict[str, Any]:

    return CalculationTools.calculate_final_payable(
        claimed_amount=request.claimed_amount,
        non_payable_amount=request.non_payable_amount,
        deductible=request.deductible,
        copay_percentage=request.copay_percentage,
    )