from pydantic import BaseModel
from typing import Optional, Dict, Any

class SearchQuery(BaseModel):
    query: str
    top_k: int = 50
    filters: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    image_id: int
    thumbnail_url: str
    image_url: str
    uploaded_at: str
    category: Optional[str] = None
    description: Optional[str] = None
    score: float
    ai_status: str = "done"
    
    class Config:
        from_attributes = True
