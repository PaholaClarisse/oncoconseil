from pydantic import BaseModel
from datetime import datetime

class DocumentOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    nombre_chunks: int

    class Config:
        from_attributes = True