from pydantic import BaseModel
from typing import List, Optional

class Stats(BaseModel):
    total_photos: int
    analyzed_photos: int
    completion_rate: float
    delta_total_photos_pct: float

class Distribution(BaseModel):
    name: str
    value: int

class Timeline(BaseModel):
    date: str
    count: int

class TopCategory(BaseModel):
    category: str
    count: int
    percentage: float

class AnalyticsResponse(BaseModel):
    distribution: List[Distribution]
    timeline: List[Timeline]
    topCategories: List[TopCategory]
