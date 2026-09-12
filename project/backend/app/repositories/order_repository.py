from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order, OrderStatus


class OrderRepository:
    """Handles persistence operations for Order and OrderItem entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, order_id: int) -> Optional[Order]:
        stmt = select(Order).where(Order.id == order_id).options(selectinload(Order.items))
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_user(self, user_id: int) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
        )
        return self.db.execute(stmt).scalars().all()

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        # Eager load items
        stmt = select(Order).where(Order.id == order.id).options(selectinload(Order.items))
        return self.db.execute(stmt).scalar_one()

    def update_status(self, order: Order, new_status: OrderStatus) -> Order:
        order.status = new_status
        self.db.commit()
        self.db.refresh(order)
        stmt = select(Order).where(Order.id == order.id).options(selectinload(Order.items))
        return self.db.execute(stmt).scalar_one()
