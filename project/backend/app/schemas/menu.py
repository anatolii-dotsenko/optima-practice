from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    display_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    image_url: Optional[str] = None
    is_available: bool = True


class MenuItemCreate(MenuItemBase):
    category_id: int


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2)
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    category_id: Optional[int] = None


class MenuItemResponse(MenuItemBase):
    id: int
    category_id: int

    model_config = ConfigDict(from_attributes=True)
