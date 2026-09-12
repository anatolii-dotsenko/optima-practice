from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_order_service
from app.core.errors import DomainException
from app.schemas.order import (
    OrderCreateRequest,
    OrderResponse,
    OrderStatusUpdate,
)
from app.schemas.user import UserResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create pre-order",
)
@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_order(
    payload: OrderCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """Place a new coffee pre-order with server-authoritative price calculation (ADR-0007)."""
    try:
        return order_service.create_order(user_id=current_user.id, request=payload)
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


@router.get("", response_model=List[OrderResponse], summary="List my orders")
@router.get("/", response_model=List[OrderResponse], include_in_schema=False)
def get_my_orders(
    current_user: UserResponse = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """List all orders for the currently authenticated user."""
    return order_service.list_orders_by_user(user_id=current_user.id)


@router.get("/{order_id}", response_model=OrderResponse, summary="Get order by ID")
def get_order(
    order_id: int,
    current_user: UserResponse = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """Get single order details for current user."""
    try:
        return order_service.get_order_by_id(order_id=order_id, user_id=current_user.id)
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )


@router.patch("/{order_id}/status", response_model=OrderResponse, summary="Update order status")
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    _current_user: UserResponse = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
):
    """Transition order status according to state machine rules (ADR-0006)."""
    try:
        return order_service.update_order_status(order_id=order_id, new_status=payload.status)
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
