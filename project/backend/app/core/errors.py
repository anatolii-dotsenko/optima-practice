"""Domain exceptions and error definitions.

Services raise domain exceptions without any web framework coupling.
"""

from typing import Any, Dict, Optional


class DomainException(Exception):
    """Base domain exception with standardized error attributes."""

    def __init__(
        self,
        message: str,
        code: str = "domain_error",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class UserAlreadyExistsError(DomainException):
    """Raised when registering a user with an already registered email."""

    def __init__(self, email: str) -> None:
        super().__init__(
            message=f"User with email '{email}' already exists",
            code="conflict",
            status_code=409,
            details={"field": "email"},
        )


class InvalidCredentialsError(DomainException):
    """Raised when authentication credentials fail validation."""

    def __init__(self, message: str = "Invalid email or password") -> None:
        super().__init__(
            message=message,
            code="unauthorized",
            status_code=401,
            details=None,
        )


class UserNotFoundError(DomainException):
    """Raised when a requested user cannot be found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(
            message=f"User '{identifier}' not found",
            code="not_found",
            status_code=404,
            details={"identifier": identifier},
        )


class UserInactiveError(DomainException):
    """Raised when an inactive user attempts to authenticate."""

    def __init__(self) -> None:
        super().__init__(
            message="User account is inactive",
            code="forbidden",
            status_code=403,
            details=None,
        )
