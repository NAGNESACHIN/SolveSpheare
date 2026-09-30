"use client";

import { useEffect, useMemo, useState } from "react";
import AnalyticsPage from "../../components/analytics/AnalyticsPage";
import ChartCard from "../../components/analytics/ChartCard";
import MetricCard from "../../components/analytics/MetricCard";
import { LoadingState, EmptyState } from "../../components/analytics/States";
import { getAspects, getTopics, Aspect, Topic } from "../../lib/api";

export default function VoiceOfCustomerPage() {
  return (
    <AnalyticsPage title="Voice of Customer" description="Turn recurring customer concerns into clear product priorities.">
      {(productId) => <Content productId={productId} />}
    </AnalyticsPage>
  );
}

function Content({ productId }: { productId: string }) {
  const [aspects, setAspects] = useState<Aspect[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([getAspects(productId), getTopics(productId)])
      .then(([a, t]) => { setAspects(a.aspects); setTopics(t.topics); })
      .finally(() => setLoading(false));
  }, [productId]);

  const negative = useMemo(() => aspects.filter((a) => a.average_sentiment < 0).sort((a, b) => a.average_sentiment - b.average_sentiment), [aspects]);
  const positive = useMemo(() => aspects.filter((a) => a.average_sentiment >= 0).sort((a, b) => b.average_sentiment - a.average_sentiment), [aspects]);
  const totalMentions = aspects.reduce((sum, a) => sum + a.mentions, 0);
  const complaintMentions = negative.reduce((sum, a) => sum + a.mentions, 0);
  const complaintShare = totalMentions ? Math.round((complaintMentions / totalMentions) * 100) : 0;

  if (loading) return <LoadingState text="Analyzing the customer voice…" />;

  return (
    <>
      <div className="kpi-grid">
        <MetricCard title="Pain Points" value={String(negative.length)} meta="Negative product attributes" danger />
        <MetricCard title="Complaint Mentions" value={complaintMentions.toLocaleString()} meta="Across detected aspects" />
        <MetricCard title="Complaint Share" value={complaintShare + "%"} meta="Of all aspect mentions" danger />
        <MetricCard title="Customer Themes" value={String(topics.length)} meta="Discovered review topics" />
      </div>

      <section className="two-column">
        <ChartCard title="Top Customer Pain Points" subtitle="Prioritize attributes with negative sentiment and repeated mentions.">
          {negative.length === 0 ? <EmptyState text="No negative aspect signals detected yet." /> : (
            <div className="voc-list">
              {negative.slice(0, 8).map((item, index) => (
                <div className="voc-row" key={item.aspect}>
                  <span className="voc-rank">{index + 1}</span>
                  <div className="voc-main"><strong>{item.aspect}</strong><small>{item.mentions} mentions</small></div>
                  <div className="voc-track"><i style={{ width: Math.max(10, Math.min(100, Math.abs(item.average_sentiment) * 100)) + "%" }} /></div>
                  <strong className="negative-text">{item.average_sentiment.toFixed(2)}</strong>
                </div>
              ))}
            </div>
          )}
        </ChartCard>

        <ChartCard title="What Customers Appreciate" subtitle="Positive attributes that can be protected and reinforced.">
          {positive.length === 0 ? <EmptyState text="No positive aspect signals detected yet." /> : (
            <div className="voc-list">
              {positive.slice(0, 8).map((item) => (
                <div className="voc-row" key={item.aspect}>
                  <span className="voc-icon">✓</span>
                  <div className="voc-main"><strong>{item.aspect}</strong><small>{item.mentions} mentions</small></div>
                  <div className="voc-track positive-track"><i style={{ width: Math.max(10, Math.min(100, item.average_sentiment * 100)) + "%" }} /></div>
                  <strong className="positive-text">+{item.average_sentiment.toFixed(2)}</strong>
                </div>
              ))}
            </div>
          )}
        </ChartCard>
      </section>

      <ChartCard title="Customer Complaint Themes" subtitle="Topics that help explain the language behind recurring feedback.">
        {topics.length === 0 ? <EmptyState text="Run product analysis to discover customer themes." /> : (
          <div className="voc-topic-grid">
            {topics.slice(0, 8).map((topic) => (
              <article className="voc-topic" key={topic.topic_id}>
                <strong>{topic.name}</strong>
                <span>{topic.review_count} reviews</span>
                <small>{Object.values(topic.keywords || {}).flat().slice(0, 5).join(" · ") || "No keywords available"}</small>
              </article>
            ))}
          </div>
        )}
      </ChartCard>

      <ChartCard title="Action Priorities" subtitle="Rule-based recommendations generated from current aspect signals.">
        {negative.length === 0 ? <EmptyState text="No action priorities available until negative feedback is detected." /> : (
          <div className="priority-grid">
            {negative.slice(0, 4).map((item, index) => (
              <article className="priority-card" key={item.aspect}>
                <div className="priority-header"><span>P{index + 1}</span><strong>{item.aspect}</strong></div>
                <p>{item.mentions} customer mentions with an average sentiment of {item.average_sentiment.toFixed(2)}.</p>
                <div className="recommendation"><strong>Suggested action</strong><p>{recommendationFor(item.aspect)}</p></div>
              </article>
            ))}
          </div>
        )}
      </ChartCard>
    </>
  );
}

function recommendationFor(aspect: string) {
  const actions: Record<string, string> = {
    battery: "Investigate battery-drain patterns, power-management settings, and hardware variance in affected reviews.",
    performance: "Profile the slowest workflows and prioritize performance fixes for the scenarios customers mention most.",
    camera: "Review image quality complaints by lighting and capture scenario, then target the most repeated failure mode.",
    display: "Check brightness, color, touch response, and panel consistency against the reported customer issues.",
    design: "Group recurring usability or build-quality complaints and validate them with focused product testing.",
    price: "Compare perceived value against the features customers mention and identify the largest value gaps.",
    software: "Cluster recurring software bugs and prioritize issues that appear across multiple customer reviews.",
    delivery: "Review fulfillment and carrier performance for the affected orders and reduce repeated delivery failure points.",
    "customer service": "Audit recurring support complaints and identify response-time or resolution gaps.",
    quality: "Investigate repeated quality defects and trace them to the relevant manufacturing or QA stage."
  };
  return actions[aspect.toLowerCase()] || "Review the affected feedback, identify the recurring failure mode, and validate a targeted product or process improvement.";
}
