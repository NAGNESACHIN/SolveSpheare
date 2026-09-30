import React from "react";

export default function ChartCard({ title, subtitle, children }: { title:string; subtitle?:string; children:React.ReactNode }) {
  return <section className="panel"><div className="panel-head"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div></div>{children}</section>;
}
