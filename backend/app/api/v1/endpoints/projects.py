from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectMemberAdd, ProjectMemberResponse
)
from app.models.user import User
from app.models.project import Project, ProjectMember, ProjectMemberRole

router = APIRouter()

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    project = Project(
        name=project_data.name,
        description=project_data.description,
        created_by=user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Add creator as owner
    member = ProjectMember(
        project_id=project.id,
        user_id=user.id,
        role=ProjectMemberRole.OWNER
    )
    db.add(member)
    db.commit()
    
    return project

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all projects user has access to"""
    # Get projects where user is creator or member
    member_projects = db.query(Project).join(ProjectMember).filter(
        ProjectMember.user_id == user.id
    ).all()
    
    return member_projects

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project details"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check access
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    return project

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project details"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if owner
    if project.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can update"
        )
    
    # Update fields
    for key, value in project_data.dict(exclude_unset=True).items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can delete"
        )
    
    db.delete(project)
    db.commit()
    
    return None

@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
async def add_project_member(
    project_id: int,
    member_data: ProjectMemberAdd,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a member to project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can add members"
        )
    
    # Check if already member
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == member_data.user_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member"
        )
    
    member = ProjectMember(
        project_id=project_id,
        user_id=member_data.user_id,
        role=member_data.role
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    
    return member
