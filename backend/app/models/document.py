from typing import List, Dict, Any
from pydantic import BaseModel

class OCRLine(BaseModel):
    text: str
    confidence: float
    box: List[List[int]]
    page: int = 1

class Document(BaseModel):
    id: str
    filename: str
    size: str
    date: str
    tags: List[str]
    status: str = "Indexed"
    full_text: str = ""
    text_lines: List[OCRLine] = []
