from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.analytics import (
    Stats, Distribution, Timeline, TopCategory, AnalyticsResponse
)
from app.models.user import User
from app.models.image import Image, ImageDescription, AIStatus

router = APIRouter()

@router.get("/stats", response_model=Stats)
async def get_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall statistics"""
    total_photos = db.query(func.count(Image.id)).scalar()
    analyzed_photos = db.query(func.count(Image.id)).filter(
        Image.ai_status == AIStatus.DONE
    ).scalar()
    
    completion_rate = analyzed_photos / total_photos if total_photos > 0 else 0
    
    # Calculate delta (7 days ago vs current)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_photos = db.query(func.count(Image.id)).filter(
        Image.upload_date >= seven_days_ago
    ).scalar()
    
    delta_pct = (recent_photos / total_photos * 100) if total_photos > 0 else 0
    
    return {
        "total_photos": total_photos,
        "analyzed_photos": analyzed_photos,
        "completion_rate": completion_rate,
        "delta_total_photos_pct": delta_pct
    }

@router.get("/distribution", response_model=List[Distribution])
async def get_distribution(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get distribution of photos by category"""
    results = db.query(
        ImageDescription.category,
        func.count(ImageDescription.id).label('count')
    ).join(Image).filter(
        ImageDescription.category.isnot(None)
    ).group_by(ImageDescription.category).all()
    
    return [
        {"name": category, "value": count}
        for category, count in results
    ]

@router.get("/timeline", response_model=List[Timeline])
async def get_timeline(
    period: str = "7d",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get timeline of photo uploads"""
    # Parse period
    days = 7
    if period == "30d":
        days = 30
    elif period == "90d":
        days = 90
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get daily counts
    results = db.query(
        func.date(Image.upload_date).label('date'),
        func.count(Image.id).label('count')
    ).filter(
        Image.upload_date >= start_date
    ).group_by(func.date(Image.upload_date)).order_by(func.date(Image.upload_date)).all()
    
    return [
        {"date": date.strftime("%b %d"), "count": count}
        for date, count in results
    ]

@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete analytics data"""
    # Distribution
    distribution_data = db.query(
        ImageDescription.category,
        func.count(ImageDescription.id).label('count')
    ).join(Image).filter(
        ImageDescription.category.isnot(None)
    ).group_by(ImageDescription.category).all()
    
    distribution = [
        {"name": category, "value": count}
        for category, count in distribution_data
    ]
    
    # Timeline (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    timeline_data = db.query(
        func.date(Image.upload_date).label('date'),
        func.count(Image.id).label('count')
    ).filter(
        Image.upload_date >= seven_days_ago
    ).group_by(func.date(Image.upload_date)).order_by(func.date(Image.upload_date)).all()
    
    timeline = [
        {"date": date.strftime("%b %d"), "count": count}
        for date, count in timeline_data
    ]
    
    # Top categories with percentages
    total_photos = db.query(func.count(Image.id)).scalar()
    
    top_categories_data = db.query(
        ImageDescription.category,
        func.count(ImageDescription.id).label('count')
    ).join(Image).filter(
        ImageDescription.category.isnot(None)
    ).group_by(ImageDescription.category).order_by(
        func.count(ImageDescription.id).desc()
    ).limit(10).all()
    
    top_categories = [
        {
            "category": category,
            "count": count,
            "percentage": (count / total_photos * 100) if total_photos > 0 else 0
        }
        for category, count in top_categories_data
    ]
    
    return {
        "distribution": distribution,
        "timeline": timeline,
        "topCategories": top_categories
    }
