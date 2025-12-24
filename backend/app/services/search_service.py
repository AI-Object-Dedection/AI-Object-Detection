from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.image import Image, ImageDescription, ImageEmbedding, AIStatus
from app.models.project import ProjectMember
from app.services.embedding_service import EmbeddingService
from app.schemas.search import SearchResult

class SearchService:
    """Service for semantic search functionality"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    async def semantic_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        user_id: int,
        db: Session
    ) -> List[SearchResult]:
        """
        Perform semantic search on images
        
        Args:
            query: Natural language search query
            top_k: Number of results to return
            filters: Optional filters (category, dateRange, etc.)
            user_id: ID of user performing search
            db: Database session
        
        Returns:
            List of search results with similarity scores
        """
        # Encode query
        query_embedding = self.embedding_service.encode_query(query)
        
        # Get user's accessible projects
        accessible_projects = db.query(ProjectMember.project_id).filter(
            ProjectMember.user_id == user_id
        ).all()
        project_ids = [p[0] for p in accessible_projects]
        
        # Base query - join images with embeddings and descriptions
        query_base = db.query(
            Image,
            ImageDescription,
            ImageEmbedding
        ).join(
            ImageDescription, Image.id == ImageDescription.image_id
        ).join(
            ImageEmbedding, Image.id == ImageEmbedding.image_id
        ).filter(
            and_(
                Image.ai_status == AIStatus.DONE,
                Image.project_id.in_(project_ids)
            )
        )
        
        # Apply filters
        if filters:
            # Category filter
            if filters.get('category') and filters['category'] != 'All':
                query_base = query_base.filter(
                    ImageDescription.category == filters['category']
                )
            
            # Date range filter
            if filters.get('dateRange'):
                start_date = self._parse_date_range(filters['dateRange'])
                if start_date:
                    query_base = query_base.filter(
                        Image.upload_date >= start_date
                    )
        
        # Get all candidates
        candidates = query_base.all()
        
        # Compute similarity scores
        results = []
        for image, description, embedding in candidates:
            # Compute cosine similarity
            similarity = self.embedding_service.compute_similarity(
                query_embedding,
                embedding.embedding
            )
            
            if similarity >= settings.SIMILARITY_THRESHOLD:
                results.append({
                    "image_id": image.id,
                    "thumbnail_url": f"/uploads/{image.thumbnail_path}" if image.thumbnail_path else f"/uploads/{image.file_path}",
                    "image_url": f"/uploads/{image.file_path}",
                    "uploaded_at": image.upload_date.isoformat(),
                    "category": description.category,
                    "description": description.description_text,
                    "score": float(similarity),
                    "ai_status": "done"
                })
        
        # Sort by similarity score and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def _parse_date_range(self, date_range: str) -> Optional[datetime]:
        """Parse date range string to datetime"""
        now = datetime.utcnow()
        
        if date_range == "Last 7 days":
            return now - timedelta(days=7)
        elif date_range == "Last 30 days":
            return now - timedelta(days=30)
        elif date_range == "Last 90 days":
            return now - timedelta(days=90)
        elif date_range == "Last year":
            return now - timedelta(days=365)
        
        return None
