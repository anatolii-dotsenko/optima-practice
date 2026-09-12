from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.order import OrderItem


class MenuItem(Base, TimestampMixin):
    """MenuItem ORM model for coffee drinks and food products."""

    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="items")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="menu_item")

    def __repr__(self) -> str:
        return (
            f"<MenuItem id={self.id} name='{self.name}' price={self.price} "
            f"available={self.is_available}>"
        )
