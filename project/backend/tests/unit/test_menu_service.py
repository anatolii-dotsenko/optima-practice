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


def test_update_menu_item_success(db_session: Session, sample_menu_item):
    from app.schemas.menu import MenuItemUpdate

    service = MenuService(CategoryRepository(db_session), MenuItemRepository(db_session))
    updated = service.update_menu_item(
        sample_menu_item.id,
        MenuItemUpdate(price=Decimal("99.50"), description="Оновлений опис"),
    )
    assert updated.price == Decimal("99.50")
    assert updated.description == "Оновлений опис"


def test_toggle_item_availability_success(db_session: Session, sample_menu_item):
    service = MenuService(CategoryRepository(db_session), MenuItemRepository(db_session))
    toggled = service.toggle_item_availability(sample_menu_item.id, False)
    assert toggled.is_available is False

    restored = service.toggle_item_availability(sample_menu_item.id, True)
    assert restored.is_available is True


def test_delete_menu_item_success(db_session: Session, sample_menu_item):
    service = MenuService(CategoryRepository(db_session), MenuItemRepository(db_session))
    service.delete_menu_item(sample_menu_item.id)

    with pytest.raises(MenuItemNotFoundError):
        service.get_menu_item_by_id(sample_menu_item.id)


def test_category_crud_service(db_session: Session):
    from app.schemas.menu import CategoryCreate, CategoryUpdate

    service = MenuService(CategoryRepository(db_session), MenuItemRepository(db_session))
    cat = service.create_category(
        CategoryCreate(name="Смузі", slug="smoothie", description="Фруктові смузі")
    )
    assert cat.id is not None
    assert cat.slug == "smoothie"

    updated = service.update_category(cat.id, CategoryUpdate(name="Свіжі смузі"))
    assert updated.name == "Свіжі смузі"

    service.delete_category(cat.id)
    with pytest.raises(CategoryNotFoundError):
        service.get_category_by_id(cat.id)
