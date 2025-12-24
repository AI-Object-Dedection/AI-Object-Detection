from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_project_access
from app.core.config import settings
from app.schemas.image import ImageResponse, ImageDetail
from app.models.user import User
from app.models.image import Image, ImageStatus, AIStatus
from app.services.file_service import FileService
from app.services.ai_service import AIService

router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_photos(
    files: List[UploadFile] = File(...),
    project_id: int = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload multiple photos to a project"""
    # Verify project access
    project = db.query(__import__('app.models.project', fromlist=['Project']).Project).filter(
        __import__('app.models.project', fromlist=['Project']).Project.id == project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    file_service = FileService()
    ai_service = AIService()
    uploaded_images = []
    
    for file in files:
        # Validate file
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            continue
        
        # Save file
        file_path, thumbnail_path = await file_service.save_upload(file, project_id)
        
        # Create image record
        image = Image(
            project_id=project_id,
            uploader_id=user.id,
            file_path=file_path,
            thumbnail_path=thumbnail_path,
            original_filename=file.filename,
            upload_date=datetime.utcnow(),
            ai_status=AIStatus.PENDING,
            status=ImageStatus.PENDING
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        
        # Trigger AI processing in background
        # In production, use Celery or similar
        try:
            await ai_service.process_image(image.id, db)
        except Exception as e:
            print(f"AI processing failed for image {image.id}: {e}")
        
        uploaded_images.append(image)
    
    return {
        "success": True,
        "uploaded": len(uploaded_images),
        "message": f"Successfully uploaded {len(uploaded_images)} photo(s)"
    }

@router.get("", response_model=List[ImageResponse])
async def get_photos(
    project_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get photos with optional project filter"""
    query = db.query(Image)
    
    if project_id:
        # Verify project access
        project = db.query(__import__('app.models.project', fromlist=['Project']).Project).filter(
            __import__('app.models.project', fromlist=['Project']).Project.id == project_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        query = query.filter(Image.project_id == project_id)
    
    images = query.offset(offset).limit(limit).all()
    
    # Format response
    result = []
    for img in images:
        result.append({
            "image_id": img.id,
            "thumbnail_url": f"/uploads/{img.thumbnail_path}" if img.thumbnail_path else f"/uploads/{img.file_path}",
            "image_url": f"/uploads/{img.file_path}",
            "uploaded_at": img.upload_date,
            "taken_at": img.taken_at,
            "status": img.status.value,
            "category": img.description.category if img.description else None,
            "description": img.description.description_text if img.description else None,
            "ai_status": img.ai_status.value
        })
    
    return result

@router.get("/{image_id}", response_model=ImageDetail)
async def get_photo_detail(
    image_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a photo"""
    image = db.query(Image).filter(Image.id == image_id).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Verify project access
    project = db.query(__import__('app.models.project', fromlist=['Project']).Project).filter(
        __import__('app.models.project', fromlist=['Project']).Project.id == image.project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this image"
        )
    
    return {
        "image_id": image.id,
        "thumbnail_url": f"/uploads/{image.thumbnail_path}" if image.thumbnail_path else f"/uploads/{image.file_path}",
        "image_url": f"/uploads/{image.file_path}",
        "uploaded_at": image.upload_date,
        "taken_at": image.taken_at,
        "status": image.status.value,
        "category": image.description.category if image.description else None,
        "description": image.description.description_text if image.description else None,
        "ai_status": image.ai_status.value,
        "file_size": image.file_size,
        "width": image.width,
        "height": image.height,
        "uploader_id": image.uploader_id,
        "project_id": image.project_id
    }

@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    image_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a photo"""
    image = db.query(Image).filter(Image.id == image_id).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Check if user is uploader or project owner
    project = db.query(__import__('app.models.project', fromlist=['Project']).Project).filter(
        __import__('app.models.project', fromlist=['Project']).Project.id == image.project_id
    ).first()
    
    if image.uploader_id != user.id and project.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this image"
        )
    
    # Delete file
    file_service = FileService()
    await file_service.delete_file(image.file_path)
    if image.thumbnail_path:
        await file_service.delete_file(image.thumbnail_path)
    
    db.delete(image)
    db.commit()
    
    return None
