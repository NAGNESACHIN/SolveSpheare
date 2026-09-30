const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export async function request<T>(path:string, options:RequestInit={}) {
  const response=await fetch(`${API_URL}${path}`,{...options,cache:"no-store"});
  if(!response.ok) throw new Error(`API request failed: ${response.status}`);
  return response.json() as Promise<T>;
}
