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


class CategoryNotFoundError(DomainException):
    """Raised when a requested category does not exist."""

    def __init__(self, category_id: int) -> None:
        super().__init__(
            message=f"Category with ID {category_id} not found",
            code="category_not_found",
            status_code=404,
            details={"category_id": category_id},
        )


class MenuItemNotFoundError(DomainException):
    """Raised when a requested menu item does not exist."""

    def __init__(self, item_id: int) -> None:
        super().__init__(
            message=f"Menu item with ID {item_id} not found",
            code="menu_item_not_found",
            status_code=404,
            details={"menu_item_id": item_id},
        )


class MenuItemUnavailableError(DomainException):
    """Raised when an item in the cart is currently out of stock / unavailable."""

    def __init__(self, item_name: str, item_id: int) -> None:
        super().__init__(
            message=f"Item '{item_name}' is currently not available for ordering",
            code="menu_item_unavailable",
            status_code=400,
            details={"menu_item_id": item_id, "item_name": item_name},
        )


class OrderNotFoundError(DomainException):
    """Raised when a requested order does not exist."""

    def __init__(self, order_id: int) -> None:
        super().__init__(
            message=f"Order with ID {order_id} not found",
            code="order_not_found",
            status_code=404,
            details={"order_id": order_id},
        )


class InvalidOrderStateError(DomainException):
    """Raised when an order transition violates the state machine rules (ADR-0006)."""

    def __init__(self, current_status: str, target_status: str) -> None:
        super().__init__(
            message=f"Cannot transition order from '{current_status}' to '{target_status}'",
            code="invalid_state_transition",
            status_code=400,
            details={"current_status": current_status, "target_status": target_status},
        )
