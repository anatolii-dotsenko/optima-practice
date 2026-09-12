"""Authentication and user management domain service.

Strict layer boundary rule: This module MUST NOT import web frameworks
(FastAPI, Starlette, etc.).
"""

from app.core.config import settings
from app.core.errors import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserInactiveError,
    UserNotFoundError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse


class AuthService:
    """Domain service encapsulating registration and authentication logic."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def register(self, data: RegisterRequest) -> UserResponse:
        """Register a new user account.

        Raises:
            UserAlreadyExistsError: If the email is already in use.
        """
        existing_user = self.user_repo.get_by_email(data.email)
        if existing_user is not None:
            raise UserAlreadyExistsError(email=data.email)

        hashed_password = hash_password(data.password)
        user = self.user_repo.create_user(
            email=data.email,
            hashed_password=hashed_password,
            full_name=data.full_name,
        )

        return UserResponse.model_validate(user)

    def authenticate(self, data: LoginRequest) -> TokenResponse:
        """Authenticate user credentials and issue an access token.

        Raises:
            InvalidCredentialsError: If email or password is incorrect.
            UserInactiveError: If the account has been disabled.
        """
        user = self.user_repo.get_by_email(data.email)
        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UserInactiveError()

        expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        access_token = create_access_token(
            subject=user.id,
            extra_claims={"email": user.email},
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in_seconds,
        )

    def get_current_user_profile(self, user_id: int) -> UserResponse:
        """Retrieve user profile by primary identifier.

        Raises:
            UserNotFoundError: If no matching user is found.
            UserInactiveError: If the user is marked inactive.
        """
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(identifier=str(user_id))

        if not user.is_active:
            raise UserInactiveError()

        return UserResponse.model_validate(user)
