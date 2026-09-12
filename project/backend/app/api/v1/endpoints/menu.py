from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_admin_user, get_menu_service
from app.core.errors import DomainException
from app.schemas.menu import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ItemAvailabilityUpdate,
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
)
from app.schemas.user import UserResponse
from app.services.menu_service import MenuService

router = APIRouter()


# --- Categories Endpoints ---


@router.get("/categories", response_model=List[CategoryResponse], summary="List menu categories")
def get_categories(
    menu_service: MenuService = Depends(get_menu_service),
):
    """Retrieve all active menu categories ordered by display order."""
    return menu_service.list_categories()


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create menu category (admin only)",
)
def create_category(
    payload: CategoryCreate,
    menu_service: MenuService = Depends(get_menu_service),
    _current_admin: UserResponse = Depends(get_current_admin_user),
):
    """Create a new menu category (requires admin privileges)."""
    try:
        return menu_service.create_category(payload)
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Update menu category (admin only)",
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    menu_service: MenuService = Depends(get_menu_service),
    _current_admin: UserResponse = Depends(get_current_admin_user),
):
    """Update an existing category (requires admin privileges)."""
    try:
        return menu_service.update_category(category_id, payload)
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete menu category (admin only)",
)
def delete_category(
    category_id: int,
    menu_service: MenuService = Depends(get_menu_service),
    _current_admin: UserResponse = Depends(get_current_admin_user),
):
    """Delete a category (requires admin privileges)."""
    try:
        menu_service.delete_category(category_id)
        return None
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


# --- Menu Items Endpoints ---


@router.get("/items", response_model=List[MenuItemResponse], summary="List menu items")
def get_menu_items(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    available_only: bool = Query(True, description="Filter only available items for public menu"),
    menu_service: MenuService = Depends(get_menu_service),
):
    """Retrieve menu items with optional category filtering, availability, and search."""
    try:
        return menu_service.list_menu_items(
            category_id=category_id, search=search, available_only=available_only
        )
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
    summary="Create menu item (admin only)",
)
def create_menu_item(
    payload: MenuItemCreate,
    menu_service: MenuService = Depends(get_menu_service),
    _current_admin: UserResponse = Depends(get_current_admin_user),
):
    """Create a new menu item (requires admin privileges)."""
    try:
        return menu_service.create_menu_item(payload)
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


@router.put(
    "/items/{item_id}",
    response_model=MenuItemResponse,
    summary="Update menu item (admin only)",
)
def update_menu_item(
    item_id: int,
    payload: MenuItemUpdate,
    menu_service: MenuService = Depends(get_menu_service),
    _current_admin: UserResponse = Depends(get_current_admin_user),
):
    """Update an existing menu item (requires admin privileges)."""
    try:
        return menu_service.update_menu_item(item_id=item_id, data=payload)
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


@router.patch(
    "/items/{item_id}/availability",
    response_model=MenuItemResponse,
    summary="Toggle menu item availability in stop-list (admin only)",
)
def toggle_item_availability(
    item_id: int,
    payload: ItemAvailabilityUpdate,
    menu_service: MenuService = Depends(get_menu_service),
    _current_admin: UserResponse = Depends(get_current_admin_user),
):
    """Instantly toggle menu item availability in stop-list (requires admin privileges)."""
    try:
        return menu_service.toggle_item_availability(
            item_id=item_id, is_available=payload.is_available
        )
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete menu item (admin only)",
)
def delete_menu_item(
    item_id: int,
    menu_service: MenuService = Depends(get_menu_service),
    _current_admin: UserResponse = Depends(get_current_admin_user),
):
    """Delete a menu item from the catalog (requires admin privileges)."""
    try:
        menu_service.delete_menu_item(item_id)
        return None
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
