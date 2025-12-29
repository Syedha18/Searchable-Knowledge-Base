from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime

class VisualElement(BaseModel):
    pdf_name: str
    page_number: int
    type: Literal["image", "table"]
    filename: str
    file_path: Optional[str]

    caption: Optional[str] = None
    content_summary: Optional[str] = None

    table_metadata: Optional[dict] = None

    created_at: datetime
