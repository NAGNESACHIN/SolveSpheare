"use client";

import { useEffect, useMemo, useState } from "react";
import AnalyticsPage from "../../components/analytics/AnalyticsPage";
import ChartCard from "../../components/analytics/ChartCard";
import MetricCard from "../../components/analytics/MetricCard";
import { LoadingState, EmptyState } from "../../components/analytics/States";
import { generateInsights, getInsights } from "../../lib/analytics-api";
import type { Insight } from "../../types/analytics";

export default function InsightsPage() {
  return (
    <AnalyticsPage
      title="AI Insights"
      description="Turn review signals into evidence-backed product actions."
    >
      {productId => <Content productId={productId} />}
    </AnalyticsPage>
  );
}

function Content({ productId }: { productId: string }) {
  const [items, setItems] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    setError("");
    getInsights(productId)
      .then(r => setItems(r.insights))
      .catch(() => setError("Could not load AI insights."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [productId]);

  const highPriority = useMemo(
    () => items.filter(i => i.severity === "high").length,
    [items]
  );
  const opportunities = useMemo(
    () => items.filter(i => i.insight_type === "opportunity").length,
    [items]
  );
  const confidence = useMemo(() => {
    if (!items.length) return 0;
    return Math.round(
      (items.reduce((sum, item) => sum + (item.confidence ?? 0), 0) / items.length) * 100
    );
  }, [items]);
  const summary = items.find(i => i.insight_type === "summary");

  async function handleGenerate() {
    setGenerating(true);
    setError("");
    try {
      const result = await generateInsights(productId);
      setItems(result.insights);
    } catch {
      setError("Insight generation failed. Run product analysis first, then try again.");
    } finally {
      setGenerating(false);
    }
  }

  if (loading) return <LoadingState text="Loading AI insights…" />;

  return (
    <>
      <div className="insight-toolbar">
        <div>
          <p className="eyebrow">EVIDENCE-BACKED INTELLIGENCE</p>
          <p className="header-note">
            Generate a fresh interpretation from the product's analyzed reviews, sentiment, aspects, and topics.
          </p>
        </div>
        <button className="primary-button" onClick={handleGenerate} disabled={generating}>
          {generating ? "Generating…" : "Generate Insights"}
        </button>
      </div>

      {error && <div className="alert">{error}</div>}

      {!items.length ? (
        <ChartCard title="Ready to generate" subtitle="No insight snapshot exists for this product yet.">
          <EmptyState text="Run Generate Insights to turn your existing review analytics into summaries, pain points, opportunities, and recommendations." />
        </ChartCard>
      ) : (
        <>
          <div className="kpi-grid">
            <MetricCard title="Insights" value={String(items.length)} meta="Generated signals" />
            <MetricCard title="High Priority" value={String(highPriority)} meta="Requires attention" danger={highPriority > 0} />
            <MetricCard title="Opportunities" value={String(opportunities)} meta="Positive signals" />
            <MetricCard title="Confidence" value={`${confidence}%`} meta="Average insight confidence" />
          </div>

          {summary && (
            <ChartCard title="Executive Summary" subtitle="What the current review evidence says">
              <p className="insight-summary">{summary.summary}</p>
              {summary.recommendation && (
                <div className="recommendation">
                  <strong>Recommended focus</strong>
                  <p>{summary.recommendation}</p>
                </div>
              )}
            </ChartCard>
          )}

          <div className="insight-grid">
            {items.filter(i => i.id !== summary?.id).map(i => (
              <ChartCard
                key={i.id}
                title={i.title}
                subtitle={`${i.insight_type} · ${i.severity || "normal"} · ${i.confidence != null ? Math.round(i.confidence * 100) + "% confidence" : "confidence n/a"}`}
              >
                <p className="insight-summary">{i.summary}</p>
                {i.recommendation && (
                  <div className="recommendation">
                    <strong>Recommendation</strong>
                    <p>{i.recommendation}</p>
                  </div>
                )}
                {i.evidence && (
                  <details className="evidence-details">
                    <summary>View supporting evidence</summary>
                    <pre>{JSON.stringify(i.evidence, null, 2)}</pre>
                  </details>
                )}
              </ChartCard>
            ))}
          </div>
        </>
      )}
    </>
  );
}
