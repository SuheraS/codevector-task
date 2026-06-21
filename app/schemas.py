from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    price: Decimal
    created_at: datetime
    updated_at: datetime


class ProductsPage(BaseModel):
    items: list[ProductOut]
    next_cursor: str | None = None
    snapshot: datetime
    has_more: bool


class ErrorResponse(BaseModel):
    detail: str = Field(...)
