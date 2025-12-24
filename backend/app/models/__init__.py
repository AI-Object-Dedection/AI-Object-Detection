"""
Models package initialization
Import all models here for Alembic migrations
"""
from app.core.database import Base
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.image import Image, ImageDescription, ImageEmbedding

__all__ = [
    "Base",
    "User",
    "Project",
    "ProjectMember",
    "Image",
    "ImageDescription",
    "ImageEmbedding"
]
