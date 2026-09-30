"use client";

import { useEffect, useState } from "react";
import { getOverview, getProducts, Product, Overview } from "../lib/api";

const demoSentiment = [
  { label: "Positive", value: 68, className: "positive" },
  { label: "Neutral", value: 18, className: "neutral" },
  { label: "Negative", value: 14, className: "negative" }
];

const aspects = [
  ["Battery", 124, 0.72],
  ["Display", 98, 0.81],
  ["Performance", 87, 0.61],
  ["Camera", 76, 0.18],
  ["Price", 65, -0.41],
  ["Delivery", 52, -0.63]
];

export default function Dashboard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [selected, setSelected] = useState("");

  useEffect(() => {
    Promise.all([getProducts(), getOverview()])
      .then(([productData, overviewData]) => {
        setProducts(productData);
        setOverview(overviewData);
        if (productData[0]) setSelected(productData[0].id);
      })
      .catch(() => undefined);
  }, []);

  const sentiment = overview?.sentiment_distribution ?? {};
  const total = overview?.total_reviews ?? 0;
  const rating = overview?.average_rating ?? 0;

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
          </div>
          <div className="product-control">
            <label>Product</label>
            <select value={selected} onChange={(e) => setSelected(e.target.value)}>
              {products.map((p) => <option value={p.id} key={p.id}>{p.name}</option>)}
            </select>
            <button className="primary">Analyze Product</button>
          </div>
        </header>

        <section className="kpi-grid">
          <Kpi title="Total Reviews" value={total.toLocaleString()} meta="Customer feedback" />
          <Kpi title="Average Rating" value={rating ? `${rating.toFixed(1)} ★` : "—"} meta="Out of 5" />
          <Kpi title="Positive Sentiment" value={`${sentiment.positive ?? 0}%`} meta="Overall sentiment" />
          <Kpi title="Negative Sentiment" value={`${sentiment.negative ?? 0}%`} meta="Needs attention" danger />
        </section>

        <section className="two-column">
          <Panel title="Sentiment Overview" subtitle="Customer emotional response">
            <div className="sentiment-layout">
              <div className="donut" style={{ background: `conic-gradient(var(--positive) 0 ${sentiment.positive ?? 0}%, var(--neutral) ${sentiment.positive ?? 0}% ${(sentiment.positive ?? 0) + (sentiment.neutral ?? 0)}%, var(--negative) ${(sentiment.positive ?? 0) + (sentiment.neutral ?? 0)}% 100%)` }}>
                <div><strong>{sentiment.positive ?? 0}%</strong><span>Positive</span></div>
              </div>
              <div className="legend">
                {demoSentiment.map((s) => <div className="legend-row" key={s.label}><span className={`dot ${s.className}`} />{s.label}<strong>{sentiment[s.label.toLowerCase()] ?? s.value}%</strong></div>)}
              </div>
            </div>
          </Panel>

          <Panel title="Voice of Customer" subtitle="Recurring customer pain points">
            <div className="pain-list">
              {["Slow charging", "Delivery delays", "Software issues", "Price / value"].map((x, i) => (
                <div className="pain" key={x}><span className={i < 2 ? "severity high" : "severity medium"}>!</span><div><strong>{x}</strong><small>{[84,61,47,39][i]} mentions</small></div></div>
              ))}
            </div>
            <button className="text-button">View all complaints →</button>
          </Panel>
        </section>

        <Panel title="Aspect Sentiment" subtitle="What customers feel about each product attribute">
          <div className="aspect-list">
            {aspects.map(([name, mentions, score]) => {
              const n = Number(score);
              const width = Math.max(8, Math.round(Math.abs(n) * 100));
              return <div className="aspect-row" key={String(name)}>
                <span className="aspect-name">{name}</span><span className="mentions">{String(mentions)} mentions</span>
                <div className="bar"><i className={n >= 0 ? "bar-positive" : "bar-negative"} style={{ width: `${width}%` }} /></div>
                <strong className={n >= 0 ? "score positive-text" : "score negative-text"}>{n > 0 ? "+" : ""}{n.toFixed(2)}</strong>
              </div>;
            })}
          </div>
        </Panel>

        <section className="two-column bottom">
          <Panel title="Customer Topics" subtitle="Automatically discovered themes">
            <div className="topic-grid">{["🔋 Battery", "📱 Camera", "⚡ Performance", "💰 Price", "📦 Delivery", "⚙ Software"].map(t => <div className="topic" key={t}>{t}<span>View topic →</span></div>)}</div>
          </Panel>
          <Panel title="Recent Reviews" subtitle="Latest customer feedback">
            <div className="review-list">
              <Review stars="★★★★★" text="Excellent battery life and display." sentiment="Positive" />
              <Review stars="★★☆☆☆" text="Package arrived late and damaged." sentiment="Negative" />
              <Review stars="★★★★☆" text="Great performance for the price." sentiment="Positive" />
            </div>
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

function Review({ stars, text, sentiment }: { stars: string; text: string; sentiment: string }) {
  return <div className="review"><div><span className="stars">{stars}</span><strong>{text}</strong></div><span className={sentiment === "Positive" ? "pill positive-pill" : "pill negative-pill"}>{sentiment}</span></div>;
}
