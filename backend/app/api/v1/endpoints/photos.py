"""
Photos API Endpoints - Image upload and management
"""
import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.config import settings
from app.models.photo import Photo
from app.schemas.photo import PhotoResponse, PhotoListResponse, UploadResponse
from app.api.v1.endpoints.auth import get_current_user
from app.services.analysis_service import analyze_photo, analyze_photo_by_id

router = APIRouter(prefix="/photos", tags=["Photos"])

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


def get_photo_url(filename: str) -> str:
    """Generate full URL for photo using the configured public base URL."""
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    return f"{base}/uploads/{filename}"


@router.get("", response_model=List[PhotoResponse])
async def get_photos(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get user's photos with optional filtering.
    """
    query = db.query(Photo).filter(Photo.user_id == current_user.id)
    
    if category and category != "All":
        query = query.filter(Photo.category == category)
    
    if project_id:
        query = query.filter(Photo.project_id == project_id)
    
    # Order by newest first
    query = query.order_by(desc(Photo.created_at))
    
    # Pagination
    offset = (page - 1) * per_page
    photos = query.offset(offset).limit(per_page).all()
    
    # Add URLs to photos with frontend-compatible field names
    result = []
    for photo in photos:
        photo_url = get_photo_url(photo.filename)
        result.append(PhotoResponse(
            id=photo.id,
            image_id=photo.id,
            filename=photo.filename,
            original_filename=photo.original_filename,
            file_size=photo.file_size,
            width=photo.width,
            height=photo.height,
            category=photo.category,
            description=photo.description,
            confidence=photo.confidence,
            detected_objects=photo.detected_objects,
            project_id=photo.project_id,
            tags=photo.tags,
            user_id=photo.user_id,
            created_at=photo.created_at,
            uploaded_at=photo.created_at,
            analyzed_at=photo.analyzed_at,
            url=photo_url,
            thumbnail=photo_url,
            thumbnail_url=photo_url,
            status="analyzed" if photo.category else "pending"
        ))
    
    return result


@router.post("/upload", response_model=UploadResponse)
async def upload_photos(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    project_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Upload multiple photos.
    """
    uploaded_photos = []
    errors = []
    
    for file in files:
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith("image/"):
                errors.append(f"{file.filename}: Not a valid image file")
                continue
            
            # Check file size
            contents = await file.read()
            if len(contents) > settings.MAX_UPLOAD_SIZE:
                errors.append(f"{file.filename}: File too large (max {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB)")
                continue
            
            # Generate unique filename
            ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Create database record
            db_photo = Photo(
                filename=unique_filename,
                original_filename=file.filename or "unknown",
                file_path=file_path,
                file_size=len(contents),
                mime_type=file.content_type,
                project_id=project_id,
                user_id=current_user.id
            )
            db.add(db_photo)
            db.commit()
            db.refresh(db_photo)

            # Kick off AI analysis in the background so the upload returns fast.
            # The detector (mock now, SAM3 later) fills in category/objects/etc.
            background_tasks.add_task(analyze_photo_by_id, db_photo.id)

            # Create response
            photo_response = PhotoResponse.model_validate(db_photo)
            photo_response.url = get_photo_url(unique_filename)
            photo_response.thumbnail = get_photo_url(unique_filename)
            photo_response.status = "pending"
            uploaded_photos.append(photo_response)
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    return UploadResponse(
        success=len(uploaded_photos) > 0,
        uploaded=len(uploaded_photos),
        photos=uploaded_photos,
        errors=errors
    )


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a specific photo by ID.
    """
    photo = db.query(Photo).filter(
        Photo.id == photo_id,
        Photo.user_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    photo_response = PhotoResponse.model_validate(photo)
    photo_response.url = get_photo_url(photo.filename)
    photo_response.thumbnail = get_photo_url(photo.filename)
    
    return photo_response


@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a photo.
    """
    photo = db.query(Photo).filter(
        Photo.id == photo_id,
        Photo.user_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Delete file from disk
    if os.path.exists(photo.file_path):
        os.remove(photo.file_path)
    
    # Delete from database
    db.delete(photo)
    db.commit()

    return {"success": True, "message": "Photo deleted"}


@router.post("/{photo_id}/analyze", response_model=PhotoResponse)
async def analyze_photo_endpoint(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Run (or re-run) AI detection on a single photo and return the updated record.

    Uses whichever detector is active (DETECTOR_BACKEND): the mock detector now,
    the trained SAM3 model once it is connected.
    """
    photo = db.query(Photo).filter(
        Photo.id == photo_id,
        Photo.user_id == current_user.id
    ).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        photo = analyze_photo(photo, db)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    photo_response = PhotoResponse.model_validate(photo)
    photo_response.url = get_photo_url(photo.filename)
    photo_response.thumbnail = get_photo_url(photo.filename)
    photo_response.status = "analyzed" if photo.category else "pending"
    return photo_response
