from fastapi import APIRouter, Query
from src.index.searcher import search_query

router = APIRouter()

@router.get("/search/keyword")
def keyword_search(q: str = Query(..., min_length=1), limit: int = 5):
    results = search_query(q, index_dir="indexdir", limit=limit)
    return {"query": q, "results": results}
