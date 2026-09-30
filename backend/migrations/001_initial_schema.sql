CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(150), category VARCHAR(150), description TEXT,
    external_product_id VARCHAR(255), source VARCHAR(100),
    average_rating NUMERIC(3,2), review_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    external_review_id VARCHAR(255), title TEXT, review_text TEXT NOT NULL,
    rating NUMERIC(2,1), reviewer_name VARCHAR(255), verified_purchase BOOLEAN,
    review_date TIMESTAMPTZ, source VARCHAR(100), language VARCHAR(20),
    helpful_votes INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_review_source_external UNIQUE(source, external_review_id)
);
CREATE TABLE IF NOT EXISTS aspects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL, description TEXT,
    parent_aspect_id UUID REFERENCES aspects(id) ON DELETE SET NULL,
    CONSTRAINT uq_aspect_product_name UNIQUE(product_id, name)
);
CREATE TABLE IF NOT EXISTS sentiment_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    sentiment_label VARCHAR(30) NOT NULL, score NUMERIC(6,5),
    positive_score NUMERIC(6,5), negative_score NUMERIC(6,5), neutral_score NUMERIC(6,5),
    model_name VARCHAR(150), model_version VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS review_aspects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    aspect_id UUID NOT NULL REFERENCES aspects(id) ON DELETE CASCADE,
    mention_text TEXT, sentiment_label VARCHAR(30), sentiment_score NUMERIC(6,5),
    confidence NUMERIC(6,5), start_position INTEGER, end_position INTEGER,
    CONSTRAINT uq_review_aspect_mention UNIQUE(review_id, aspect_id, mention_text)
);
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL, description TEXT, topic_type VARCHAR(50), keywords JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_topic_product_name UNIQUE(product_id, name)
);
CREATE TABLE IF NOT EXISTS review_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    relevance_score NUMERIC(6,5), confidence NUMERIC(6,5),
    CONSTRAINT uq_review_topic UNIQUE(review_id, topic_id)
);
CREATE TABLE IF NOT EXISTS analysis_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_type VARCHAR(100) NOT NULL, model_name VARCHAR(150) NOT NULL,
    model_version VARCHAR(100), parameters JSONB, started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ, status VARCHAR(30) NOT NULL DEFAULT 'completed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS ai_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    review_id UUID REFERENCES reviews(id) ON DELETE SET NULL,
    aspect_id UUID REFERENCES aspects(id) ON DELETE SET NULL,
    topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
    insight_type VARCHAR(100) NOT NULL, title VARCHAR(500) NOT NULL,
    summary TEXT NOT NULL, recommendation TEXT, evidence JSONB,
    severity VARCHAR(30), confidence NUMERIC(6,5),
    model_name VARCHAR(150), model_version VARCHAR(100),
    period_start TIMESTAMPTZ, period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews(review_date);
CREATE INDEX IF NOT EXISTS idx_sentiment_review ON sentiment_scores(review_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_label ON sentiment_scores(sentiment_label);
CREATE INDEX IF NOT EXISTS idx_review_aspects_review ON review_aspects(review_id);
CREATE INDEX IF NOT EXISTS idx_review_aspects_aspect ON review_aspects(aspect_id);
CREATE INDEX IF NOT EXISTS idx_review_topics_review ON review_topics(review_id);
CREATE INDEX IF NOT EXISTS idx_review_topics_topic ON review_topics(topic_id);
CREATE INDEX IF NOT EXISTS idx_insights_product ON ai_insights(product_id);
CREATE INDEX IF NOT EXISTS idx_topics_keywords ON topics USING GIN(keywords);
CREATE INDEX IF NOT EXISTS idx_insights_evidence ON ai_insights USING GIN(evidence);
