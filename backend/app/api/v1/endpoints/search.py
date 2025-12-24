from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.search import SearchQuery, SearchResult
from app.models.user import User
from app.services.search_service import SearchService

router = APIRouter()

@router.post("", response_model=List[SearchResult])
async def search_images(
    query_data: SearchQuery,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Semantic search through images using natural language query
    
    Example queries:
    - "concrete work in the last week"
    - "excavation with safety equipment"
    - "electrical installation on second floor"
    """
    search_service = SearchService()
    results = await search_service.semantic_search(
        query=query_data.query,
        top_k=query_data.top_k,
        filters=query_data.filters,
        user_id=user.id,
        db=db
    )
    
    return results
