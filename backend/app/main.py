from fastapi import FastAPI
from .routes.reviews import router as reviews_router
from .routes.analytics import router as analytics_router

app = FastAPI(
    title="Product Review Intelligence & Voice of Customer Analytics API",
    version="0.1.0",
    description="Review ingestion, NLP analytics and Voice of Customer intelligence.",
)

app.include_router(reviews_router)
app.include_router(analytics_router)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
