export type SentimentResponse = { product_id:string; distribution:Record<string,number> };
export type Aspect = { aspect:string; mentions:number; average_sentiment:number };
export type Topic = { topic_id:string; name:string; keywords:Record<string,string[]>; review_count:number; average_relevance:number };
export type Insight = { id:string; insight_type:string; title:string; summary:string; recommendation?:string|null; severity?:string|null; confidence?:number|null; evidence?:unknown };
