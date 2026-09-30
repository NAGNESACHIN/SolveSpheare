export default function MetricCard({ title, value, meta, danger=false }: { title:string; value:string; meta?:string; danger?:boolean }) {
  return <article className={danger ? "kpi danger" : "kpi"}><span>{title}</span><strong>{value}</strong>{meta && <small>{meta}</small>}</article>;
}
