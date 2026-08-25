from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """
    Individual validation or processing error.
    """

    field: str | None = None

    message: str

    code: str


class ErrorResponse(BaseModel):
    """
    Standard API error response.
    """

    success: bool = False

    error_code: str

    message: str

    details: list[ErrorDetail] = Field(
        default_factory=list,
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    trace_id: str | None = None