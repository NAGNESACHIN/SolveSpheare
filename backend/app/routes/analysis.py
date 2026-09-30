from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database.models import Aspect, Review, ReviewAspect, SentimentScore, Topic, ReviewTopic
from ..database.session import get_db
from ..services.analysis import analyze_product, analyze_review

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.post("/reviews/{review_id}")
def analyze_single_review(review_id: UUID, db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    result = analyze_review(db, review)
    db.commit()
    return result

@router.post("/products/{product_id}")
def analyze_product_reviews(product_id: UUID, db: Session = Depends(get_db)):
    try:
        return analyze_product(db, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

@router.get("/products/{product_id}/sentiment")
def product_sentiment(product_id: UUID, db: Session = Depends(get_db)):
    rows = db.execute(
        select(SentimentScore.sentiment_label, func.count(SentimentScore.id))
        .join(Review, Review.id == SentimentScore.review_id)
        .where(Review.product_id == product_id)
        .group_by(SentimentScore.sentiment_label)
    ).all()
    return {"product_id": str(product_id), "distribution": {label: count for label, count in rows}}

@router.get("/products/{product_id}/aspects")
def product_aspects(product_id: UUID, db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            Aspect.name,
            func.count(ReviewAspect.id),
            func.avg(ReviewAspect.sentiment_score),
        )
        .join(ReviewAspect, ReviewAspect.aspect_id == Aspect.id)
        .join(Review, Review.id == ReviewAspect.review_id)
        .where(Review.product_id == product_id)
        .group_by(Aspect.name)
        .order_by(func.count(ReviewAspect.id).desc())
    ).all()

    return {
        "product_id": str(product_id),
        "aspects": [
            {"aspect": name, "mentions": count, "average_sentiment": round(float(avg or 0), 4)}
            for name, count, avg in rows
        ],
    }

@router.get("/products/{product_id}/topics")
def product_topics(product_id: UUID, db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            Topic.id,
            Topic.name,
            Topic.keywords,
            func.count(ReviewTopic.id),
            func.avg(ReviewTopic.relevance_score),
        )
        .join(ReviewTopic, ReviewTopic.topic_id == Topic.id)
        .join(Review, Review.id == ReviewTopic.review_id)
        .where(Review.product_id == product_id)
        .group_by(Topic.id, Topic.name, Topic.keywords)
        .order_by(func.count(ReviewTopic.id).desc())
    ).all()

    return {
        "product_id": str(product_id),
        "topics": [
            {
                "topic_id": str(topic_id),
                "name": name,
                "keywords": keywords or {},
                "review_count": count,
                "average_relevance": round(float(avg or 0), 4),
            }
            for topic_id, name, keywords, count, avg in rows
        ],
    }
