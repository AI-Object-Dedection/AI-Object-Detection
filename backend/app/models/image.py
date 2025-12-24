from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import enum

from app.core.database import Base
from app.core.config import settings

class ImageStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"

class AIStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File info
    file_path = Column(String, nullable=False)
    thumbnail_path = Column(String)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    
    # Metadata
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    taken_at = Column(DateTime(timezone=True))
    
    # AI processing
    ai_status = Column(Enum(AIStatus), default=AIStatus.PENDING)
    status = Column(Enum(ImageStatus), default=ImageStatus.PENDING)
    
    # Relationships
    project = relationship("Project", back_populates="images")
    description = relationship("ImageDescription", back_populates="image", uselist=False)
    embedding = relationship("ImageEmbedding", back_populates="image", uselist=False)
    
    def __repr__(self):
        return f"<Image {self.id} - {self.original_filename}>"

class ImageDescription(Base):
    __tablename__ = "image_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), unique=True, nullable=False)
    
    # AI generated content
    model_name = Column(String, nullable=False)
    description_text = Column(Text, nullable=False)
    category = Column(String)  # Excavation, Concrete, Electrical, etc.
    
    # Optional safety analysis
    ppe_detected = Column(String)  # JSON string of detected PPE
    safety_score = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    image = relationship("Image", back_populates="description")
    
    def __repr__(self):
        return f"<ImageDescription for image={self.image_id}>"

class ImageEmbedding(Base):
    __tablename__ = "image_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), unique=True, nullable=False)
    
    # Vector embedding
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=False)
    embedding_model = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    image = relationship("Image", back_populates="embedding")
    
    def __repr__(self):
        return f"<ImageEmbedding for image={self.image_id}>"
