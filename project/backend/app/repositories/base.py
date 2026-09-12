"""Base repository interface."""

from typing import Generic, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository encapsulating database queries for an entity."""

    def __init__(self, model: Type[ModelType], db: Session) -> None:
        self.model = model
        self.db = db

    def get_by_id(self, id_: int) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        return self.db.get(self.model, id_)

    def create(self, obj: ModelType) -> ModelType:
        """Persist a new entity instance."""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType) -> ModelType:
        """Commit updates to an attached entity."""
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        """Remove an entity from persistence."""
        self.db.delete(obj)
        self.db.commit()
