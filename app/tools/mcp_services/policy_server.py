from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from app.tools.policy_tools import PolicyTools


app = FastAPI(
    title="Claim Adjudication Policy Tool Server",
    version="1.0.0",
)

policy_tools = PolicyTools()


class PolicySearchRequest(BaseModel):
    query: str
    max_results: int = 5


class PolicyDocumentRequest(BaseModel):
    filename: str


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "healthy": True,
        "service": "policy_tool_server",
    }


@app.post("/tools/search-policy")
def search_policy(
    request: PolicySearchRequest,
) -> dict[str, Any]:

    results = policy_tools.search_policy(
        query=request.query,
        max_results=request.max_results,
    )

    return {
        "success": True,
        "tool": "search_policy",
        "query": request.query,
        "results": results,
    }


@app.post("/tools/get-policy")
def get_policy(
    request: PolicyDocumentRequest,
) -> dict[str, Any]:

    return policy_tools.get_policy_document(
        request.filename
    )