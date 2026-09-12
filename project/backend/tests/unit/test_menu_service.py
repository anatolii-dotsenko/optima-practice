from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.core.errors import CategoryNotFoundError, MenuItemNotFoundError
from app.repositories.menu_repository import CategoryRepository, MenuItemRepository
from app.schemas.menu import MenuItemCreate
from app.services.menu_service import MenuService


def test_list_categories_success(db_session: Session, sample_category):
    service = MenuService(CategoryRepository(db_session), MenuItemRepository(db_session))
    categories = service.list_categories()
    assert len(categories) == 1
    assert categories[0].slug == "coffee"


def test_list_menu_items_with_filter(db_session: Session, sample_menu_item):
    service = MenuService(CategoryRepository(db_session), MenuItemRepository(db_session))
    # By category
    items = service.list_menu_items(category_id=sample_menu_item.category_id)
    assert len(items) == 1
    assert items[0].name == "Капучино"

    # By search
    found = service.list_menu_items(search="капуч")
    assert len(found) == 1

    not_found = service.list_menu_items(search="unknown")
    assert len(not_found) == 0


def test_get_menu_item_not_found(db_session: Session):
    service = MenuService(CategoryRepository(db_session), MenuItemRepository(db_session))
    with pytest.raises(MenuItemNotFoundError):
        service.get_menu_item_by_id(999999)


def test_create_menu_item_invalid_category_raises_error(db_session: Session):
    service = MenuService(CategoryRepository(db_session), MenuItemRepository(db_session))
    with pytest.raises(CategoryNotFoundError):
        service.create_menu_item(
            MenuItemCreate(
                category_id=99999,
                name="Новий напій",
                price=Decimal("50.00"),
            )
        )
