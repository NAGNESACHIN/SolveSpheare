const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  return response.json();
}

export type Product = { id: string; name: string; category?: string | null; brand?: string | null };
export type Overview = {
  total_reviews: number;
  average_rating: number;
  sentiment_distribution: Record<string, number>;
};

export async function getProducts() {
  return request<Product[]>("/api/products");
}

export async function getOverview() {
  return request<Overview>("/api/analytics/overview");
}
