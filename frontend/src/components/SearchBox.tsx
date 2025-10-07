import { useState } from "react";
import useSearch from "../hooks/useSearch";
import { highlightQuery } from "../utils/highlight";

export default function SearchBox() {
    const [query, setQuery] = useState("");
    const [mode, setMode] = useState<"keyword" | "semantic">("keyword");
    const { results, loading, error, search } = useSearch();

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        search(query, mode);
    };

    return (
        <div className="max-w-3xl mx-auto mt-10 p-6">
            <form onSubmit={handleSearch} className="flex gap-2">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={`Search (${mode})...`}
                    className="w-full p-3 border border-gray-600 rounded-lg bg-gray-800 text-white"
                />
                <select
                    value={mode}
                    onChange={(e) => setMode(e.target.value as "keyword" | "semantic")}
                    className="p-3 bg-gray-700 text-white rounded-lg border border-gray-600"
                >
                    <option value="keyword">Keyword</option>
                    <option value="semantic">Semantic</option>
                </select>
                <button type="submit" className="bg-blue-600 px-5 py-3 rounded-lg text-white">
                    {loading ? "Searching..." : "Search"}
                </button>
            </form>

            {error && <p className="text-red-500 mt-4">{error}</p>}

            <div className="mt-6 space-y-4">
                {results.map((r, i) => (
                    <div key={i} className="p-4 bg-gray-900 border border-gray-700 rounded-lg">
                        <h3 className="font-semibold text-lg text-blue-400">{r.title}</h3>
                        <p
                            className="text-gray-300 mt-1"
                            dangerouslySetInnerHTML={{ __html: highlightQuery(r.content, query) }}
                        ></p>
                        {r.score !== undefined && (
                            <p className="text-sm text-gray-500 mt-1">Score: {r.score.toFixed(3)}</p>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
