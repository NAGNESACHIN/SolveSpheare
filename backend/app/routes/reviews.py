from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
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


@router.post("/reviews/upload", status_code=201)
async def upload_reviews_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    import csv
    import io

    raw = await file.read()
    try:
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded")

    required = {"product_id", "review_text"}
    if not required.issubset(set(rows[0].keys()) if rows else set()):
        raise HTTPException(status_code=400, detail="CSV must contain product_id and review_text columns")

    created = 0
    for row in rows:
        try:
            product_id = UUID(row["product_id"])
        except ValueError:
            continue
        if db.get(Product, product_id) is None or not row.get("review_text", "").strip():
            continue
        review = Review(
            product_id=product_id,
            review_text=row["review_text"].strip(),
            title=row.get("title") or None,
            rating=float(row["rating"]) if row.get("rating") else None,
            reviewer_name=row.get("reviewer_name") or None,
            verified_purchase=row.get("verified_purchase", "").lower() == "true" if row.get("verified_purchase") else None,
            source=row.get("source") or file.filename,
            external_review_id=row.get("external_review_id") or None,
            language=row.get("language") or "en",
        )
        db.add(review)
        created += 1

    db.commit()
    return {"filename": file.filename, "rows_received": len(rows), "reviews_created": created}
