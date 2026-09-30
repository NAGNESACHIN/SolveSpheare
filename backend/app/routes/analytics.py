from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database.models import Review, SentimentScore
from ..database.session import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

def build_overview(db: Session, product_id: UUID | None = None):
    review_stmt = select(func.count(Review.id), func.avg(Review.rating))
    sentiment_stmt = select(SentimentScore.sentiment_label, func.count(SentimentScore.id)).join(
        Review, Review.id == SentimentScore.review_id
    )

    if product_id:
        review_stmt = review_stmt.where(Review.product_id == product_id)
        sentiment_stmt = sentiment_stmt.where(Review.product_id == product_id)

    total_reviews, average_rating = db.execute(review_stmt).one()
    sentiment_rows = db.execute(
        sentiment_stmt.group_by(SentimentScore.sentiment_label)
    ).all()

    return {
        "product_id": str(product_id) if product_id else None,
        "total_reviews": total_reviews or 0,
        "average_rating": round(float(average_rating), 2) if average_rating is not None else 0,
        "sentiment_distribution": {label: count for label, count in sentiment_rows},
    }

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    return build_overview(db)

@router.get("/products/{product_id}/overview")
def product_overview(product_id: UUID, db: Session = Depends(get_db)):
    return build_overview(db, product_id)
