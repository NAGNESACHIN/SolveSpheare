const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { ...options, cache: "no-store" });
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  return response.json();
}

export type Product = { id: string; name: string; category?: string | null; brand?: string | null };
export type Overview = { product_id?: string | null; total_reviews: number; average_rating: number; sentiment_distribution: Record<string, number> };
export type Aspect = { aspect: string; mentions: number; average_sentiment: number };
export type Topic = { topic_id: string; name: string; keywords: Record<string, string[]>; review_count: number; average_relevance: number };
export type Review = { id: string; product_id?: string; review_text: string; title?: string | null; rating?: number | null; reviewer_name?: string | null; source?: string | null; verified_purchase?: boolean | null; review_date?: string | null };

export async function getProducts() { return request<Product[]>("/api/products"); }
export async function getOverview(productId?: string) { return request<Overview>(productId ? `/api/analytics/products/${productId}/overview` : "/api/analytics/overview"); }
export async function getAspects(productId: string) { return request<{ aspects: Aspect[] }>(`/api/analysis/products/${productId}/aspects`); }
export async function getTopics(productId: string) { return request<{ topics: Topic[] }>(`/api/analysis/products/${productId}/topics`); }
export async function getReviews(productId: string) { return request<Review[]>(`/api/reviews?product_id=${productId}`); }
export async function analyzeProduct(productId: string) { return request<{ status: string }>(`/api/analysis/products/${productId}`, { method: "POST" }); }
export async function generateInsights(productId: string) { return request<{ status: string; insights_created: number }>(`/api/insights/products/${productId}/generate`, { method: "POST" }); }

export type ReviewAnalysis = { review_id:string; sentiment:{label:string;score:number|null;positive_score:number|null;negative_score:number|null;neutral_score:number|null}|null; aspects:{name:string;mention:string|null;sentiment:string|null;score:number|null;confidence:number|null}[]; topics:{name:string;relevance:number|null;confidence:number|null}[]; ai_explanation?:{title:string;explanation:string;key_signal:string;confidence:number}|null };
export async function getReviewAnalysis(reviewId:string){return request<ReviewAnalysis>(`/api/analysis/reviews/${reviewId}`);}
