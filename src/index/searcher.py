from whoosh.qparser import QueryParser
from whoosh import index


def search_query(query: str, index_dir="indexdir", limit=5):
    """
    Search the indexed PDFs for a given query string.
    Returns the top results with path and snippet.
    """
    idx = index.open_dir(index_dir)
    qp = QueryParser("content", schema=idx.schema)
    q = qp.parse(query)

    with idx.searcher() as searcher:
        results = searcher.search(q, limit=limit)
        matches = [{"path": r["path"], "snippet": r["content"][:200]} for r in results]
    return matches
