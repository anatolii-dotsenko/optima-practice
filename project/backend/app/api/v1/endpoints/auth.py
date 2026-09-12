"""Authentication endpoints for registration, login, and profile access."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service, get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.error import ErrorResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user profile with hashed password credentials.",
    responses={
        201: {"model": UserResponse, "description": "User created successfully"},
        409: {"model": ErrorResponse, "description": "Email address is already registered"},
        422: {"model": ErrorResponse, "description": "Payload validation error"},
    },
)
def register(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new customer or staff user."""
    return auth_service.register(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and obtain JWT token",
    description="Validates email and password, returning a Bearer JWT access token.",
    responses={
        200: {"model": TokenResponse, "description": "Authentication successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials provided"},
        403: {"model": ErrorResponse, "description": "Account is inactive"},
        422: {"model": ErrorResponse, "description": "Payload validation error"},
    },
)
def login(
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate with email and password to receive an access token."""
    return auth_service.authenticate(data)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Fetches authenticated user information using Bearer token.",
    responses={
        200: {"model": UserResponse, "description": "Current user profile"},
        401: {"model": ErrorResponse, "description": "Missing, invalid, or expired token"},
    },
)
def get_me(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Retrieve profile data for the currently authenticated user."""
    return current_user
