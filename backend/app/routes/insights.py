from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database.models import AIInsight
from ..database.session import get_db

router = APIRouter(prefix="/api/insights", tags=["insights"])

@router.get("/products/{product_id}")
def product_insights(product_id: UUID, db: Session = Depends(get_db)):
    rows = db.execute(
        select(AIInsight)
        .where(AIInsight.product_id == product_id)
        .order_by(AIInsight.created_at.desc())
        .limit(50)
    ).scalars().all()

    return {
        "product_id": str(product_id),
        "insights": [
            {
                "id": str(row.id),
                "insight_type": row.insight_type,
                "title": row.title,
                "summary": row.summary,
                "recommendation": row.recommendation,
                "severity": row.severity,
                "confidence": float(row.confidence) if row.confidence is not None else None,
                "evidence": row.evidence,
            }
            for row in rows
        ],
    }
