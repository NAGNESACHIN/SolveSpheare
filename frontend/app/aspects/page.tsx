"use client";
import {useEffect,useState} from "react";
import AnalyticsPage from "../../components/analytics/AnalyticsPage";
import ChartCard from "../../components/analytics/ChartCard";
import {LoadingState,EmptyState} from "../../components/analytics/States";
import {getAspects} from "../../lib/analytics-api";
import type {Aspect} from "../../types/analytics";

export default function AspectsPage(){return <AnalyticsPage title="Aspect Intelligence" description="See which product attributes drive positive and negative feedback.">{productId=><Content productId={productId}/>}</AnalyticsPage>;}
function Content({productId}:{productId:string}){const [items,setItems]=useState<Aspect[]>([]);const[loading,setLoading]=useState(true);useEffect(()=>{setLoading(true);getAspects(productId).then(r=>setItems(r.aspects)).finally(()=>setLoading(false));},[productId]);if(loading)return <LoadingState/>;if(!items.length)return <EmptyState text="Run product analysis to discover aspects."/>;return <ChartCard title="Aspect Sentiment" subtitle="Mention volume and average sentiment"><div className="aspect-list">{items.map(a=><div className="aspect-row" key={a.aspect}><span className="aspect-name">{a.aspect}</span><span className="mentions">{a.mentions} mentions</span><div className="bar"><i className={a.average_sentiment>=0?"bar-positive":"bar-negative"} style={{width:`${Math.max(8,Math.abs(a.average_sentiment)*100)}%`}}/></div><strong className={a.average_sentiment>=0?"positive-text":"negative-text"}>{a.average_sentiment>0?"+":""}{a.average_sentiment.toFixed(2)}</strong></div>)}</div></ChartCard>;}
