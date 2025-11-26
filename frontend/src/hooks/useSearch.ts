// src/hooks/useSearch.ts
import { API_BASE_URL } from '../config';

export async function searchDocuments(query: string, top_k = 10) {
    const res = await fetch(`${API_BASE_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k }),
    });

    if (!res.ok) throw new Error(`Search failed: ${res.statusText}`);
    return res.json();
}
