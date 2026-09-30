from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    brand: str | None = None
    category: str | None = None
    description: str | None = None
    source: str | None = None

class ProductOut(ProductCreate):
    id: UUID
    review_count: int
    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    product_id: UUID
    review_text: str = Field(min_length=1)
    title: str | None = None
    rating: float | None = Field(default=None, ge=0, le=5)
    reviewer_name: str | None = None
    verified_purchase: bool | None = None
    review_date: datetime | None = None
    source: str | None = None
    external_review_id: str | None = None
    language: str | None = "en"

class ReviewOut(ReviewCreate):
    id: UUID
    class Config:
        from_attributes = True
