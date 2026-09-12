from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_menu_service
from app.core.errors import DomainException
from app.schemas.menu import (
    CategoryResponse,
    MenuItemCreate,
    MenuItemResponse,
)
from app.schemas.user import UserResponse
from app.services.menu_service import MenuService

router = APIRouter()


@router.get("/categories", response_model=List[CategoryResponse], summary="List menu categories")
def get_categories(
    menu_service: MenuService = Depends(get_menu_service),
):
    """Retrieve all active menu categories ordered by display order."""
    return menu_service.list_categories()


@router.get("/items", response_model=List[MenuItemResponse], summary="List menu items")
def get_menu_items(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    menu_service: MenuService = Depends(get_menu_service),
):
    """Retrieve all available menu items with optional category filtering and search."""
    try:
        return menu_service.list_menu_items(category_id=category_id, search=search)
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


@router.get("/items/{item_id}", response_model=MenuItemResponse, summary="Get menu item by ID")
def get_menu_item(
    item_id: int,
    menu_service: MenuService = Depends(get_menu_service),
):
    """Retrieve single menu item details."""
    try:
        return menu_service.get_menu_item_by_id(item_id)
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


@router.post(
    "/items",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create menu item",
)
def create_menu_item(
    payload: MenuItemCreate,
    menu_service: MenuService = Depends(get_menu_service),
    _current_user: UserResponse = Depends(get_current_user),
):
    """Create a new menu item (requires authentication)."""
    try:
        return menu_service.create_menu_item(payload)
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
