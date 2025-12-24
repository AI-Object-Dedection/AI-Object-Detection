from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
import numpy as np

from app.core.config import settings
from app.models.image import ImageEmbedding

class EmbeddingService:
    """Service for creating and managing text embeddings"""
    
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
    
    async def create_embedding(self, image_id: int, text: str, db: Session):
        """Create embedding for text and save to database"""
        try:
            # Generate embedding
            embedding_vector = self.model.encode(text)
            
            # Save to database
            embedding = ImageEmbedding(
                image_id=image_id,
                embedding=embedding_vector.tolist(),
                embedding_model=settings.EMBEDDING_MODEL
            )
            db.add(embedding)
            db.commit()
            
            return embedding
            
        except Exception as e:
            print(f"Embedding creation error: {e}")
            return None
    
    def encode_query(self, query: str) -> np.ndarray:
        """Encode search query to embedding vector"""
        return self.model.encode(query)
    
    def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
