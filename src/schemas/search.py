from pydantic import BaseModel

class SearchResult(BaseModel):
    heading: str
    text: str
    distance: float
    file_name: str     
    page_number: int
