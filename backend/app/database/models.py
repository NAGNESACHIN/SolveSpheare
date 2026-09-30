import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .session import Base

class Product(Base):
    __tablename__ = "products"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(150))
    category: Mapped[str | None] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)
    external_product_id: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str | None] = mapped_column(String(100))
    average_rating: Mapped[float | None] = mapped_column(Numeric(3,2))
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    reviews: Mapped[list["Review"]] = relationship(back_populates="product", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("source", "external_review_id", name="uq_review_source_external"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    external_review_id: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(Text)
    review_text: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[float | None] = mapped_column(Numeric(2,1))
    reviewer_name: Mapped[str | None] = mapped_column(String(255))
    verified_purchase: Mapped[bool | None] = mapped_column(Boolean)
    review_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[str | None] = mapped_column(String(100))
    language: Mapped[str | None] = mapped_column(String(20))
    helpful_votes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    product: Mapped[Product] = relationship(back_populates="reviews")
    sentiment_scores: Mapped[list["SentimentScore"]] = relationship(cascade="all, delete-orphan")

class Aspect(Base):
    __tablename__ = "aspects"
    __table_args__ = (UniqueConstraint("product_id", "name", name="uq_aspect_product_name"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    parent_aspect_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("aspects.id", ondelete="SET NULL"))

class SentimentScore(Base):
    __tablename__ = "sentiment_scores"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    sentiment_label: Mapped[str] = mapped_column(String(30), nullable=False)
    score: Mapped[float | None] = mapped_column(Numeric(6,5))
    positive_score: Mapped[float | None] = mapped_column(Numeric(6,5))
    negative_score: Mapped[float | None] = mapped_column(Numeric(6,5))
    neutral_score: Mapped[float | None] = mapped_column(Numeric(6,5))
    model_name: Mapped[str | None] = mapped_column(String(150))
    model_version: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("product_id", "name", name="uq_topic_product_name"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    topic_type: Mapped[str | None] = mapped_column(String(50))
    keywords: Mapped[dict | None] = mapped_column(JSONB)

class ReviewAspect(Base):
    __tablename__ = "review_aspects"
    __table_args__ = (UniqueConstraint("review_id", "aspect_id", "mention_text", name="uq_review_aspect_mention"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    aspect_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("aspects.id", ondelete="CASCADE"), nullable=False)
    mention_text: Mapped[str | None] = mapped_column(Text)
    sentiment_label: Mapped[str | None] = mapped_column(String(30))
    sentiment_score: Mapped[float | None] = mapped_column(Numeric(6,5))
    confidence: Mapped[float | None] = mapped_column(Numeric(6,5))
    start_position: Mapped[int | None] = mapped_column(Integer)
    end_position: Mapped[int | None] = mapped_column(Integer)

class ReviewTopic(Base):
    __tablename__ = "review_topics"
    __table_args__ = (UniqueConstraint("review_id", "topic_id", name="uq_review_topic"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    topic_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    relevance_score: Mapped[float | None] = mapped_column(Numeric(6,5))
    confidence: Mapped[float | None] = mapped_column(Numeric(6,5))

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_type: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(150), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(100))
    parameters: Mapped[dict | None] = mapped_column(JSONB)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class AIInsight(Base):
    __tablename__ = "ai_insights"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    review_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="SET NULL"))
    aspect_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("aspects.id", ondelete="SET NULL"))
    topic_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="SET NULL"))
    insight_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text)
    evidence: Mapped[dict | None] = mapped_column(JSONB)
    severity: Mapped[str | None] = mapped_column(String(30))
    confidence: Mapped[float | None] = mapped_column(Numeric(6,5))
    model_name: Mapped[str | None] = mapped_column(String(150))
    model_version: Mapped[str | None] = mapped_column(String(100))
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
