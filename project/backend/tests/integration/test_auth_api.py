"""Integration tests for authentication REST endpoints."""

from fastapi.testclient import TestClient

from app.models.user import User


def test_register_endpoint_success(client: TestClient) -> None:
    """Verify POST /api/v1/auth/register returns 201 and created user schema without password."""
    payload = {
        "email": "customer@example.com",
        "password": "CoffeePassword123!",
        "full_name": "Oksana Petrenko",
    }
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "customer@example.com"
    assert data["full_name"] == "Oksana Petrenko"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "hashed_password" not in data
    assert "password" not in data


def test_register_endpoint_duplicate_conflict(client: TestClient, sample_user: User) -> None:
    """Verify POST /api/v1/auth/register with duplicate email returns 409 Conflict."""
    payload = {
        "email": sample_user.email,
        "password": "NewPassword123!",
        "full_name": "Another Name",
    }
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409
    data = response.json()
    assert data["code"] == "conflict"
    assert "already exists" in data["message"]
    assert data["details"] == {"field": "email"}


def test_register_endpoint_invalid_email(client: TestClient) -> None:
    """Verify POST /api/v1/auth/register with malformed email returns 422."""
    payload = {
        "email": "not-an-email",
        "password": "ValidPassword123!",
        "full_name": "Test User",
    }
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "validation_failed"


def test_register_endpoint_weak_password(client: TestClient) -> None:
    """Verify POST /api/v1/auth/register with weak password (missing digits) returns 422."""
    payload = {
        "email": "test@example.com",
        "password": "onlylettersnohash",
        "full_name": "Test User",
    }
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "validation_failed"


def test_login_endpoint_success(client: TestClient, sample_user: User) -> None:
    """Verify POST /api/v1/auth/login returns 200 with JWT access token."""
    payload = {
        "email": sample_user.email,
        "password": "ExistingPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 3600


def test_login_endpoint_invalid_password(client: TestClient, sample_user: User) -> None:
    """Verify POST /api/v1/auth/login with wrong password returns 401 Unauthorized."""
    payload = {
        "email": sample_user.email,
        "password": "WrongPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "unauthorized"


def test_login_endpoint_nonexistent_user(client: TestClient) -> None:
    """Verify POST /api/v1/auth/login with unknown email returns 401 Unauthorized."""
    payload = {
        "email": "ghost@example.com",
        "password": "SomePassword123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "unauthorized"


def test_login_endpoint_inactive_user(client: TestClient, inactive_user: User) -> None:
    """Verify POST /api/v1/auth/login for inactive user returns 403 Forbidden."""
    payload = {
        "email": inactive_user.email,
        "password": "InactivePassword123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 403
    data = response.json()
    assert data["code"] == "forbidden"


def test_get_me_endpoint_authenticated(client: TestClient, sample_user: User) -> None:
    """Verify GET /api/v1/auth/me with valid Bearer token returns current user profile."""
    # Obtain token first
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": sample_user.email, "password": "ExistingPassword123!"},
    )
    token = login_res.json()["access_token"]

    # Request profile
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_user.email
    assert data["full_name"] == sample_user.full_name
    assert data["id"] == sample_user.id


def test_get_me_endpoint_unauthenticated(client: TestClient) -> None:
    """Verify GET /api/v1/auth/me without token returns 401 Unauthorized."""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "unauthorized"


def test_health_check(client: TestClient) -> None:
    """Verify GET /health returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
