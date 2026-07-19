from typing import List, Optional
from pydantic import BaseModel

class Folder(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    document_ids: List[str] = []
