"""User repository implementing persistence queries for users."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository handling database queries for User entities."""

    def __init__(self, db: Session) -> None:
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Query user by email address (case-insensitive)."""
        stmt = select(User).where(User.email == email.strip().lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def create_user(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        """Instantiate and persist a new User entity."""
        user = User(
            email=email.strip().lower(),
            hashed_password=hashed_password,
            full_name=full_name.strip(),
            is_active=is_active,
            is_superuser=is_superuser,
        )
        return self.create(user)
