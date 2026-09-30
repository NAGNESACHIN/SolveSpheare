import { request } from "./request";
import type { Aspect, Insight, SentimentResponse, Topic } from "../types/analytics";

export async function getSentiment(productId:string){return request<SentimentResponse>(`/api/analysis/products/${productId}/sentiment`);}
export async function getAspects(productId:string){return request<{product_id:string;aspects:Aspect[]}>(`/api/analysis/products/${productId}/aspects`);}
export async function getTopics(productId:string){return request<{product_id:string;topics:Topic[]}>(`/api/analysis/products/${productId}/topics`);}
export async function getInsights(productId:string){return request<{product_id:string;insights:Insight[]}>(`/api/insights/products/${productId}`);}
export async function analyzeProduct(productId:string){return request<{status:string}>(`/api/analysis/products/${productId}`,{method:"POST"});}
