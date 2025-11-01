// src/hooks/useSearch.ts
import { useState } from 'react';
import { API_BASE_URL } from '../config';

// --- 1. Define the "Shapes" of our API Data ---
// These types are *only* for the POST /search endpoint.

export interface SearchResult {
    heading: string;
    text: string;
    distance: number;
    file_name: string;   // <-- NEW
    page_number: number; // <-- NEW
}

export interface SearchResponse {
    results: SearchResult[];
}

// Define what our hook will return
export interface UseSearchReturn {
    data: SearchResponse | null;
    isLoading: boolean;
    error: string | null;
    // The function our components will call
    execute: (query: string, topK?: number) => Promise<void>;
}

// --- 2. The Custom Hook ---

export function useSearch(): UseSearchReturn {
    const [data, setData] = useState<SearchResponse | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    /**
     * Executes a raw search against the /search endpoint.
     * @param query The user's search query string.
     * @param topK The number of results to return (default: 5).
     */
    const execute = async (query: string, topK: number = 5) => {
        setIsLoading(true);
        setError(null);

        const url = `${API_BASE_URL}/search`;

        // Build the request body
        const body = {
            query: query,
            top_k: topK,
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
            });

            if (!response.ok) {
                // Handle HTTP errors
                const errData = await response.json();
                throw new Error(
                    errData.detail || `HTTP Error: ${response.statusText}`
                );
            }

            const responseData = (await response.json()) as SearchResponse;
            setData(responseData);
        } catch (err) {
            if (err instanceof Error) {
                setError(err.message);
            } else {
                setError('An unknown error occurred.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return { data, isLoading, error, execute };
}