from fastapi import APIRouter

from app.api.v1.endpoints import auth, projects, photos, search, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(photos.router, prefix="/photos", tags=["photos"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
