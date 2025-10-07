from fastapi import APIRouter, Query
from src.index.semantic_searcher import SemanticSearcher

router = APIRouter()
semantic_searcher = SemanticSearcher(index_dir="semantic_index")

@router.get("/search/semantic")
def semantic_search(q: str = Query(..., min_length=1), top_k: int = 5):
    results = semantic_searcher.search(q, top_k=top_k)
    return {"query": q, "results": results}
