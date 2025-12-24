from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ImageBase(BaseModel):
    original_filename: str

class ImageUpload(BaseModel):
    project_id: int

class ImageResponse(BaseModel):
    image_id: int
    thumbnail_url: str
    image_url: str
    uploaded_at: datetime
    taken_at: Optional[datetime] = None
    status: str
    category: Optional[str] = None
    description: Optional[str] = None
    ai_status: str
    
    class Config:
        from_attributes = True

class ImageDescriptionResponse(BaseModel):
    image_id: int
    description_text: str
    category: Optional[str] = None
    ppe_detected: Optional[str] = None
    safety_score: Optional[float] = None
    
    class Config:
        from_attributes = True

class ImageDetail(ImageResponse):
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    uploader_id: int
    project_id: int
    
    class Config:
        from_attributes = True
