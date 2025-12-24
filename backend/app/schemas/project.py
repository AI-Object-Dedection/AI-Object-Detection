from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    status: str
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProjectMemberAdd(BaseModel):
    user_id: int
    role: str = "viewer"

class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: str
    joined_at: datetime
    
    class Config:
        from_attributes = True
