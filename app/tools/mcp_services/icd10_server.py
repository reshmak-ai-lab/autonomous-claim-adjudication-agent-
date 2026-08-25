from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from app.tools.icd10_tools import ICD10Tools


app = FastAPI(
    title="Claim Adjudication ICD-10 Tool Server",
    version="1.0.0",
)

icd10_tools = ICD10Tools()


class ICD10LookupRequest(BaseModel):
    code: str


class DiagnosisSearchRequest(BaseModel):
    diagnosis: str


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "healthy": True,
        "service": "icd10_tool_server",
    }


@app.post("/tools/lookup-icd10")
def lookup_icd10(
    request: ICD10LookupRequest,
) -> dict[str, Any]:

    return icd10_tools.lookup_code(
        request.code
    )


@app.post("/tools/search-diagnosis")
def search_diagnosis(
    request: DiagnosisSearchRequest,
) -> dict[str, Any]:

    return {
        "success": True,
        "results": icd10_tools.search_diagnosis(
            request.diagnosis
        ),
    }