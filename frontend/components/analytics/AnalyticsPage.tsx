"use client";

import type React from "react";

import { useEffect, useState } from "react";
import { getProducts, Product } from "../../lib/api";
import AppShell from "../layout/AppShell";

export default function AnalyticsPage({
  title,
  description,
  children
}: {
  title: string;
  description: string;
  children: (productId: string) => React.ReactNode;
}) {
  const [products, setProducts] = useState<Product[]>([]);
  const [selected, setSelected] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getProducts()
      .then(data => {
        setProducts(data);
        if (data[0]) setSelected(data[0].id);
      })
      .catch(() => setError("Could not connect to the analytics API."));
  }, []);

  return (
    <AppShell>
      <header className="topbar">
        <div>
          <p className="eyebrow">PRODUCT INTELLIGENCE</p>
          <h1>{title}</h1>
          <p className="header-note">{description}</p>
        </div>
        <div className="product-control">
          <label>Product</label>
          <select value={selected} onChange={e => setSelected(e.target.value)}>
            {products.length === 0 && <option value="">No products</option>}
            {products.map(p => <option value={p.id} key={p.id}>{p.name}</option>)}
          </select>
        </div>
      </header>
      {error && <div className="alert">{error}</div>}
      {!selected ? <div className="loading">Loading product intelligence…</div> : children(selected)}
    </AppShell>
  );
}
