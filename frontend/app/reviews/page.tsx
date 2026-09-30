"use client";
import {useEffect,useMemo,useState} from "react";
import AnalyticsPage from "../../components/analytics/AnalyticsPage";
import ChartCard from "../../components/analytics/ChartCard";
import FilterBar from "../../components/analytics/FilterBar";
import {LoadingState,EmptyState} from "../../components/analytics/States";
import {getReviews,Review} from "../../lib/api";

export default function ReviewsPage(){return <AnalyticsPage title="Reviews Explorer" description="Search, filter, and inspect the customer feedback behind your analytics.">{productId=><Content productId={productId}/>}</AnalyticsPage>;}

function Content({productId}:{productId:string}){
 const[items,setItems]=useState<Review[]>([]),[loading,setLoading]=useState(true),[search,setSearch]=useState(""),[rating,setRating]=useState("all"),[selected,setSelected]=useState<Review|null>(null);
 useEffect(()=>{setLoading(true);getReviews(productId).then(setItems).finally(()=>setLoading(false));},[productId]);
 const filtered=useMemo(()=>items.filter(r=>(!search||`${r.title||""} ${r.review_text} ${r.reviewer_name||""}`.toLowerCase().includes(search.toLowerCase()))&&(rating==="all"||String(Math.round(r.rating||0))===rating)),[items,search,rating]);
 if(loading)return <LoadingState text="Loading customer reviews…"/>;
 return <><ChartCard title="Customer Reviews" subtitle={`${filtered.length} of ${items.length} reviews shown`}><FilterBar search={search} onSearch={setSearch}><select value={rating} onChange={e=>setRating(e.target.value)}><option value="all">All ratings</option>{[5,4,3,2,1].map(n=><option key={n} value={n}>{n} stars</option>)}</select></FilterBar>{!filtered.length?<EmptyState text="No reviews match the current filters."/>:<div className="review-table">{filtered.map(r=><button className="review-row" key={r.id} onClick={()=>setSelected(r)}><div><span className="stars">{r.rating? "★".repeat(Math.round(r.rating)):"—"}</span><strong>{r.title||r.review_text.slice(0,80)}</strong><p>{r.review_text.slice(0,150)}{r.review_text.length>150?"…":""}</p></div><span className="pill">{r.source||"Review"}</span></button>)}</div>}</ChartCard>{selected&&<div className="drawer-backdrop" onClick={()=>setSelected(null)}><aside className="review-drawer" onClick={e=>e.stopPropagation()}><button className="drawer-close" onClick={()=>setSelected(null)}>×</button><p className="eyebrow">REVIEW DETAIL</p><h2>{selected.title||"Customer Review"}</h2><div className="stars">{selected.rating? "★".repeat(Math.round(selected.rating)):"No rating"}</div><p className="drawer-text">{selected.review_text}</p><div className="drawer-meta"><span>Reviewer: {selected.reviewer_name||"Anonymous"}</span><span>Source: {selected.source||"Unknown"}</span><span>Verified: {selected.verified_purchase==null?"Unknown":selected.verified_purchase?"Yes":"No"}</span></div></aside></div>}</>;
}