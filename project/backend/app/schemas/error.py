"""Standard error response schemas."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response structure as required by engineering specifications."""

    code: str = Field(..., description="Machine-readable error code", example="validation_failed")
    message: str = Field(
        ..., description="Human-readable error explanation", example="Field validation failed"
    )
    details: Optional[Dict[str, Any]] = Field(
        None, description="Granular error metadata or field pointers"
    )
