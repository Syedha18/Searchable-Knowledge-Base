from fastapi import APIRouter
from src.index.semantic_indexer import SemanticIndexer
from pathlib import Path

router = APIRouter()
indexer = SemanticIndexer(index_dir="semantic_index")

@router.post("/index/add")
def add_pdfs(folder_path: str):
    folder = Path(folder_path)
    if not folder.exists():
        return {"error": "Folder not found"}
    indexer.add_documents_batch(folder_path)
    return {"status": "success", "indexed_folder": str(folder_path)}
