"""Pytest fixtures for unit and integration testing."""

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.security import hash_password
from app.main import app
from app.models.base import Base
from app.models.user import User

# In-memory SQLite engine for fast, isolated tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create fresh database tables for each test and provide a session."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a TestClient with database dependency overridden."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_user(db_session: Session) -> User:
    """Pre-populate a registered test user in the database."""
    user = User(
        email="existing@example.com",
        hashed_password=hash_password("ExistingPassword123!"),
        full_name="Existing User",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def inactive_user(db_session: Session) -> User:
    """Pre-populate an inactive test user in the database."""
    user = User(
        email="inactive@example.com",
        hashed_password=hash_password("InactivePassword123!"),
        full_name="Inactive User",
        is_active=False,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(sample_user: User) -> dict:
    """Generate valid Bearer Authorization headers for sample_user."""
    from app.core.security import create_access_token

    token = create_access_token(subject=str(sample_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def sample_category(db_session: Session):
    """Pre-populate a test category."""
    from app.models.category import Category

    cat = Category(
        name="Кава",
        slug="coffee",
        description="Кавові напої",
        display_order=1,
        is_active=True,
    )
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


@pytest.fixture(scope="function")
def sample_menu_item(db_session: Session, sample_category):
    """Pre-populate an available menu item."""
    from decimal import Decimal

    from app.models.menu_item import MenuItem

    item = MenuItem(
        category_id=sample_category.id,
        name="Капучино",
        description="Класичний капучино",
        price=Decimal("65.00"),
        image_url="https://example.com/cappuccino.jpg",
        is_available=True,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture(scope="function")
def unavailable_menu_item(db_session: Session, sample_category):
    """Pre-populate an unavailable menu item."""
    from decimal import Decimal

    from app.models.menu_item import MenuItem

    item = MenuItem(
        category_id=sample_category.id,
        name="Матча Лате",
        description="Японська матча",
        price=Decimal("80.00"),
        image_url="https://example.com/matcha.jpg",
        is_available=False,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item
