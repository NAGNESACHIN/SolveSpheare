from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database.models import AIInsight
from ..database.session import get_db
from ..services.insights import generate_product_insights

router = APIRouter(prefix="/api/insights", tags=["insights"])


def serialize(row: AIInsight) -> dict:
    return {
        "id": str(row.id),
        "insight_type": row.insight_type,
        "title": row.title,
        "summary": row.summary,
        "recommendation": row.recommendation,
        "severity": row.severity,
        "confidence": float(row.confidence) if row.confidence is not None else None,
        "evidence": row.evidence,
    }


@router.post("/products/{product_id}/generate")
def generate_insights(product_id: UUID, db: Session = Depends(get_db)):
    try:
        rows = generate_product_insights(db, product_id)
        db.commit()
        return {
            "product_id": str(product_id),
            "status": "completed",
            "insights_created": len(rows),
            "insights": [serialize(row) for row in rows],
        }
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {exc}")


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
        "insights": [serialize(row) for row in rows],
    }
