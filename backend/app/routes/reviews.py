from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database.models import Product, Review
from ..database.session import get_db
from ..schemas.reviews import ProductCreate, ProductOut, ReviewCreate, ReviewOut

router = APIRouter(prefix="/api", tags=["reviews"])

@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return list(db.scalars(select(Product).order_by(Product.created_at.desc())).all())

@router.post("/reviews", response_model=ReviewOut, status_code=201)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)):
    if db.get(Product, payload.product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    review = Review(**payload.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@router.get("/reviews", response_model=list[ReviewOut])
def list_reviews(product_id: UUID | None = None, db: Session = Depends(get_db)):
    stmt = select(Review).order_by(Review.created_at.desc())
    if product_id:
        stmt = stmt.where(Review.product_id == product_id)
    return list(db.scalars(stmt).all())
