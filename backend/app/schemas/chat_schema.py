from typing import List, Optional
from pydantic import BaseModel

class ChatQueryRequest(BaseModel):
    message: str
    doc_ids: Optional[List[str]] = None

class CitationSchema(BaseModel):
    source_index: int
    filename: str
    pages: List[int]

class ChatQueryResponse(BaseModel):
    reply: str
    citations: List[CitationSchema]
    chunks_searched: int
