"""FastAPI dependency injection wiring."""

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import DomainException
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

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
