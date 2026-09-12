"""Unit tests for core security utilities (hashing and JWT tokens)."""

from datetime import timedelta

import jwt
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_produces_bcrypt_hash() -> None:
    """Arrange, Act, Assert: Verify that hash_password returns a non-empty, distinct bcrypt hash."""
    # Arrange
    plain = "MySecretPass123!"

    # Act
    hashed1 = hash_password(plain)
    hashed2 = hash_password(plain)

    # Assert
    assert hashed1 != plain
    assert hashed1.startswith("$2b$")
    assert hashed1 != hashed2  # Distinct salts per call


def test_verify_password_success_and_failure() -> None:
    """Arrange, Act, Assert: Verify matching password succeeds and non-matching fails."""
    # Arrange
    plain = "CorrectPassword123!"
    hashed = hash_password(plain)

    # Act & Assert (success scenario)
    assert verify_password(plain, hashed) is True

    # Act & Assert (invalid input scenario)
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False


def test_create_and_decode_access_token_success() -> None:
    """Verify JWT token encoding and decoding extracts subject and extra claims."""
    # Arrange
    user_id = 42
    extra = {"email": "test@example.com"}

    # Act
    token = create_access_token(subject=user_id, extra_claims=extra)
    payload = decode_access_token(token)

    # Assert
    assert payload["sub"] == "42"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload
    assert "iat" in payload


def test_decode_access_token_expired_raises_error() -> None:
    """Arrange, Act, Assert: Verify expired token raises ExpiredSignatureError."""
    # Arrange: token created with negative expiry (already in the past)
    token = create_access_token(subject=1, expires_delta=timedelta(seconds=-10))

    # Act & Assert
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_decode_access_token_invalid_signature_raises_error() -> None:
    """Arrange, Act, Assert: Tampering with token payload raises InvalidSignatureError."""
    # Arrange
    token = create_access_token(subject=1)
    tampered_token = token[:-5] + "XXXXX"

    # Act & Assert
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(tampered_token)
