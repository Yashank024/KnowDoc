from typing import Any, Optional
from pydantic import BaseModel

class APIResponseEnvelope(BaseModel):
    status: str # 'success' or 'error'
    message: Optional[str] = None
    data: Optional[Any] = None

class HealthStatusResponse(BaseModel):
    status: str
    engine: str
    device: str
