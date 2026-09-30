# Backend

FastAPI service for review ingestion, analytics, NLP processing and Voice of Customer intelligence.

## Local setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Set `DATABASE_URL` to your PostgreSQL connection string before starting the API.

## Core endpoints

- `GET /health`
- `POST /api/products`
- `GET /api/products`
- `POST /api/reviews`
- `GET /api/reviews?product_id=<uuid>`
- `POST /api/reviews/upload`
- `POST /api/analysis/reviews/<review_id>`
- `POST /api/analysis/products/<product_id>`
- `GET /api/analysis/products/<product_id>/sentiment`
- `GET /api/analysis/products/<product_id>/aspects`
- `GET /api/analysis/products/<product_id>/topics`
- `GET /api/analytics/overview`

## NLP pipeline

```text
Raw review
   -> text cleaning
   -> sentiment classification
   -> aspect extraction
   -> aspect-level sentiment
   -> TF-IDF + NMF topic discovery
   -> PostgreSQL analytics tables
```

The current MVP uses deterministic/rule-based sentiment and aspect dictionaries plus scikit-learn topic modeling. This avoids large model downloads during deployment and provides a stable baseline for later transformer-based upgrades.

## Demo data

Run the migration first, then execute `seed.sql`. The seed creates one demo smartphone product and six realistic reviews. Use the product ID:

`00000000-0000-0000-0000-000000000001`

Then call:

```http
POST /api/analysis/products/00000000-0000-0000-0000-000000000001
```

After analysis, the sentiment, aspect and topic endpoints can be used to populate the dashboard.
