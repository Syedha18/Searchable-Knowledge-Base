from src.repositories.visual_repository import (
    insert_visual_elements,
    delete_by_pdf
)
from src.config.settings import USE_MONGODB
from datetime import datetime

def build_visual_documents(pdf_name: str, visual_results: dict):
    docs = []

    for img in visual_results.get("images", []):
        docs.append({
            "pdf_name": pdf_name,
            "page_number": img["page"],
            "type": "image",
            "filename": img["filename"],
            "file_path": img["path"],
            "caption": img.get("caption"),
            "created_at": datetime.utcnow(),
        })

    for tbl in visual_results.get("tables", []):
        docs.append({
            "pdf_name": pdf_name,
            "page_number": tbl["page"],
            "type": "table",
            "filename": tbl["filename"],
            "file_path": tbl["path"],
            "table_metadata": {
                "rows": tbl.get("rows"),
                "columns": tbl.get("columns"),
            },
            "created_at": datetime.utcnow(),
        })

    return docs
