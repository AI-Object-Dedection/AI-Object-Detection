"""
API v1 Router - Combines all API endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth_router)

# Add more routers here as needed
# api_router.include_router(images_router, prefix="/images", tags=["Images"])
# api_router.include_router(detection_router, prefix="/detection", tags=["Detection"])
