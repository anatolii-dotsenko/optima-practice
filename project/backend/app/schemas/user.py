"""User data transfer objects (DTOs)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Shared user attributes."""

    email: EmailStr = Field(..., description="User email address", example="user@example.com")
    full_name: str = Field(
        ..., min_length=2, max_length=100, description="User full name", example="Ivan Kovalenko"
    )


class UserResponse(UserBase):
    """User response schema returned to clients. Never exposes password hash."""

    id: int = Field(..., description="Unique user identifier", example=1)
    is_active: bool = Field(..., description="Account active status", example=True)
    created_at: datetime = Field(..., description="Timestamp when account was created")

    model_config = ConfigDict(from_attributes=True)
