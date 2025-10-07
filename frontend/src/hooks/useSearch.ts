import { useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../config";

export interface SearchResult {
    rank: string;
    path: string;
    title: string;
    content: string;
    score?: number;
}

export default function useSearch() {
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const search = async (query: string, mode: "keyword" | "semantic" = "keyword") => {
        if (!query.trim()) return;
        setLoading(true);
        setError(null);
        try {
            const res = await axios.get(`${API_BASE_URL}/search/${mode}`, {
                params: { q: query },
            });
            setResults(res.data.results || []);
        } catch (err: any) {
            setError(err.message || "Search failed");
        } finally {
            setLoading(false);
        }
    };

    return { results, loading, error, search };
}
