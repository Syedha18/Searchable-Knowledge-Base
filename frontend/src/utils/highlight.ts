export function highlightMultipleSnippets(
    text: string,
    query: string,
    snippetLength = 50,
    maxSnippets = 3
): string[] {
    if (!query) return [text.slice(0, snippetLength*2) + (text.length > snippetLength*2 ? "…" : "")];

    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
    const matches = [...text.matchAll(regex)];

    if (!matches.length) return [text.slice(0, snippetLength*2) + (text.length > snippetLength*2 ? "…" : "")];

    const snippets: string[] = [];
    let count = 0;

    for (const match of matches) {
        if (count >= maxSnippets) break;

        const start = Math.max(match.index! - snippetLength, 0);
        const end = Math.min(match.index! + query.length + snippetLength, text.length);
        let snippet = text.slice(start, end);

        // Highlight all occurrences in the snippet
        snippet = snippet.replace(regex, '<mark class="bg-yellow-400 text-black">$1</mark>');

        snippets.push(snippet);
        count++;
    }

    return snippets;
}
