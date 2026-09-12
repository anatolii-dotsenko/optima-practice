from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_admin_user, get_current_user, get_order_service
from app.core.errors import DomainException
from app.models.order import OrderStatus
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


@router.get(
    "/admin",
    response_model=List[OrderResponse],
    summary="List all orders (admin/barista only)",
)
def get_all_orders_admin(
    status: Optional[OrderStatus] = Query(None, description="Filter orders by status"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _current_admin: UserResponse = Depends(get_current_admin_user),
    order_service: OrderService = Depends(get_order_service),
):
    """Retrieve all customer orders across the system for staff/barista queue management."""
    orders = order_service.list_all_orders(status=status, limit=limit, offset=offset)
    result = []
    for ord in orders:
        resp = OrderResponse.model_validate(ord)
        if ord.user:
            resp.customer_email = ord.user.email
            resp.customer_name = ord.user.full_name
        result.append(resp)
    return result


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
        order = order_service.update_order_status(order_id=order_id, new_status=payload.status)
        resp = OrderResponse.model_validate(order)
        if order.user:
            resp.customer_email = order.user.email
            resp.customer_name = order.user.full_name
        return resp
    except DomainException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message, "details": e.details},
        )
