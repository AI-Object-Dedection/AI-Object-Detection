import os
import shutil
from datetime import datetime
from fastapi import UploadFile
from PIL import Image
from typing import Tuple

from app.core.config import settings

class FileService:
    """Service for handling file uploads and storage"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_upload(
        self, 
        file: UploadFile, 
        project_id: int
    ) -> Tuple[str, str]:
        """
        Save uploaded file and create thumbnail
        Returns: (file_path, thumbnail_path)
        """
        # Create project directory
        project_dir = os.path.join(self.upload_dir, f"project_{project_id}")
        os.makedirs(project_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        ext = os.path.splitext(file.filename)[1]
        filename = f"{timestamp}{ext}"
        
        file_path = os.path.join(project_dir, filename)
        
        # Save original file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create thumbnail
        thumbnail_path = await self._create_thumbnail(file_path, project_dir)
        
        # Return relative paths
        rel_file_path = os.path.join(f"project_{project_id}", filename)
        rel_thumbnail_path = os.path.join(f"project_{project_id}", os.path.basename(thumbnail_path))
        
        return rel_file_path, rel_thumbnail_path
    
    async def _create_thumbnail(
        self, 
        file_path: str, 
        output_dir: str,
        size: Tuple[int, int] = (400, 300)
    ) -> str:
        """Create thumbnail from image"""
        try:
            img = Image.open(file_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            thumbnail_filename = f"thumb_{os.path.basename(file_path)}"
            thumbnail_path = os.path.join(output_dir, thumbnail_filename)
            
            img.save(thumbnail_path, quality=85, optimize=True)
            return thumbnail_path
        except Exception as e:
            print(f"Thumbnail creation failed: {e}")
            return file_path
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            full_path = os.path.join(self.upload_dir, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
            return True
        except Exception as e:
            print(f"File deletion failed: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """Get file metadata"""
        full_path = os.path.join(self.upload_dir, file_path)
        
        if not os.path.exists(full_path):
            return {}
        
        stats = os.stat(full_path)
        
        try:
            img = Image.open(full_path)
            width, height = img.size
        except:
            width, height = None, None
        
        return {
            "size": stats.st_size,
            "width": width,
            "height": height
        }
