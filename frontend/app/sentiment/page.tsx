"use client";
import {useEffect,useState} from "react";
import AnalyticsPage from "../../components/analytics/AnalyticsPage";
import ChartCard from "../../components/analytics/ChartCard";
import MetricCard from "../../components/analytics/MetricCard";
import {LoadingState,EmptyState} from "../../components/analytics/States";
import {getSentiment} from "../../lib/analytics-api";

export default function SentimentPage(){return <AnalyticsPage title="Sentiment Intelligence" description="Measure customer emotional response across reviews.">{productId=><SentimentContent productId={productId}/>}</AnalyticsPage>;}
function SentimentContent({productId}:{productId:string}){
 const [data,setData]=useState<Record<string,number>|null>(null); const [loading,setLoading]=useState(true); const [error,setError]=useState("");
 useEffect(()=>{setLoading(true);getSentiment(productId).then(r=>setData(r.distribution)).catch(()=>setError("Sentiment data could not be loaded.")).finally(()=>setLoading(false));},[productId]);
 if(loading)return <LoadingState/>; if(error)return <div className="alert">{error}</div>; if(!data)return <EmptyState/>;
 const total=Object.values(data).reduce((a,b)=>a+b,0)||1, pos=data.positive||0, neu=data.neutral||0, neg=data.negative||0;
 return <><section className="kpi-grid"><MetricCard title="Analyzed Reviews" value={String(total)} meta="Reviews with sentiment"/><MetricCard title="Positive" value={`${Math.round(pos/total*100)}%`} meta={`${pos} reviews`}/><MetricCard title="Neutral" value={`${Math.round(neu/total*100)}%`} meta={`${neu} reviews`}/><MetricCard title="Negative" value={`${Math.round(neg/total*100)}%`} meta={`${neg} reviews`} danger/></section><ChartCard title="Sentiment Distribution" subtitle="Current product-level sentiment"><div className="analytics-bars">{[["Positive",pos,"bar-positive"],["Neutral",neu,"bar-neutral"],["Negative",neg,"bar-negative"]].map(([label,value,cls])=><div className="analytics-bar-row" key={String(label)}><strong>{label}</strong><div className="bar"><i className={String(cls)} style={{width:`${Number(value)/total*100}%`}}/></div><span>{String(value)}</span></div>)}</div></ChartCard></>;
}
