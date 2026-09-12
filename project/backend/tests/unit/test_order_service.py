from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.core.errors import (
    InvalidOrderStateError,
    MenuItemNotFoundError,
    MenuItemUnavailableError,
)
from app.models.order import OrderStatus
from app.repositories.menu_repository import MenuItemRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreateRequest, OrderItemCreate
from app.services.order_service import OrderService


def test_create_order_calculates_server_authoritative_total(
    db_session: Session, sample_user, sample_menu_item
):
    service = OrderService(OrderRepository(db_session), MenuItemRepository(db_session))
    req = OrderCreateRequest(
        items=[OrderItemCreate(menu_item_id=sample_menu_item.id, quantity=3)],
        notes="Гарячіше, будь ласка",
    )
    order = service.create_order(user_id=sample_user.id, request=req)

    assert order.id is not None
    assert order.status == OrderStatus.PENDING
    assert order.total_amount == Decimal("195.00")  # 65.00 * 3
    assert len(order.items) == 1
    assert order.items[0].unit_price == Decimal("65.00")
    assert order.items[0].item_name == "Капучино"


def test_create_order_unavailable_item_raises_error(
    db_session: Session, sample_user, unavailable_menu_item
):
    service = OrderService(OrderRepository(db_session), MenuItemRepository(db_session))
    req = OrderCreateRequest(
        items=[OrderItemCreate(menu_item_id=unavailable_menu_item.id, quantity=1)]
    )
    with pytest.raises(MenuItemUnavailableError):
        service.create_order(user_id=sample_user.id, request=req)


def test_create_order_missing_item_raises_error(db_session: Session, sample_user):
    service = OrderService(OrderRepository(db_session), MenuItemRepository(db_session))
    req = OrderCreateRequest(items=[OrderItemCreate(menu_item_id=999999, quantity=1)])
    with pytest.raises(MenuItemNotFoundError):
        service.create_order(user_id=sample_user.id, request=req)


def test_order_state_machine_legal_and_illegal_transitions(
    db_session: Session, sample_user, sample_menu_item
):
    service = OrderService(OrderRepository(db_session), MenuItemRepository(db_session))
    req = OrderCreateRequest(items=[OrderItemCreate(menu_item_id=sample_menu_item.id, quantity=1)])
    order = service.create_order(user_id=sample_user.id, request=req)

    # PENDING -> CONFIRMED (legal)
    order = service.update_order_status(order.id, OrderStatus.CONFIRMED)
    assert order.status == OrderStatus.CONFIRMED

    # CONFIRMED -> READY (legal)
    order = service.update_order_status(order.id, OrderStatus.READY)
    assert order.status == OrderStatus.READY

    # READY -> COMPLETED (legal)
    order = service.update_order_status(order.id, OrderStatus.COMPLETED)
    assert order.status == OrderStatus.COMPLETED

    # COMPLETED -> CANCELLED (illegal from terminal)
    with pytest.raises(InvalidOrderStateError):
        service.update_order_status(order.id, OrderStatus.CANCELLED)


def test_list_all_orders_admin_service(db_session: Session, sample_user, sample_menu_item):
    service = OrderService(OrderRepository(db_session), MenuItemRepository(db_session))
    req = OrderCreateRequest(items=[OrderItemCreate(menu_item_id=sample_menu_item.id, quantity=2)])
    service.create_order(user_id=sample_user.id, request=req)

    all_orders = service.list_all_orders()
    assert len(all_orders) >= 1

    pending_orders = service.list_all_orders(status=OrderStatus.PENDING)
    assert len(pending_orders) >= 1

    completed_orders = service.list_all_orders(status=OrderStatus.COMPLETED)
    assert len(completed_orders) == 0
