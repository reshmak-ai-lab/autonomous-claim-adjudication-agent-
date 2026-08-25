from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/policies",
    tags=["Policies"],
)


class PolicyQueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
    )


@router.get("/{policy_id}")
def get_policy(policy_id: str) -> dict:
    """
    Retrieve policy information.
    """

    # Repository/service integration will be added here.
    return {
        "policy_id": policy_id,
        "status": "active",
        "message": "Policy lookup service ready.",
    }


@router.post("/query")
def query_policy(
    request: PolicyQueryRequest,
) -> dict:
    """
    Query policy documents using the RAG layer.

    The actual implementation should call:
        app.rag.retriever
    """

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Policy question cannot be empty.",
        )

    return {
        "question": question,
        "status": "accepted",
        "message": "Policy RAG query received.",
    }