from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from app.tools.tariff_tools import TariffTools


app = FastAPI(
    title="Claim Adjudication Tariff Tool Server",
    version="1.0.0",
)

tariff_tools = TariffTools()


class TariffRequest(BaseModel):
    hospital_id: str
    procedure_code: str


class ProcedureSearchRequest(BaseModel):
    procedure: str


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "healthy": True,
        "service": "tariff_tool_server",
    }


@app.post("/tools/get-tariff")
def get_tariff(
    request: TariffRequest,
) -> dict[str, Any]:

    return tariff_tools.get_tariff(
        hospital_id=request.hospital_id,
        procedure_code=request.procedure_code,
    )


@app.post("/tools/search-procedure")
def search_procedure(
    request: ProcedureSearchRequest,
) -> dict[str, Any]:

    return {
        "success": True,
        "results": tariff_tools.search_procedure(
            request.procedure
        ),
    }