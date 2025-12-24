from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.user import User
from app.models.project import Project, ProjectMember

async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

async def verify_project_access(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    """Verify user has access to project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is creator or member
    is_creator = project.created_by == user.id
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user.id
    ).first() is not None
    
    if not (is_creator or is_member):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    return project
