"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";

const items = [
  ["Overview", "/"],
  ["Reviews", "/reviews"],
  ["Sentiment", "/sentiment"],
  ["Aspects", "/aspects"],
  ["Topics", "/topics"],
  ["Voice of Customer", "/voc"],
  ["AI Insights", "/insights"]
] as const;

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span>◆</span> SolveSpheare</div>
        <nav>
          {items.map(([label, href]) => (
            <Link className={pathname === href ? "nav-item active" : "nav-item"} href={href} key={href}>
              {label}
            </Link>
          ))}
        </nav>
        <Link className="nav-item settings" href="/settings">⚙ Settings</Link>
      </aside>
      <section className="content">{children}</section>
    </main>
  );
}
