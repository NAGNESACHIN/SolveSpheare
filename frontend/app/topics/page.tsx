"use client";
import {useEffect,useState} from "react";
import AnalyticsPage from "../../components/analytics/AnalyticsPage";
import ChartCard from "../../components/analytics/ChartCard";
import {LoadingState,EmptyState} from "../../components/analytics/States";
import {getTopics} from "../../lib/analytics-api";
import type {Topic} from "../../types/analytics";

export default function TopicsPage(){return <AnalyticsPage title="Topic Intelligence" description="Discover recurring themes and emerging customer conversations.">{productId=><Content productId={productId}/>}</AnalyticsPage>;}
function Content({productId}:{productId:string}){const[items,setItems]=useState<Topic[]>([]);const[loading,setLoading]=useState(true);useEffect(()=>{setLoading(true);getTopics(productId).then(r=>setItems(r.topics)).finally(()=>setLoading(false));},[productId]);if(loading)return <LoadingState/>;if(!items.length)return <EmptyState text="Run product analysis to discover customer topics."/>;return <ChartCard title="Customer Topics" subtitle="Automatically discovered themes"><div className="topic-grid">{items.map(t=><article className="topic" key={t.topic_id}><strong>{t.name}</strong><small>{t.review_count} reviews · relevance {t.average_relevance.toFixed(2)}</small><span>{Object.values(t.keywords||{}).flat().slice(0,5).join(" · ")||"No keywords"} →</span></article>)}</div></ChartCard>;}
