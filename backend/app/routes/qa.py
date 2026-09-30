from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database.models import AIInsight, Aspect, Product, Review, ReviewAspect, ReviewTopic, SentimentScore, Topic
from ..database.session import get_db
from ..services.llm import generate_product_answer

router = APIRouter(prefix="/api/qa", tags=["qa"])

class ProductQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=500)

@router.post("/products/{product_id}")
def ask_product(product_id: UUID, payload: ProductQuestion, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    sentiment_rows = db.execute(select(SentimentScore.sentiment_label, func.count(SentimentScore.id)).join(Review, Review.id == SentimentScore.review_id).where(Review.product_id == product_id).group_by(SentimentScore.sentiment_label)).all()
    aspect_rows = db.execute(select(Aspect.name, func.count(ReviewAspect.id), func.avg(ReviewAspect.sentiment_score)).join(ReviewAspect, ReviewAspect.aspect_id == Aspect.id).join(Review, Review.id == ReviewAspect.review_id).where(Review.product_id == product_id).group_by(Aspect.name).order_by(func.count(ReviewAspect.id).desc()).limit(12)).all()
    topic_rows = db.execute(select(Topic.name, func.count(ReviewTopic.id), func.avg(ReviewTopic.relevance_score)).join(ReviewTopic, ReviewTopic.topic_id == Topic.id).join(Review, Review.id == ReviewTopic.review_id).where(Review.product_id == product_id).group_by(Topic.name).order_by(func.count(ReviewTopic.id).desc()).limit(8)).all()
    insights = list(db.scalars(select(AIInsight).where(AIInsight.product_id == product_id).order_by(AIInsight.created_at.desc()).limit(12)).all())
    reviews = list(db.scalars(select(Review).where(Review.product_id == product_id).order_by(Review.created_at.desc()).limit(20)).all())

    snapshot = {
        "product": product.name,
        "question": payload.question,
        "review_count": len(reviews),
        "sentiment_distribution": {label: count for label, count in sentiment_rows},
        "aspects": [{"name": name, "mentions": count, "average_sentiment": round(float(avg or 0), 4)} for name, count, avg in aspect_rows],
        "topics": [{"name": name, "review_count": count, "average_relevance": round(float(avg or 0), 4)} for name, count, avg in topic_rows],
        "insights": [{"type": i.insight_type, "title": i.title, "summary": i.summary, "recommendation": i.recommendation} for i in insights],
        "recent_reviews": [{"title": r.title, "rating": r.rating, "text": r.review_text[:600]} for r in reviews],
    }

    answer = generate_product_answer(snapshot)
    if answer is None:
        raise HTTPException(status_code=503, detail="AI Q&A is not configured. Add OPENAI_API_KEY to the backend environment.")
    return {"product_id": str(product_id), "question": payload.question, "answer": answer}
