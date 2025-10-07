export function highlightQuery(
    text: string,
    query: string,
    snippetLength = 50
): string {
    if (!query) return text;

    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
    const matches = [...text.matchAll(regex)];

    if (!matches.length) return text.slice(0, snippetLength * 2) + (text.length > snippetLength * 2 ? "…" : "");

    // Take first match for snippet
    const firstMatch = matches[0];
    const start = Math.max(firstMatch.index! - snippetLength, 0);
    const end = Math.min(firstMatch.index! + query.length + snippetLength, text.length);

    const snippet = text.slice(start, end);

    // Highlight query
    const highlighted = snippet.replace(regex, '<mark class="bg-yellow-400 text-black">$1</mark>');
    return highlighted;
}
