"use client";

import { useEffect, useState } from "react";
import {
  getAspects,
  getOverview,
  getProducts,
  getReviews,
  getTopics,
  analyzeProduct,
  generateInsights,
  Aspect,
  Overview,
  Product,
  Review,
  Topic
} from "../lib/api";

export default function Dashboard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selected, setSelected] = useState("");
  const [overview, setOverview] = useState<Overview | null>(null);
  const [aspects, setAspects] = useState<Aspect[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState("");

  useEffect(() => {
    getProducts()
      .then((data) => {
        setProducts(data);
        if (data[0]) setSelected(data[0].id);
      })
      .catch(() => setError("Could not connect to the analytics API."));
  }, []);

  const loadDashboard = () => {
    if (!selected) return;
    setLoading(true);
    setError("");
    Promise.all([
      getOverview(selected),
      getAspects(selected),
      getTopics(selected),
      getReviews(selected)
    ])
      .then(([overviewData, aspectData, topicData, reviewData]) => {
        setOverview(overviewData);
        setAspects(aspectData.aspects);
        setTopics(topicData.topics);
        setReviews(reviewData.slice(0, 5));
      })
      .catch(() => setError("Some dashboard data could not be loaded. Run product analysis first."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDashboard();
  }, [selected]);

  const runFullAnalysis = async () => {
    if (!selected || analyzing) return;
    setAnalyzing(true);
    setError("");
    setAnalysisStatus("Analyzing reviews, sentiment, aspects, and topics…");
    try {
      await analyzeProduct(selected);
      setAnalysisStatus("Generating evidence-backed AI insights…");
      await generateInsights(selected);
      setAnalysisStatus("Refreshing dashboard…");
      await loadDashboard();
      setAnalysisStatus("Analysis complete.");
      window.setTimeout(() => setAnalysisStatus(""), 2500);
    } catch {
      setError("Product intelligence generation failed. Check the backend logs and try again.");
      setAnalysisStatus("");
    } finally {
      setAnalyzing(false);
    }
  };

  const distribution = overview?.sentiment_distribution ?? {};
  const totalAnalyzed = Object.values(distribution).reduce((sum, value) => sum + value, 0);
  const positive = totalAnalyzed ? Math.round(((distribution.positive ?? 0) / totalAnalyzed) * 100) : 0;
  const neutral = totalAnalyzed ? Math.round(((distribution.neutral ?? 0) / totalAnalyzed) * 100) : 0;
  const negative = totalAnalyzed ? Math.max(0, 100 - positive - neutral) : 0;

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span>◆</span> SolveSpheare</div>
        <nav>
          {["Overview", "Reviews", "Sentiment", "Aspects", "Topics", "Voice of Customer", "AI Insights"].map((item, i) => (
            <button className={i === 0 ? "nav-item active" : "nav-item"} key={item}>{item}</button>
          ))}
        </nav>
        <button className="nav-item settings">⚙ Settings</button>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">PRODUCT INTELLIGENCE</p>
            <h1>Customer Voice Dashboard</h1>
            <p className="header-note">Turn customer reviews into product decisions.</p>
          </div>
          <div className="product-control">
            <label>Product</label>
            <select value={selected} onChange={(e) => setSelected(e.target.value)}>
              {products.length === 0 && <option value="">No products</option>}
              {products.map((p) => <option value={p.id} key={p.id}>{p.name}</option>)}
            </select>
            <button className="primary" onClick={runFullAnalysis} disabled={analyzing}>{analyzing ? "Analyzing…" : "Analyze Product"}</button>
          </div>
        </header>

        {error && <div className="alert">{error}</div>}
        {analysisStatus && <div className="loading">{analysisStatus}</div>}
        {loading && !analyzing && <div className="loading">Loading product intelligence…</div>}

        <section className="kpi-grid">
          <Kpi title="Total Reviews" value={(overview?.total_reviews ?? 0).toLocaleString()} meta="Customer feedback" />
          <Kpi title="Average Rating" value={overview?.average_rating ? `${overview.average_rating.toFixed(1)} ★` : "—"} meta="Out of 5" />
          <Kpi title="Positive Sentiment" value={`${positive}%`} meta={`${distribution.positive ?? 0} analyzed reviews`} />
          <Kpi title="Negative Sentiment" value={`${negative}%`} meta={`${distribution.negative ?? 0} analyzed reviews`} danger />
        </section>

        <section className="two-column">
          <Panel title="Sentiment Overview" subtitle="Customer emotional response">
            <div className="sentiment-layout">
              <div className="donut" style={{ background: `conic-gradient(var(--positive) 0 ${positive}%, var(--neutral) ${positive}% ${positive + neutral}%, var(--negative) ${positive + neutral}% 100%)` }}>
                <div><strong>{positive}%</strong><span>Positive</span></div>
              </div>
              <div className="legend">
                <Legend label="Positive" value={positive} className="positive" />
                <Legend label="Neutral" value={neutral} className="neutral" />
                <Legend label="Negative" value={negative} className="negative" />
              </div>
            </div>
          </Panel>

          <Panel title="Voice of Customer" subtitle="Highest-frequency customer concerns">
            {aspects.length === 0 ? <Empty text="Run analysis to discover customer pain points." /> : (
              <div className="pain-list">
                {aspects.filter(a => a.average_sentiment < 0).slice(0, 4).map((a) => (
                  <div className="pain" key={a.aspect}><span className="severity high">!</span><div><strong>{a.aspect}</strong><small>{a.mentions} mentions · sentiment {a.average_sentiment.toFixed(2)}</small></div></div>
                ))}
                {aspects.every(a => a.average_sentiment >= 0) && <Empty text="No negative aspect signals detected." />}
              </div>
            )}
            <button className="text-button">View all complaints →</button>
          </Panel>
        </section>

        <Panel title="Aspect Sentiment" subtitle="What customers feel about each product attribute">
          {aspects.length === 0 ? <Empty text="No aspect analysis available yet." /> : (
            <div className="aspect-list">
              {aspects.slice(0, 8).map((item) => {
                const n = item.average_sentiment;
                const width = Math.max(8, Math.round(Math.abs(n) * 100));
                return (
                  <div className="aspect-row" key={item.aspect}>
                    <span className="aspect-name">{item.aspect}</span>
                    <span className="mentions">{item.mentions} mentions</span>
                    <div className="bar"><i className={n >= 0 ? "bar-positive" : "bar-negative"} style={{ width: `${width}%` }} /></div>
                    <strong className={n >= 0 ? "score positive-text" : "score negative-text"}>{n > 0 ? "+" : ""}{n.toFixed(2)}</strong>
                  </div>
                );
              })}
            </div>
          )}
        </Panel>

        <section className="two-column bottom">
          <Panel title="Customer Topics" subtitle="Automatically discovered themes">
            {topics.length === 0 ? <Empty text="No topics discovered yet." /> : (
              <div className="topic-grid">
                {topics.slice(0, 6).map((topic) => (
                  <div className="topic" key={topic.topic_id}>
                    <strong>{topic.name}</strong>
                    <small>{topic.review_count} reviews · relevance {topic.average_relevance.toFixed(2)}</small>
                    <span>{Object.values(topic.keywords || {}).flat().slice(0, 4).join(" · ") || "View topic"} →</span>
                  </div>
                ))}
              </div>
            )}
          </Panel>

          <Panel title="Recent Reviews" subtitle="Latest customer feedback">
            {reviews.length === 0 ? <Empty text="No reviews found for this product." /> : (
              <div className="review-list">
                {reviews.map((review) => (
                  <Review key={review.id} review={review} />
                ))}
              </div>
            )}
          </Panel>
        </section>
      </section>
    </main>
  );
}

function Kpi({ title, value, meta, danger = false }: { title: string; value: string; meta: string; danger?: boolean }) {
  return <article className={danger ? "kpi danger" : "kpi"}><span>{title}</span><strong>{value}</strong><small>{meta}</small></article>;
}

function Panel({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return <section className="panel"><div className="panel-head"><div><h2>{title}</h2><p>{subtitle}</p></div></div>{children}</section>;
}

function Legend({ label, value, className }: { label: string; value: number; className: string }) {
  return <div className="legend-row"><span className={`dot ${className}`} />{label}<strong>{value}%</strong></div>;
}

function Review({ review }: { review: Review }) {
  const rating = review.rating ?? 0;
  return <div className="review"><div><span className="stars">{rating ? "★".repeat(Math.round(rating)) + "☆".repeat(5 - Math.round(rating)) : "—"}</span><strong>{review.title || review.review_text.slice(0, 70)}</strong></div><span className="pill">{review.source || "Review"}</span></div>;
}

function Empty({ text }: { text: string }) {
  return <div className="empty">{text}</div>;
}
