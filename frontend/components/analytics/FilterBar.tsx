"use client";
import type React from "react";
export default function FilterBar({search,onSearch,children}:{search?:string;onSearch?:(value:string)=>void;children?:React.ReactNode}){return <div className="filter-bar">{onSearch&&<input value={search||""} onChange={e=>onSearch(e.target.value)} placeholder="Search reviews…"/>}{children}</div>;}
