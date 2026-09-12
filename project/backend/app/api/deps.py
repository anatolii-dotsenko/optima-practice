"""FastAPI dependency injection wiring."""

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import DomainException
from app.core.security import decode_access_token
from app.repositories.menu_repository import CategoryRepository, MenuItemRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.menu_service import MenuService
from app.services.order_service import OrderService

security_bearer = HTTPBearer(auto_error=False)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency provider for AuthService."""
    user_repo = UserRepository(db)
    return AuthService(user_repo)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Extract, decode, and validate the JWT Bearer token to return the current user."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "unauthorized",
                "message": "Missing authentication token",
                "details": None,
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "unauthorized",
                "message": "Invalid or expired access token",
                "details": None,
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return auth_service.get_current_user_profile(user_id)
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


def get_current_admin_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Verify that the current user possesses superuser/admin privileges."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "forbidden",
                "message": "Admin privileges required for this operation",
                "details": None,
            },
        )
    return current_user


def get_menu_service(db: Session = Depends(get_db)) -> MenuService:
    """Dependency provider for MenuService."""
    category_repo = CategoryRepository(db)
    menu_item_repo = MenuItemRepository(db)
    return MenuService(category_repo, menu_item_repo)


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """Dependency provider for OrderService."""
    order_repo = OrderRepository(db)
    menu_item_repo = MenuItemRepository(db)
    return OrderService(order_repo, menu_item_repo)
