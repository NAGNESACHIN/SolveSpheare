export function LoadingState({ text="Loading analytics…" }: { text?:string }) { return <div className="loading">{text}</div>; }
export function EmptyState({ text="No analytics available yet." }: { text?:string }) { return <div className="empty">{text}</div>; }
