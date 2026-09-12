from typing import Optional, Sequence

from app.core.errors import CategoryNotFoundError, MenuItemNotFoundError
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.repositories.menu_repository import CategoryRepository, MenuItemRepository
from app.schemas.menu import (
    CategoryCreate,
    CategoryUpdate,
    MenuItemCreate,
    MenuItemUpdate,
)


class MenuService:
    """Pure domain service for Menu and Category business logic.
    Strictly zero imports from web frameworks (FastAPI / Starlette).
    """

    def __init__(
        self,
        category_repo: CategoryRepository,
        menu_item_repo: MenuItemRepository,
    ) -> None:
        self.category_repo = category_repo
        self.menu_item_repo = menu_item_repo

    def list_categories(self) -> Sequence[Category]:
        return self.category_repo.list_active()

    def get_category_by_id(self, category_id: int) -> Category:
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(category_id)
        return category

    def create_category(self, data: CategoryCreate) -> Category:
        category = Category(
            name=data.name,
            slug=data.slug,
            description=data.description,
            display_order=data.display_order,
            is_active=True,
        )
        return self.category_repo.create(category)

    def update_category(self, category_id: int, data: CategoryUpdate) -> Category:
        category = self.get_category_by_id(category_id)
        update_dict = data.model_dump(exclude_unset=True)
        return self.category_repo.update(category, update_dict)

    def delete_category(self, category_id: int) -> None:
        category = self.get_category_by_id(category_id)
        self.category_repo.delete(category)

    def list_menu_items(
        self,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        available_only: bool = True,
    ) -> Sequence[MenuItem]:
        if category_id is not None:
            self.get_category_by_id(category_id)
        return self.menu_item_repo.list_items(
            category_id=category_id,
            search=search,
            available_only=available_only,
        )

    def get_menu_item_by_id(self, item_id: int) -> MenuItem:
        item = self.menu_item_repo.get_by_id(item_id)
        if not item:
            raise MenuItemNotFoundError(item_id)
        return item

    def create_menu_item(self, data: MenuItemCreate) -> MenuItem:
        # Validate category exists
        self.get_category_by_id(data.category_id)

        item = MenuItem(
            category_id=data.category_id,
            name=data.name,
            description=data.description,
            price=data.price,
            image_url=data.image_url,
            is_available=data.is_available,
        )
        return self.menu_item_repo.create(item)

    def update_menu_item(self, item_id: int, data: MenuItemUpdate) -> MenuItem:
        item = self.get_menu_item_by_id(item_id)
        update_dict = data.model_dump(exclude_unset=True)
        if "category_id" in update_dict and update_dict["category_id"] is not None:
            self.get_category_by_id(update_dict["category_id"])
        return self.menu_item_repo.update(item, update_dict)

    def delete_menu_item(self, item_id: int) -> None:
        item = self.get_menu_item_by_id(item_id)
        self.menu_item_repo.delete(item)

    def toggle_item_availability(self, item_id: int, is_available: bool) -> MenuItem:
        item = self.get_menu_item_by_id(item_id)
        return self.menu_item_repo.update(item, {"is_available": is_available})
