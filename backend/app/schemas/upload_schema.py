from typing import List, Dict, Any
from pydantic import BaseModel

class OCRLineSchema(BaseModel):
    text: str
    confidence: float
    box: List[List[int]]
    page: int = 1

class UploadResponse(BaseModel):
    status: str
    document_id: str
    filename: str
    size: str
    tags: List[str]
    text_lines: List[OCRLineSchema]
    full_text: str
