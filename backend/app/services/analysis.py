from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..database.models import (
    AnalysisRun, Aspect, Product, Review, ReviewAspect, ReviewTopic,
    SentimentScore, Topic,
)
from .aspects import extract_aspects
from .sentiment import analyze_sentiment
from .text_cleaning import clean_text
from .topics import discover_topics

MODEL_NAME = "rule-based-nlp"
MODEL_VERSION = "1.0"

def _now():
    return datetime.now(timezone.utc)

def analyze_review(db: Session, review: Review) -> dict:
    text = clean_text(review.review_text)
    sentiment = analyze_sentiment(text)

    db.execute(delete(SentimentScore).where(SentimentScore.review_id == review.id))
    db.execute(delete(ReviewAspect).where(ReviewAspect.review_id == review.id))

    db.add(SentimentScore(
        review_id=review.id,
        sentiment_label=sentiment["label"],
        score=sentiment["score"],
        positive_score=sentiment["positive_score"],
        negative_score=sentiment["negative_score"],
        neutral_score=sentiment["neutral_score"],
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
    ))

    aspect_results = extract_aspects(text)
    saved_aspects = []
    for item in aspect_results:
        aspect = db.scalar(select(Aspect).where(
            Aspect.product_id == review.product_id,
            Aspect.name == item["aspect"],
        ))
        if aspect is None:
            aspect = Aspect(product_id=review.product_id, name=item["aspect"])
            db.add(aspect)
            db.flush()

        db.add(ReviewAspect(
            review_id=review.id,
            aspect_id=aspect.id,
            mention_text=item["mention_text"],
            sentiment_label=item["sentiment"]["label"],
            sentiment_score=item["sentiment"]["score"],
            confidence=item["confidence"],
            start_position=item["start_position"],
            end_position=item["end_position"],
        ))
        saved_aspects.append(item["aspect"])

    return {
        "review_id": str(review.id),
        "sentiment": sentiment,
        "aspects": sorted(set(saved_aspects)),
    }

def analyze_product(db: Session, product_id: UUID) -> dict:
    product = db.get(Product, product_id)
    if product is None:
        raise ValueError("Product not found")

    run = AnalysisRun(
        analysis_type="full_product_analysis",
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        parameters={"topic_method": "tfidf_nmf", "max_topics": 5},
        started_at=_now(),
        status="running",
    )
    db.add(run)
    db.flush()

    try:
        reviews = list(db.scalars(
            select(Review).where(Review.product_id == product_id).order_by(Review.created_at.asc())
        ).all())

        review_results = [analyze_review(db, review) for review in reviews]
        db.flush()

        review_ids = [r.id for r in reviews]
        if review_ids:
            db.execute(delete(ReviewTopic).where(ReviewTopic.review_id.in_(review_ids)))

        topics = discover_topics([clean_text(r.review_text) for r in reviews])
        topic_results = []

        for topic_data in topics:
            topic = db.scalar(select(Topic).where(
                Topic.product_id == product_id,
                Topic.name == topic_data["name"],
            ))
            if topic is None:
                topic = Topic(
                    product_id=product_id,
                    name=topic_data["name"],
                    description=f"Automatically discovered topic: {topic_data['name']}",
                    topic_type="discovered",
                    keywords={"terms": topic_data["keywords"]},
                )
                db.add(topic)
                db.flush()
            else:
                topic.keywords = {"terms": topic_data["keywords"]}

            weights = topic_data["weights"]
            for idx, review in enumerate(reviews):
                relevance = float(weights[idx])
                if relevance <= 0:
                    continue
                db.add(ReviewTopic(
                    review_id=review.id,
                    topic_id=topic.id,
                    relevance_score=round(relevance, 5),
                    confidence=min(1.0, round(relevance, 5)),
                ))

            topic_results.append({
                "topic_id": str(topic.id),
                "name": topic.name,
                "keywords": topic_data["keywords"],
            })

        run.status = "completed"
        run.completed_at = _now()
        db.commit()

        return {
            "product_id": str(product_id),
            "reviews_analyzed": len(reviews),
            "review_results": review_results,
            "topics": topic_results,
            "analysis_run_id": str(run.id),
        }
    except Exception:
        db.rollback()
        run = db.get(AnalysisRun, run.id)
        if run:
            run.status = "failed"
            run.completed_at = _now()
            db.commit()
        raise
