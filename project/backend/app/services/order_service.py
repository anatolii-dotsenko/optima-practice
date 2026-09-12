from decimal import Decimal
from typing import Dict, List, Sequence, Set

from app.core.errors import (
    InvalidOrderStateError,
    MenuItemNotFoundError,
    MenuItemUnavailableError,
    OrderNotFoundError,
)
from app.models.order import Order, OrderItem, OrderStatus
from app.repositories.menu_repository import MenuItemRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreateRequest


class OrderService:
    """Pure domain service for Order placement and state lifecycle management.
    Zero imports from web frameworks.
    Enforces ADR-0006 (State Machine) and ADR-0007 (Server-Authoritative Pricing).
    """

    # Legal transitions matrix (ADR-0006)
    ALLOWED_TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
        OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED: {OrderStatus.READY, OrderStatus.CANCELLED},
        OrderStatus.READY: {OrderStatus.COMPLETED, OrderStatus.CANCELLED},
        OrderStatus.COMPLETED: set(),  # Terminal state
        OrderStatus.CANCELLED: set(),  # Terminal state
    }

    def __init__(
        self,
        order_repo: OrderRepository,
        menu_item_repo: MenuItemRepository,
    ) -> None:
        self.order_repo = order_repo
        self.menu_item_repo = menu_item_repo

    def create_order(self, user_id: int, request: OrderCreateRequest) -> Order:
        """Creates an order with server-calculated prices and item availability check (ADR-0007)."""
        item_ids = [i.menu_item_id for i in request.items]
        menu_items = self.menu_item_repo.get_by_ids(item_ids)
        items_map = {item.id: item for item in menu_items}

        total_amount = Decimal("0.00")
        order_items: List[OrderItem] = []

        for req_item in request.items:
            menu_item = items_map.get(req_item.menu_item_id)
            if not menu_item:
                raise MenuItemNotFoundError(req_item.menu_item_id)

            if not menu_item.is_available:
                raise MenuItemUnavailableError(
                    item_name=menu_item.name,
                    item_id=menu_item.id,
                )

            unit_price = menu_item.price
            subtotal = unit_price * req_item.quantity
            total_amount += subtotal

            order_items.append(
                OrderItem(
                    menu_item_id=menu_item.id,
                    quantity=req_item.quantity,
                    unit_price=unit_price,
                    item_name=menu_item.name,
                )
            )

        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            notes=request.notes,
            items=order_items,
        )

        return self.order_repo.create(order)

    def get_order_by_id(self, order_id: int, user_id: int) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order or order.user_id != user_id:
            raise OrderNotFoundError(order_id)
        return order

    def list_orders_by_user(self, user_id: int) -> Sequence[Order]:
        return self.order_repo.list_by_user(user_id)

    def update_order_status(self, order_id: int, new_status: OrderStatus) -> Order:
        """Transitions order status according to legal state matrix (ADR-0006)."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)

        current_status = order.status
        allowed = self.ALLOWED_TRANSITIONS.get(current_status, set())

        if new_status not in allowed:
            raise InvalidOrderStateError(
                current_status=current_status.value,
                target_status=new_status.value,
            )

        return self.order_repo.update_status(order, new_status)
