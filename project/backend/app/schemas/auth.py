"""Authentication request and response schemas."""

import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """User registration payload."""

    email: EmailStr = Field(..., description="Unique email address", example="user@example.com")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be at least 8 characters and contain both letters and digits",
        example="SecurePass123!",
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the user",
        example="Ivan Kovalenko",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v


class LoginRequest(BaseModel):
    """User login payload."""

    email: EmailStr = Field(..., description="User email address", example="user@example.com")
    password: str = Field(..., description="Account password", example="SecurePass123!")


class TokenResponse(BaseModel):
    """Authentication token response payload."""

    access_token: str = Field(..., description="JWT Bearer access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token lifespan in seconds", example=3600)
