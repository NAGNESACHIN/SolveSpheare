"use client";
import {useEffect,useState} from "react";
import AnalyticsPage from "../../components/analytics/AnalyticsPage";
import ChartCard from "../../components/analytics/ChartCard";
import {LoadingState,EmptyState} from "../../components/analytics/States";
import {getInsights} from "../../lib/analytics-api";
import type {Insight} from "../../types/analytics";

export default function InsightsPage(){return <AnalyticsPage title="AI Insights" description="Turn review signals into evidence-backed product actions.">{productId=><Content productId={productId}/>}</AnalyticsPage>;}
function Content({productId}:{productId:string}){const[items,setItems]=useState<Insight[]>([]);const[loading,setLoading]=useState(true);useEffect(()=>{setLoading(true);getInsights(productId).then(r=>setItems(r.insights)).finally(()=>setLoading(false));},[productId]);if(loading)return <LoadingState/>;if(!items.length)return <EmptyState text="No AI insights have been generated for this product yet."/>;return <div className="insight-grid">{items.map(i=><ChartCard key={i.id} title={i.title} subtitle={`${i.insight_type} · ${i.severity||"normal"} · ${i.confidence!=null?Math.round(i.confidence*100)+"% confidence":"confidence n/a"}`}><p className="insight-summary">{i.summary}</p>{i.recommendation&&<div className="recommendation"><strong>Recommendation</strong><p>{i.recommendation}</p></div>}</ChartCard>)}</div>;}
