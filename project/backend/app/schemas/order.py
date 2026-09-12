from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., ge=1, le=50, description="Quantity to order")


class OrderCreateRequest(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_length=1, description="List of items to order")
    notes: Optional[str] = Field(None, max_length=500, description="Barista instructions")


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    unit_price: Decimal
    item_name: str

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    notes: Optional[str] = None
    items: List[OrderItemResponse]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
