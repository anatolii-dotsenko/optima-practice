from typing import List, Optional, Sequence

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.menu_item import MenuItem


class CategoryRepository:
    """Handles persistence operations for Category entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.execute(
            select(Category).where(Category.id == category_id)
        ).scalar_one_or_none()

    def get_by_slug(self, slug: str) -> Optional[Category]:
        return self.db.execute(select(Category).where(Category.slug == slug)).scalar_one_or_none()

    def list_active(self) -> Sequence[Category]:
        stmt = (
            select(Category)
            .where(Category.is_active.is_(True))
            .order_by(Category.display_order.asc(), Category.name.asc())
        )
        return self.db.execute(stmt).scalars().all()

    def create(self, category: Category) -> Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category


class MenuItemRepository:
    """Handles persistence operations for MenuItem entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, item_id: int) -> Optional[MenuItem]:
        return self.db.execute(select(MenuItem).where(MenuItem.id == item_id)).scalar_one_or_none()

    def get_by_ids(self, item_ids: List[int]) -> Sequence[MenuItem]:
        if not item_ids:
            return []
        stmt = select(MenuItem).where(MenuItem.id.in_(item_ids))
        return self.db.execute(stmt).scalars().all()

    def list_items(
        self,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        available_only: bool = False,
    ) -> Sequence[MenuItem]:
        stmt = select(MenuItem)
        if category_id is not None:
            stmt = stmt.where(MenuItem.category_id == category_id)
        if available_only:
            stmt = stmt.where(MenuItem.is_available.is_(True))
        if search:
            pattern = f"%{search}%"
            # Support both PostgreSQL (case-insensitive ilike)
            # and SQLite (multiple like patterns for Cyrillic)
            stmt = stmt.where(
                or_(
                    MenuItem.name.ilike(pattern),
                    MenuItem.description.ilike(pattern),
                    MenuItem.name.like(f"%{search.lower()}%"),
                    MenuItem.name.like(f"%{search.capitalize()}%"),
                    MenuItem.name.like(f"%{search.title()}%"),
                    MenuItem.description.like(f"%{search.lower()}%"),
                )
            )
        stmt = stmt.order_by(MenuItem.category_id.asc(), MenuItem.name.asc())
        return self.db.execute(stmt).scalars().all()

    def create(self, item: MenuItem) -> MenuItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
