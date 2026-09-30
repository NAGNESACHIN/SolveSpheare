from collections import Counter
from datetime import datetime
import os
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from .llm import generate_customer_voice_summary

from ..database.models import (
    AIInsight,
    Aspect,
    Product,
    Review,
    ReviewAspect,
    ReviewTopic,
    SentimentScore,
    Topic,
)

ASPECT_ACTIONS = {
    "battery": "Investigate battery drain patterns and prioritize power-efficiency improvements across common usage scenarios.",
    "performance": "Review performance bottlenecks and reproduce the reported slowdowns under the usage conditions reflected in customer feedback.",
    "camera": "Review camera quality complaints by shooting condition and prioritize the most frequently reported quality gaps.",
    "display": "Investigate the display issues reported by customers and validate them across brightness, color, and viewing conditions.",
    "design": "Preserve the design strengths while addressing the specific usability or build-quality concerns appearing in negative feedback.",
    "price": "Evaluate perceived value against the features customers mention and consider whether pricing, packaging, or feature communication needs adjustment.",
    "software": "Prioritize recurring software defects and usability friction, then validate fixes against the affected customer scenarios.",
    "delivery": "Investigate fulfillment and delivery delays by carrier, location, and order stage to reduce repeated delivery complaints.",
    "customer service": "Review support response and resolution workflows for the scenarios generating repeated customer complaints.",
    "quality": "Identify the underlying quality failures behind repeated complaints and strengthen quality-control checks around those failure modes.",
}


def _confidence(mentions: int, sentiment: float | None) -> float:
    frequency = min(1.0, mentions / 30)
    polarity = min(1.0, abs(sentiment or 0.0))
    return round(min(0.98, 0.55 + 0.30 * frequency + 0.13 * polarity), 5)


def _severity(mentions: int, sentiment: float | None) -> str:
    negative = sentiment is not None and sentiment < -0.15
    if negative and mentions >= 20:
        return "high"
    if negative and mentions >= 8:
        return "medium"
    return "low"


def generate_product_insights(db: Session, product_id: UUID) -> list[AIInsight]:
    product = db.get(Product, product_id)
    if product is None:
        raise ValueError("Product not found")

    reviews = list(db.scalars(select(Review).where(Review.product_id == product_id)).all())
    sentiment_rows = db.execute(
        select(SentimentScore.sentiment_label, func.count(SentimentScore.id))
        .join(Review, Review.id == SentimentScore.review_id)
        .where(Review.product_id == product_id)
        .group_by(SentimentScore.sentiment_label)
    ).all()
    sentiment_counts = Counter({label: count for label, count in sentiment_rows})

    aspect_rows = db.execute(
        select(
            Aspect.id,
            Aspect.name,
            func.count(ReviewAspect.id),
            func.avg(ReviewAspect.sentiment_score),
        )
        .join(ReviewAspect, ReviewAspect.aspect_id == Aspect.id)
        .join(Review, Review.id == ReviewAspect.review_id)
        .where(Review.product_id == product_id)
        .group_by(Aspect.id, Aspect.name)
        .order_by(func.count(ReviewAspect.id).desc())
    ).all()

    topic_rows = db.execute(
        select(
            Topic.id,
            Topic.name,
            func.count(ReviewTopic.id),
            func.avg(ReviewTopic.relevance_score),
        )
        .join(ReviewTopic, ReviewTopic.topic_id == Topic.id)
        .join(Review, Review.id == ReviewTopic.review_id)
        .where(Review.product_id == product_id)
        .group_by(Topic.id, Topic.name)
        .order_by(func.count(ReviewTopic.id).desc())
    ).all()

    # Insights are regenerated from the current analysis snapshot.
    db.execute(delete(AIInsight).where(AIInsight.product_id == product_id))
    created: list[AIInsight] = []
    now = datetime.utcnow()

    total = len(reviews)
    positive = sentiment_counts.get("positive", 0)
    negative = sentiment_counts.get("negative", 0)
    neutral = sentiment_counts.get("neutral", 0)

    if total:
        summary = (
            f"{product.name} has {total} analyzed review"
            f"{'s' if total != 1 else ''}. "
            f"{positive} are positive, {neutral} neutral, and {negative} negative."
        )
        if aspect_rows:
            top_aspect = aspect_rows[0]
            summary += f" The most frequently discussed aspect is {top_aspect[1]} with {top_aspect[2]} mentions."
        created.append(
            AIInsight(
                product_id=product_id,
                insight_type="summary",
                title="Customer Voice Summary",
                summary=summary,
                recommendation="Use the recurring negative aspects as the starting point for product and service improvement, while preserving strongly positive attributes.",
                evidence={
                    "review_count": total,
                    "sentiment_distribution": dict(sentiment_counts),
                    "top_aspects": [{"name": row[1], "mentions": row[2]} for row in aspect_rows[:5]],
                    "top_topics": [{"name": row[1], "review_count": row[2]} for row in topic_rows[:5]],
                },
                severity="low",
                confidence=0.9 if total >= 10 else 0.72,
                model_name="rules",
                model_version="0.1",
                period_end=now,
            )
        )

    for aspect_id, name, mentions, avg_sentiment in aspect_rows[:8]:
        sentiment = float(avg_sentiment) if avg_sentiment is not None else 0.0
        if sentiment < -0.10:
            severity = _severity(mentions, sentiment)
            created.append(
                AIInsight(
                    product_id=product_id,
                    aspect_id=aspect_id,
                    insight_type="pain_point",
                    title=f"{name.title()} is a recurring customer concern",
                    summary=f"{name.title()} appears in {mentions} review signals with an average aspect sentiment of {sentiment:.2f}. This indicates recurring negative customer feedback that merits investigation.",
                    recommendation=ASPECT_ACTIONS.get(name.lower(), f"Investigate the recurring {name.lower()} complaints and validate the root causes against the supporting reviews."),
                    evidence={
                        "aspect": name,
                        "mentions": mentions,
                        "average_sentiment": sentiment,
                        "severity_basis": {"negative_sentiment": True, "mention_count": mentions},
                    },
                    severity=severity,
                    confidence=_confidence(mentions, sentiment),
                    model_name="rules",
                    model_version="0.1",
                    period_end=now,
                )
            )
        elif sentiment > 0.15 and mentions >= 3:
            created.append(
                AIInsight(
                    product_id=product_id,
                    aspect_id=aspect_id,
                    insight_type="opportunity",
                    title=f"Customers appreciate {name}",
                    summary=f"{name.title()} has {mentions} mentions with an average aspect sentiment of {sentiment:.2f}, making it a clear positive customer signal.",
                    recommendation=f"Preserve this strength and consider using {name.lower()} as a differentiating attribute in product positioning and future iterations.",
                    evidence={"aspect": name, "mentions": mentions, "average_sentiment": sentiment},
                    severity="low",
                    confidence=_confidence(mentions, sentiment),
                    model_name="rules",
                    model_version="0.1",
                    period_end=now,
                )
            )

    if topic_rows and total:
        topic_id, topic_name, topic_count, relevance = topic_rows[0]
        share = topic_count / total
        if share >= 0.20:
            created.append(
                AIInsight(
                    product_id=product_id,
                    topic_id=topic_id,
                    insight_type="topic_insight",
                    title=f"{topic_name.title()} is a dominant customer theme",
                    summary=f"The {topic_name} theme appears in {topic_count} review-topic assignments, representing roughly {share:.0%} of analyzed reviews.",
                    recommendation=f"Track {topic_name.lower()} as a recurring customer theme and segment future reviews around it to identify changes over time.",
                    evidence={"topic": topic_name, "review_count": topic_count, "share": round(share, 4), "average_relevance": float(relevance or 0)},
                    severity="medium" if share >= 0.35 else "low",
                    confidence=min(0.95, round(0.65 + share * 0.6, 5)),
                    model_name="rules",
                    model_version="0.1",
                    period_end=now,
                )
            )

    snapshot = {
        "product": product.name,
        "review_count": total,
        "sentiment_distribution": dict(sentiment_counts),
        "aspects": [
            {
                "name": row[1],
                "mentions": row[2],
                "average_sentiment": round(float(row[3] or 0), 4),
            }
            for row in aspect_rows[:8]
        ],
        "topics": [
            {
                "name": row[1],
                "review_count": row[2],
                "average_relevance": round(float(row[3] or 0), 4),
            }
            for row in topic_rows[:5]
        ],
    }

    llm_result = generate_customer_voice_summary(snapshot)
    if llm_result:
        try:
            confidence = max(0.0, min(1.0, float(llm_result.get("confidence", 0.7))))
        except (TypeError, ValueError):
            confidence = 0.7

        created.append(
            AIInsight(
                product_id=product_id,
                insight_type="llm_summary",
                title=str(llm_result.get("title") or "AI Customer Voice Summary")[:500],
                summary=str(llm_result.get("summary") or "AI enrichment was generated from the current analytics snapshot."),
                recommendation=str(llm_result.get("recommendation") or "") or None,
                evidence=snapshot,
                severity="low",
                confidence=confidence,
                model_name=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
                model_version="responses-api",
                period_end=now,
            )
        )

    db.add_all(created)
    db.flush()
    return created
