from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base

class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"

class ProjectMemberRole(str, enum.Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    members = relationship("ProjectMember", back_populates="project")
    images = relationship("Image", back_populates="project")
    
    def __repr__(self):
        return f"<Project {self.name}>"

class ProjectMember(Base):
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(ProjectMemberRole), default=ProjectMemberRole.VIEWER)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="members")
    
    def __repr__(self):
        return f"<ProjectMember project={self.project_id} user={self.user_id}>"
