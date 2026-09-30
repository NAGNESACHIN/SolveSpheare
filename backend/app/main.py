from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .routes.reviews import router as reviews_router
from .routes.analytics import router as analytics_router
from .routes.analysis import router as analysis_router

app = FastAPI(
    title="Product Review Intelligence & Voice of Customer Analytics API",
    version="0.1.0",
    description="Review ingestion, NLP analytics and Voice of Customer intelligence.",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reviews_router)
app.include_router(analytics_router)
app.include_router(analysis_router)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
