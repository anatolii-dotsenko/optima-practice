"""Unit tests for AuthService with isolated repository mocks."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.core.errors import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserInactiveError,
)
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


@pytest.fixture
def mock_user_repo() -> MagicMock:
    """Provide a mock UserRepository for isolation."""
    return MagicMock(spec=UserRepository)


@pytest.fixture
def auth_service(mock_user_repo: MagicMock) -> AuthService:
    """Provide AuthService injected with the mock repository."""
    return AuthService(user_repo=mock_user_repo)


def test_register_user_success(auth_service: AuthService, mock_user_repo: MagicMock) -> None:
    """Arrange, Act, Assert: Verify successful user registration."""
    # Arrange
    req = RegisterRequest(
        email="newuser@example.com",
        password="SecurePassword123!",
        full_name="New User",
    )
    mock_user_repo.get_by_email.return_value = None

    mock_created = User(
        id=10,
        email="newuser@example.com",
        hashed_password="hashed_placeholder",
        full_name="New User",
        is_active=True,
        is_superuser=False,
    )
    mock_created.created_at = datetime.now(timezone.utc)
    mock_created.updated_at = datetime.now(timezone.utc)
    mock_user_repo.create_user.return_value = mock_created

    # Act
    res = auth_service.register(req)

    # Assert
    assert res.id == 10
    assert res.email == "newuser@example.com"
    assert res.full_name == "New User"
    assert res.is_active is True
    mock_user_repo.get_by_email.assert_called_once_with("newuser@example.com")
    mock_user_repo.create_user.assert_called_once()


def test_register_duplicate_email_raises_conflict(
    auth_service: AuthService, mock_user_repo: MagicMock
) -> None:
    """Verify registration with existing email raises UserAlreadyExistsError."""
    # Arrange
    req = RegisterRequest(
        email="existing@example.com",
        password="SecurePassword123!",
        full_name="Duplicate User",
    )
    mock_user_repo.get_by_email.return_value = User(id=1, email="existing@example.com")

    # Act & Assert
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        auth_service.register(req)

    assert exc_info.value.code == "conflict"
    assert exc_info.value.status_code == 409
    mock_user_repo.create_user.assert_not_called()


def test_authenticate_success(auth_service: AuthService, mock_user_repo: MagicMock) -> None:
    """Arrange, Act, Assert: Verify successful credential authentication."""
    # Arrange
    plain = "ValidPassword123!"
    hashed = hash_password(plain)
    user = User(id=5, email="valid@example.com", hashed_password=hashed, is_active=True)
    mock_user_repo.get_by_email.return_value = user

    req = LoginRequest(email="valid@example.com", password=plain)

    # Act
    token_res = auth_service.authenticate(req)

    # Assert
    assert token_res.access_token is not None
    assert token_res.token_type == "bearer"
    assert token_res.expires_in > 0


def test_authenticate_invalid_password_raises_unauthorized(
    auth_service: AuthService, mock_user_repo: MagicMock
) -> None:
    """Arrange, Act, Assert: Verify incorrect password raises InvalidCredentialsError."""
    # Arrange
    user = User(
        id=5,
        email="valid@example.com",
        hashed_password=hash_password("CorrectPass123!"),
        is_active=True,
    )
    mock_user_repo.get_by_email.return_value = user
    req = LoginRequest(email="valid@example.com", password="WrongPassword123!")

    # Act & Assert
    with pytest.raises(InvalidCredentialsError) as exc_info:
        auth_service.authenticate(req)

    assert exc_info.value.code == "unauthorized"
    assert exc_info.value.status_code == 401


def test_authenticate_user_not_found_raises_unauthorized(
    auth_service: AuthService, mock_user_repo: MagicMock
) -> None:
    """Arrange, Act, Assert: Verify non-existent email raises InvalidCredentialsError."""
    # Arrange
    mock_user_repo.get_by_email.return_value = None
    req = LoginRequest(email="nonexistent@example.com", password="SomePassword123!")

    # Act & Assert
    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate(req)


def test_authenticate_inactive_user_raises_forbidden(
    auth_service: AuthService, mock_user_repo: MagicMock
) -> None:
    """Arrange, Act, Assert: Verify disabled user raises UserInactiveError."""
    # Arrange
    plain = "Pass12345!"
    user = User(
        id=7,
        email="inactive@example.com",
        hashed_password=hash_password(plain),
        is_active=False,
    )
    mock_user_repo.get_by_email.return_value = user
    req = LoginRequest(email="inactive@example.com", password=plain)

    # Act & Assert
    with pytest.raises(UserInactiveError) as exc_info:
        auth_service.authenticate(req)

    assert exc_info.value.code == "forbidden"
    assert exc_info.value.status_code == 403
