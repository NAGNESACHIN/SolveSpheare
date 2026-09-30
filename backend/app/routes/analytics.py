from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..database.models import Review, SentimentScore
from ..database.session import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    total_reviews = db.scalar(select(func.count(Review.id))) or 0
    average_rating = db.scalar(select(func.avg(Review.rating))) or 0
    sentiment_rows = db.execute(
        select(SentimentScore.sentiment_label, func.count(SentimentScore.id))
        .group_by(SentimentScore.sentiment_label)
    ).all()
    return {
        "total_reviews": total_reviews,
        "average_rating": round(float(average_rating), 2),
        "sentiment_distribution": {label: count for label, count in sentiment_rows},
    }
