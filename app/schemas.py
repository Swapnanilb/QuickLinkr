from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
import re

class URLCreate(BaseModel):
    url: str
    custom_code: Optional[str] = None
    expires_in_days: Optional[int] = None
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        # Basic URL pattern validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # host...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_pattern.match(v):
            raise ValueError('Invalid URL format')
        return v

class URLResponse(BaseModel):
    short_url: str
    qr_code: str

class URLInfo(BaseModel):
    original_url: str
    short_code: str
    clicks: int
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AnalyticsData(BaseModel):
    total_urls: int
    total_clicks: int
    clicks_today: int
    clicks_this_week: int
    top_urls: List[dict]
    daily_clicks: List[dict]

class BulkURLCreate(BaseModel):
    urls: List[str]

class BulkURLResponse(BaseModel):
    results: List[URLResponse]